# Voice Cloner

This app generates speech conditioned on an uploaded voice sample using Coqui XTTS v2.

## Run the XTTS service

Use Python 3.11 (pinned in `.python-version`). The XTTS model requires substantial memory and may take time to download and load on first startup.

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/` to use the app locally. The service loads the XTTS v2 model and accepts authorized WAV, MP3, OGG, FLAC, or M4A samples up to 25 MB. Select the text's language from the languages supported by XTTS; each request conditions generation on the supplied sample.

## GitHub Pages

GitHub Pages can host the static interface, but it cannot run the Python model. To use the published page, deploy this FastAPI service to a host with sufficient memory, then enter its HTTPS URL in the **XTTS service URL** field. The service allows requests from this project's GitHub Pages origin. Do not expose a development server directly to the public internet.

GitHub Pages source: branch `main`, folder `/(root)`.
