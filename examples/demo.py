# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import sys

sys.path.append('..')
from chatpilot import AgenticaAgent

if __name__ == '__main__':
    # LLM response
    m = AgenticaAgent(
        model_type='deepseek', model_name="deepseek-chat", enable_search_tool=False,
        enable_url_crawler_tool=False, enable_run_python_code_tool=False, verbose=True
    )
    print(m)
    r = m.stream_run("一句话介绍北京")
    print(r, "".join(r))

    # Enable search tool, url crawler tool, run python code tool
    m = AgenticaAgent(
        model_type='azure', model_name="gpt-4o", enable_search_tool=True,
        enable_url_crawler_tool=True, enable_run_python_code_tool=True, verbose=True,
    )
    questions = [
        "一句话介绍北京",
        "俄乌战争的最新进展",
        "找出小于或等于90的所有素数。你可以实现古老的算法“埃拉托斯特尼筛法”，该算法通过多次筛选来找出一定范围内所有的素数。",
        "今天莫斯科有啥新闻消息，给出3个？",
        "第一个新闻可信吗？给出理由。",
        "https://arxiv.org/pdf/2302.13971.pdf 分析这个论文",
    ]
    for i in questions:
        print(i)
        r = m.stream_run(i)
        print(r, "".join(r))
        print("===")
