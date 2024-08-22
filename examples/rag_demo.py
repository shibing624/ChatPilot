# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import sys

sys.path.append('..')
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from chatpilot.rag_fusion import RagFusion

if __name__ == '__main__':
    file_url = "https://docs.smith.langchain.com/overview"
    loader = WebBaseLoader(file_url)
    docs = loader.load()
    print(docs)
    web_documents = RecursiveCharacterTextSplitter(
        chunk_size=2000, chunk_overlap=200
    ).split_documents(docs)
    print('web_documents:', web_documents)
    rag_fusion = RagFusion(web_documents)
    question = "LangSmith是啥"
    result = rag_fusion.run(question)
    print(result)

    all_documents = {
        "doc1": "气候变化及其经济影响。",
        "doc2": "由于气候变化引起的公共卫生问题。",
        "doc3": "气候变化：社会视角。",
        "doc4": "应对气候变化的技术解决方案。",
        "doc5": "需要进行政策改变以应对气候变化。",
        "doc6": "气候变化及其对生物多样性的影响。",
        "doc7": "气候变化：科学和模型。",
        "doc8": "全球变暖：气候变化的一个子集。",
        "doc9": "气候变化如何影响日常天气。",
        "doc10": "关于气候变化活动主义的历史。",
    }

    text_documents = [Document(page_content=doc, metadata={"source": f"{id}"}) for id, doc in all_documents.items()]
    rag_fusion = RagFusion(text_documents)
    question = "气候变化的影响"
    result = rag_fusion.run(question)
    print(result)
