# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
)
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from chatpilot.apps.auth_utils import get_current_user
from chatpilot.config import (
    OPENAI_API_BASE_URLS,
    OPENAI_API_KEYS,
    UPLOAD_DIR,
    OpenAIClientWrapper
)
from chatpilot.constants import ERROR_MESSAGES

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.OPENAI_API_KEYS = OPENAI_API_KEYS
app.state.OPENAI_API_BASE_URLS = OPENAI_API_BASE_URLS
if app.state.OPENAI_API_KEYS and app.state.OPENAI_API_KEYS[0]:
    app.state.CLIENT_MANAGER = OpenAIClientWrapper(
        keys=OPENAI_API_KEYS, base_urls=OPENAI_API_BASE_URLS
    )
else:
    app.state.CLIENT_MANAGER = None


@app.post("/transcribe")
def transcribe(
        file: UploadFile = File(...),
        user=Depends(get_current_user),
):
    if file.content_type not in ["audio/mpeg", "audio/wav"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.FILE_NOT_SUPPORTED,
        )
    if not app.state.OPENAI_API_KEYS[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.OPENAI_NOT_FOUND,
        )

    try:
        filename = file.filename
        file_path = f"{UPLOAD_DIR}/{filename}"
        contents = file.file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        client = app.state.CLIENT_MANAGER.get_client()
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        return {"text": transcript.strip()}
    except Exception as e:
        logger.error(e)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )
