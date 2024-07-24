# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import sys
import unittest

sys.path.append('..')
from chatpilot import LangchainAssistant
from chatpilot.config import DEEPSEEK_API_KEY,DEEPSEEK_API_BASE


class DeepseekTestCase(unittest.TestCase):
    def test_tool_usage(self):
        """
        usage for chat
        from openai import OpenAI
        # for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
        client = OpenAI(api_key="<your API key>", base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
          ],
            max_tokens=1024,
            temperature=0.7,
            stream=False
        )

        print(response.choices[0].message.content)

        """
        m = LangchainAssistant(
            agent_type='react',
            model_type='openai',
            model_name='deepseek-chat',
            model_api_key=DEEPSEEK_API_KEY,
            model_api_base=DEEPSEEK_API_BASE,
            max_iterations=1,
            max_execution_time=10,
            streaming=False,
        )
        print(m)
        print(m.run('一句话介绍南京', []))
        i = "俄乌战争的最新进展?"
        print(i)
        r = m.run(i, [])
        print(r)
        print("===")

        print(m.run("计算88888*4444.3=?"))
        print(m.run("我前面问了啥"))


    def test_stream(self):
        m = LangchainAssistant(
            model_type='openai',
            model_name='deepseek-chat',
            model_api_key=DEEPSEEK_API_KEY,
            model_api_base=DEEPSEEK_API_BASE,
            max_iterations=1,
            max_execution_time=10,
            streaming=True,
        )
        print(m.llm)
        print(m.run('一句话介绍南京', []))

        import asyncio
        async def d():
            questions = [
                "人体最大的器官是啥",
                # "人体最大的器官是啥",
                # "how many letters in the word 'educabe'?",
                # "它是一个真的单词吗？",
            ]
            for i in questions:
                print(i)
                events = await m.astream_run(i)
                async for event in events:
                    print(event)
                    print("===")
                    pass

        asyncio.run(d())


if __name__ == '__main__':
    unittest.main()
