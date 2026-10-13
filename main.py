import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool
from TTS.api import TTS

MAX_AUDIO_SIZE = 25 * 1024 * 1024
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
SUPPORTED_LANGUAGES = {
    "ar", "cs", "de", "en", "es", "fr", "hi", "hu", "it", "ja",
    "ko", "nl", "pl", "pt", "ru", "tr", "zh-cn",
}
logger = logging.getLogger(__name__)
app = FastAPI(title="Voice Cloner")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://divyanegi7065.github.io",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

print("Loading AI Voice Model...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")


def remove_file(path: Optional[str]):
    if not path:
        return
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        logger.exception("Could not remove temporary file %s", path)


@app.get("/")
async def read_index():
    return FileResponse(Path(__file__).with_name("index.html"), media_type="text/html")


@app.post("/clone")
async def clone_voice(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(...),
    text: str = Form(...),
    language: str = Form(default="en"),
):
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Please enter text to speak.")
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Choose a language supported by XTTS.")

    input_path = None
    output_path = None
    generation_succeeded = False
    try:
        file_extension = os.path.splitext(audio_file.filename or "")[1].lower()
        if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Unsupported audio format. Please upload WAV, MP3, OGG, FLAC, or M4A.",
            )

        content = await audio_file.read(MAX_AUDIO_SIZE + 1)
        if not content:
            raise HTTPException(status_code=400, detail="The uploaded audio file is empty.")
        if len(content) > MAX_AUDIO_SIZE:
            raise HTTPException(status_code=413, detail="The audio sample must be 25 MB or smaller.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            input_path = temp_file.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
            output_path = temp_output.name

        await run_in_threadpool(
            tts.tts_to_file,
            text=cleaned_text,
            speaker_wav=input_path,
            language=language,
            file_path=output_path,
        )

        background_tasks.add_task(remove_file, input_path)
        background_tasks.add_task(remove_file, output_path)
        generation_succeeded = True
        return FileResponse(output_path, media_type="audio/wav", filename="cloned_voice.wav")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Voice generation failed")
        raise HTTPException(
            status_code=500,
            detail="Voice generation failed. Check the XTTS service logs for details and try again.",
        ) from exc
    finally:
        if not generation_succeeded:
            remove_file(input_path)
            remove_file(output_path)
