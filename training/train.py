"""
Multi-Sport PyTorch Pose Estimation Training Script

Trains a ResNet-50 backbone with keypoint regression heads.
Supports multiple sports via --sport flag, loading per-sport configs.

Works on CPU (local testing) or CUDA/MPS (GPU training).
Reads labels directly from labeled-data/{sport}/*/labels.csv files.
"""

import argparse
import csv
import json
import os
import random
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

import torchvision.models as models
import torchvision.transforms as T

PROJECT_ROOT = Path(__file__).parent.parent


def load_sport_config(sport: str) -> dict:
    config_path = Path(__file__).parent / "configs" / f"{sport}.json"
    if not config_path.exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


class SportKeypointDataset(Dataset):
    """Dataset that loads frames and keypoint labels from labeled-data/*/labels.csv."""

    def __init__(self, samples, num_keypoints, swap_pairs, input_size, transform=None, augment=False):
        self.samples = samples
        self.num_keypoints = num_keypoints
        self.swap_pairs = swap_pairs
        self.input_size = input_size
        self.transform = transform
        self.augment = augment

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, keypoints, mask = self.samples[idx]

        img = cv2.imread(img_path)
        if img is None:
            raise RuntimeError(f"Failed to load image: {img_path}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img = cv2.resize(img, (self.input_size[1], self.input_size[0]))

        kps = keypoints.copy()

        if self.augment and random.random() > 0.5:
            img = np.fliplr(img).copy()
            kps[:, 0] = 1.0 - kps[:, 0]

            for i, j in self.swap_pairs:
                kps[[i, j]] = kps[[j, i]]
                mask[[i, j]] = mask[[j, i]]

        if self.augment:
            if random.random() > 0.5:
                factor = random.uniform(0.8, 1.2)
                img = np.clip(img * factor, 0, 255).astype(np.uint8)
            if random.random() > 0.5:
                factor = random.uniform(0.8, 1.2)
                mean = img.mean()
                img = np.clip((img - mean) * factor + mean, 0, 255).astype(np.uint8)

        img_tensor = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
        if self.transform:
            img_tensor = self.transform(img_tensor)

        kps_tensor = torch.from_numpy(kps.flatten()).float()
        mask_tensor = torch.from_numpy(np.repeat(mask, 2)).float()

        return img_tensor, kps_tensor, mask_tensor


def load_labels(labeled_data_dir: Path, num_keypoints: int, min_keypoints: int = 4):
    samples = []

    for folder in sorted(labeled_data_dir.iterdir()):
        if not folder.is_dir():
            continue

        csv_path = folder / "labels.csv"
        if not csv_path.exists():
            continue

        with open(csv_path) as f:
            reader = csv.reader(f)
            rows = list(reader)

        if len(rows) < 4:
            continue

        for row in rows[3:]:
            if not row or not row[0].strip():
                continue

            frame_name = row[0].strip()
            img_path = folder / frame_name

            if not img_path.exists():
                continue

            values = row[1:]
            keypoints = np.zeros((num_keypoints, 2), dtype=np.float64)
            mask = np.zeros(num_keypoints, dtype=bool)

            img = cv2.imread(str(img_path))
            if img is None:
                continue
            orig_h, orig_w = img.shape[:2]

            for bp_idx in range(num_keypoints):
                x_idx = bp_idx * 2
                y_idx = bp_idx * 2 + 1

                if x_idx < len(values) and y_idx < len(values):
                    x_str = values[x_idx].strip()
                    y_str = values[y_idx].strip()

                    if x_str and y_str:
                        try:
                            x = float(x_str)
                            y = float(y_str)
                            keypoints[bp_idx] = [x / orig_w, y / orig_h]
                            mask[bp_idx] = True
                        except ValueError:
                            pass

            n_labeled = mask.sum()
            if n_labeled >= min_keypoints:
                samples.append((str(img_path), keypoints, mask))

    return samples


class PoseEstimationModel(nn.Module):
    """ResNet-50 backbone with keypoint regression head."""

    def __init__(self, num_keypoints: int = 10, pretrained: bool = True):
        super().__init__()

        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        backbone = models.resnet50(weights=weights)

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
        features = self.features(x)
        return self.head(features)


def masked_mse_loss(pred, target, mask):
    diff = (pred - target) ** 2
    masked_diff = diff * mask
    n_labeled = mask.sum()
    if n_labeled == 0:
        return torch.tensor(0.0, device=pred.device)
    return masked_diff.sum() / n_labeled


def train_one_epoch(model, dataloader, optimizer, device):
    model.train()
    total_loss = 0.0
    n_batches = 0

    for imgs, kps, masks in dataloader:
        imgs = imgs.to(device)
        kps = kps.to(device)
        masks = masks.to(device)

        optimizer.zero_grad()
        pred = model(imgs)
        loss = masked_mse_loss(pred, kps, masks)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / max(n_batches, 1)


@torch.no_grad()
def evaluate(model, dataloader, device, num_keypoints, input_size):
    model.eval()
    total_loss = 0.0
    n_batches = 0

    kp_errors = np.zeros(num_keypoints)
    kp_counts = np.zeros(num_keypoints)

    for imgs, kps, masks in dataloader:
        imgs = imgs.to(device)
        kps = kps.to(device)
        masks = masks.to(device)

        pred = model(imgs)
        loss = masked_mse_loss(pred, kps, masks)
        total_loss += loss.item()
        n_batches += 1

        pred_np = pred.cpu().numpy().reshape(-1, num_keypoints, 2)
        kps_np = kps.cpu().numpy().reshape(-1, num_keypoints, 2)
        masks_np = masks.cpu().numpy().reshape(-1, num_keypoints, 2)[:, :, 0]

        pred_px = pred_np.copy()
        pred_px[:, :, 0] *= input_size[1]
        pred_px[:, :, 1] *= input_size[0]

        kps_px = kps_np.copy()
        kps_px[:, :, 0] *= input_size[1]
        kps_px[:, :, 1] *= input_size[0]

        dist = np.sqrt(((pred_px - kps_px) ** 2).sum(axis=-1))

        for bp_idx in range(num_keypoints):
            labeled = masks_np[:, bp_idx] > 0
            if labeled.any():
                kp_errors[bp_idx] += dist[labeled, bp_idx].sum()
                kp_counts[bp_idx] += labeled.sum()

    avg_loss = total_loss / max(n_batches, 1)

    with np.errstate(divide="ignore", invalid="ignore"):
        avg_kp_errors = np.where(kp_counts > 0, kp_errors / kp_counts, 0)

    return avg_loss, avg_kp_errors


def main():
    parser = argparse.ArgumentParser(description="Train multi-sport pose estimation model")
    parser.add_argument("--sport", type=str, required=True, help="Sport name (snowboard, skiing, running, home_workout)")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--val-split", type=float, default=0.2, help="Validation split ratio")
    parser.add_argument("--min-keypoints", type=int, default=4, help="Min labeled keypoints per frame")
    parser.add_argument("--patience", type=int, default=15, help="Early stopping patience")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for model")
    parser.add_argument("--no-pretrained", action="store_true", help="Don't use ImageNet pretrained weights")
    args = parser.parse_args()

    config = load_sport_config(args.sport)
    num_keypoints = config["num_keypoints"]
    input_size = tuple(config["input_size"])
    swap_pairs = [tuple(p) for p in config["swap_pairs"]]
    bodyparts = config["bodyparts"]

    print("=" * 60)
    print(f"Sports Coach AI - {args.sport.title()} Pose Estimation Training")
    print("=" * 60)
    print(f"Keypoints: {num_keypoints}, Input: {input_size}")

    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"Device: CUDA ({torch.cuda.get_device_name(0)})")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Device: Apple MPS")
    else:
        device = torch.device("cpu")
        print("Device: CPU (training will be slow)")

    labeled_data_dir = PROJECT_ROOT / "labeled-data" / args.sport
    if not labeled_data_dir.exists():
        labeled_data_dir = PROJECT_ROOT / "labeled-data"

    print(f"\nLoading labels from {labeled_data_dir}...")
    samples = load_labels(labeled_data_dir, num_keypoints, min_keypoints=args.min_keypoints)
    print(f"Found {len(samples)} usable frames (>= {args.min_keypoints} keypoints each)")

    if len(samples) < 5:
        print("ERROR: Not enough labeled frames for training. Need at least 5.")
        sys.exit(1)

    random.seed(42)
    indices = list(range(len(samples)))
    random.shuffle(indices)
    n_val = max(1, int(len(samples) * args.val_split))
    val_indices = indices[:n_val]
    train_indices = indices[n_val:]

    train_samples = [samples[i] for i in train_indices]
    val_samples = [samples[i] for i in val_indices]
    print(f"Train: {len(train_samples)} frames, Val: {len(val_samples)} frames")

    normalize = T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    train_dataset = SportKeypointDataset(
        train_samples, num_keypoints, swap_pairs, input_size, transform=normalize, augment=True
    )
    val_dataset = SportKeypointDataset(
        val_samples, num_keypoints, swap_pairs, input_size, transform=normalize, augment=False
    )

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)

    model = PoseEstimationModel(
        num_keypoints=num_keypoints,
        pretrained=not args.no_pretrained,
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\nModel: ResNet-50 + Regression Head")
    print(f"Parameters: {total_params:,} total, {trainable_params:,} trainable")

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5, verbose=True,
    )

    output_dir = Path(args.output_dir) if args.output_dir else PROJECT_ROOT / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nTraining for up to {args.epochs} epochs (patience={args.patience})...")
    print("-" * 60)

    best_val_loss = float("inf")
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "val_pixel_errors": []}

    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, device)
        val_loss, val_kp_errors = evaluate(model, val_loader, device, num_keypoints, input_size)
        mean_pixel_error = val_kp_errors[val_kp_errors > 0].mean() if (val_kp_errors > 0).any() else 0

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_pixel_errors"].append(val_kp_errors.tolist())

        lr = optimizer.param_groups[0]["lr"]
        print(
            f"Epoch {epoch:3d}/{args.epochs} | "
            f"Train Loss: {train_loss:.6f} | "
            f"Val Loss: {val_loss:.6f} | "
            f"Pixel Err: {mean_pixel_error:.1f}px | "
            f"LR: {lr:.2e}"
        )

        scheduler.step(val_loss)

        if val_loss < best_val_loss - 1e-6:
            best_val_loss = val_loss
            patience_counter = 0

            checkpoint = {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": val_loss,
                "val_pixel_errors": val_kp_errors.tolist(),
                "bodyparts": bodyparts,
                "input_size": input_size,
                "sport": args.sport,
            }
            torch.save(checkpoint, output_dir / f"best_model_{args.sport}.pt")
            print(f"  -> Saved best model (val_loss={val_loss:.6f})")
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                print(f"\nEarly stopping at epoch {epoch} (no improvement for {args.patience} epochs)")
                break

    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"Best validation loss: {best_val_loss:.6f}")

    checkpoint = torch.load(output_dir / f"best_model_{args.sport}.pt", weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    _, final_errors = evaluate(model, val_loader, device, num_keypoints, input_size)

    print(f"\nPer-keypoint pixel errors (at {input_size[1]}x{input_size[0]}):")
    for bp_idx, bp_name in enumerate(bodyparts):
        err = final_errors[bp_idx]
        if err > 0:
            print(f"  {bp_name:20s}: {err:.1f} px")
        else:
            print(f"  {bp_name:20s}: N/A (no val samples)")

    with open(output_dir / f"training_history_{args.sport}.json", "w") as f:
        json.dump(history, f, indent=2)

    model_filename = config.get("model_filename", f"{args.sport}_pose_model.pt")
    export_path = output_dir / model_filename
    torch.save({
        "model_state_dict": model.state_dict(),
        "bodyparts": bodyparts,
        "input_size": input_size,
        "best_val_loss": best_val_loss,
        "best_epoch": checkpoint["epoch"],
        "sport": args.sport,
    }, export_path)
    print(f"\nExported inference model: {export_path}")
    print(f"Training history: {output_dir / f'training_history_{args.sport}.json'}")


if __name__ == "__main__":
    main()
