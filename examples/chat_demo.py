# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import os
import sys

sys.path.append('..')

from chatpilot import ChatAgent

from dotenv import load_dotenv  # noqa

load_dotenv('../.env', override=True, verbose=True)

if __name__ == '__main__':
    m = ChatAgent(
        model_type='azure',
        model_name="gpt-35-turbo",
        model_api_key=os.getenv("OPENAI_API_KEYS"),
        model_api_base=os.getenv("OPENAI_API_BASE_URLS"),
        search_name="serper",
        agent_type="react",
        enable_search_tool=True,
        enable_run_python_code_tool=True,
        enable_crawler_tool=False,
    )

    questions = [
        # "今天的俄罗斯相关的新闻top3有哪些？",
        # "今天北京的天气怎么样？",
        "人类最大的器官是？"
    ]
    for i in questions:
        print(i)
        r = m.run(i)
        print(r)
        print("===")
