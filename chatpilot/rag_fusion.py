# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description:
pip install langchain langchain-community langchain-openai
"""

from typing import List

from langchain.load import dumps, loads
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.embeddings.text2vec import Text2vecEmbeddings
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from loguru import logger
import os
from chatpilot.config import RAG_TEMPLATE,OPENAI_API_KEY,OPENAI_API_BASE


class RagFusion:
    def __init__(
            self,
            documents: List[Document],
            model_api_key: str = os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY,
            model_api_base: str = os.getenv("OPENAI_API_BASE") or OPENAI_API_BASE,
            openai_model: str = "gpt-3.5-turbo-1106",
            generate_model: str = "gpt-3.5-turbo-16k",
            temperature: float = 0.0,
    ):
        """
        RagFusion
            1. Generate multiple queries
            2. Retrieve documents with multiple queries
            3. Rerank documents with reciprocal rank fusion, and return the top-k documents
            4. Generate answer with RAG model
        :param documents:
        """
        self.requery_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个有用的助手，可以根据单个输入查询生成多个搜索查询。"),
            ("user", "生成多个与此相关的搜索查询: {original_query}\n\nOUTPUT (4 queries):"),
        ])
        # Using LLM generate more queries
        self.requery_model = ChatOpenAI(
            openai_api_key=model_api_key,
            openai_api_base=model_api_base,
            temperature=temperature,
            model=openai_model,
        )
        vectorstore = Chroma.from_documents(
            documents,
            OpenAIEmbeddings(
                openai_api_key=model_api_key,
                openai_api_base=model_api_base,
            )
        )
        self.retriever = vectorstore.as_retriever()

        self.rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

        # LLM to RAG model
        self.generate_model = ChatOpenAI(
            openai_api_key=model_api_key,
            openai_api_base=model_api_base,
            temperature=temperature,
            model=generate_model,
        )

    @staticmethod
    def reciprocal_rank_fusion(results: list[list], k=60, topk=10):
        """Reciprocal Rank Fusion (RRF) for fusing the results of multiple retrievers."""
        fused_scores = {}
        for docs in results:
            # Assumes the docs are returned in sorted order of relevance
            for rank, doc in enumerate(docs):
                doc_str = dumps(doc)
                if doc_str not in fused_scores:
                    fused_scores[doc_str] = 0
                fused_scores[doc_str] += 1 / (rank + k)

        reranked_results = [
            (loads(doc), score)
            for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        ]
        result_str = "\n".join([doc.page_content for doc, score in reranked_results[:topk]])
        logger.debug(f"Reciprocal rank fusion result: {reranked_results}, topk str: {result_str}")
        return result_str

    def run(self, question: str):
        # RAG pipeline
        rag_chain = (
                {
                    "context": {"original_query": RunnablePassthrough()} | self.requery_prompt |
                               self.requery_model | StrOutputParser() | (lambda x: x.split("\n")) |
                               self.retriever.map() | self.reciprocal_rank_fusion,
                    "question": RunnablePassthrough()
                }
                | self.rag_prompt
                | self.generate_model
                | StrOutputParser()
        )
        r = rag_chain.invoke(question)
        return r


if __name__ == '__main__':
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
    print('text_documents:', text_documents)
    rag_fusion = RagFusion(text_documents)
    question = "气候变化及其经济影响"
    result = rag_fusion.run(question)
    print(result)
