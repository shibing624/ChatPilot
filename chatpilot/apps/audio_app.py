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
from openai import Client
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from chatpilot.apps.auth_utils import get_current_user
from chatpilot.config import (
    OPENAI_BASE_URL,
    OPENAI_API_KEY,
    UPLOAD_DIR,
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
app.state.OPENAI_API_KEY = OPENAI_API_KEY
app.state.OPENAI_BASE_URL = OPENAI_BASE_URL


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
    if not app.state.OPENAI_API_KEY:
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

        client = Client(api_key=app.state.OPENAI_API_KE, base_url=app.state.OPENAI_BASE_URL)
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
