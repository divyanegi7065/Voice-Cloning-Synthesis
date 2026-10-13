import os
import tempfile
from typing import Optional

import requests
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from TTS.api import TTS

app = FastAPI(title="Voice Cloner")

templates = Jinja2Templates(directory="templates")
templates.env.cache = None  # Fixes Python 3.14 compatibility error

print("Loading AI Voice Model...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")


def remove_file(path: Optional[str]):
    if not path:
        return
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/clone")
async def clone_voice(
    background_tasks: BackgroundTasks,
    audio_file: Optional[UploadFile] = File(default=None),
    audio_url: Optional[str] = Form(default=None),
    text: str = Form(...),
):
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Please enter text to speak.")

    if not audio_file and not audio_url:
        raise HTTPException(
            status_code=400,
            detail="Please provide either an uploaded audio file or a valid audio URL.",
        )

    input_path = None
    output_path = None
    try:
        if audio_url and audio_url.strip():
            parsed_url = audio_url.strip()
            if not parsed_url.startswith(("http://", "https://")):
                raise HTTPException(status_code=400, detail="Audio URL must start with http:// or https://.")
            try:
                response = requests.get(parsed_url, timeout=30)
                response.raise_for_status()
            except requests.RequestException as exc:
                raise HTTPException(status_code=400, detail=f"Failed to download audio from URL: {exc}") from exc

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(response.content)
                input_path = temp_file.name

        elif audio_file and audio_file.filename:
            allowed_extensions = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
            file_extension = os.path.splitext(audio_file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported audio format. Please upload WAV, MP3, OGG, FLAC, or M4A.",
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                content = await audio_file.read()
                temp_file.write(content)
                input_path = temp_file.name
        else:
            raise HTTPException(status_code=400, detail="Please provide either an audio file or an audio URL.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_output:
            output_path = temp_output.name

        tts.tts_to_file(
            text=cleaned_text,
            speaker_wav=input_path,
            language="en",
            file_path=output_path,
        )

        background_tasks.add_task(remove_file, input_path)
        background_tasks.add_task(remove_file, output_path)
        return FileResponse(output_path, media_type="audio/ogg", filename="cloned_voice.ogg")
    except HTTPException:
        if input_path:
            background_tasks.add_task(remove_file, input_path)
        if output_path:
            background_tasks.add_task(remove_file, output_path)
        raise
