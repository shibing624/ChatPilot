# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import os
from typing import Any, List

from langchain.agents import AgentExecutor
from langchain.agents import tool
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.callbacks.manager import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from langchain.chains import LLMMathChain
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import Tool
from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI

OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")


class SerperSearchRetriever(BaseRetriever):
    search: GoogleSerperAPIWrapper = None

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun, **kwargs: Any
    ) -> List[Document]:
        return [Document(page_content=self.search.run(query))]

    async def _aget_relevant_documents(
            self,
            query: str,
            *,
            run_manager: AsyncCallbackManagerForRetrieverRun,
            **kwargs: Any,
    ) -> List[Document]:
        raise NotImplementedError()


search_engine = GoogleSerperAPIWrapper()
search_engine.gl = 'cn'
search_engine.hl = 'zh-cn'
search_engine.serper_api_key = SERPER_API_KEY
print(search_engine)


@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
# planner = load_chat_planner(model)
# executor = load_agent_executor(model, tools, verbose=True)
# agent = PlanAndExecute(planner=planner, executor=executor)

llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
tools = [
    Tool(
        name="Search",
        func=search_engine.run,
        description="useful for when you need to answer questions about current events",
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math",
    ),
    Tool(
        name="WordLength",
        func=get_word_length.invoke,
        description="useful for when you need to answer questions about word length",
    ),
    PythonREPLTool(),
]

# from langchain.tools import DuckDuckGoSearchRun, E2BDataAnalysisTool

# tools = tools + [E2BDataAnalysisTool(api_key="e2b_94635a6ef534d914ada9ecc8523aaa3fc6ae0fa4")]


MEMORY_KEY = "chat_history"
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个有用的AI助理。
            你的任务是帮助用户回答问题。对于每个问题，你需要判断是否应该使用你的内置知识库回答，还是需要使用工具（tool，你有搜索、计算器、字符串长度计算、python代码解释器工具）来提供答案。以下是你的决策标准：

1. 如果问题涉及以下情况，请直接使用你的内置知识库回答：
   - 常识性问题，如数学问题（例如1+1等于几）、科学事实（例如水的化学式是什么）、语言学问题（例如某个单词的意思）。
   - 历史事实或普遍接受的知识，如历史事件的日期、科学理论的基本解释。
   - 日常生活问题，如“我为什么没有参加父母的婚礼？”这类逻辑或常识性问题。
   - 文化常识，如文学作品的作者、电影的演员。
   - 个人建议或常见问题解答，如“如何修复自行车轮胎？”或者“如何煮意面？”。

2. 如果问题涉及以下情况，请使用工具：
   - 最新新闻事件或最近发生的事情。
   - 特定日期或时间点之后的信息更新，如“最新的奥斯卡获奖名单”或“2024年的美国总统是谁？”。
   - 实时数据或统计，如股票市场、体育比赛结果、天气预报。
   - 特定个人的近期动态或社交媒体更新。
   - 高度专业化或地域性的问题，如特定产品的用户评价、某地的餐馆推荐。

现在，请根据上述标准来判断用户的问题应该如何回答。如果你决定使用工具，请回复“让我来使用工具”并执行后给出答案；如果你决定直接回答，请回复答案。
            """,
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm_with_tools = llm.bind_tools(tools)

agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x["chat_history"] if "chat_history" in x else [],
        }
        | prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)


def run_and_update_chat_history(agent_executor, input: str, chat_history: List = None) -> List:
    chat_history = chat_history or []
    result = agent_executor.invoke({"input": input, "chat_history": chat_history})
    print(result)
    if result["intermediate_steps"]:
        try:
            tool_step_log = result["intermediate_steps"][0][0].log
        except:
            tool_step_log = ""
        content = tool_step_log + result["output"]
    else:
        content = result["output"]
    chat_history.extend(
        [
            HumanMessage(content=input),
            AIMessage(content=content),
        ]
    )
    return chat_history


if __name__ == '__main__':
    def demo1():

        questions = [
            "今天武汉的天气怎么样？",
        ]
        for i in questions:
            print(i)
            r = run_and_update_chat_history(agent_executor, i, None)
            print(r)
            print("===")


    def demo2():
        chat_history = []
        questions = [
            "how many letters in the word 'educabe'?",
            "is that a real word?",
        ]
        for i in questions:
            print(i)
            r = run_and_update_chat_history(agent_executor, i, chat_history)
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
            r = run_and_update_chat_history(agent_executor, i, None)
            print(r)
            print("===")


    demo1()
