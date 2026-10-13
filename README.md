# Voice Cloner

A FastAPI app that clones a voice from an uploaded audio sample or URL and turns text into speech using Coqui XTTS.

## Features

- Upload a reference voice sample or provide a public audio URL
- Enter text to generate spoken output
- FastAPI web UI for simple testing

## Run locally

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

## Notes

- The app loads a large XTTS model on startup and may take a minute to initialize on first run.
- This project is intended for local development or a machine with adequate GPU/CPU resources.
