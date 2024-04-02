# syntax=docker/dockerfile:1
FROM node:alpine as build
WORKDIR /app
RUN wget "https://github.com/shibing624/ChatPilot/archive/refs/heads/main.zip" | unzip main.zip | mv ChatPilot-main /app
RUN wget "https://github.com/shibing624/ChatPilot/releases/download/v0.0.2/build.zip" | unzip build.zip | mv build /app/ChatPilot-main/web/

FROM python:3.11-slim-bookworm as base
WORKDIR /app/ChatPilot-main

ENV ENV=prod
ENV PORT ""

ENV OLLAMA_BASE_URL ""
ENV OPENAI_API_BASE_URLS ""
ENV OPENAI_API_KEYS ""

ENV WEBUI_SECRET_KEY ""

ENV SCARF_NO_ANALYTICS true
ENV DO_NOT_TRACK true

# RAG Embedding Model Settings
ENV RAG_EMBEDDING_MODEL="shibing624/text2vec-base-multilingual"

RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip3 install -r requirements.txt

CMD [ "bash", "start.sh"]
