# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import sys
import unittest

sys.path.append('..')
from chatpilot import AgenticaAssistant


class AZTestCase(unittest.TestCase):
    def test_llm(self):
        m = AgenticaAssistant(
            model_type='azure',
            model_name='gpt-4o',
        )
        print(m.llm)
        print(m.run('一句话介绍南京'))


if __name__ == '__main__':
    unittest.main()
