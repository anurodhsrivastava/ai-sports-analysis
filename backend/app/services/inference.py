"""
Pose Estimation Inference Service
Extracts keypoints from video frames using the trained PyTorch model.

Performance features:
- Batch inference (configurable batch_size) -- Fix #1
- FP16 half-precision on CUDA/MPS -- Fix #2
- Eager model loading + warmup -- Fix #5
- Proxy video downscale for faster frame I/O
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn

from ..sports.base import SportDefinition

# Input size must match training (H, W)
INPUT_SIZE = (256, 384)

# ImageNet normalization constants (pre-allocated)
_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
_STD = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

# Proxy downscale threshold
_PROXY_HEIGHT = 480


def _create_proxy_video(video_path: Path, orig_height: int) -> Path | None:
    if orig_height <= _PROXY_HEIGHT:
        return None
    if not shutil.which("ffmpeg"):
        return None

    proxy = Path(tempfile.mktemp(suffix=".mp4"))
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", str(video_path),
                "-vf", f"scale=-2:{_PROXY_HEIGHT}",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
                "-an", "-y", str(proxy),
            ],
            check=True,
            capture_output=True,
        )
        print(f"Proxy video created: {orig_height}p -> {_PROXY_HEIGHT}p")
        return proxy
    except (subprocess.CalledProcessError, FileNotFoundError):
        proxy.unlink(missing_ok=True)
        return None


class _PoseModel(nn.Module):
    """ResNet-50 backbone with keypoint regression head (matches training arch)."""

    def __init__(self, num_keypoints: int = 10):
        super().__init__()
        import torchvision.models as models

        backbone = models.resnet50(weights=None)
        children = list(backbone.children())
        self.frozen_backbone = nn.Sequential(*children[:7])
        self.layer4 = children[7]
        self.avgpool = children[8]
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(2048, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(512, num_keypoints * 2),
        )

    def forward(self, x):
        x = self.frozen_backbone(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = self.head(x)
        return torch.clamp(x, 0.0, 1.0)


class PyTorchPoseEstimator:
    """Pose estimator using the trained PyTorch ResNet-50 model."""

    def __init__(self, model_path: str | Path, num_keypoints: int = 10):
        self.model_path = Path(model_path)
        self._num_keypoints = num_keypoints
        self._model: _PoseModel | None = None
        self._device: torch.device | None = None
        self._use_fp16: bool = False

    def _init_model(self) -> None:
        if self._model is not None:
            return

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Train a model first with training/train.py"
            )

        if torch.cuda.is_available():
            self._device = torch.device("cuda")
            self._use_fp16 = True
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self._device = torch.device("mps")
            self._use_fp16 = True
        else:
            self._device = torch.device("cpu")
            self._use_fp16 = False

        checkpoint = torch.load(
            self.model_path, map_location=self._device, weights_only=True
        )
        self._model = _PoseModel(num_keypoints=self._num_keypoints).to(self._device)
        self._model.load_state_dict(checkpoint["model_state_dict"])
        self._model.eval()

        if self._use_fp16:
            self._model = self._model.half()

        print(
            f"Loaded pose model from {self.model_path} on {self._device}"
            f" (fp16={self._use_fp16}, keypoints={self._num_keypoints})"
        )

    def warmup(self) -> None:
        self._init_model()
        dummy = torch.randn(1, 3, INPUT_SIZE[0], INPUT_SIZE[1]).to(self._device)
        if self._use_fp16:
            dummy = dummy.half()
        with torch.no_grad():
            self._model(dummy)
        print("Model warmup complete")

    def _preprocess_frame(self, frame: np.ndarray) -> torch.Tensor:
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (INPUT_SIZE[1], INPUT_SIZE[0]))
        t = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
        t = (t - _MEAN) / _STD
        return t

    @torch.no_grad()
    def predict_batch(self, frames: list[np.ndarray]) -> list[np.ndarray]:
        self._init_model()

        tensors: list[torch.Tensor] = []
        sizes: list[tuple[int, int]] = []

        for frame in frames:
            h, w = frame.shape[:2]
            sizes.append((h, w))
            tensors.append(self._preprocess_frame(frame))

        batch = torch.stack(tensors).to(self._device)
        if self._use_fp16:
            batch = batch.half()

        preds = self._model(batch).float().cpu().numpy()

        results: list[np.ndarray] = []
        for i, (h, w) in enumerate(sizes):
            pred = preds[i].reshape(self._num_keypoints, 2)
            kp = np.zeros((self._num_keypoints, 3))
            kp[:, 0] = pred[:, 0] * w
            kp[:, 1] = pred[:, 1] * h
            kp[:, 2] = 0.9
            results.append(kp)

        return results

    @torch.no_grad()
    def predict_frame(self, frame: np.ndarray) -> np.ndarray:
        return self.predict_batch([frame])[0]

    def predict_video(
        self,
        video_path: str | Path,
        sample_rate: int = 3,
        batch_size: int = 8,
    ) -> tuple[list[np.ndarray], list[int], float]:
        self._init_model()

        cap_orig = cv2.VideoCapture(str(video_path))
        if not cap_orig.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        fps = cap_orig.get(cv2.CAP_PROP_FPS) or 30.0
        orig_w = int(cap_orig.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_h = int(cap_orig.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap_orig.release()

        proxy_path = _create_proxy_video(Path(video_path), orig_h)
        use_proxy = proxy_path is not None
        read_path = str(proxy_path) if use_proxy else str(video_path)

        try:
            cap = cv2.VideoCapture(read_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {read_path}")

            proxy_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            proxy_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            all_keypoints: list[np.ndarray] = []
            frame_indices: list[int] = []
            batch_frames: list[np.ndarray] = []
            batch_indices: list[int] = []
            frame_idx = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % sample_rate == 0:
                    batch_frames.append(frame)
                    batch_indices.append(frame_idx)

                    if len(batch_frames) >= batch_size:
                        results = self.predict_batch(batch_frames)
                        all_keypoints.extend(results)
                        frame_indices.extend(batch_indices)
                        batch_frames = []
                        batch_indices = []

                frame_idx += 1

            if batch_frames:
                results = self.predict_batch(batch_frames)
                all_keypoints.extend(results)
                frame_indices.extend(batch_indices)

            cap.release()

            if use_proxy and (proxy_w != orig_w or proxy_h != orig_h):
                scale_x = orig_w / proxy_w
                scale_y = orig_h / proxy_h
                for kp in all_keypoints:
                    kp[:, 0] *= scale_x
                    kp[:, 1] *= scale_y

        finally:
            if use_proxy and proxy_path:
                proxy_path.unlink(missing_ok=True)

        return all_keypoints, frame_indices, fps


class MockPoseEstimator:
    """Mock estimator for development/testing when no trained model is available.

    Uses frame-level visual features (brightness, edge density, spatial
    distribution of motion) to seed keypoint positions so that different
    videos produce meaningfully different coaching results.
    """

    def __init__(self, sport_definition: SportDefinition | None = None):
        self._definition = sport_definition
        self._prev_gray: np.ndarray | None = None

    @staticmethod
    def _frame_features(frame: np.ndarray, prev_gray: np.ndarray | None):
        """Extract cheap visual features from a frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Brightness and contrast
        brightness = float(np.mean(gray)) / 255.0  # 0-1
        contrast = float(np.std(gray)) / 128.0      # ~0-1

        # Edge density (proxy for texture / detail)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = float(np.sum(edges > 0)) / (h * w)

        # Inter-frame motion magnitude
        motion = 0.0
        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            motion = float(np.mean(diff)) / 255.0

        # Centre of brightness mass (indicates where the subject is)
        moments = cv2.moments(gray)
        if moments["m00"] > 0:
            cx_ratio = moments["m10"] / moments["m00"] / w
            cy_ratio = moments["m01"] / moments["m00"] / h
        else:
            cx_ratio, cy_ratio = 0.5, 0.5

        return gray, brightness, contrast, edge_density, motion, cx_ratio, cy_ratio

    def predict_frame(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]
        gray, brightness, contrast, edge_density, motion, cx_r, cy_r = (
            self._frame_features(frame, self._prev_gray)
        )
        self._prev_gray = gray

        # Use detected centre-of-mass as body centre instead of frame centre
        cx = w * np.clip(cx_r, 0.2, 0.8)
        cy = h * np.clip(cy_r, 0.2, 0.8)

        sport_id = self._definition.sport_id if self._definition else ""

        if sport_id == "snowboard":
            return self._mock_snowboard(w, h, cx, cy, brightness, contrast, edge_density, motion)
        elif sport_id == "skiing":
            return self._mock_skiing(w, h, cx, cy, brightness, contrast, edge_density, motion)

        # Fallback: use mock_keypoints_fn but perturb based on frame
        if self._definition and self._definition.mock_keypoints_fn:
            kp = self._definition.mock_keypoints_fn(w, h)
            # Perturb using frame features so different frames give different poses
            noise_scale = 15.0 + motion * 80.0 + (1.0 - contrast) * 30.0
            kp[:, :2] += np.random.normal(0, noise_scale, kp[:, :2].shape)
            return kp

        n = self._definition.num_keypoints if self._definition else 10
        kp = np.zeros((n, 3))
        for i in range(n):
            kp[i] = [cx + np.random.normal(0, 30), cy + np.random.normal(0, 50), 0.9]
        return kp

    def _mock_snowboard(
        self, w, h, cx, cy, brightness, contrast, edge_density, motion
    ) -> np.ndarray:
        """Generate snowboard keypoints influenced by frame features.

        Key idea:
        - More motion -> more dynamic pose -> knees more/less bent
        - Higher contrast -> cleaner detection -> less noise
        - Brightness affects which "phase" of a turn we simulate
        """
        # Simulate different riding stances based on frame features
        # motion drives knee angle: high motion = extended (bad), low = flexed (good)
        knee_extend = motion * 60 + brightness * 20  # 0-80 range of extension
        # shoulder rotation driven by brightness variation
        shoulder_twist = brightness * 25 + edge_density * 40  # degrees

        # Base body proportions relative to frame
        body_h = h * 0.6
        shoulder_w = w * 0.08

        head_y = cy - body_h * 0.42
        shoulder_y = cy - body_h * 0.30
        hip_y = cy - body_h * 0.03
        knee_y = cy + body_h * 0.18 - knee_extend * 0.3  # higher knees when extended
        ankle_y = cy + body_h * 0.35
        board_y = cy + body_h * 0.40

        # Shoulder twist -> lateral offset
        twist_offset = shoulder_twist * 0.4

        kp = np.array([
            [cx, head_y, 0.95],                                          # head
            [cx - shoulder_w - twist_offset, shoulder_y, 0.92],          # nose_shoulder
            [cx + shoulder_w + twist_offset, shoulder_y, 0.91],          # tail_shoulder
            [cx, hip_y, 0.93],                                           # center_hips
            [cx - w * 0.06, knee_y, 0.88],                              # front_knee
            [cx + w * 0.06, knee_y, 0.87],                              # back_knee
            [cx - w * 0.08, ankle_y, 0.85],                             # front_ankle
            [cx + w * 0.08, ankle_y, 0.84],                             # back_ankle
            [cx - w * 0.14, board_y, 0.90],                             # board_nose
            [cx + w * 0.14, board_y, 0.89],                             # board_tail
        ], dtype=np.float64)

        # Small random noise scaled by contrast (clearer image = less noise)
        noise = 2.0 + (1.0 - contrast) * 5.0
        kp[:, :2] += np.random.normal(0, noise, kp[:, :2].shape)
        return kp

    def _mock_skiing(
        self, w, h, cx, cy, brightness, contrast, edge_density, motion
    ) -> np.ndarray:
        """Generate skiing keypoints influenced by frame features."""
        knee_extend = motion * 50 + brightness * 25
        hip_twist = brightness * 20 + edge_density * 30
        body_h = h * 0.6

        head_y = cy - body_h * 0.42
        shoulder_y = cy - body_h * 0.30
        hip_y = cy - body_h * 0.03
        knee_y = cy + body_h * 0.18 - knee_extend * 0.25
        ankle_y = cy + body_h * 0.35
        pole_y = cy + body_h * 0.10

        # Ski tips
        ski_spread = w * 0.05 + edge_density * w * 0.08  # parallelism degrades with edge density

        # Must match skiing BODYPART_INDICES order (14 keypoints):
        # head, left_shoulder, right_shoulder, center_hips,
        # left_knee, right_knee, left_ankle, right_ankle,
        # left_ski_tip, left_ski_tail, right_ski_tip, right_ski_tail,
        # left_pole_tip, right_pole_tip
        kp = np.array([
            [cx, head_y, 0.95],                                    # 0: head
            [cx - w * 0.07, shoulder_y, 0.92],                     # 1: left_shoulder
            [cx + w * 0.07, shoulder_y, 0.91],                     # 2: right_shoulder
            [cx, hip_y, 0.93],                                     # 3: center_hips
            [cx - w * 0.05, knee_y, 0.88],                        # 4: left_knee
            [cx + w * 0.05, knee_y, 0.87],                        # 5: right_knee
            [cx - w * 0.06, ankle_y, 0.85],                       # 6: left_ankle
            [cx + w * 0.06, ankle_y, 0.84],                       # 7: right_ankle
            [cx - w * 0.06 - ski_spread, ankle_y + 10, 0.82],     # 8: left_ski_tip
            [cx - w * 0.06, ankle_y + 30, 0.80],                  # 9: left_ski_tail
            [cx + w * 0.06 + ski_spread, ankle_y + 10, 0.81],     # 10: right_ski_tip
            [cx + w * 0.06, ankle_y + 30, 0.79],                  # 11: right_ski_tail
            [cx - w * 0.04, pole_y, 0.80],                        # 12: left_pole_tip
            [cx + w * 0.04, pole_y, 0.79],                        # 13: right_pole_tip
        ], dtype=np.float64)

        noise = 2.0 + (1.0 - contrast) * 5.0
        kp[:, :2] += np.random.normal(0, noise, kp[:, :2].shape)
        return kp

    def predict_video(
        self,
        video_path: str | Path,
        sample_rate: int = 3,
        batch_size: int = 8,
    ) -> tuple[list[np.ndarray], list[int], float]:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        all_keypoints: list[np.ndarray] = []
        frame_indices: list[int] = []
        frame_idx = 0
        self._prev_gray = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % sample_rate == 0:
                keypoints = self.predict_frame(frame)
                all_keypoints.append(keypoints)
                frame_indices.append(frame_idx)
            frame_idx += 1

        cap.release()
        return all_keypoints, frame_indices, fps


# Estimator cache per sport
_estimator_cache: dict[str, PyTorchPoseEstimator | MockPoseEstimator] = {}


def create_estimator(sport_id: str) -> PyTorchPoseEstimator | MockPoseEstimator:
    """Factory: create or retrieve a cached estimator for a sport."""
    if sport_id in _estimator_cache:
        return _estimator_cache[sport_id]

    from ..config import settings
    from ..sports.registry import SportRegistry

    definition = SportRegistry.get_definition(sport_id)
    model_path = settings.models_dir / definition.model_filename

    if model_path.exists() and str(model_path).endswith(".pt"):
        estimator = PyTorchPoseEstimator(model_path, num_keypoints=definition.num_keypoints)
    else:
        print(
            f"Model not found at {model_path} for {sport_id}, using mock estimator. "
            "Train and export a model for real inference."
        )
        estimator = MockPoseEstimator(definition)

    _estimator_cache[sport_id] = estimator
    return estimator
