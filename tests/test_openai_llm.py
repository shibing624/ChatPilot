# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""

import sys
import unittest

sys.path.append('..')
from chatpilot import LangchainAssistant
from chatpilot.config import OPENAI_API_KEY, OPENAI_API_BASE


class BaseTestCase(unittest.TestCase):

    def test_case1(self):
        """测试"""
        w = '，'
        comma_res = [0.0]
        print(w, comma_res)
        self.assertEqual(comma_res[0], 0.0)

    def test_tool_usage(self):
        m = LangchainAssistant(model_api_base=OPENAI_API_BASE,
                               model_api_key=OPENAI_API_KEY,
                               max_iterations=1,
                               max_execution_time=30, )
        print(m)
        print(m.llm)
        i = "hi?"
        print(i)
        r = m.run(i, [])
        print(r)
        print("===")

        #
        # m.ChatAgnet(openai_model='gpt-3.5-turbo-16k')
        # print(m.llm, '\ngpt-3.5-turbo-16k' )
        # print(i)
        # r = m.run(i, [])
        # print(r)
        # print("===")

        # m.ChatAgnet(openai_model='gpt-3.5-trubo-instruct')
        # print(m.llm, '\ngpt-3.5-trubo-instruct')
        # print(i)
        # r = m.run(i, [])
        # print(r)
        # print("===")

        # m.ChatAgnet(openai_model='gpt-4')
        # print(m.llm, '\ngpt-4' )
        # print(i)
        # r = m.run(i, [])
        # print(r)
        # print("===")
        #
        # m.ChatAgnet(openai_model='gpt-4-1106-preview')
        # print(m.llm, '\ngpt-4-1106-preview' )
        # print(i)
        # r = m.run(i, [])
        # print(r)
        # print("===")

        # m.ChatAgnet(openai_model='gpt-3.5-turbo-16k-0613')
        # print(m.llm, '\ngpt-3.5-turbo-16k-0613')
        # print(i)
        # r = m.run(i, [])
        # print(r)
        # print("===")

        # m.ChatAgnet(openai_model='gpt-4-32k-0613')
        # print(m.llm, '\ngpt-4-32k-0613')
        # print(i)
        # r = m.run(i, [])
        # print(r)
        # print("===")
        #
        # m.ChatAgnet(openai_model='gpt-4-vision-preview')
        # print(m.llm, '\ngpt-4-vision-preview')
        # print(i)
        # r = m.run(i, [])
        # print(r)
        # print("===")


if __name__ == '__main__':
    unittest.main()
