# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import asyncio
import hashlib
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import aiohttp
import requests
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from loguru import logger
from pydantic import BaseModel

from chatpilot.apps.auth_utils import (
    get_current_user,
    get_admin_user,
)
from chatpilot.chat_agent import ChatAgent
from chatpilot.config import (
    OPENAI_API_BASE_URLS,
    OPENAI_API_KEYS,
    CACHE_DIR,
    MODEL_FILTER_ENABLED,
    MODEL_FILTER_LIST,
    SERPER_API_KEY,
    OpenAIClientWrapper,
    RPD,
    RPM,
    MODEL_TYPE
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

app.state.MODEL_FILTER_ENABLED = MODEL_FILTER_ENABLED
app.state.MODEL_FILTER_LIST = MODEL_FILTER_LIST

app.state.OPENAI_API_KEYS = OPENAI_API_KEYS
app.state.OPENAI_API_BASE_URLS = OPENAI_API_BASE_URLS
if app.state.OPENAI_API_KEYS and app.state.OPENAI_API_KEYS[0]:
    # openai audio speech (TTS)
    app.state.CLIENT_MANAGER = OpenAIClientWrapper(
        keys=OPENAI_API_KEYS, base_urls=OPENAI_API_BASE_URLS
    )
else:
    app.state.CLIENT_MANAGER = None

app.state.MODELS = {}

# User request tracking
user_request_tracker = defaultdict(lambda: {"daily": [], "minute": []})


async def request_rate_limiter(
        user=Depends(get_current_user),
        max_daily_requests: int = RPD,
        max_minute_requests: int = RPM
):
    """Unified request rate limiter for both RPD and RPM limits, with support for unlimited requests."""
    if max_daily_requests <= 0 and max_minute_requests <= 0:
        # 如果RPD和RPM都设置为-1，则不限制请求
        return

    now = datetime.now()
    today = now.date()
    current_minute = now.replace(second=0, microsecond=0)

    user_requests = user_request_tracker[user.id]

    # 如果不是无限制，则进行请求记录和限制检查
    if max_daily_requests > 0:
        # 清理过期的每日请求记录
        user_requests["daily"] = [dt for dt in user_requests["daily"] if dt.date() == today]
        # 检查每日请求限制
        if len(user_requests["daily"]) >= max_daily_requests:
            logger.warning(f"Reach request rate limit, user: {user.email}, RPD: {max_daily_requests}")
            raise HTTPException(status_code=429, detail=ERROR_MESSAGES.RPD_LIMIT)

    if max_minute_requests > 0:
        # 清理过期的每分钟请求记录
        user_requests["minute"] = [dt for dt in user_requests["minute"] if dt > current_minute - timedelta(minutes=1)]
        # 检查每分钟请求限制
        if len(user_requests["minute"]) >= max_minute_requests:
            logger.warning(f"Reach request rate limit, user: {user.email}, RPM: {max_minute_requests}")
            raise HTTPException(status_code=429, detail=ERROR_MESSAGES.RPM_LIMIT)

    # 记录新的请求
    user_requests["daily"].append(now)
    user_requests["minute"].append(now)


@app.middleware("http")
async def check_url(request: Request, call_next):
    if len(app.state.MODELS) == 0:
        await get_all_models()

    response = await call_next(request)
    return response


class UrlsUpdateForm(BaseModel):
    urls: List[str]


class KeysUpdateForm(BaseModel):
    keys: List[str]


@app.get("/urls")
async def get_openai_urls(user=Depends(get_admin_user)):
    return {"OPENAI_API_BASE_URLS": app.state.OPENAI_API_BASE_URLS}


@app.post("/urls/update")
async def update_openai_urls(form_data: UrlsUpdateForm, user=Depends(get_admin_user)):
    app.state.OPENAI_API_BASE_URLS = form_data.urls
    logger.info(f"update app.state.OPENAI_API_BASE_URLS: {app.state.OPENAI_API_BASE_URLS}")
    return {"OPENAI_API_BASE_URLS": app.state.OPENAI_API_BASE_URLS}


@app.get("/keys")
async def get_openai_keys(user=Depends(get_admin_user)):
    return {"OPENAI_API_KEYS": app.state.OPENAI_API_KEYS}


@app.post("/keys/update")
async def update_openai_key(form_data: KeysUpdateForm, user=Depends(get_admin_user)):
    app.state.OPENAI_API_KEYS = form_data.keys
    logger.info(f"update app.state.OPENAI_API_KEYS: {app.state.OPENAI_API_KEYS}")
    return {"OPENAI_API_KEYS": app.state.OPENAI_API_KEYS}


@app.post("/audio/speech")
async def speech(
        request: Request,
        user=Depends(get_current_user),
        rate_limit=Depends(request_rate_limiter),
):
    r = None
    try:
        api_key, base_url = app.state.CLIENT_MANAGER.get_next_key_base_url()
        body = await request.body()
        name = hashlib.sha256(body).hexdigest()

        SPEECH_CACHE_DIR = Path(CACHE_DIR).joinpath("./audio/speech/")
        SPEECH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        file_path = SPEECH_CACHE_DIR.joinpath(f"{name}.mp3")
        file_body_path = SPEECH_CACHE_DIR.joinpath(f"{name}.json")

        # Check if the file already exists in the cache
        if file_path.is_file():
            return FileResponse(file_path)

        headers = {}
        headers["Authorization"] = f"Bearer {api_key}"
        headers["Content-Type"] = "application/json"

        try:
            r = requests.post(
                url=f"{base_url}/audio/speech",
                data=body,
                headers=headers,
                stream=True,
            )
            r.raise_for_status()

            # Save the streaming content to a file
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            with open(file_body_path, "w") as f:
                json.dump(json.loads(body.decode("utf-8")), f)

            # Return the saved file
            return FileResponse(file_path)

        except Exception as e:
            logger.error(e)
            error_detail = "Server Connection Error"
            if r is not None:
                try:
                    res = r.json()
                    if "error" in res:
                        error_detail = f"External: {res['error']}"
                except:
                    error_detail = f"External: {e}"

            raise HTTPException(status_code=r.status_code, detail=error_detail)

    except ValueError:
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES.OPENAI_NOT_FOUND)


async def fetch_url(url, key):
    try:
        headers = {"Authorization": f"Bearer {key}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return None


def merge_models_lists(model_lists):
    merged_list = []

    for idx, models in enumerate(model_lists):
        merged_list.extend(
            [
                {**model, "urlIdx": idx}
                for model in models if model["id"]
            ]
        )
    return merged_list


async def get_all_models():
    logger.debug(f"model_type: {MODEL_TYPE}, base urls size: {len(app.state.OPENAI_API_BASE_URLS)}, "
                 f"keys size: {len(app.state.OPENAI_API_KEYS)}")
    if MODEL_TYPE == 'azure':
        models = {"data": [{"id": "gpt-35-turbo", "name": "Gpt-35-Turbo", "urlIdx": 0}]}
    else:
        if len(app.state.OPENAI_API_KEYS) == 1 and app.state.OPENAI_API_KEYS[0] == "":
            models = {"data": []}
        else:
            tasks = [
                fetch_url(f"{url}/models", app.state.OPENAI_API_KEYS[idx])
                for idx, url in enumerate(list(set(app.state.OPENAI_API_BASE_URLS)))
            ]
            responses = await asyncio.gather(*tasks)
            responses = list(
                filter(lambda x: x is not None and "error" not in x, responses)
            )
            models = {
                "data": merge_models_lists(
                    list(map(lambda response: response["data"], responses))
                )
            }
    app.state.MODELS = {model["id"]: model for model in models["data"]}
    logger.debug(f"get_all_models done, size: {len(app.state.MODELS)}, {app.state.MODELS}")
    return models


@app.get("/models")
@app.get("/models/{url_idx}")
async def get_models(url_idx: Optional[int] = None, user=Depends(get_current_user)):
    r = None
    if url_idx is None:
        models = await get_all_models()
        if app.state.MODEL_FILTER_ENABLED:
            if user.role == "user":
                models["data"] = list(
                    filter(
                        lambda model: model["id"] in app.state.MODEL_FILTER_LIST,
                        models["data"],
                    )
                )
                return models
        return models
    else:
        try:
            logger.debug(f"get_models url_idx: {url_idx}")
            url = app.state.OPENAI_API_BASE_URLS[url_idx]
            r = requests.request(method="GET", url=f"{url}/models")
            r.raise_for_status()

            response_data = r.json()
            if url:
                response_data["data"] = list(
                    filter(lambda model: model["id"], response_data["data"])
                )

            return response_data
        except Exception as e:
            logger.error(e)
            error_detail = "Server Connection Error"
            if r is not None:
                try:
                    res = r.json()
                    if "error" in res:
                        error_detail = f"External: {res['error']}"
                except:
                    error_detail = f"External: {e}"

            raise HTTPException(
                status_code=r.status_code if r else 500,
                detail=error_detail,
            )


def proxy_other_request(api_key, base_url, path, body, method):
    """Proxy the request to OpenAI API with a modified body for gpt-4-vision-preview model."""
    # Try to decode the body of the request from bytes to a UTF-8 string (Require add max_token to fix gpt-4-vision)
    try:
        body = body.decode("utf-8")
        body = json.loads(body)

        model_idx = app.state.MODELS[body.get("model")]["urlIdx"]

        # Check if the model is "gpt-4-vision-preview" and set "max_tokens" to 4000
        # This is a workaround until OpenAI fixes the issue with this model
        if body.get("model") == "gpt-4-vision-preview":
            if "max_tokens" not in body:
                body["max_tokens"] = 4000
            print("Modified body_dict:", body)

        # Fix for ChatGPT calls failing because the num_ctx key is in body
        if "num_ctx" in body:
            # If 'num_ctx' is in the dictionary, delete it
            # Leaving it there generates an error with the
            # OpenAI API (Feb 2024)
            del body["num_ctx"]

        # Convert the modified body back to JSON
        body = json.dumps(body)
    except json.JSONDecodeError as e:
        logger.error(f"Error loading request body into a dictionary: {e}")

    target_url = f"{base_url}/{path}"

    headers = {}
    headers["Authorization"] = f"Bearer {api_key}"
    headers["Content-Type"] = "application/json"

    r = requests.request(
        method=method,
        url=target_url,
        data=body,
        headers=headers,
        stream=True,
    )
    r.raise_for_status()
    # Check if response is SSE
    if "text/event-stream" in r.headers.get("Content-Type", ""):
        return StreamingResponse(
            r.iter_content(chunk_size=8192),
            status_code=r.status_code,
            headers=dict(r.headers),
        )
    else:
        response_data = r.json()
        return response_data


@app.api_route("/{path:path}", methods=["POST"])
async def proxy(
        path: str,
        request: Request,
        user=Depends(get_current_user),
        rate_limit=Depends(request_rate_limiter),
):
    method = request.method
    logger.debug(f"Proxying request to OpenAI: {path}, method: {method}, "
                 f"user: {user.id} {user.name} {user.email} {user.role}")

    if not app.state.OPENAI_API_KEYS[0]:
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES.API_KEY_NOT_FOUND)

    body = await request.body()

    try:
        body_dict = json.loads(body.decode("utf-8"))

        # Get the next key and base URL from the client manager
        api_key, base_url = app.state.CLIENT_MANAGER.get_next_key_base_url()
        show_api_key = api_key[:4] + "..." + api_key[-4:]
        logger.debug(f"Using API key: {show_api_key}, base URL: {base_url}")

        model_name = body_dict.get('model', 'gpt-3.5-turbo')
        max_tokens = body_dict.get("max_tokens", 1024)
        temperature = body_dict.get("temperature", 0.7)
        num_ctx = body_dict.get('num_ctx', 1024)
        messages = body_dict.get("messages", [])
        logger.debug(f"model_name: {model_name}, max_tokens: {max_tokens}, "
                     f"num_ctx: {num_ctx}, messages size: {len(messages)}")
        system_prompt = ""
        history = []
        for message in messages:
            if message["role"] == "user":
                history.append(HumanMessage(content=str(message["content"])))
            elif message["role"] == "assistant":
                history.append(AIMessage(content=str(message["content"])))
            elif message["role"] == "system":
                system_prompt = str(message["content"])
        history = history[:-1]  # drop the last message, which is the current user question
        user_question = ""
        if messages and messages[-1]["role"] == "user":
            user_question = messages[-1]["content"]

        if not isinstance(user_question, str):
            return proxy_other_request(api_key, base_url, path, body, method)

        # Create a new ChatAgent instance for each request
        chat_agent = ChatAgent(
            model_type=MODEL_TYPE,
            model_name=model_name,
            model_api_key=api_key,
            model_api_base=base_url,
            search_name="serper" if SERPER_API_KEY else "duckduckgo",
            verbose=True,
            temperature=temperature,
            max_tokens=max_tokens,
            max_context_tokens=num_ctx,
            streaming=True,
            max_iterations=2,
            max_execution_time=60,
            system_prompt=system_prompt,
        )
        events = await chat_agent.astream_run(user_question, chat_history=history)
        created = int(time.time())

        async def event_generator():
            """组装为OpenAI格式流式输出"""
            async for event in events:
                kind = event['event']
                if kind in ['on_tool_start', 'on_chat_model_stream']:
                    if kind == "on_tool_start":
                        c = f"Invoking: `{event['name']}`\n```\n{event['data'].get('input', '')}\n```\n\n"
                    else:
                        c = event['data']['chunk'].content

                    data_structure = {
                        "id": event.get('id', 'default_id'),
                        "object": "chat.completion.chunk",
                        "created": event.get('created', created),
                        "model": model_name,
                        "system_fingerprint": event.get('system_fingerprint', ''),
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": c},
                                "logprobs": None,
                                "finish_reason": None
                            }
                        ]
                    }
                    formatted_data = f"data: {json.dumps(data_structure)}\n\n"
                    yield formatted_data.encode()

            formatted_data_done = f"data: [DONE]\n\n"
            yield formatted_data_done.encode()

        return StreamingResponse(event_generator(), media_type='text/event-stream')
    except Exception as e:
        logger.error(e)
        error_detail = "Server Connection Error"
        raise HTTPException(status_code=500, detail=error_detail)
