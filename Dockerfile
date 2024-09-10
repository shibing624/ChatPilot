FROM python:3.11-slim-bookworm
WORKDIR /app
COPY . /app
ENV ENV prod
# RAG Embedding Model Settings
ENV RAG_EMBEDDING_MODEL "text-embedding-ada-002"

RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu #--no-cache-dir
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple #--no-cache-dir

CMD ["bash", "start.sh"]