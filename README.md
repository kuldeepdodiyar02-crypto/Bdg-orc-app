# BDG OCR Android App

This is an Android app built with **Kivy** + **Buildozer** that:
- Lets you input your **OCR.space API key** inside the app (no rebuild needed).
- Selects a screenshot from your device.
- Sends it to OCR.space API for text extraction.
- Detects `R`, `G`, or `V` color results from BDG game history.
- Predicts the next color based on simple pattern analysis.

---

## 🚀 How to Build APK in GitHub (Cloud Build)

1. **Extract this ZIP** into a new folder.
2. Initialize Git and push to your GitHub repo:
   ```bash
   git init
   git add .
   git commit -m "BDG OCR App with API Key Input"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```
3. This repo already includes `.github/workflows/android-build.yml`  
   GitHub Actions will automatically run **Buildozer** inside Docker and build an `.apk`.
4. After the workflow finishes, open the Actions tab → select the latest run → download the APK from the **Artifacts** section.

---

## 📱 How to Use the App

1. Install the APK on your Android device (allow installation from unknown sources).
2. Open the app → you'll first see the **API Key Screen**.
3. Paste your OCR.space API key here (Get it free from https://ocr.space/ocrapi).
4. Tap Save → you will go to the main screen.
5. Tap **Select Screenshot** → choose your BDG result screenshot.
6. The app will send it to OCR.space, extract the text, and show detected results + prediction.

---

## 🛠 Requirements for Local Build (Optional)
If you want to build APK locally instead of cloud build:
- Install Python 3.10+
- Install Buildozer and dependencies
- Run:
  ```bash
  buildozer android debug
  ```

---

## ⚠️ Notes
- OCR requires an internet connection.
- Your API key is stored locally in the app's storage (not uploaded anywhere except OCR.space).
- Offline OCR is possible but would make the APK size ~80MB+.

---

Enjoy 🎯  
