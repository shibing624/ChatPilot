[**🇨🇳中文**](https://github.com/shibing624/ChatPilot/blob/main/README.md) | [**🌐English**](https://github.com/shibing624/ChatPilot/blob/main/README_EN.md) 

<div align="center">
  <a href="https://github.com/shibing624/ChatPilot">
    <img src="https://github.com/shibing624/ChatPilot/blob/main/docs/favicon.png" height="150" alt="Logo">
  </a>
</div>

-----------------

# ChatPilot: Chat Agent
[![PyPI version](https://badge.fury.io/py/ChatPilot.svg)](https://badge.fury.io/py/ChatPilot)
[![Downloads](https://static.pepy.tech/badge/ChatPilot)](https://pepy.tech/project/ChatPilot)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![python_version](https://img.shields.io/badge/Python-3.9%2B-green.svg)](requirements.txt)
[![GitHub issues](https://img.shields.io/github/issues/shibing624/ChatPilot.svg)](https://github.com/shibing624/ChatPilot/issues)
[![Wechat Group](https://img.shields.io/badge/wechat-group-green.svg?logo=wechat)](#Contact)

**ChatPilot**: Implements AgentChat dialogue, supports Google search, file URL dialogue (RAG), code interpreter function, reproduces Kimi Chat (file, drag in; URL, send out), supports OpenAI/Azure API.


## Features

- This project implements the Agent question and answer dialogue of ReAct and OpenAI Function Call based on LangChain, and supports the automatic calling of the following tools:
   - Internet search tool: Google Search API (Serper/DuckDuckGo)
   - URL automatic parsing tool: reproduces the function of sending Kimi Chat URL
   - Python code interpreter: supports E2B virtual environment and local python compiler environment to run code
- This project implements retrieval-enhanced RAG file Q&A that supports query rewriting based on LangChain
- Supports separation of front-end and back-end services. The front-end uses Svelte and the back-end uses FastAPI.
- Support voice input and output, support image generation
- Support user management, permission control, support import and export of chat records
## Demo

Official Demo: https://chat.mulanai.com

![](https://github.com/shibing624/ChatPilot/blob/main/docs/shot.png)

## Install
```shell
pip install -U chatpilot
```

or

```shell
git clone https://github.com/shibing624/ChatPilot.git
cd ChatPilot
pip install -e .
```


## Usage

### Local deployment

#### 1. Build front-end web

Two ways to build the front end:
1. Download the packaged and compiled front-end [buid.zip](https://github.com/shibing624/ChatPilot/releases/download/0.1.2/build.zip) and extract it to the project web directory.
2. Build the front end yourself using npm:

Requirements:

- 🐰 [Node.js](https://nodejs.org/en) >= 20.10
- 🐍 [Python](https://python.org) >= 3.10

```sh
git clone https://github.com/shibing624/ChatPilot.git
cd ChatPilot/

# Copying required .env file
cp .env.example .env

# Building Frontend Using Node
cd web
npm install
npm run build
```
Output: The project `web` directory outputs the `build` folder, which contains the front-end compilation output files.
#### 2. Start the backend service

```shell
cd ..
pip install -r requirements.txt -U
bash start.sh
```
Ok, now your application is running: http://0.0.0.0:8080 Enjoy! 😄

### CLI

code: [cli.py](https://github.com/shibing624/ChatPilot/blob/main/chatpilot/cli.py)

```
> chatpilot -h                                    
usage: __main__.py [-h] [--model MODEL] [--search SEARCH] [--openai_api_key OPENAI_API_KEY] [--openai_api_base OPENAI_API_BASE] [--serper_api_key SERPER_API_KEY]



chatpilot cli


options:
  -h, --help            show this help message and exit
  --model MODEL         openai model name
  --search SEARCH       search engine name, e.g. duckduckgo, serper
  --openai_api_key OPENAI_API_KEY
                        openai api key
  --openai_api_base OPENAI_API_BASE
                        openai api base url
  --serper_api_key SERPER_API_KEY
                        serper api key
```

run：

```shell
pip install chatpilot -U
chatpilot
```

> User: Input question，e.g: "introduce beijing"

## Contact


- Issue (suggestion): [![GitHub issues](https://img.shields.io/github/issues/shibing624/ChatPilot.svg)](https://github.com/shibing624/ChatPilot/issues)
- Email me: xuming: xuming624@qq.com
- WeChat Me: Add me* WeChat ID: xuming624, Remarks: Name-Company-NLP* to join the NLP communication group.
<img src="docs/wechat.jpeg" width="200" />


## Citation

If you use ChatPilot in your research, please cite it in the following format:
APA:
```latex
Xu, M. ChatPilot: LLM agent toolkit (Version 0.0.2) [Computer software]. https://github.com/shibing624/ChatPilot
```

BibTeX:
```latex
@misc{ChatPilot,
  author = {Ming Xu},
  title = {ChatPilot: llm agent},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/shibing624/ChatPilot}},
}
```

## License


The licensing agreement is [The Apache License 2.0](LICENSE), which is free for commercial use. Please attach the link to ChatPilot and the license agreement in the product description.


## Contribute
The project code is still very rough. If you have any improvements to the code, you are welcome to submit it back to this project. Before submitting, please pay attention to the following two points:

  - Add corresponding unit tests in `tests`
  - Use `python -m pytest -v` to run all unit tests to ensure that all unit tests pass

You can then submit a PR.

## Reference

- [Open WebUI](https://github.com/shibing624/ChatPilot)
- [langchain-ai/langchain](https://github.com/langchain-ai/langchain)