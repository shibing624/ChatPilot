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


class SmithTestCase(unittest.TestCase):

    def test_smith_usage(self):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = "xx"
        os.environ["LANGCHAIN_PROJECT"] = "langchain_for_chatpilot_development_V1"

        m = ChatAgent(openai_model='gpt-3.5-turbo', max_iterations=1, max_execution_time=30, )
        print(m.llm)
        i = "计算8888*4544.2"
        print(i)
        r = m.run(i, [])
        print(r)
        print("===")

        m = ChatAgent(openai_model='gpt-4-1106-preview')
        print(i)
        r = m.run(i, [])
        print(r)
        print("===")


if __name__ == '__main__':
    unittest.main()
