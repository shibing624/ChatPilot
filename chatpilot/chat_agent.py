# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import os
from typing import List, Optional
from langchain_openai import ChatOpenAI, AzureChatOpenAI
import tiktoken
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.tools import StructuredTool
from langchain_community.chat_models import ChatTongyi
from langchain_community.document_loaders import WebBaseLoader, OnlinePDFLoader
from langchain_community.tools import E2BDataAnalysisTool
from langchain_community.utilities import GoogleSerperAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from loguru import logger

from chatpilot.config import (
    RUN_PYTHON_CODE_TOOL_DESC,
    SYSTEM_PROMPT,
    SEARCH_TOOL_DESC,
    CRAWLER_TOOL_DESC,
    MODEL_TOKEN_LIMIT,
    ENABLE_SEARCH_TOOL,
    ENABLE_CRAWLER_TOOL,
    ENABLE_RUN_PYTHON_CODE_TOOL,
)


class ChatAgent:
    def __init__(
            self,
            model_type: str = "openai",
            model_name: str = "gpt-3.5-turbo-1106",
            model_api_key: str = os.getenv("OPENAI_API_KEY"),
            model_api_base: str = os.getenv("OPENAI_API_BASE"),
            search_name: Optional[str] = "serper",
            enable_search_tool: bool = ENABLE_SEARCH_TOOL,
            enable_crawler_tool: bool = ENABLE_CRAWLER_TOOL,
            enable_run_python_code_tool: bool = ENABLE_RUN_PYTHON_CODE_TOOL,
            verbose: bool = True,
            max_iterations: int = 3,
            max_execution_time: int = 120,
            temperature: float = 0.7,
            num_memory_turns: int = -1,
            max_tokens: int = 256,
            max_context_tokens: int = 1024,
            streaming: bool = False,
            system_prompt: str = SYSTEM_PROMPT,
            **kwargs
    ):
        """
        Initializes the ChatAgent with the given parameters.

        :param model_type: The type of the model, such as "openai" or "azure".
        :param model_name: The model name of OpenAI.
        :param model_api_key: The API keys for the OpenAI API.
        :param model_api_base: The base URLs for the OpenAI API.
        :param search_name: The name of the search engine to use, such as "serper" or "duckduckgo".
        :param enable_search_tool: If True, enables the search tool.
        :param enable_crawler_tool: If True, enables the web URL crawler tool.
        :param enable_run_python_code_tool: If True, enables the run Python code tool.
        :param verbose: If True, enables verbose logging.
        :param max_iterations: The maximum number of iterations for the agent executor.
        :param max_execution_time: The maximum execution time in seconds.
        :param temperature: The temperature for the OpenAI model.
        :param num_memory_turns: The number of memory turns to keep in the chat history, -1 for unlimited.
        :param max_tokens: The maximum number of tokens for the OpenAI model to generate.
        :param max_context_tokens: The maximum number of context tokens to use, prompt max tokens.
        :param streaming: If True, enables streaming mode.
        :param system_prompt: The system prompt to use for the ChatAgent.
        :param kwargs: Additional keyword arguments.
        """
        # Check max tokens
        total_limit = MODEL_TOKEN_LIMIT.get(model_name, 4096)
        # FIXME
        # https://community.openai.com/t/why-is-gpt-3-5-turbo-1106-max-tokens-limited-to-4096/494973/3
        max_tokens = min(max_tokens, 4096)
        if max_tokens + max_context_tokens > total_limit:
            logger.warning(f"The sum of max_tokens and max_context_tokens should be less than "
                           f"{total_limit}, but got {max_tokens + max_context_tokens}")
            # Adjust max_tokens and max_context_tokens proportionally to fit within the total_limit
            total_requested = max_tokens + max_context_tokens
            max_tokens = min(int((max_tokens / total_requested) * total_limit), 4096)
            max_context_tokens = total_limit - max_tokens
            logger.warning(f"Adjusted max_tokens to {max_tokens} and max_context_tokens to {max_context_tokens}")
        self.max_tokens = max_tokens
        self.max_context_tokens = max_context_tokens
        # Define llm
        if model_type == 'azure':
            self.llm = AzureChatOpenAI(
                openai_api_version=os.environ.get("OPENAI_API_VERSION"),
                openai_api_base=model_api_base,
                openai_api_key=model_api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=max_execution_time,
                streaming=streaming,
                **kwargs
            )
        elif model_type == 'openai':
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=model_api_key,
                openai_api_base=model_api_base,
                max_tokens=max_tokens,
                timeout=max_execution_time,
                streaming=streaming,
                **kwargs
            )
        elif model_type == 'dashscope':
            self.llm = ChatTongyi(
                model_name=model_name,
                dashscope_api_key=model_api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=max_execution_time,
                streaming=streaming,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        self.model_type = model_type
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_execution_time = max_execution_time
        self.streaming = streaming

        self.max_iterations = max_iterations
        self.verbose = verbose
        self.search_name = search_name
        self.system_prompt = system_prompt if system_prompt else SYSTEM_PROMPT

        # Define tools
        self.enable_search_tool = enable_search_tool
        self.enable_crawler_tool = enable_crawler_tool
        self.enable_run_python_code_tool = enable_run_python_code_tool
        self.tools = self._initialize_tools()

        # Define agent
        self.chat_history = []
        self.num_memory_turns = num_memory_turns
        if self.tools:
            self.agent_executor = self._initialize_agent_executor()
        else:
            self.agent_executor = self._initialize_chat_chain()
        logger.debug(f"ChatAgent initialized with model: {model_name}")

    def _initialize_search_engine(self):
        """
        Initializes the search engine based on the provided name.

        :param search_name: The name of the search engine.
        :return: An instance of the search engine.
        """
        if self.search_name == "serper":
            serper_api_key = os.getenv("SERPER_API_KEY")
            if not serper_api_key:
                raise ValueError("Missing `SERPER_API_KEY` environment variable.")
            search_engine = GoogleSerperAPIWrapper()
            search_engine.gl = 'cn'
            search_engine.hl = 'zh-cn'
            search_engine.serper_api_key = serper_api_key
        else:
            search_engine = DuckDuckGoSearchAPIWrapper()
        logger.debug(f"Initialized search engine: {self.search_name}")
        return search_engine

    def _initialize_tools(self):
        """
        Initializes the tools used by the ChatAgent.

        :return: A list of Tool instances.
        """
        E2B_API_KEY = os.environ.get("E2B_API_KEY", None)
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
        if self.enable_search_tool:
            # Define the search engine
            self.search_engine = self._initialize_search_engine()
            tools.append(Tool(name="Search", func=self.search_engine.run, description=SEARCH_TOOL_DESC))
        if self.enable_run_python_code_tool:
            tools.append(run_python_code_tool)
        if self.enable_crawler_tool:
            tools.append(web_url_crawler_tool)
        return tools

    def _initialize_agent_executor(self):
        """
        Initializes the AgentExecutor for the ChatAgent.

        :return: An instance of AgentExecutor.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        # logger.debug(f"Initialized ChatAgent prompt: {prompt}")
        if self.model_type in ['openai', 'azure']:
            llm_with_tools = self.llm.bind_tools(self.tools)
            agent = (
                    {
                        "input": lambda x: x["input"],
                        "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
                        "chat_history": lambda x: x["chat_history"] if "chat_history" in x and x[
                            "chat_history"] else [],
                    }
                    | prompt
                    | llm_with_tools
                    | OpenAIToolsAgentOutputParser()
            )
        else:
            agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            return_intermediate_steps=True,
            max_iterations=self.max_iterations,
            max_execution_time=self.max_execution_time,
            handle_parsing_errors=True,
        ).with_config({"run_name": "ChatAgent"})

    def _initialize_chat_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ]
        )
        # parser = StrOutputParser()
        chain = prompt | self.llm | OpenAIToolsAgentOutputParser()
        return chain.with_config({"run_name": "ChatAgent"})

    def count_token_length(self, text):
        """Count token length."""
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            model = "cl100k_base"
            encoding = tiktoken.get_encoding(model)
        length = len(encoding.encode(text))
        return length

    def _trim_chat_history_to_max_context_tokens(self, chat_history: List):
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

    def run(self, input_str: str, chat_history: Optional[List] = None):
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
            chat_history = self._trim_chat_history_to_max_context_tokens(chat_history)
        output = self.agent_executor.invoke(
            {"input": input_str, "chat_history": chat_history}
        )
        if hasattr(output, "log"):
            output_str = output.log
        else:
            output_str = output.get('output', '')
        chat_history.extend(
            [HumanMessage(content=input_str), AIMessage(content=output_str)]
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
            chat_history = self._trim_chat_history_to_max_context_tokens(chat_history)
        events = self.agent_executor.astream_events(
            {"input": input_str, "chat_history": chat_history},
            version="v1"
        )
        return events
