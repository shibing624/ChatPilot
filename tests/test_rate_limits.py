# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import os
import sys

import httpx
import pytest

sys.path.append('..')
from chatpilot.apps.openai_app import app
from chatpilot.config import RPM, RPD

FAKE_USER_TOKEN = os.getenv("CHATPILOT_API_KEY")
print(RPD, RPM)


@pytest.mark.asyncio
async def test_rate_limiter_per_minute():
    # 测试每分钟请求限制
    async with httpx.AsyncClient(app=app, base_url='http://127.0.0.1:8080/') as ac:
        # 模拟在一分钟内发送多个请求
        headers = {"Authorization": f"Bearer {FAKE_USER_TOKEN}"}
        payload = {
            "model": "gpt-35-turbo",
            "messages": [{"role": "user", "content": "hi"}]
        }
        for i in range(RPM + 1):  # 假设每分钟限制为100次请求
            response = await ac.post("chat/completions", headers=headers, json=payload)
            print(i, response, response.status_code)
            if response.status_code == 429:
                break
            else:
                assert response.status_code == 200, "应该返回200 OK"
        assert response.status_code == 429, "应该返回429 Too Many Requests"


@pytest.mark.asyncio
async def test_daily_rate_limiter():
    # 测试每日请求限制
    async with httpx.AsyncClient(app=app, base_url='http://127.0.0.1:8080/') as ac:
        # 模拟在一天内发送超过每日限制的请求
        headers = {"Authorization": f"Bearer {FAKE_USER_TOKEN}"}
        payload = {
            "model": "gpt-35-turbo",
            "messages": [{"role": "user", "content": "hi"}]
        }
        for i in range(RPD + 1):  # 假设每日限制为100次请求
            response = await ac.post("chat/completions", headers=headers, json=payload)
            print(i, response.status_code)
            if response.status_code == 429:
                break
            else:
                assert response.status_code == 200, "应该返回200 OK"
        assert response.status_code == 429, "应该返回429 Too Many Requests"
