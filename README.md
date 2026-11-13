# 🛡️ QR Sentinel — AI-Powered QR Code Threat Detection Platform

> **Scan QR codes with confidence.** QR Sentinel analyzes QR code images and the URLs they contain, applying machine-learning-based threat classification to detect quishing attacks, malicious redirects, payment fraud, and more.

> [!WARNING]
> **SYNTHETIC DATA DISCLAIMER**: The bundled ML model was trained exclusively on **synthetic/generated data**. Real-world detection performance will vary significantly. Do **not** use this tool as the sole gatekeeper for production security decisions without retraining on verified real-world threat intelligence data.

---

## 📸 Screenshots

| Upload & Analyze | Risk Report | URL Details |
|---|---|---|
| *(screenshot placeholder)* | *(screenshot placeholder)* | *(screenshot placeholder)* |

---

## ⚡ Quick Start (3 Commands)

```bash
# 1. Install backend dependencies & train the model
pip install -r backend/requirements.txt && python backend/ml/train.py

# 2. Start the backend API server
uvicorn backend.main:app --reload --port 8000

# 3. Start the frontend dev server (new terminal)
cd frontend && npm install && npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **QR Decoding** | Decodes QR codes from uploaded images using `pyzbar` + OpenCV fallback |
| 🧠 **ML Threat Classification** | Random Forest / Logistic Regression model scores URL threat probability |
| 📊 **Risk Engine** | Combines ML score + rule-based heuristics → LOW / MEDIUM / HIGH / INCONCLUSIVE |
| 🔗 **Payload Type Detection** | Identifies URL_HTTP, URL_HTTPS, UPI_PAYMENT, EMAIL, PHONE, WIFI, VCARD, TEXT |
| 💳 **Payment Fraud Detection** | Flags suspicious UPI payment requests |
| 🔄 **Robustness Testing** | Tests QR code readability under various image distortions |
| 🤖 **Explainability** | Feature-level explanations for every risk decision |
| 📈 **Model Metrics** | Live model performance dashboard endpoint |
| 🐳 **Docker Support** | One-command containerized deployment |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        React Frontend                        │
│         (Vite + TypeScript + TailwindCSS + shadcn/ui)       │
└───────────────────────────┬─────────────────────────────────┘
                            │  HTTP / REST (port 8000)
┌───────────────────────────▼─────────────────────────────────┐
│                    FastAPI Backend                            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ QR Decoder  │  │ URL Analyzer │  │  Feature Extractor │  │
│  │  (pyzbar /  │→ │ (19 features)│→ │  + ML Classifier   │  │
│  │  OpenCV)    │  │              │  │  (RF / LR + calib) │  │
│  └─────────────┘  └──────────────┘  └─────────┬──────────┘  │
│                                               │              │
│  ┌────────────────────────────────────────────▼──────────┐  │
│  │              Risk Engine                               │  │
│  │  (ML score + rule-based heuristics → Risk Level)      │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────▼──────────────┐
              │     Model Artifacts        │
              │  threat_classifier.joblib  │
              │  feature_schema.json       │
              │  training_metrics.json     │
              └────────────────────────────┘
```

---

## 📡 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/qr/analyze` | Full QR analysis (decode + classify + risk) |
| `POST` | `/api/v1/qr/decode` | Decode QR code only (no ML) |
| `POST` | `/api/v1/qr/distort` | Test QR robustness under distortions |
| `POST` | `/api/v1/qr/compare` | Compare two QR code images |
| `POST` | `/api/v1/url/analyze` | Analyze a raw URL (no image) |
| `GET`  | `/api/v1/model/status` | Model status and version info |
| `GET`  | `/api/v1/model/metrics` | Model performance metrics |
| `GET`  | `/api/v1/system/health` | Health check |

Full schema documentation: [docs/API.md](docs/API.md)

---

## 🛠️ Setup Instructions

### Windows

```powershell
# Prerequisites: Python 3.10+, Node.js 18+
git clone <repo-url>
cd "QR_scam Detector"

# Backend
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
python backend\ml\train.py        # Train model (creates backend/models/)

# Frontend
cd frontend
npm install
cd ..

# Run
# Terminal 1:
venv\Scripts\uvicorn backend.main:app --reload --port 8000
# Terminal 2:
cd frontend && npm run dev
```

### macOS / Linux

```bash
# Prerequisites: Python 3.10+, Node.js 18+
git clone <repo-url>
cd "QR_scam Detector"

# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
python backend/ml/train.py        # Train model

# Frontend
cd frontend && npm install && cd ..

# Run
# Terminal 1:
uvicorn backend.main:app --reload --port 8000
# Terminal 2:
cd frontend && npm run dev
```

> [!NOTE]
> On Linux, you may need system packages for `pyzbar`:
> ```bash
> sudo apt-get install libzbar0        # Debian/Ubuntu
> sudo dnf install zbar                # Fedora/RHEL
> ```

### macOS (Homebrew)

```bash
brew install zbar
```

---

## 🐳 Docker

```bash
# Build and start all services
docker-compose up --build

# Stop
docker-compose down
```

Services exposed:
- Backend API: **http://localhost:8000**
- Frontend: **http://localhost:5173**

See [docker-compose.yml](docker-compose.yml) for full configuration.

---

## ⚠️ Known Limitations

1. **Synthetic Training Data** — The ML model has never seen real phishing URLs. Accuracy on real-world threats is unknown.
2. **No URL Fetching** — The system analyzes URL structure only; it does not fetch or render the destination page.
3. **QR Image Quality** — Heavily distorted, blurred, or damaged QR codes may fail to decode.
4. **No Authentication** — v1 has no API authentication. Do not expose the backend to the public internet without adding auth.
5. **Rate Limiting** — Basic in-memory rate limiting only; not suitable for high-traffic production use.
6. **Short URL Expansion** — Shortened URLs (bit.ly, tinyurl, etc.) are flagged as suspicious but not expanded.
7. **Single Service** — No persistent storage, no audit log, no user accounts in v1.

---

## 📂 Project Structure

```
QR_scam Detector/
├── backend/
│   ├── api/v1/endpoints/   # FastAPI route handlers
│   ├── core/               # Config, logging, exceptions
│   ├── ml/                 # Training and evaluation scripts
│   ├── models/             # Saved model artifacts (generated)
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # Business logic services
│   ├── tests/              # Pytest test suite
│   └── main.py             # FastAPI application entry point
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   └── lib/            # API client, utilities
│   └── package.json
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DATASET.md
│   ├── ML_PIPELINE.md
│   ├── SECURITY.md
│   ├── SETUP.md
│   └── THREAT_MODEL.md
├── docker-compose.yml
├── Dockerfile.backend
├── .env.example
└── README.md
```

---

## 📚 Documentation Index

| Document | Description |
|---|---|
| [API Reference](docs/API.md) | All endpoints, schemas, curl examples |
| [Architecture](docs/ARCHITECTURE.md) | System design and data flow |
| [ML Pipeline](docs/ML_PIPELINE.md) | Model training, features, evaluation |
| [Threat Model](docs/THREAT_MODEL.md) | Threats addressed and limitations |
| [Setup Guide](docs/SETUP.md) | Detailed per-OS setup instructions |
| [Dataset](docs/DATASET.md) | Synthetic dataset description |
| [Security](docs/SECURITY.md) | Security hardening notes |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

```
MIT License

Copyright (c) 2026 QR Sentinel Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
