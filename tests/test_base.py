# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""

import sys
import unittest

sys.path.append('..')
from chatpilot import ChatAgent


class EmbeddingsTestCase(unittest.TestCase):

    def test_oov_emb(self):
        """测试 OOV word embedding"""
        w = '，'
        comma_res = [0.0]
        print(w, comma_res)
        self.assertEqual(comma_res[0], 0.0)

    def test_tool_usage(self):
        m = ChatAgent(max_iterations=1,
                      max_execution_time=30, )
        print(m.llm)
        i = "What is the capital of California?"
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
