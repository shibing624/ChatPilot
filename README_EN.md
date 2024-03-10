[**🇨🇳中文**](https://github.com/shibing624/chatagent/blob/main/README.md) | [**🌐English**](https://github.com/shibing624/chatagent/blob/main/README_EN.md) | [**📖文档/Docs**](https://github.com/shibing624/chatagent/wiki) | [**🤖模型/Models**](https://huggingface.co/shibing624) 

<div align="center">
  <a href="https://github.com/shibing624/chatagent">
    <img src="https://github.com/shibing624/chatagent/blob/main/docs/logo.png" height="150" alt="Logo">
  </a>
</div>

-----------------

# chatagent: chat agent
[![PyPI version](https://badge.fury.io/py/chatagent.svg)](https://badge.fury.io/py/chatagent)
[![Downloads](https://static.pepy.tech/badge/chatagent)](https://pepy.tech/project/chatagent)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![python_version](https://img.shields.io/badge/Python-3.5%2B-green.svg)](requirements.txt)
[![GitHub issues](https://img.shields.io/github/issues/shibing624/chatagent.svg)](https://github.com/shibing624/chatagent/issues)
[![Wechat Group](https://img.shields.io/badge/wechat-group-green.svg?logo=wechat)](#Contact)


**chatagent**: Text to Vector, Get Sentence Embeddings. 文本向量化，把文本(包括词、句子、段落)表征为向量矩阵。

**chatagent**实现了Word2Vec、RankBM25、BERT、Sentence-BERT、CoSENT等多种文本表征、文本相似度计算模型，并在文本语义匹配（相似度计算）任务上比较了各模型的效果。

## Features
### Agent

1. search
2. rag
3. chat
4. crawler

## Demo

Official Demo: https://www.chatagent.com/product/short_text_sim/

HuggingFace Demo: https://huggingface.co/spaces/shibing624/chatagent

![](https://github.com/shibing624/chatagent/blob/main/docs/hf.png)

run example: [examples/gradio_demo.py](https://github.com/shibing624/chatagent/blob/main/examples/gradio_demo.py) to see the demo:
```shell
python examples/gradio_demo.py
```

## Install
```shell
pip install -U chatagent
```

or

```shell
pip install -r requirements.txt

git clone https://github.com/shibing624/chatagent.git
cd chatagent
pip install --no-deps .
```

## Usage

#### FastAPI服务

- 安装：
```pip install fastapi uvicorn```

- 启动服务：

example: [examples/fastapi_server_demo.py](https://github.com/shibing624/chatagent/blob/main/examples/fastapi_server_demo.py)
```shell
cd examples
python fastapi_server_demo.py
```

- 调用服务：
```shell
curl -X 'GET' \
  'http://0.0.0.0:8001/emb?q=hello' \
  -H 'accept: application/json'
```



## Contact

- Issue(建议)：[![GitHub issues](https://img.shields.io/github/issues/shibing624/chatagent.svg)](https://github.com/shibing624/chatagent/issues)
- 邮件我：xuming: xuming624@qq.com
- 微信我：加我*微信号：xuming624, 备注：姓名-公司-NLP* 进NLP交流群。

<img src="docs/wechat.jpeg" width="200" />


## Citation

如果你在研究中使用了chatagent，请按如下格式引用：

APA:
```latex
Xu, M. chatagent: LLM agent toolkit (Version 0.0.2) [Computer software]. https://github.com/shibing624/chatagent
```

BibTeX:
```latex
@misc{chatagent,
  author = {Ming Xu},
  title = {chatagent: llm agent},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/shibing624/chatagent}},
}
```

## License


授权协议为 [The Apache License 2.0](LICENSE)，可免费用做商业用途。请在产品说明中附加chatagent的链接和授权协议。


## Contribute
项目代码还很粗糙，如果大家对代码有所改进，欢迎提交回本项目，在提交之前，注意以下两点：

 - 在`tests`添加相应的单元测试
 - 使用`python -m pytest -v`来运行所有单元测试，确保所有单测都是通过的

之后即可提交PR。
