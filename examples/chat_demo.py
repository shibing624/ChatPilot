# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import os
import sys

sys.path.append('..')

from chatpilot import LangchainAssistant

from dotenv import load_dotenv  # noqa

load_dotenv('../.env', override=True, verbose=True)

if __name__ == '__main__':

    def demo6():
        import asyncio
        m = LangchainAssistant(
            model_type='openai',
            model_name="gpt-3.5-turbo",
            model_api_key=os.getenv("OPENAI_API_KEYS"),
            model_api_base=os.getenv("OPENAI_API_BASE_URLS"),
            search_name="serper",
            agent_type="react",
            enable_search_tool=True,
            streaming=True,
        )
        async def d():
            questions = [
                "俄罗斯今日新闻top3",
                "人体最大的器官是啥",
                # "how many letters in the word 'educabe'?",
                # "它是一个真的单词吗？",
            ]
            for i in questions:
                print(i)
                events = await m.astream_run(i)
                async for event in events:
                    print(event)
                    print("===")

        asyncio.run(d())


    demo6()

    def demo5():
        m = LangchainAssistant(
            search_name="serper",
            agent_type="react",
            enable_search_tool=True,
            enable_run_python_code_tool=True,
        )
        questions = [
            "人类最大的器官是？"
        ]
        for i in questions:
            print(i)
            r = m.run(i)
            print(r)
            print("===")

    demo5()
