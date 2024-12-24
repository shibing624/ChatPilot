# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
from typing import Optional

from agentica import PythonAgent, AzureOpenAIChat, OpenAIChat, Agent, MoonshotChat, DeepSeekChat
from agentica.tools.search_serper_tool import SearchSerperTool
from agentica.tools.url_crawler_tool import UrlCrawlerTool

from chatpilot.config import (
    ENABLE_SEARCH_TOOL,
    ENABLE_URL_CRAWLER_TOOL,
    ENABLE_RUN_PYTHON_CODE_TOOL,
)


class AgenticaAgent:
    def __init__(
            self,
            model_type: str = "openai",
            model_name: str = "gpt-3.5-turbo",
            enable_search_tool: Optional[bool] = None,
            enable_url_crawler_tool: Optional[bool] = None,
            enable_run_python_code_tool: Optional[bool] = None,
            system_prompt: Optional[str] = None,
            verbose: Optional[bool] = False,
            add_chat_history_to_messages: Optional[bool] = True,
            **kwargs
    ):
        """
        Initializes the ChatAgent with the given parameters.

        :param model_type: The type of the model, such as "openai" / "azure" / "moonshot" / "deepseek".
        :param model_name: The model name of OpenAI.
        :param enable_search_tool: If True, enables the search tool.
        :param enable_url_crawler_tool: If True, enables the web URL crawler tool.
        :param enable_run_python_code_tool: If True, enables the run Python code tool.
        :param system_prompt: The system prompt to use for the model.
        :param verbose: If True, enables verbose logging.
        :param add_chat_history_to_messages: If True, adds the chat history to the messages.
        :param kwargs: Additional keyword arguments.
        """
        if model_type == 'azure':
            self.llm = AzureOpenAIChat(
                id=model_name,
                **kwargs
            )
        elif model_type == 'openai':
            self.llm = OpenAIChat(
                id=model_name,
                **kwargs
            )
        elif model_type == "moonshot":
            self.llm = MoonshotChat(
                id=model_name,
                **kwargs
            )
        elif model_type == "deepseek":
            self.llm = DeepSeekChat(
                id=model_name,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        self.model_type = model_type
        self.model_name = model_name

        # Define tools
        enable_search_tool = enable_search_tool if enable_search_tool is not None else ENABLE_SEARCH_TOOL
        enable_url_crawler_tool = (
            enable_url_crawler_tool if enable_url_crawler_tool is not None else ENABLE_URL_CRAWLER_TOOL
        )
        enable_run_python_code_tool = (
            enable_run_python_code_tool if enable_run_python_code_tool is not None else ENABLE_RUN_PYTHON_CODE_TOOL
        )
        self.tools = []
        if enable_search_tool:
            self.tools.append(SearchSerperTool())
        if enable_url_crawler_tool:
            self.tools.append(UrlCrawlerTool())
        if enable_run_python_code_tool:
            self.model = PythonAgent(
                model=self.llm,
                tools=self.tools,
                description=system_prompt,
                add_datetime_to_instructions=True,
                add_history_to_messages=add_chat_history_to_messages,
                show_tool_calls=True,
                read_chat_history=True,
                debug_mode=verbose,
            )
        else:
            self.model = Agent(
                model=self.llm,
                tools=self.tools,
                description=system_prompt,
                add_datetime_to_instructions=True,
                add_history_to_messages=add_chat_history_to_messages,
                show_tool_calls=True,
                read_chat_history=True,
                debug_mode=verbose,
            )
        self.verbose = verbose

    def __repr__(self):
        return f"AgenticaAgent(model={self.llm}, tools={self.tools})"

    def stream_run(self, input_str: str):
        """
        runs the given input string through the ChatAgent and returns the result.

        :param input_str: The input string to process.
        :return: An asynchronous generator of events.
        """

        return self.model.run(input_str, stream=True)

    def run(self, input_str: str):
        """
        runs the given input string through the ChatAgent and returns the result.

        :param input_str: The input string to process.
        :return: The result of the processing.
        """
        return self.model.run(input_str, stream=False)
