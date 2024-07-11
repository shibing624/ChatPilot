# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import os
import sys
import unittest

sys.path.append('..')
from chatpilot import LangchainAssistant

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"


class TyTestCase(unittest.TestCase):
    def test_llm(self):
        from langchain_community.chat_models import ChatTongyi
        m = ChatTongyi()

        r = m.invoke("中国首都是哪里?")
        print(r)
        print(m.metadata)

    def test_tool_usage(self):
        from chatpilot.config import DASHSCOPE_API_KEY
        m = LangchainAssistant(
            model_type='dashscope',
            model_name='qwen-max',
            model_api_key=DASHSCOPE_API_KEY,
            max_iterations=1,
            max_execution_time=10, )
        print(m.llm)
        print(m.run('一句话介绍南京'))
        i = "俄乌战争的最新进展?"
        print(i)
        r = m.run(i)
        print(r)
        print("===")

        print(m.run("计算88888*4444.3=?", []))


if __name__ == '__main__':
    unittest.main()
