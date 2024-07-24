# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import sys
import unittest

sys.path.append('..')
from chatpilot import LangchainAssistant
from chatpilot.config import MOONSHOT_API_KEY, MOONSHOT_API_BASE


class KimiTestCase(unittest.TestCase):
    def test_tool_usage(self):
        m = LangchainAssistant(
            agent_type='tool',
            model_type='openai',
            model_name='moonshot-v1-8k',
            model_api_key=MOONSHOT_API_KEY,
            model_api_base=MOONSHOT_API_BASE,
            max_iterations=1,
            max_execution_time=10,
            enable_search_tool=True,
            enable_run_python_code_tool=True,
            enable_url_crawler_tool=True,
            streaming=False,
        )
        print(m)
        print(m.run('https://python.langchain.com/docs/integrations/tools/search_tools 总结这个文章', []))
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
            model_name='moonshot-v1-8k',
            model_api_key=MOONSHOT_API_KEY,
            model_api_base=MOONSHOT_API_BASE,
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
