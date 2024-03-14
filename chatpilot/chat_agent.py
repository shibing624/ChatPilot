# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
from datetime import datetime
from typing import List, Optional

import tiktoken
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
    OPENAI_API_BASE_URLS,
    OPENAI_API_KEYS,
    E2B_API_KEY,
    RUN_PYTHON_CODE_DESC,
    SYSTEM_PROMPT,
    OpenAIClientWrapper,
)


class ChatAgent:
    def __init__(
            self,
            openai_model: str = "gpt-3.5-turbo-1106",
            search_engine_name: str = "serper",
            verbose: bool = True,
            max_iterations: int = 3,
            max_execution_time: int = 120,
            temperature: float = 0.7,
            num_memory_turns: int = -1,
            max_tokens: Optional[int] = None,
            max_context_tokens: int = 8192,
            streaming: bool = False,
            openai_api_bases: List[str] = OPENAI_API_BASE_URLS,
            openai_api_keys: List[str] = OPENAI_API_KEYS,
            **kwargs
    ):
        """
        Initializes the ChatAgent with the given parameters.

        :param openai_model: The model name of OpenAI.
        :param search_engine_name: The name of the search engine to use.
        :param verbose: If True, enables verbose logging.
        :param max_iterations: The maximum number of iterations for the agent executor.
        :param max_execution_time: The maximum execution time in seconds.
        :param temperature: The temperature for the OpenAI model.
        :param num_memory_turns: The number of memory turns to keep in the chat history, -1 for unlimited.
        :param max_tokens: The maximum number of tokens for the OpenAI model.
        :param streaming: If True, enables streaming mode.
        :param max_context_tokens: The maximum number of context tokens to use.
        :param openai_api_bases: The base URLs for the OpenAI API.
        :param openai_api_keys: The API keys for the OpenAI API.
        :param kwargs: Additional keyword arguments.
        """
        if not openai_api_keys and not openai_api_keys[0]:
            raise Exception("Missing `OPENAI_API_KEYS` environment variable.")
        self.max_context_tokens = max_context_tokens
        self.max_iterations = max_iterations
        self.max_execution_time = max_execution_time
        self.verbose = verbose
        self.credentials_manager = OpenAIClientWrapper(
            keys=openai_api_keys, base_urls=openai_api_bases
        )
        openai_api_key, openai_api_base = self.credentials_manager.get_next_key_base_url()
        # Define llm
        self.llm = ChatOpenAI(
            model=openai_model,
            temperature=temperature,
            openai_api_base=openai_api_base,
            openai_api_key=openai_api_key,
            max_tokens=max_tokens,
            timeout=max_execution_time,
            streaming=streaming,
            **kwargs
        )

        # Define the search engine
        self.search_engine = self._initialize_search_engine(search_engine_name)

        # Define tools
        self.tools = self._initialize_tools()

        # Define agent
        self.chat_history = []
        self.num_memory_turns = num_memory_turns
        self.agent_executor = self._initialize_agent_executor()
        logger.debug(f"ChatAgent initialized with model: {openai_model}")

    @staticmethod
    def _initialize_search_engine(search_engine_name: str):
        """
        Initializes the search engine based on the provided name.

        :param search_engine_name: The name of the search engine.
        :return: An instance of the search engine.
        """
        if search_engine_name == "serper":
            if not SERPER_API_KEY:
                raise ValueError("Missing `SERPER_API_KEY` environment variable.")
            search_engine = GoogleSerperAPIWrapper()
            search_engine.gl = 'cn'
            search_engine.hl = 'zh-cn'
            search_engine.serper_api_key = SERPER_API_KEY
        else:
            search_engine = DuckDuckGoSearchAPIWrapper()
            search_engine.region = 'cn-zh'
        logger.debug(f"Initialized search engine: {search_engine_name}")
        return search_engine

    def _initialize_tools(self):
        """
        Initializes the tools used by the ChatAgent.

        :return: A list of Tool instances.
        """
        if E2B_API_KEY:
            run_python_code_tool = E2BDataAnalysisTool(api_key=E2B_API_KEY)
        else:
            run_python_code_tool = PythonREPLTool()
        run_python_code_tool.description = RUN_PYTHON_CODE_DESC
        tools = [
            Tool(
                name="Search",
                func=self.search_engine.run,
                description="Useful for when you need to search the web for information.",
            ),
            run_python_code_tool
        ]
        return tools

    def _initialize_agent_executor(self):
        """
        Initializes the AgentExecutor for the ChatAgent.

        :return: An instance of AgentExecutor.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT.format(current_date=current_date)),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        agent = (
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
                    "chat_history": lambda x: x["chat_history"] if "chat_history" in x and x["chat_history"] else [],
                }
                | prompt
                | self.llm.bind_tools(self.tools)
                | OpenAIToolsAgentOutputParser()
        )
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            return_intermediate_steps=True,
            max_iterations=self.max_iterations,
            max_execution_time=self.max_execution_time,
            handle_parsing_errors=True,
        ).with_config({"run_name": "ChatAgent"})

    def update_credentials(self):
        """Update credentials."""
        new_key, new_base_url = self.credentials_manager.get_next_key_base_url()
        self.llm.openai_api_key = new_key
        self.llm.openai_api_base = new_base_url

    def update_llm_params(
            self,
            model_name: str = None,
            streaming: bool = None,
            temperature: float = None,
            max_tokens: int = None
    ):
        """Update llm params."""
        logger.debug(
            f"Updating LLM params: model_name={model_name}, "
            f"temperature={temperature}, "
            f"max_tokens={max_tokens}, "
            f"streaming={streaming}"
        )
        self.llm.model_name = model_name if model_name is not None else self.llm.model_name
        self.llm.streaming = streaming if streaming is not None else self.llm.streaming
        self.llm.temperature = temperature if temperature is not None else self.llm.temperature
        self.llm.max_tokens = max_tokens if max_tokens is not None else self.llm.max_tokens

    def count_token_length(self, text):
        """Count token length."""
        encoding = tiktoken.get_encoding("cl100k_base")
        length = len(encoding.encode(text))
        return length

    def _trim_chat_history_to_max_tokens(self, chat_history: List):
        """
        Trims the chat history to ensure it does not exceed the max_context_tokens limit.

        :param chat_history: The current chat history.
        :return: A trimmed chat history.
        """
        total_tokens = 0
        trimmed_history = []
        for message in reversed(chat_history):
            message_tokens = self.count_token_length(message.content)
            if total_tokens + message_tokens > self.max_context_tokens:
                break
            trimmed_history.insert(0, message)
            total_tokens += message_tokens
        return trimmed_history

    def run(self, input_str: str, chat_history: Optional[List] = None) -> dict:
        """
        Runs the given input string through the ChatAgent and returns the result.

        :param input_str: The input string to process.
        :param chat_history: Optional; the current chat history.
        :return: A dictionary containing the output of the agent.
        """
        chat_history = chat_history if chat_history is not None else self.chat_history
        if chat_history:
            chat_history = (
                chat_history[-self.num_memory_turns * 2:]
                if self.num_memory_turns > 0 else chat_history
            )
            chat_history = self._trim_chat_history_to_max_tokens(chat_history)
        output = self.agent_executor.invoke(
            {"input": input_str, "chat_history": chat_history}
        )
        chat_history.extend(
            [HumanMessage(content=input_str), AIMessage(content=output["output"])]
        )
        self.chat_history = chat_history
        return output

    async def astream_run(self, input_str: str, chat_history: Optional[List] = None):
        """
        Asynchronously runs the given input string through the ChatAgent and returns the result.

        :param input_str: The input string to process.
        :param chat_history: Optional; the current chat history.
        :return: An asynchronous generator of events.
        """
        chat_history = chat_history if chat_history is not None else self.chat_history
        if chat_history:
            chat_history = (
                chat_history[-self.num_memory_turns * 2:]
                if self.num_memory_turns > 0 else chat_history
            )
            chat_history = self._trim_chat_history_to_max_tokens(chat_history)
        events = self.agent_executor.astream_events(
            {"input": input_str, "chat_history": chat_history},
            version="v1"
        )
        return events


if __name__ == '__main__':
    m = ChatAgent()

    questions = [
        "how many letters in the word 'educabe'?",
        "它是一个真的单词吗？",
    ]
    for i in questions:
        print(i)
        print(m.llm.model_name, m.llm)
        m.run(i)
        m.update_credentials()
        m.update_llm_params(model_name="gpt-3.5-turbo", temperature=0.2, max_tokens=20)

        print("===")


    async def main():
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

    asyncio.run(main())
