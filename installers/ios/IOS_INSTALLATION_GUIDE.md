# 📱 iOS Installation Guide: Frappe Autonomous Enterprise Studio
## How to Install and Run Frappe AES on iPhone and iPad as a Native App

Frappe AES is designed as an Apple iOS Progressive Web App (PWA) with full offline support, standalone display mode, and native hardware camera barcode/QR scanner integration.

---

## Method 1: Instant 1-Tap Safari Installation (Recommended)

1. Open **Safari** on your iPhone or iPad.
2. Navigate to your running Frappe AES Studio instance URL (or hosted site).
3. Tap the **Share** button (the square with an arrow pointing upward at the bottom of the screen).
4. Scroll down and tap **"Add to Home Screen"** (marked with a `+` icon).
5. (Optional) Name the app **Frappe AES**.
6. Tap **"Add"** in the top right corner.

> 🎉 **Result**: A native Frappe AES icon will appear on your iPhone/iPad home screen. When launched, it opens in **full-screen standalone mode** without Safari address bars or browser controls.

---

## Method 2: Enterprise MDM Installation (`.mobileconfig`)

For corporate fleet deployment across enterprise iPhones and iPads:
1. Distribute [`FrappeAES.mobileconfig`](FrappeAES.mobileconfig) via Apple Configurator, Microsoft Intune, Jamf Pro, or direct email attachment.
2. On the iOS device, open the profile and tap **Install**.
3. Authenticate with your device passcode.
4. The managed WebClip will lock onto the user's home screen.

---

## Features on iOS:
- **Full Touch Ergonomics**: Optimized for dynamic island, notch viewports, and swipe gestures.
- **Voice Dictation**: Uses native iOS Siri / Web Speech API for voice prompts.
- **Camera Barcode / QR Scanning**: Native iOS camera permissions allow instant physical asset checkouts.
- **Offline Resilience**: Service worker caches UI assets for connectivity drops.
