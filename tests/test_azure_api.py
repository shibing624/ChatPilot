# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import os
import sys
import unittest

sys.path.append('..')
from chatpilot import ChatAgent
from chatpilot.config import OPENAI_API_KEY

os.environ['OPENAI_API_VERSION'] = '2023-05-15'
os.environ['ENABLE_SEARCH_TOOL'] = "False"
os.environ['ENABLE_CRAWLER_TOOL'] = "False"
os.environ['ENABLE_RUN_PYTHON_CODE_TOOL'] = "False"
class AZTestCase(unittest.TestCase):

    def test_tool_usage(self):

        m = ChatAgent(
            model_type='azure',
            model_name='gpt-35-turbo',
            model_api_key=OPENAI_API_KEY,
            model_api_base='https://westeurope.api.cognitive.microsoft.com/openai/deployments/gpt-35-turbo',
            max_iterations=1,
            max_execution_time=10,
            streaming=False,
        )
        print(m.llm)
        print(m.run('https://python.langchain.com/docs/integrations/tools/search_tools 总结这个文章', []))
        print(m.run('一句话介绍南京', []))
        i = "俄乌战争的最新进展?"
        print(i)
        r = m.run(i, [])
        print(r)
        print("===")

        print(m.run("计算88888*4444.3=?"))
        print(m.run("我前面问了啥"))

    def test_url_crawler(self):
        m = ChatAgent(
            model_type='azure',
            model_name='gpt-35-turbo',
            model_api_key=OPENAI_API_KEY,
            model_api_base='https://westeurope.api.cognitive.microsoft.com/openai/deployments/gpt-35-turbo',
            max_iterations=3,
            max_execution_time=60,
            streaming=False,
        )
        print(m.llm)
        print(m.run('https://python.langchain.com/docs/integrations/tools/search_tools 总结这个文章', []))

    def test_stream(self):
        m = ChatAgent(
            model_type='azure',
            model_name='gpt-35-turbo',
            model_api_key=OPENAI_API_KEY,
            model_api_base='https://westeurope.api.cognitive.microsoft.com/openai/deployments/gpt-35-turbo',
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
