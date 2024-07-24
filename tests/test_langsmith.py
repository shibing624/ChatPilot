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


class SmithTestCase(unittest.TestCase):

    def test_smith_usage(self):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

        m = LangchainAssistant(model_name='gpt-3.5-turbo', max_iterations=1, max_execution_time=30, )
        print(m.llm)
        i = "计算8888*4544.2"
        print(i)
        r = m.run(i, [])
        print(r)
        print("===")

        m = LangchainAssistant(model_name='gpt-4-1106-preview')
        print(i)
        r = m.run(i, [])
        print(r)
        print("===")


if __name__ == '__main__':
    unittest.main()
