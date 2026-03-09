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
        self.features = nn.Sequential(*list(backbone.children())[:-1])
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(2048, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, num_keypoints * 2),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.head(self.features(x))


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
    """Mock estimator for development/testing when no trained model is available."""

    def __init__(self, sport_definition: SportDefinition | None = None):
        self._definition = sport_definition

    def predict_frame(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]
        if self._definition and self._definition.mock_keypoints_fn:
            return self._definition.mock_keypoints_fn(w, h)

        # Fallback: generic centered pose
        n = self._definition.num_keypoints if self._definition else 10
        cx, cy = w / 2, h / 2
        kp = np.zeros((n, 3))
        for i in range(n):
            kp[i] = [cx + np.random.normal(0, 30), cy + np.random.normal(0, 50), 0.9]
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
