# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import sys
import unittest

sys.path.append('..')
from chatpilot import AgenticaAgent


class AZTestCase(unittest.TestCase):
    def test_llm(self):
        m = AgenticaAgent(
            model_type='azure',
            model_name='gpt-4o',
            enable_search_tool=True,
        )
        print(m.llm)
        print(m.run('一句话介绍南京'))

        r = m.stream_run('俄乌战争的最新进展')
        print(r)
        for i in r:
            print(i.get_content_as_string())


if __name__ == '__main__':
    unittest.main()
