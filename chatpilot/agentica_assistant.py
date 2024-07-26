# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
from typing import Optional

from agentica import PythonAssistant, AzureOpenAILLM, OpenAILLM, Assistant
from agentica.tools.search_serper import SearchSerperTool
from agentica.tools.url_crawler import UrlCrawlerTool

from chatpilot.config import (
    ENABLE_SEARCH_TOOL,
    ENABLE_URL_CRAWLER_TOOL,
    ENABLE_RUN_PYTHON_CODE_TOOL,
)


class AgenticaAssistant:
    def __init__(
            self,
            model_type: str = "openai",
            model_name: str = "gpt-3.5-turbo-1106",
            enable_search_tool: Optional[bool] = None,
            enable_url_crawler_tool: Optional[bool] = None,
            enable_run_python_code_tool: Optional[bool] = None,
            verbose: bool = True,
            **kwargs
    ):
        """
        Initializes the ChatAgent with the given parameters.

        :param model_type: The type of the model, such as "openai" / "azure".
        :param model_name: The model name of OpenAI.
        :param model_api_key: The API keys for the OpenAI API.
        :param model_api_base: The base URLs for the OpenAI API.
        :param search_name: The name of the search engine to use, such as "serper" or "duckduckgo".
        :param agent_type: The type of the agent, such as "react" or "tools".
        :param enable_search_tool: If True, enables the search tool.
        :param enable_url_crawler_tool: If True, enables the web URL crawler tool.
        :param enable_run_python_code_tool: If True, enables the run Python code tool.
        :param verbose: If True, enables verbose logging.
        :param kwargs: Additional keyword arguments.
        """
        if model_type == 'azure':
            self.llm = AzureOpenAILLM(
                model=model_name,
                **kwargs
            )
        elif model_type == 'openai':
            self.llm = OpenAILLM(
                model=model_name,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        self.model_type = model_type
        self.model_name = model_name
        self.verbose = verbose

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
            self.model = PythonAssistant(
                llm=self.llm,
                tools=self.tools,
                description="你是一个有用的AI助手，请用中文回答问题",
                add_datetime_to_instructions=True,
                add_chat_history_to_messages=True,
                show_tool_calls=True,
                read_chat_history=True,
                debug_mode=True,
            )
        else:
            self.model = Assistant(
                llm=self.llm,
                tools=self.tools,
                description="你是一个有用的AI助手，请用中文回答问题",
                add_datetime_to_instructions=True,
                add_chat_history_to_messages=True,
                show_tool_calls=True,
                read_chat_history=True,
                debug_mode=True,
            )

    def __repr__(self):
        return f"AgenticaAssistant(llm={self.llm}, tools={self.tools})"

    def stream_run(self, input_str: str):
        """
        runs the given input string through the ChatAgent and returns the result.

        :param input_str: The input string to process.
        :return: An asynchronous generator of events.
        """

        return self.model.run(input_str, stream=True, print_output=False)

    def run(self, input_str: str):
        """
        runs the given input string through the ChatAgent and returns the result.

        :param input_str: The input string to process.
        :return: The result of the processing.
        """
        return self.model.run(input_str, stream=False, print_output=False)
