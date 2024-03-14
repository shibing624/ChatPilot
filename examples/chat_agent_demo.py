# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import sys

sys.path.append('..')

from chatpilot import ChatAgent

m = ChatAgent()

if __name__ == '__main__':
    def demo1():
        questions = [
            "https://arxiv.org/pdf/2302.13971.pdf 分析这个论文",
            "俄乌战争的最新进展",
        ]
        for i in questions:
            print(i)
            r = m.run(i)
            print(r)
            print("===")


    def demo2():
        questions = [
            "how many letters in the word 'educabe'?",
            "is that a real word?",
        ]
        for i in questions:
            print(i)
            r = m.run(i)
            print(r)
            print("===")


    def demo3():
        questions = [
            "今天的俄罗斯相关的新闻top3有哪些？",
            "今天北京的天气怎么样？",
            "我当前文件目录名称是啥？",
            "找出小于或等于76的所有素数。你可以实现古老的算法“埃拉托斯特尼筛法”，该算法通过多次筛选来找出一定范围内所有的素数。",

            "《哈姆雷特》是谁写的？",
            "大象的怀孕期是多久？"
        ]
        for i in questions:
            print(i)
            r = m.run(i, [])
            print(r)
            print("===")


    def demo4():
        questions = [
            "找出小于或等于90的所有素数。你可以实现古老的算法“埃拉托斯特尼筛法”，该算法通过多次筛选来找出一定范围内所有的素数。",
            "今天莫斯科有啥新闻消息，给出3个？",
            "第一个新闻可信吗？给出理由。",
        ]
        for i in questions:
            print(i)
            r = m.run(i)
            print(r)
            print("===")


    def demo5():

        questions = [
            "https://python.langchain.com/docs/modules/agents/quick_start "
            "https://python.langchain.com/docs/modules/agents/tools/custom_tools 比较2个文章的异同",
            "how many letters in the word 'educabe'?",
            "它是一个真的单词吗？",
            "给出俄罗斯新闻top2",
        ]
        for i in questions:
            print(i)
            print(m.llm.model_name, m.llm)
            m.run(i)
            print("===")


    def async_demo6():
        import asyncio
        async def d():
            m = ChatAgent()

            questions = [
                "俄罗斯今日新闻top3",
                # "人体最大的器官是啥",
                # "how many letters in the word 'educabe'?",
                # "它是一个真的单词吗？",
            ]
            for i in questions:
                print(i)
                events = await m.astream_run(i)
                async for event in events:
                    print(event)
                    print("===")
                    pass

        asyncio.run(d())


    demo1()
