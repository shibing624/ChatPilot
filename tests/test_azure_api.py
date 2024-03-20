# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""

import sys
import unittest

sys.path.append('..')
from chatpilot import ChatAgent


class AZTestCase(unittest.TestCase):

    def test_tool_usage(self):
        m = ChatAgent(
            openai_api_version='2023-05-15',
            openai_model='gpt-35-turbo',
            openai_api_key='xx',
            openai_api_base='https://xx.api.cognitive.microsoft.com',
            max_iterations=1,
            max_execution_time=10, )
        print(m.llm)
        print(m.run('一句话介绍南京', []))
        i = "俄乌战争的最新进展?"
        print(i)
        r = m.run(i, [])
        print(r)
        print("===")

        print(m.run("计算88888*4444.3=?", []))


if __name__ == '__main__':
    unittest.main()
