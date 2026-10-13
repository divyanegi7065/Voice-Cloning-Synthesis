# Voice Cloner

This repository contains a GitHub Pages frontend demo and a FastAPI backend for local use.

## GitHub Pages frontend

The root `index.html` is a static frontend suitable for GitHub Pages. It can play a selected audio sample locally and preview typed text using the browser's built-in speech synthesis.

The GitHub Pages version does **not** run XTTS and does **not** clone voices. GitHub Pages only serves static files. To publish it, open the repository's **Settings → Pages** and select **Deploy from a branch**, branch **`main`**, folder **`/(root)`**. The site is published at `https://divyanegi7065.github.io/Voice-Cloning-Synthesis/`.

## Run the voice-cloning backend locally

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn requests TTS
   ```
2. Start the app:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Open:
   ```text
   http://localhost:8000/
   ```

The FastAPI interface uses Coqui XTTS to clone a voice from an uploaded audio sample or URL. It is separate from the static GitHub Pages demo and requires a machine with adequate memory and CPU/GPU resources.
