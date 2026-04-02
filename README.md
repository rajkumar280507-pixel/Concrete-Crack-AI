# Concrete Crack Intelligence Suite (CCIS) 🏗️
### AI-Powered Forensic Structural Inspection Platform

**Concrete Crack Intelligence Suite (CCIS)** is a state-of-the-art engineering platform for the autonomous detection, quantification, and forensic assessment of concrete fractures. It transforms visual inspections into quantitative engineering data mapped to civil standards.

---

## 🌟 Key Features
- **9-Phase Inspection Pipeline**: A deterministic forensic chain from surface validation to final hazard assessment.
- **Sub-Pixel Quantification**: Calibrated measurement of crack length, average aperture (width), and maximum width.
- **Adaptive Multi-Mode Analysis**: Select specialized detection logic for Structural, Alligator (Fatigue), Hairline, or Thermal cracks.
- **PDF Forensic Reports**: Automated generation of archived PDF reports for legal and engineering documentation.
- **Real-Time Stream**: Low-latency video engine for immediate on-site structural preliminary checks.

## 🛠️ Technical Stack
- **Engine:** Python 3.10+
- **Vision Architecture:** OpenCV / PyTorch
- **Backend Infrastructure:** Flask
- **Aesthetics & UI:** Responsive HTML5 / Modern CSS (Dark Mode Optimized)
- **Database:** SQLite3 Forensic Store

## 📂 Project Structure
```text
crack-detection-ai/
├── src/                    # Forensic Vision Engine
│   ├── detect_crack.py     # End-to-End Orchestration
│   ├── measurement.py      # Dimensional & Severity Logic
│   ├── segmentation.py     # Adaptive Signal Acquisition
│   └── visualization.py    # Professional HUD Overlays
├── webapp/                 # Inspector Interface
│   ├── app.py              # Flask Forensic Controller
│   └── templates/index.html # High-Performance Dashboard
├── models/                 # Pre-trained Vision Weights (Optional)
└── forensic_v1.db          # Inspection Database
```

## 🚀 Getting Started
1.  **Environment Setup:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Launch Platform:**
    ```bash
    python webapp/app.py
    ```
3.  **Inspection Access:** Visit `http://localhost:5000`

---
*Developed for Structural Health Monitoring and Civil Forensic Analysis.*
