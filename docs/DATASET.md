# QR Sentinel — Threat Intelligence Dataset Documentation

## 1. Dataset Status & Synthetic Data Transparency

> [!WARNING]
> **SYNTHETIC_DEMO DATASET NOTICE**
> The machine learning model included in this distribution was trained on an algorithmically generated synthetic dataset of 5,000 samples (2,500 benign, 2,500 malicious).
> 
> No fabricated empirical claims are made regarding real-world phishing detection rates. This pipeline demonstrates the technical ML architecture, feature engineering schema, cross-validation, and probability calibration.

---

## 2. Synthetic Dataset Generation Methodology

The synthetic data generation engine is located at `backend/ml/train.py`. It constructs statistical feature vectors reflecting known structural patterns in benign versus malicious destinations without downloading live payloads.

### Benign Distribution (`label = 0`):
- **URL Length:** Normally distributed around 80 characters ($\mu=80, \sigma=25$).
- **Hostname Length:** Normally distributed around 15 characters ($\mu=15, \sigma=5$).
- **HTTPS Adoption:** 90% probability of HTTPS scheme.
- **Subdomain Count:** 0 to 2 levels.
- **Top-Level Domains (TLD):** Standard common TLDs (`.com`, `.org`, `.edu`, `.net`).
- **IP Hostnames:** 0% (standard domains only).
- **URL Shorteners:** 0%.
- **Special Character Density:** Beta distribution ($\alpha=1, \beta=10$), low entropy.

### Malicious Distribution (`label = 1`):
- **URL Length:** Normally distributed around 180 characters ($\mu=180, \sigma=60$).
- **Hostname Length:** Normally distributed around 30 characters ($\mu=30, \sigma=15$).
- **HTTPS Adoption:** 55% HTTP / 45% HTTPS (modern quishing frequently abuses free Let's Encrypt certificates).
- **IP Hostnames:** 25% prevalence of raw IPv4/IPv6 host addresses.
- **URL Shorteners:** 20% prevalence of shortening services (`bit.ly`, `tinyurl.com`, `t.co`, `cutt.ly`).
- **Suspicious TLDs:** 40% prevalence of high-abuse TLDs (`.tk`, `.ml`, `.ga`, `.xyz`, `.top`).
- **Punycode / IDN Homographs:** 15% prevalence of `xn--` internationalized prefix.
- **Special Character Density:** Beta distribution ($\alpha=3, \beta=5$), elevated entropy.

---

## 3. Recommended Production Datasets

For enterprise or production deployment, retrain the classifier using verified threat intelligence repositories:

1. **PhishTank:** Publicly accessible, community-verified phishing URL feed updated hourly.
2. **OpenPhish:** Free community feed providing active phishing URL indicators.
3. **URLhaus (abuse.ch):** Malware distribution URLs and command-and-control infrastructure.
4. **Tranco / Cisco Umbrella Top 1M:** Reliable baseline for benign domain distributions.
5. **Kaggle Malicious and Benign URLs Dataset:** Multi-class corpus of 400,000+ labeled URLs.

---

## 4. Retraining on Custom Data

To retrain the platform with your own dataset:

1. Prepare a CSV file containing URL strings and binary labels (`0` for benign, `1` for malicious).
2. Extract the 19 feature schema via `backend/services/url_analyzer.py`.
3. Execute the training pipeline:

```bash
python backend/ml/train.py --dataset path/to/your_dataset.csv
```

4. The pipeline will automatically:
   - Split train/validation/test sets with stratification.
   - Fit and compare candidate models (Random Forest vs Logistic Regression).
   - Apply isotonic probability calibration.
   - Save artifacts to `backend/models/`.

