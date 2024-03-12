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

from chatpilot.apps.auth_utils import get_current_user
from chatpilot.config import UPLOAD_DIR
from chatpilot.constants import ERROR_MESSAGES

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/transcribe")
def transcribe(
        file: UploadFile = File(...),
        user=Depends(get_current_user),
):
    print(file.content_type)

    if file.content_type not in ["audio/mpeg", "audio/wav"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.FILE_NOT_SUPPORTED,
        )

    try:
        from faster_whisper import WhisperModel
        filename = file.filename
        file_path = f"{UPLOAD_DIR}/{filename}"
        contents = file.file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
            f.close()

        # model = WhisperModel(
        #     WHISPER_MODEL,
        #     device="auto",
        #     compute_type="int8",
        #     download_root=WHISPER_MODEL_DIR,
        # )
        model = None

        segments, info = model.transcribe(file_path, beam_size=5)
        print(
            "Detected language '%s' with probability %f"
            % (info.language, info.language_probability)
        )

        transcript = "".join([segment.text for segment in list(segments)])

        return {"text": transcript.strip()}
    except ImportError as ie:
        print(ie)
    except Exception as e:
        print(e)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )
