# ⚙️ QR Sentinel — Setup Guide

## Prerequisites

| Tool | Minimum Version | Download |
|---|---|---|
| Python | 3.10+ | https://python.org/downloads |
| Node.js | 18+ | https://nodejs.org |
| Git | Any | https://git-scm.com |
| Docker (optional) | 24+ | https://docker.com |

---

## Windows — Step-by-Step Setup

### 1. Clone the Repository

```powershell
git clone <repository-url>
cd "QR_scam Detector"
```

### 2. Create Python Virtual Environment

```powershell
python -m venv venv
```

Verify it was created:

```powershell
dir venv\Scripts\python.exe
```

### 3. Activate Virtual Environment

```powershell
venv\Scripts\activate
```

Your prompt should change to show `(venv)`.

### 4. Install Backend Dependencies

```powershell
pip install -r backend\requirements.txt
```

> [!NOTE]
> `pyzbar` requires `zbar` native libraries. On Windows, the Python `pyzbar` package bundles the DLLs automatically — no additional installation needed.

### 5. Train the ML Model

```powershell
python backend\ml\train.py
```

Expected output:

```
[INFO] Generating synthetic dataset (10000 samples)...
[INFO] Training RandomForestClassifier...
[INFO] Training LogisticRegression...
[INFO] Best model: RandomForest (F1=0.954)
[INFO] Calibrating model...
[INFO] Saving artifacts to backend/models/
[INFO] Training complete. Metrics saved to backend/models/training_metrics.json
```

### 6. Install Frontend Dependencies

Open a **second terminal**:

```powershell
cd "QR_scam Detector\frontend"
npm install
```

### 7. Start the Backend

In terminal 1 (with venv active):

```powershell
venv\Scripts\uvicorn backend.main:app --reload --port 8000
```

Verify: open http://localhost:8000/api/v1/system/health in your browser.

### 8. Start the Frontend

In terminal 2:

```powershell
cd "QR_scam Detector\frontend"
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## macOS — Step-by-Step Setup

### 1. Install system dependencies

```bash
brew install zbar
```

### 2. Clone and set up

```bash
git clone <repository-url>
cd "QR_scam Detector"

python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

python backend/ml/train.py
```

### 3. Frontend

```bash
cd frontend && npm install && cd ..
```

### 4. Run

```bash
# Terminal 1 (backend):
uvicorn backend.main:app --reload --port 8000

# Terminal 2 (frontend):
cd frontend && npm run dev
```

---

## Linux — Step-by-Step Setup

### 1. Install system dependencies

**Debian / Ubuntu:**

```bash
sudo apt-get update
sudo apt-get install -y libzbar0 libzbar-dev python3-venv python3-pip
```

**Fedora / RHEL / CentOS:**

```bash
sudo dnf install -y zbar python3-virtualenv python3-pip
```

### 2. Clone and set up

```bash
git clone <repository-url>
cd "QR_scam Detector"

python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

python backend/ml/train.py
```

### 3. Frontend

```bash
cd frontend && npm install && cd ..
```

### 4. Run

```bash
# Terminal 1 (backend):
uvicorn backend.main:app --reload --port 8000

# Terminal 2 (frontend):
cd frontend && npm run dev
```

---

## Model Training Command Reference

```bash
# Train (creates/overwrites backend/models/)
python backend/ml/train.py

# Evaluate existing model
python backend/ml/evaluate.py

# Force retrain with custom sample count (if supported)
python backend/ml/train.py --samples 20000
```

---

## Docker Compose Instructions

The easiest way to run the full stack:

```bash
# Build images and start services (from project root)
docker-compose up --build

# Run in the background
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

Services:

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| Frontend | http://localhost:5173 |
| API Docs (Swagger) | http://localhost:8000/docs |

> [!NOTE]
> The first `docker-compose up --build` runs `python backend/ml/train.py` inside the container. This takes ~60 seconds. The backend will not be ready until training completes.

---

## Environment Variables Reference

Copy `.env.example` to `.env` and edit as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment: `development`, `production`, `test` |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload file size in megabytes |
| `MODEL_DIR` | `backend/models` | Path to model artifacts directory |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated list of allowed CORS origins |
| `RATE_LIMIT_QR` | `30/minute` | Rate limit for QR analysis endpoints |
| `RATE_LIMIT_URL` | `60/minute` | Rate limit for URL analysis endpoint |
| `HOST` | `0.0.0.0` | Backend bind host |
| `PORT` | `8000` | Backend bind port |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Frontend: backend API URL |

---

## Troubleshooting FAQ

### ❓ `zbar` / `pyzbar` ImportError

**Windows**: Reinstall pyzbar — the DLLs should be bundled:
```powershell
pip install --force-reinstall pyzbar
```

**Linux**: Install the system library:
```bash
sudo apt-get install libzbar0
```

**macOS**: Install via Homebrew:
```bash
brew install zbar
```

---

### ❓ `MODEL_NOT_LOADED` error on startup

The model artifacts are missing. Run the training script:
```bash
python backend/ml/train.py
```

---

### ❓ CORS error in browser

Your frontend is running on a port not in `CORS_ORIGINS`. Add it to your `.env`:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

### ❓ Port 8000 already in use

Find and kill the process using port 8000:

**Windows**:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**macOS/Linux**:
```bash
lsof -ti:8000 | xargs kill -9
```

---

### ❓ `npm install` fails on Windows

Try with `--legacy-peer-deps`:
```powershell
npm install --legacy-peer-deps
```

---

### ❓ QR code not detected

- Ensure the image is clear and well-lit
- Try a higher resolution image
- Check that the entire QR code is visible in the frame (no cropping)
- Try the `/api/v1/qr/distort` endpoint to see robustness scores
- For programmatic testing, generate a fresh QR code:
  ```python
  import qrcode
  img = qrcode.make("https://example.com")
  img.save("test_qr.png")
  ```

---

### ❓ Docker build fails on `pyzbar` / `zbar`

Make sure your `Dockerfile.backend` installs the system library before pip:
```dockerfile
RUN apt-get update && apt-get install -y libzbar0 && rm -rf /var/lib/apt/lists/*
```

---

### ❓ Frontend shows "Network Error" or blank page

1. Confirm the backend is running: `curl http://localhost:8000/api/v1/system/health`
2. Check `VITE_API_BASE_URL` in `frontend/.env` or `frontend/.env.local`
3. Check browser console for CORS errors — see CORS FAQ above
