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
    def test_url_crawler(self):
        m = AgenticaAssistant(
            model_type='azure',
            model_name='gpt-4o',
        )
        print(m.llm)
        print(m.run('https://python.langchain.com/docs/integrations/tools/search_tools 总结这个文章'))


if __name__ == '__main__':
    unittest.main()
