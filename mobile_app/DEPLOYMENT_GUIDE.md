# Concrete Crack Intelligence Suite (CCIS) - Mobile Deployment Guide

## 1. Safety Logic Gates (Project Engineering)
The app follows strict forensic rules defined in the backend API:
- **Non-Concrete Gate:** If the surface is not concrete, the app will hide severity/hazard metrics and show a warning.
- **Quality Gate:** Low-quality images trigger a re-upload request instead of showing fake data.
- **Metric Verification:** Analysis is only shown if a valid crack is confirmed by the OpenCV pipeline.

## 2. AdMob Monetization
The app uses Google AdMob. I have implemented **Test Ad IDs** for safety.
- **Placement:** Banner ads are positioned at the bottom of the Home and History screens.
- **Production Switch:** To use real ads, replace the IDs in `lib/services/ad_manager.dart` with your production unit IDs and update the `APPLICATION_ID` in your `AndroidManifest.xml`.

## 3. How to Run Locally
1. Ensure your Flask server is running on your PC.
2. If using an Android Emulator, the app connects via `10.0.2.2:5000`.
3. For Physical Devices, replace `10.0.2.2` in `api_service.dart` with your PC's actual local IP address (e.g., `192.168.1.10`).

## 4. Academic Presentation Tips
- Highlight the **Logic Gates** during your demo—it shows you care about engineering ethics and avoiding false positives.
- Demonstrate the **History Screen** to show data persistence using SQLite.
- Mention the **Monetization Layer** as a part of your "Project Scaling" or "Commercialization" roadmap.
