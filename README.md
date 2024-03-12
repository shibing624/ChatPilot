[**🇨🇳中文**](https://github.com/shibing624/ChatPilot/blob/main/README.md) | [**🌐English**](https://github.com/shibing624/ChatPilot/blob/main/README_EN.md) | [**📖文档/Docs**](https://github.com/shibing624/ChatPilot/wiki) | [**🤖模型/Models**](https://huggingface.co/shibing624) 

<div align="center">
  <a href="https://github.com/shibing624/ChatPilot">
    <img src="https://github.com/shibing624/ChatPilot/blob/main/docs/logo.png" height="150" alt="Logo">
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


**ChatPilot**: Chat with Agent.


## Features
### Agent

1. search
2. rag：本项目新增了基于langchain的RAG fusion实现[rag_fusion.py](https://github.com/shibing624/ChatPilot/blob/main/chatpilot/rag_fusion.py)，多个近似query的检索结果融合，提升检索准确率
3. chat
4. crawler

## Demo

Official Demo: https://chat.mulanai.com

HuggingFace Demo: https://huggingface.co/spaces/shibing624/ChatPilot

![](https://github.com/shibing624/ChatPilot/blob/main/docs/hf.png)

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

## How to Install Without Docker

While we strongly recommend using our convenient Docker container installation for optimal support, we understand that some situations may require a non-Docker setup, especially for development purposes. Please note that non-Docker installations are not officially supported, and you might need to troubleshoot on your own.

### Project Components

Open WebUI consists of two primary components: the frontend and the backend (which serves as a reverse proxy, handling static frontend files, and additional features). Both need to be running concurrently for the development environment.

:::info
The backend is required for proper functionality
:::

### Requirements 📦

- 🐰 [Node.js](https://nodejs.org/en) >= 20.10 or [Bun](https://bun.sh) >= 1.0.21
- 🐍 [Python](https://python.org) >= 3.11

### Build and Install 🛠️

Run the following commands to install:

```sh
git clone https://github.com/shibing624/ChatPilot.git
cd ChatPilot/

# Copying required .env file
cp .env.example .env

# Building Frontend Using Node
cd web
npm install
npm run build

# Serving Frontend with the Backend
cd ..
pip install -r requirements.txt -U
bash start.sh
```

You should have Open WebUI up and running at http://localhost:8080/. Enjoy! 😄

## Usage

### 1. 构建前端web

两种方法构建前端：
1. 下载打包好的前端ui，https://github.com/shibing624/SmartSearch/releases/download/0.1.0/ui.zip 解压到项目根目录直接使用。
2. 自己使用npm构建前端（需要nodejs 18以上版本）
```shell
cd web && npm install && npm run build
```
输出：项目根目录产出`ui`文件夹，包含前端静态文件。

### 2. 启动后端服务

```shell
python main.py
```
好了，现在你的搜索应用正在运行：http://0.0.0.0:8080


## Contact

- Issue(建议)：[![GitHub issues](https://img.shields.io/github/issues/shibing624/ChatPilot.svg)](https://github.com/shibing624/ChatPilot/issues)
- 邮件我：xuming: xuming624@qq.com
- 微信我：加我*微信号：xuming624, 备注：姓名-公司-NLP* 进NLP交流群。

<img src="docs/wechat.jpeg" width="200" />


## Citation

如果你在研究中使用了ChatPilot，请按如下格式引用：

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


授权协议为 [The Apache License 2.0](LICENSE)，可免费用做商业用途。请在产品说明中附加ChatPilot的链接和授权协议。


## Contribute
项目代码还很粗糙，如果大家对代码有所改进，欢迎提交回本项目，在提交之前，注意以下两点：

 - 在`tests`添加相应的单元测试
 - 使用`python -m pytest -v`来运行所有单元测试，确保所有单测都是通过的

之后即可提交PR。

## Reference

- [Open WebUI](https://github.com/shibing624/ChatPilot)
- [langchain-ai/langchain](https://github.com/langchain-ai/langchain)