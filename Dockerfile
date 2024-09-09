# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm
WORKDIR /app
COPY . /app
ENV ENV prod
ENV PORT ""

ENV OLLAMA_BASE_URL ""
# RAG Embedding Model Settings
ENV RAG_EMBEDDING_MODEL "shibing624/text2vec-base-multilingual"

RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu #--no-cache-dir
RUN pip3 install -r requirements.txt #--no-cache-dir

CMD ["bash", "start.sh"]