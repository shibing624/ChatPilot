# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import json
import time
from datetime import datetime
from http import HTTPStatus
from typing import Any, AsyncGenerator, Dict, List, Union

import dashscope
from dashscope.aigc.generation import Generation
from dashscope.api_entities.aiohttp_request import AioHttpRequest
from dashscope.api_entities.api_request_data import ApiRequestData
from dashscope.api_entities.api_request_factory import _get_protocol_params
from dashscope.api_entities.dashscope_response import (
    GenerationOutput,
    GenerationResponse,
    Message,
)
from dashscope.client.base_api import BaseAioApi
from dashscope.common.constants import SERVICE_API_PATH, ApiProtocol
from dashscope.common.error import (
    InputDataRequired,
    InputRequired,
    ModelRequired,
    UnsupportedApiProtocol,
)
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from loguru import logger
from pydantic import BaseModel

from chatpilot.apps.auth_utils import (
    get_current_user,
)
from chatpilot.config import (
    MODEL_FILTER_ENABLED,
    MODEL_FILTER_LIST,
    RPD,
    DASHSCOPE_API_KEY,
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

app.state.DASHSCOPE_API_KEY = DASHSCOPE_API_KEY
app.state.ENABLED = True if DASHSCOPE_API_KEY else False
app.state.MODELS = {}

# User request counter, format is {user_id: (date, count)}
user_request_counts = {}


class UrlsUpdateForm(BaseModel):
    urls: List[str]


class KeysUpdateForm(BaseModel):
    keys: List[str]


@app.middleware("http")
async def check_url(request: Request, call_next):
    logger.debug("check_url")
    if len(app.state.MODELS) == 0:
        await get_all_models()
    else:
        pass

    response = await call_next(request)
    return response


async def get_all_models():
    logger.debug("get_all_models")
    if not app.state.DASHSCOPE_API_KEY:
        models = {"data": []}
    else:
        app.state.ENABLED = True
        models = {"data": [
            {"id": "qwen-max", "name": "Qwen Max"},
            {"id": "qwen-turbo", "name": "Qwen Turbo"},
        ]}
        app.state.MODELS = {model["id"]: model for model in models["data"]}
        logger.debug(f"get_all_models done, size: {len(app.state.MODELS)}")
    return models


@app.get("/models")
async def get_models(user=Depends(get_current_user)):
    try:
        return await get_all_models()
    except Exception as e:
        app.state.ENABLED = False
        raise HTTPException(status_code=400, detail=ERROR_MESSAGES.DEFAULT(e))


def build_api_arequest(
        model: str, input: object, task_group: str, task: str, function: str, api_key: str, is_service=True, **kwargs
):
    (
        api_protocol,
        ws_stream_mode,
        is_binary_input,
        http_method,
        stream,
        async_request,
        query,
        headers,
        request_timeout,
        form,
        resources,
    ) = _get_protocol_params(kwargs)
    task_id = kwargs.pop("task_id", None)

    if api_protocol in [ApiProtocol.HTTP, ApiProtocol.HTTPS]:
        if not dashscope.base_http_api_url.endswith("/"):
            http_url = dashscope.base_http_api_url + "/"
        else:
            http_url = dashscope.base_http_api_url

        if is_service:
            http_url = http_url + SERVICE_API_PATH + "/"

        if task_group:
            http_url += "%s/" % task_group
        if task:
            http_url += "%s/" % task
        if function:
            http_url += function
        request = AioHttpRequest(
            url=http_url,
            api_key=api_key,
            http_method=http_method,
            stream=stream,
            async_request=async_request,
            query=query,
            timeout=request_timeout,
            task_id=task_id,
        )
    else:
        raise UnsupportedApiProtocol("Unsupported protocol: %s, support [http, https, websocket]" % api_protocol)

    if headers is not None:
        request.add_headers(headers=headers)

    if input is None and form is None:
        raise InputDataRequired("There is no input data and form data")

    request_data = ApiRequestData(
        model,
        task_group=task_group,
        task=task,
        function=function,
        input=input,
        form=form,
        is_binary_input=is_binary_input,
        api_protocol=api_protocol,
    )
    request_data.add_resources(resources)
    request_data.add_parameters(**kwargs)
    request.data = request_data
    return request


class AGeneration(Generation, BaseAioApi):
    @classmethod
    async def acall(
            cls,
            model: str,
            prompt: Any = None,
            history: list = None,
            api_key: str = None,
            messages: List[Message] = None,
            plugins: Union[str, Dict[str, Any]] = None,
            **kwargs,
    ) -> Union[GenerationResponse, AsyncGenerator[GenerationResponse, None]]:
        if (prompt is None or not prompt) and (messages is None or not messages):
            raise InputRequired("prompt or messages is required!")
        if model is None or not model:
            raise ModelRequired("Model is required!")
        task_group, function = "aigc", "generation"  # fixed value
        if plugins is not None:
            headers = kwargs.pop("headers", {})
            if isinstance(plugins, str):
                headers["X-DashScope-Plugin"] = plugins
            else:
                headers["X-DashScope-Plugin"] = json.dumps(plugins)
            kwargs["headers"] = headers
        input, parameters = cls._build_input_parameters(model, prompt, history, messages, **kwargs)

        api_key, model = BaseAioApi._validate_params(api_key, model)
        request = build_api_arequest(
            model=model,
            input=input,
            task_group=task_group,
            task=Generation.task,
            function=function,
            api_key=api_key,
            **kwargs,
        )
        response = await request.aio_call()
        is_stream = kwargs.get("stream", False)
        if is_stream:

            async def aresp_iterator(response):
                async for resp in response:
                    yield GenerationResponse.from_api_response(resp)

            return aresp_iterator(response)
        else:
            return GenerationResponse.from_api_response(response)


class DashScopeLLM:
    def __init__(self, model, api_key, temperature=0.8):
        self.use_system_prompt = False  # only some models support system_prompt
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.aclient: AGeneration = AGeneration
        logger.debug(f"DashScopeLLM: model={self.model}, api_key={self.api_key}")

        # check support system_message models
        support_system_models = [
            "qwen-",  # all support
            "llama2-",  # all support
            "baichuan2-7b-chat-v1",
            "chatglm3-6b",
        ]
        for support_model in support_system_models:
            if support_model in self.model:
                self.use_system_prompt = True

    def const_kwargs(self, messages: list[dict], stream: bool = False) -> dict:
        kwargs = {
            "api_key": self.api_key,
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "result_format": "message",
        }
        if self.temperature > 0:
            # different model has default temperature. only set when it"s specified.
            kwargs["temperature"] = self.temperature
        if stream:
            kwargs["incremental_output"] = True
        return kwargs

    def _check_response(self, resp: GenerationResponse):
        if resp.status_code != HTTPStatus.OK:
            raise RuntimeError(f"code: {resp.code}, request_id: {resp.request_id}, message: {resp.message}")

    def get_choice_text(self, output: GenerationOutput) -> str:
        return output.get("choices", [{}])[0].get("message", {}).get("content", "")

    def completion(self, messages: list[dict]) -> GenerationOutput:
        resp: GenerationResponse = self.aclient.call(**self.const_kwargs(messages, stream=False))
        self._check_response(resp)

        return resp.output

    async def _achat_completion(self, messages: list[dict], timeout: int = 3) -> GenerationOutput:
        resp: GenerationResponse = await self.aclient.acall(**self.const_kwargs(messages, stream=False))
        self._check_response(resp)
        return resp.output

    async def acompletion(self, messages: list[dict], timeout=3) -> GenerationOutput:
        return await self._achat_completion(messages, timeout=timeout)

    async def _achat_completion_stream(self, messages: list[dict], timeout: int = 3) -> str:
        resp = await self.aclient.acall(**self.const_kwargs(messages, stream=True))
        collected_content = []
        async for chunk in resp:
            self._check_response(chunk)
            content = chunk.output.choices[0]["message"]["content"]
            logger.debug(content)
            collected_content.append(content)
        full_content = "".join(collected_content)
        return full_content


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request, user=Depends(get_current_user)):
    method = request.method
    logger.debug(f"Proxying request to Dashscope: {path}, method: {method}, "
                 f"user: {user.id} {user.name} {user.email} {user.role}")
    if not app.state.DASHSCOPE_API_KEY:
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES.API_KEY_NOT_FOUND)

    body = await request.body()

    try:
        body_dict = json.loads(body.decode("utf-8"))
        model_name = body_dict.get('model', 'qwen-max')
        max_tokens = body_dict.get("max_tokens", 1024)
        temperature = body_dict.get("temperature", 0.7)
        num_ctx = body_dict.get('num_ctx', 1024)
        messages = body_dict.get("messages", [])
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

        llm = DashScopeLLM(model=model_name, api_key=app.state.DASHSCOPE_API_KEY, temperature=temperature)
        events = await llm.aclient.acall(**llm.const_kwargs(messages, stream=True))
        created = int(time.time())

        async def event_generator():
            async for event in events:
                c = event.output.choices[0]["message"]["content"]

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
