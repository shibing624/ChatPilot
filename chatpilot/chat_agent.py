# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
from datetime import datetime
from typing import List, Optional

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_community.tools import E2BDataAnalysisTool
from langchain_community.utilities import GoogleSerperAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI
from loguru import logger

from chatpilot.config import (
    SERPER_API_KEY,
    OPENAI_API_BASE,
    OPENAI_API_KEY,
    E2B_API_KEY,
    RUN_PYTHON_CODE_DESC,
    SYSTEM_PROMPT,
)


class ChatAgent:
    def __init__(
            self,
            openai_model: str = "gpt-3.5-turbo-1106",
            search_engine_name: str = "serper",
            verbose: bool = True,
            max_iterations: int = 5,
            max_execution_time: int = 60,
            temperature: float = 0.7,
            num_memory_turns: int = 5,
    ):
        if not OPENAI_API_KEY:
            raise Exception("Missing `OPENAI_API_KEY` environment variable.")
        # define llm
        self.llm = ChatOpenAI(
            model=openai_model,
            temperature=temperature,
            openai_api_base=OPENAI_API_BASE,
            openai_api_key=OPENAI_API_KEY
        )

        # define search engine
        if search_engine_name == "serper":
            if not SERPER_API_KEY:
                raise Exception("Missing `SERPER_API_KEY` environment variable.")
            self.search_engine = GoogleSerperAPIWrapper()
            self.search_engine.gl = 'cn'
            self.search_engine.hl = 'zh-cn'
            self.search_engine.serper_api_key = SERPER_API_KEY
        else:
            self.search_engine = DuckDuckGoSearchAPIWrapper()
            self.search_engine.region = 'cn-zh'
        logger.debug(f"search engine: {search_engine_name}")

        # define tools
        if E2B_API_KEY:
            run_python_code_tool = E2BDataAnalysisTool(api_key=E2B_API_KEY)
        else:
            run_python_code_tool = PythonREPLTool
        run_python_code_tool.description = RUN_PYTHON_CODE_DESC
        tools = [
            Tool(
                name="Search",
                func=self.search_engine.run,
                description="useful for when you need to search the web for information",
            ),
            run_python_code_tool
        ]
        llm_with_tools = self.llm.bind_tools(tools)

        # define agent
        self.chat_history = []
        self.num_memory_turns = num_memory_turns
        current_date = datetime.now().strftime("%Y-%m-%d")
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_PROMPT.format(current_date=current_date),
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        agent = (
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                        x["intermediate_steps"]
                    ),
                    "chat_history": lambda x: x["chat_history"] if "chat_history" in x and x["chat_history"] else [],
                }
                | prompt
                | llm_with_tools
                | OpenAIToolsAgentOutputParser()
        )
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            return_intermediate_steps=True,
            max_iterations=max_iterations,
            max_execution_time=max_execution_time
        )
        logger.debug(f"ChatAgent agent_executor is ready, openai_model: {openai_model}")

    def run(self, input_str: str, chat_history: Optional[List] = None) -> dict:
        """Run query through ChatAgent and return result."""
        chat_history = chat_history if chat_history is not None else self.chat_history
        if chat_history:
            chat_history = chat_history[-self.num_memory_turns * 2:] if self.num_memory_turns > 0 else chat_history
        output = self.agent_executor.invoke({"input": input_str, "chat_history": chat_history})
        chat_history.extend([HumanMessage(content=input_str), AIMessage(content=output["output"])])
        self.chat_history = chat_history
        return output


if __name__ == '__main__':
    m = ChatAgent()

    questions = [
        "how many letters in the word 'educabe'?",
        "它是一个真的单词吗？",
    ]
    for i in questions:
        print(i)
        r = m.run(i)
        print(r)
        print("===")
