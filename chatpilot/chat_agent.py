# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""

from datetime import datetime
from typing import List, Optional, Union

import tiktoken
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.tools import StructuredTool
from langchain_community.document_loaders import WebBaseLoader, OnlinePDFLoader
from langchain_community.tools import E2BDataAnalysisTool
from langchain_community.utilities import GoogleSerperAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from loguru import logger

from chatpilot.config import (
    SERPER_API_KEY,
    OPENAI_API_BASE,
    OPENAI_API_KEY,
    E2B_API_KEY,
    RUN_PYTHON_CODE_TOOL_DESC,
    SYSTEM_PROMPT,
    SEARCH_TOOL_DESC,
    CRAWLER_TOOL_DESC,
    ENABLE_CRAWLER_TOOL,
    ENABLE_RUN_PYTHON_CODE_TOOL,
    ENABLE_SEARCH_TOOL,
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
            openai_api_base: str = OPENAI_API_BASE,
            openai_api_key: str = OPENAI_API_KEY,
            serper_api_key: str = SERPER_API_KEY,
            **kwargs
    ):
        """
        Initializes the ChatAgent with the given parameters.

        :param openai_model: The model name of OpenAI.
        :param search_engine_name: The name of the search engine to use, such as "serper" or "duckduckgo".
        :param verbose: If True, enables verbose logging.
        :param max_iterations: The maximum number of iterations for the agent executor.
        :param max_execution_time: The maximum execution time in seconds.
        :param temperature: The temperature for the OpenAI model.
        :param num_memory_turns: The number of memory turns to keep in the chat history, -1 for unlimited.
        :param max_tokens: The maximum number of tokens for the OpenAI model.
        :param streaming: If True, enables streaming mode.
        :param max_context_tokens: The maximum number of context tokens to use.
        :param openai_api_base: The base URLs for the OpenAI API.
        :param openai_api_key: The API keys for the OpenAI API.
        :param kwargs: Additional keyword arguments.
        """
        if not openai_api_key:
            raise Exception("`OPENAI_API_KEY` or `OPENAI_API_KEYS` environment variable must set.")

        if search_engine_name == "serper" and not serper_api_key:
            raise ValueError("Missing `SERPER_API_KEY` environment variable.")

        self.max_context_tokens = max_context_tokens
        self.max_iterations = max_iterations
        self.max_execution_time = max_execution_time
        self.verbose = verbose
        self.search_engine_name = search_engine_name
        self.serper_api_key = serper_api_key

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
        self.openai_model = openai_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_execution_time = max_execution_time
        self.streaming = streaming
        self.openai_api_key = openai_api_key
        self.openai_api_base = openai_api_base

        # Define the search engine
        self.search_engine = self._initialize_search_engine()

        # Define tools
        self.tools = self._initialize_tools()

        # Define agent
        self.chat_history = []
        self.num_memory_turns = num_memory_turns
        self.agent_executor = self._initialize_agent_executor()
        logger.debug(f"ChatAgent initialized with model: {openai_model}")

    def _initialize_search_engine(self):
        """
        Initializes the search engine based on the provided name.

        :param search_engine_name: The name of the search engine.
        :return: An instance of the search engine.
        """
        if self.search_engine_name == "serper":
            search_engine = GoogleSerperAPIWrapper()
            search_engine.gl = 'cn'
            search_engine.hl = 'zh-cn'
            search_engine.serper_api_key = self.serper_api_key
        else:
            search_engine = DuckDuckGoSearchAPIWrapper()
        logger.debug(f"Initialized search engine: {self.search_engine_name}")
        return search_engine

    def _initialize_tools(self):
        """
        Initializes the tools used by the ChatAgent.

        :return: A list of Tool instances.
        """
        if E2B_API_KEY:
            run_python_code_tool = E2BDataAnalysisTool(api_key=E2B_API_KEY)
        else:
            from langchain_experimental.tools import PythonREPLTool, PythonAstREPLTool  # noqa
            run_python_code_tool = PythonAstREPLTool()
        run_python_code_tool.description = RUN_PYTHON_CODE_TOOL_DESC

        def web_url_crawler_func(web_url: str) -> str:
            """Web url crawler tool."""
            web_url = web_url.strip()
            if web_url.endswith(".pdf"):
                loader = OnlinePDFLoader(file_path=web_url)
            else:
                loader = WebBaseLoader(web_paths=web_url)
            data = loader.load()

            content = ""
            for d in data:
                title = d.metadata.get("title", "").strip()
                desc = d.metadata.get("description", "").strip()
                page_content = d.page_content.strip()
                content += f"title: {title}\ndescription:{desc}\n{page_content}\n\n"
            content_tokens = self.count_token_length(content)
            if content_tokens > self.max_context_tokens:
                content = content[:self.max_context_tokens]
            return content

        web_url_crawler_tool = StructuredTool.from_function(
            func=web_url_crawler_func,
            name="web_url_crawler",
            description=CRAWLER_TOOL_DESC,
        )

        tools = []
        if ENABLE_SEARCH_TOOL:
            tools.append(Tool(name="Search", func=self.search_engine.run, description=SEARCH_TOOL_DESC))
        if ENABLE_RUN_PYTHON_CODE_TOOL:
            tools.append(run_python_code_tool)
        if ENABLE_CRAWLER_TOOL:
            tools.append(web_url_crawler_tool)
        if not tools:
            raise ValueError("No tools are enabled, must enable at least one tool.")
        return tools

    def _initialize_agent_executor(self):
        """
        Initializes the AgentExecutor for the ChatAgent.

        :return: An instance of AgentExecutor.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        # logger.debug(f"Initialized ChatAgent prompt: {prompt}")
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

    def count_token_length(self, text):
        """Count token length."""
        try:
            encoding = tiktoken.encoding_for_model(self.openai_model)
        except KeyError:
            model = "cl100k_base"
            encoding = tiktoken.get_encoding(model)
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
