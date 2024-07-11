# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import json
import os
from datetime import datetime
from pathlib import Path

import yaml
from loguru import logger
from openai import OpenAI

from chatpilot.constants import ERROR_MESSAGES

pwd_path = os.path.abspath(os.path.dirname(__file__))
WEBUI_NAME = "ChatPilot"
DOTENV_PATH = os.path.realpath(os.getenv("DOTENV_PATH", os.path.join(pwd_path, "../.env")))
try:
    from dotenv import load_dotenv  # noqa

    if load_dotenv(DOTENV_PATH, override=True, verbose=True):
        logger.info(f"Loaded environment variables from {DOTENV_PATH}")
except ImportError:
    logger.debug("dotenv not installed, skipping...")

DATA_DIR = str(os.path.expanduser(os.getenv("DATA_DIR", "~/.cache/chatpilot/data")))
DB_PATH = f"{DATA_DIR}/web.db"
ENV = os.environ.get("ENV", "dev")
# Frontend build dir, which is npm build dir
FRONTEND_BUILD_DIR = str(Path(os.getenv("FRONTEND_BUILD_DIR", os.path.join(pwd_path, "../web/build"))))
# Frontend static dir, which is for static files like favicon, logo, etc
FRONTEND_STATIC_DIR = str(Path(os.getenv("FRONTEND_STATIC_DIR", os.path.join(pwd_path, "../web/static"))))

try:
    with open(f"{DATA_DIR}/config.json", "r") as f:
        CONFIG_DATA = json.load(f)
except:
    CONFIG_DATA = {}

####################################
# File Upload DIR
####################################

UPLOAD_DIR = f"{DATA_DIR}/uploads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

####################################
# Cache DIR
####################################

CACHE_DIR = f"{DATA_DIR}/cache"
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

####################################
# Docs DIR
####################################

DOCS_DIR = f"{DATA_DIR}/docs"
Path(DOCS_DIR).mkdir(parents=True, exist_ok=True)


####################################
# LITELLM_CONFIG
####################################


def create_config_file(file_path):
    directory = os.path.dirname(file_path)

    # Check if directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Data to write into the YAML file
    config_data = {
        "general_settings": {},
        "litellm_settings": {},
        "model_list": [],
        "router_settings": {},
    }

    # Write data to YAML file
    with open(file_path, "w", encoding='utf8') as file:
        yaml.dump(config_data, file)


LITELLM_CONFIG_PATH = f"{DATA_DIR}/litellm/config.yaml"

if not os.path.exists(LITELLM_CONFIG_PATH):
    logger.debug("Config file doesn't exist. Creating...")
    create_config_file(LITELLM_CONFIG_PATH)
    logger.info(f"LiteLLM Config file created successfully, path: {LITELLM_CONFIG_PATH}")

####################################
# OLLAMA_BASE_URL
####################################

OLLAMA_API_BASE_URL = os.environ.get(
    "OLLAMA_API_BASE_URL", "http://localhost:11434/api"
)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "")

if OLLAMA_BASE_URL == "" and OLLAMA_API_BASE_URL != "":
    OLLAMA_BASE_URL = (
        OLLAMA_API_BASE_URL[:-4]
        if OLLAMA_API_BASE_URL.endswith("/api")
        else OLLAMA_API_BASE_URL
    )

OLLAMA_BASE_URLS = [url.strip() for url in OLLAMA_BASE_URL.split(";")]

####################################
# OPENAI_API
####################################
MODEL_TYPE = os.environ.get("MODEL_TYPE", "openai")  # it can be openai / azure
AGENT_TYPE = os.environ.get("AGENT_TYPE", "react")  # it can be react / function_call
FRAMEWORK = os.environ.get("FRAMEWORK", "langchain")  # it can be langchain / agentica
logger.debug(f"MODEL_TYPE: {MODEL_TYPE}, AGENT_TYPE: {AGENT_TYPE}, FRAMEWORK: {FRAMEWORK}")

# api key can be multiple, separated by comma(,)
OPENAI_API_KEYS = os.environ.get("OPENAI_API_KEYS", os.environ.get("OPENAI_API_KEY"))
OPENAI_API_KEYS = [i.strip() for i in OPENAI_API_KEYS.split(",")]
OPENAI_API_KEY = OPENAI_API_KEYS[0]

# api base url can be multiple, separated by comma(,) same lengths as api keys
OPENAI_API_BASE_URLS = os.environ.get(
    "OPENAI_API_BASE_URLS", os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
)
OPENAI_API_BASE_URLS = [i.strip() for i in OPENAI_API_BASE_URLS.split(",")]
# if no api base url is provided, set it with fist one
OPENAI_API_BASE = OPENAI_API_BASE_URLS[0]
assert len(OPENAI_API_KEYS) == len(OPENAI_API_BASE_URLS), "Number of OpenAI API keys and base URLs should be the same"

# AZURE openai api
OPENAI_API_VERSION = os.environ.get("OPENAI_API_VERSION", None)
# if OPENAI_API_VERSION not None, it will use azure openai api, please set azure_endpoint to OPENAI_API_BASE,
# set api_key to OPENAI_API_KEY


MODEL_TOKEN_LIMIT = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-instruct": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-1106": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-1106-preview": 128000,
    "gpt-4-0125-preview": 128000,
    "gpt-4-vision-preview": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4-turbo-preview": 128000,
    "gpt-4-turbo-2024-04-09": 128000,
    "gpt-4o": 128000,
    "gpt-4o-2024-05-13": 128000,
    "moonshot-v1-8k": 8000,
    "moonshot-v1-32k": 32000,
    "moonshot-v1-128k": 128000,
    "deepseek-chat": 32768,
    "deepseek-coder": 16384,
}

# Dashscope Tongyi Qwen model
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")

# Deepseek api
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_BASE = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

# Moonshot api(kimi)
MOONSHOT_API_KEY = os.environ.get("MOONSHOT_API_KEY", "")
MOONSHOT_API_BASE = os.environ.get("MOONSHOT_API_BASE", "https://api.moonshot.cn/v1")

RPD = int(os.environ.get("RPD", -1))  # RPD(Request Pre Day)
RPM = int(os.environ.get("RPM", -1))  # RPM(Request Per Minute)

# Search engine
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", None)
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", None)

# code-interpreter
E2B_API_KEY = os.environ.get("E2B_API_KEY", None)

####################################
# RAG
####################################

CHROMA_DATA_PATH = f"{DATA_DIR}/vector_db"
# openai embedding is support, text2vec and sentence-transformers are also available
RAG_EMBEDDING_MODEL = os.environ.get("RAG_EMBEDDING_MODEL", "text-embedding-ada-002")

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 100))
RAG_TOP_K = int(os.environ.get("RAG_TOP_K", 5))
DOC_TEXT_LENGTH_LIMIT = int(os.environ.get("DOC_TEXT_LENGTH_LIMIT", -1))

RAG_TEMPLATE = """根据以下文档资料（context）回答问题，不要使用外部工具。
<context>
[context]
</context>

问题: [query]
"""

ENABLE_RUN_PYTHON_CODE_TOOL = os.environ.get("ENABLE_RUN_PYTHON_CODE_TOOL", "True").lower() == "true"
RUN_PYTHON_CODE_TOOL_DESC = """Python Code Interpreter Tool. ALWAYS PRINT VARIABLES TO SHOW THE VALUE. \
The environment is long running and exists across multiple executions. \
You must send the whole script every time and print your outputs. \
Script should be pure python code that can be evaluated. \
It should be in python format NOT markdown. \
The code should NOT be wrapped in backticks. \
All python packages including requests, matplotlib, scipy, numpy, pandas, \
etc are available. Create and display chart using `plt.show()`."""

ENABLE_SEARCH_TOOL = os.environ.get("ENABLE_SEARCH_TOOL", "True").lower() == "true"
SEARCH_TOOL_DESC = """A Google Search API. Useful for when you need to ask with search. Input should be a search query."""

ENABLE_URL_CRAWLER_TOOL = os.environ.get("ENABLE_URL_CRAWLER_TOOL", "True").lower() == "true"
URL_CRAWLER_TOOL_DESC = """当用户问题包含以http开头的URL链接时，可用WebUrlCrawler工具"""

current_date = datetime.now().strftime("%Y-%m-%d")
SYSTEM_PROMPT = "你是一个强大的AI助理。你会为用户提供安全，有帮助，准确的回答。\n"
# SYSTEM_PROMPT += """
# - 如果问题涉及以下情况，请直接使用你的内置知识库回答：1.常识性问题，如科学事实（例如水的化学式是什么）、语言学问题（例如某个单词的意思）;\
# 2.历史事实或普遍接受的知识，如历史事件的日期、科学理论的基本解释; \
# 3.日常生活问题，如“我为什么没有参加父母的婚礼？”这类逻辑或常识性问题; \
# 4.文化常识，如文学作品的作者、电影的演员; \
# 5.个人建议或常见问题解答，如“如何修复自行车轮胎？”或者“如何煮意面？”。
# """
SYSTEM_PROMPT += """- 【重要】注意并遵循用户问题中提到的每一条指令，尽你所能的去很好的完成用户的指令。如果指令超出了你的能力范围，礼貌的告诉用户
- 【重要】当你的回答需要事实性信息的时候，尽可能多的使用上下文中的事实性信息，包括但不限于用户上传的文档/网页，搜索的结果等
- 【重要】给出丰富，详尽且有帮助的回答
"""
SYSTEM_PROMPT += f"今天的日期: {current_date} "

REACT_RPOMPT = """
如有需要你可以使用以下工具:

{tools}

当你使用工具时，按下面格式输出:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

开始！记得用 简体中文 回答问题。
"""
####################################
# WEBUI
####################################

ENABLE_SIGNUP = os.environ.get("ENABLE_SIGNUP", "True").lower() == "true"
DEFAULT_MODELS = os.environ.get("DEFAULT_MODELS", "gpt-3.5-turbo-1106")
DEFAULT_MODELS = [i.strip() for i in DEFAULT_MODELS.split(",")]

DEFAULT_PROMPT_SUGGESTIONS = (
    CONFIG_DATA["ui"]["prompt_suggestions"]
    if "ui" in CONFIG_DATA
       and "prompt_suggestions" in CONFIG_DATA["ui"]
       and type(CONFIG_DATA["ui"]["prompt_suggestions"]) is list
    else [
        {
            "title": ["介绍北京", "执行知识问答"],
            "content": "一句话介绍北京",
        },
        {
            "title": ["帮我算题", "执行代码解释器"],
            "content": "计算38023*40334=?",
        },
        {
            "title": ["北京今日天气", "执行搜索"],
            "content": "搜索一下北京今日天气",
        },
        {
            "title": ["Show me a code snippet", "of a website's sticky header"],
            "content": "Show me a code snippet of a website's sticky header in CSS and JavaScript. "
                       "just show me the code.",
        },
    ]
)

DEFAULT_USER_ROLE = os.getenv("DEFAULT_USER_ROLE", "user")
USER_PERMISSIONS = {"chat": {"deletion": True}}

MODEL_FILTER_ENABLED = os.environ.get("MODEL_FILTER_ENABLED", False)
MODEL_FILTER_LIST = os.environ.get("MODEL_FILTER_LIST", "")
MODEL_FILTER_LIST = [model.strip() for model in MODEL_FILTER_LIST.split(",")]

####################################
# WEBUI_AUTH (Required for security)
####################################

WEBUI_AUTH = True

####################################
# WEBUI_SECRET_KEY
####################################

WEBUI_SECRET_KEY = os.environ.get(
    "WEBUI_SECRET_KEY", os.environ.get("WEBUI_JWT_SECRET_KEY", "a0b-s3cr3t")
)

if WEBUI_AUTH and WEBUI_SECRET_KEY == "":
    raise ValueError(ERROR_MESSAGES.ENV_VAR_NOT_FOUND)


class OpenAIClientWrapper:
    def __init__(self, keys, base_urls):
        """
        初始化OpenAIClientWrapper实例。

        :param keys: 一个包含API密钥的列表。
        :param base_urls: 一个包含与API密钥配套使用的基础URL的列表。
        """
        assert len(keys) == len(base_urls), "Keys and base URLs must have the same length."
        self.keys = keys
        self.base_urls = base_urls
        self.current_index = 0
        # 初始化时，选择第一个密钥和URL
        self.client = OpenAI(
            api_key=self.keys[self.current_index],
            base_url=self.base_urls[self.current_index]
        )

    def get_client(self):
        """
        获取配置了当前API密钥和基础URL的OpenAI客户端实例。

        :return: 配置了当前API密钥和URL的OpenAI客户端实例。
        """
        self.client.api_key, self.client.base_url = self.get_next_key_base_url()
        return self.client

    def get_next_key_base_url(self):
        """用于获取下一个API密钥、URL"""
        key = self.keys[self.current_index]
        base_url = self.base_urls[self.current_index]
        # 更新索引以便下次调用时使用下一个密钥
        self.current_index = (self.current_index + 1) % len(self.keys)
        return key, base_url
