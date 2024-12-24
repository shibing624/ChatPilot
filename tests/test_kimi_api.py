# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import sys
import unittest

sys.path.append('..')
from chatpilot import AgenticaAgent


class KimiTestCase(unittest.TestCase):
    def test_tool_usage(self):
        m = AgenticaAgent(
            model_type='moonshot', model_name="moonshot-v1-8k", enable_search_tool=True,
            enable_url_crawler_tool=True, enable_run_python_code_tool=True, verbose=True,
        )
        print(m)
        print(m.run('一句话介绍南京'))


if __name__ == '__main__':
    unittest.main()
