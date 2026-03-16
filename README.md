# AI Sports Coach

A multi-sport AI coaching platform that analyzes athlete technique from video using custom-trained pose estimation models. Users select a sport, upload a video, and receive biomechanical analysis with coaching tips, a 0-100 score with A-F grading, and sport-specific drills.

The system uses a custom ResNet-50 backbone with a keypoint regression head, trained with Wing Loss on sport-specific labeled data. A confidence-weighted scoring system prioritizes high-accuracy body keypoints over noisier equipment predictions, ensuring reliable coaching even as models improve.

## Supported Sports

| Sport | sport_id | Key Metrics | Model Status |
|-------|----------|-------------|--------------|
| Snowboarding | `snowboard` | Knee flexion, shoulder alignment, stance width | Trained (10 keypoints, ~56px avg error) |
| Skiing | `skiing` | Knee angle, hip alignment, ski parallelism, pole position | Trained (14 keypoints, ~67px avg error) |

Additional sports (running, home workouts, yoga, golf) have coaching logic implemented but use mock estimators pending model training.

## Key Features

- **Custom pose estimation models** per sport with ResNet-50 backbone, frozen early layers, and Wing Loss
- **Confidence-weighted scoring** -- body keypoints (high confidence) drive the score; equipment predictions (lower accuracy) are shown as informational tips
- **Sport-aware data pipeline** -- automated labeling with MediaPipe + CV-based equipment detection, per-sport bodypart configs
- **CLIP-based scene detection** warns if video doesn't match selected sport
- **A-F scoring** with severity-weighted per-category penalties and configurable score weights
- **Difficulty-leveled drills** (beginner/intermediate/advanced)
- **WebSocket push notifications** with polling fallback
- **Tiered accounts:** Free (1 saved video/sport) and Pro ($9.99/mo, 50 saved/sport)
- **Admin dashboard:** user management, analytics, discount codes
- **Stripe payments** with webhook handling
- **Mobile-responsive dark theme UI**
- **10-language i18n** with browser auto-detection

## Tech Stack

- **Backend:** FastAPI, Python 3.12, PyTorch (ResNet-50), OpenCV, SQLAlchemy, Stripe
- **Frontend:** React 19, TypeScript, Vite 7, Tailwind CSS 4, Framer Motion, react-i18next
- **ML Pipeline:** ResNet-50 with frozen backbone + Wing Loss, differential learning rates, cosine annealing with warm restarts, sport-aware auto-labeling (MediaPipe + CV)
- **Auth:** JWT (python-jose), PBKDF2-SHA256, Google/Facebook OAuth stubs
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **i18n:** 10 languages (en, fr, es, it, ja, de, de-AT, ru, hi, cs)

## Model Architecture

```
ResNet-50 Backbone
├── Frozen layers (conv1 → layer3) — ImageNet features, no gradient
├── Layer4 — fine-tuned at 0.01x learning rate
└── Regression Head
    ├── Linear(2048 → 1024) + BatchNorm + ReLU + Dropout(0.3)
    ├── Linear(1024 → 512) + BatchNorm + ReLU + Dropout(0.2)
    └── Linear(512 → N*2) + clamp(0, 1)
```

- **Loss:** Wing Loss (w=0.1, epsilon=0.02) — better gradients for small keypoint errors than MSE
- **Optimizer:** AdamW with differential LR (1e-5 backbone, 1e-3 head)
- **Scheduler:** Cosine annealing with warm restarts (T_0=20, T_mult=2) + 5-epoch linear warmup
- **Augmentation:** Horizontal flip with keypoint swap, rotation (±15°), brightness/contrast jitter, hue/saturation shift, Gaussian blur, cutout occlusion

## Project Structure

```
ai-sports-analysis/
├── backend/           # FastAPI + ML inference + coaching engine
│   ├── app/
│   │   ├── routers/   # analyze, auth, sports, payments, admin, videos
│   │   ├── services/  # inference, scene_detection, video_processor
│   │   │   └── coach_logic/  # base + per-sport coaching modules
│   │   ├── sports/    # SportRegistry + per-sport definitions
│   │   ├── tasks/     # async analysis with file-backed TaskStore
│   │   └── models/    # Pydantic schemas
│   └── tests/         # 118+ tests (e2e, quality, performance, unit)
├── frontend/          # React 19 SPA
│   ├── src/
│   │   ├── components/  # UploadZone, ResultsView, coaching cards, illustrations
│   │   ├── pages/       # Pricing, Admin (lazy-loaded)
│   │   ├── data/        # sport definitions, coaching guidance
│   │   └── services/    # API client with JWT interceptor
│   └── public/locales/  # 10 languages x 2 namespaces
├── training/          # PyTorch training scripts + per-sport configs
│   └── configs/       # snowboard.json, skiing.json (keypoints, input size, swap pairs)
├── data-collection/   # yt-dlp + motion-based frame extraction
├── dlc-config/        # Sport-aware auto-labeling (MediaPipe + CV board/ski detection)
├── models/            # Trained .pt model checkpoints
├── docs/              # ARCHITECTURE.md, DESIGN.md
└── labeled-data/      # Per-sport/per-video labeled frames with DLC-compatible CSVs
```

## Architecture Highlights

- **SportRegistry pattern:** Each sport registers a `SportDefinition` and `SportCoach`, making the system extensible to new sports without modifying core logic.
- **Confidence-weighted coaching:** Tips from equipment keypoints (ski tips, board endpoints, poles) are marked `confidence: low` with reduced `score_weight` (0.3-0.4x), preventing noisy predictions from unfairly penalizing the score.
- **Per-sport coach modules** in `app/services/coach_logic/` (`base.py` plus `snowboard.py`, `skiing.py`, etc.) encapsulate sport-specific biomechanical rules with configurable thresholds.
- **Inference strategy pattern:** `PyTorchPoseEstimator` (real models) and `MockPoseEstimator` (development), selected at runtime based on model file availability.
- **Sport-aware labeling pipeline:** `auto_label.py` uses MediaPipe with per-sport bodypart mappings; `auto_label_board.py` uses CV contour analysis for equipment endpoints (board nose/tail, ski tips/tails).
- **File-backed TaskStore** with in-memory cache for async analysis job tracking.
- **CLIP scene detection** uses ViT-B-32 to compare uploaded video frames against sport-specific text prompts.

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env  # edit with your settings
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev  # Vite dev server on :5173, proxies to :8000
```

### Training a Model

```bash
# 1. Collect frames from YouTube videos
python3 data-collection/collect_frames.py --sport skiing

# 2. Auto-label body keypoints with MediaPipe
python3 dlc-config/auto_label.py --sport skiing

# 3. Auto-label equipment endpoints (skis, board) with CV
python3 dlc-config/auto_label_board.py --sport skiing

# 4. Train the model
python3 training/train.py --sport skiing
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL` -- database connection string
- `JWT_SECRET` -- secret key for JWT token signing
- `STRIPE_SECRET_KEY` -- Stripe API secret key
- `STRIPE_WEBHOOK_SECRET` -- Stripe webhook endpoint secret
- `STRIPE_PRICE_ID_PRO` -- Stripe price ID for Pro tier
- `GOOGLE_CLIENT_ID` -- Google OAuth client ID
- `FACEBOOK_APP_ID` -- Facebook OAuth app ID
- `VITE_API_URL` -- API base URL for the frontend

## Running Tests

### Backend (118+ tests)

```bash
cd backend
python3 -m pytest tests/ -v
```

Test suites: end-to-end analysis (50), coaching quality (29), performance benchmarks (9), unit tests (30+).

### Frontend

```bash
cd frontend
npx vitest run
```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Design Document](docs/DESIGN.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

MIT License. Copyright 2025 Anurodh Srivastava. See [LICENSE](LICENSE) for details.
