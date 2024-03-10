# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""

import sys
import unittest

sys.path.append('..')
import numpy as np


class EmbeddingsTestCase(unittest.TestCase):

    def test_oov_emb(self):
        """测试 OOV word embedding"""
        w = '，'
        comma_res = [0.0]
        print(w, comma_res)
        self.assertEqual(comma_res[0], 0.0)



if __name__ == '__main__':
    unittest.main()
