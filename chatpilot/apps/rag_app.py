# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import hashlib
import json
import mimetypes
import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional, cast

from chromadb.api.types import Documents as ChromaDocuments
from chromadb.api.types import (
    EmbeddingFunction,
    Embeddings,
)
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction
from chromadb.utils.embedding_functions.text2vec_embedding_function import Text2VecEmbeddingFunction
from chromadb.utils.embedding_functions.sentence_transformer_embedding_function import (
    SentenceTransformerEmbeddingFunction
)
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import (
    WebBaseLoader,
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredEPubLoader,
    UnstructuredMarkdownLoader,
    UnstructuredXMLLoader,
    UnstructuredRSTLoader,
    UnstructuredExcelLoader,
)
from loguru import logger
from pydantic import BaseModel

from chatpilot.apps.auth_utils import get_current_user, get_admin_user
from chatpilot.apps.misc import (
    calculate_sha256,
    calculate_sha256_string,
    sanitize_filename,
    extract_folders_after_data_docs,
)
from chatpilot.apps.rag_utils import query_doc, query_collection, ChineseRecursiveTextSplitter, CHROMA_CLIENT
from chatpilot.apps.web.models.documents import (
    Documents,
    DocumentForm,
)
from chatpilot.config import (
    UPLOAD_DIR,
    DOCS_DIR,
    RAG_EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RAG_TEMPLATE,
    RAG_TOP_K,
    OPENAI_API_KEYS,
    OPENAI_API_BASE_URLS,
    DOC_TEXT_LENGTH_LIMIT,
)
from chatpilot.constants import ERROR_MESSAGES

app = FastAPI()

app.state.PDF_EXTRACT_IMAGES = False
app.state.CHUNK_SIZE = CHUNK_SIZE
app.state.CHUNK_OVERLAP = CHUNK_OVERLAP
app.state.RAG_TEMPLATE = RAG_TEMPLATE
app.state.RAG_EMBEDDING_MODEL = RAG_EMBEDDING_MODEL
app.state.TOP_K = RAG_TOP_K
app.state.OPENAI_API_KEYS = OPENAI_API_KEYS
app.state.OPENAI_API_BASE_URLS = OPENAI_API_BASE_URLS


class LiteralHashEmbeddingFunction(EmbeddingFunction[ChromaDocuments]):
    """A simple embedding function that hashes the input documents as a list of floats."""

    def _hash_document(self, document: str) -> List[float]:
        # Calculate the SHA-256 hash of the document
        hash_object = hashlib.sha256(document.encode())
        hash_list = list(hash_object.digest())
        float_list = [float(x) / 255.0 for x in hash_list]
        return float_list

    def __call__(self, input: ChromaDocuments) -> Embeddings:
        # Transform the input documents into embeddings
        embeddings = [self._hash_document(doc) for doc in input]
        return cast(Embeddings, embeddings)


class Word2VecEmbeddingFunction(EmbeddingFunction[ChromaDocuments]):
    """Word2Vec embedding function that encodes the input documents as a list of floats."""

    def __init__(self, model_name: str = "w2v-light-tencent-chinese"):
        try:
            from text2vec import Word2Vec
        except ImportError:
            raise ValueError(
                "The text2vec python package is not installed. Please install it with `pip install text2vec`"
            )
        self._model = Word2Vec(model_name_or_path=model_name)

    def __call__(self, input: ChromaDocuments) -> Embeddings:
        return cast(
            Embeddings, self._model.encode(list(input)).tolist()
        )  # noqa E501


if "text-embedding" in app.state.RAG_EMBEDDING_MODEL and app.state.OPENAI_API_KEYS and app.state.OPENAI_API_KEYS[0]:
    app.state.sentence_transformer_ef = OpenAIEmbeddingFunction(
        api_key=app.state.OPENAI_API_KEYS[0],
        api_base=app.state.OPENAI_API_BASE_URLS[0],
        model_name=app.state.RAG_EMBEDDING_MODEL,
    )
elif "text2vec" in app.state.RAG_EMBEDDING_MODEL:
    app.state.sentence_transformer_ef = Text2VecEmbeddingFunction(
        model_name=app.state.RAG_EMBEDDING_MODEL
    )
elif "w2v" in app.state.RAG_EMBEDDING_MODEL:
    app.state.sentence_transformer_ef = Word2VecEmbeddingFunction(
        model_name=app.state.RAG_EMBEDDING_MODEL
    )
else:
    app.state.sentence_transformer_ef = LiteralHashEmbeddingFunction()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.debug(f"app.state.sentence_transformer_ef: {app.state.sentence_transformer_ef}")


class CollectionNameForm(BaseModel):
    collection_name: Optional[str] = "test"


class StoreWebForm(CollectionNameForm):
    url: str


def store_data_in_vector_db(data, collection_name, overwrite: bool = False) -> bool:
    text_splitter = ChineseRecursiveTextSplitter(
        chunk_size=app.state.CHUNK_SIZE, chunk_overlap=app.state.CHUNK_OVERLAP,
        doc_text_length_limit=DOC_TEXT_LENGTH_LIMIT
    )
    docs = text_splitter.split_documents(data)

    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]

    try:
        if overwrite:
            for collection in CHROMA_CLIENT.list_collections():
                if collection_name == collection.name:
                    logger.debug(f"deleting existing collection {collection_name}")
                    CHROMA_CLIENT.delete_collection(name=collection_name)

        collection = CHROMA_CLIENT.create_collection(
            name=collection_name,
            embedding_function=app.state.sentence_transformer_ef,
        )

        collection.add(
            documents=texts, metadatas=metadatas, ids=[str(uuid.uuid1()) for _ in texts]
        )
        return True
    except Exception as e:
        logger.error(e)
        if e.__class__.__name__ == "UniqueConstraintError":
            return True

        return False


@app.get("/")
async def get_status():
    return {
        "status": True,
        "chunk_size": app.state.CHUNK_SIZE,
        "chunk_overlap": app.state.CHUNK_OVERLAP,
        "template": app.state.RAG_TEMPLATE,
        "embedding_model": app.state.RAG_EMBEDDING_MODEL,
    }


@app.get("/embedding/model")
async def get_embedding_model(user=Depends(get_admin_user)):
    return {
        "status": True,
        "embedding_model": app.state.RAG_EMBEDDING_MODEL,
    }


class EmbeddingModelUpdateForm(BaseModel):
    embedding_model: str


@app.post("/embedding/model/update")
async def update_embedding_model(
        form_data: EmbeddingModelUpdateForm, user=Depends(get_admin_user)
):
    app.state.RAG_EMBEDDING_MODEL = form_data.embedding_model
    if "text2vec" in app.state.RAG_EMBEDDING_MODEL:
        app.state.sentence_transformer_ef = (
            embedding_functions.Text2VecEmbeddingFunction(
                model_name=app.state.RAG_EMBEDDING_MODEL,
            )
        )
    elif "text-embedding" in app.state.RAG_EMBEDDING_MODEL:
        if app.state.OPENAI_API_KEYS and app.state.OPENAI_API_KEYS[0]:
            app.state.sentence_transformer_ef = (
                embedding_functions.OpenAIEmbeddingFunction(
                    api_key=app.state.OPENAI_API_KEYS[0],
                    api_base=app.state.OPENAI_API_BASE_URLS[0],
                    model_name=app.state.RAG_EMBEDDING_MODEL,
                )
            )
        else:
            raise ValueError("No OpenAI API key found")
    elif "w2v" in app.state.RAG_EMBEDDING_MODEL:
        app.state.sentence_transformer_ef = Word2VecEmbeddingFunction(
            model_name=app.state.RAG_EMBEDDING_MODEL
        )
    elif app.state.RAG_EMBEDDING_MODEL:
        app.state.sentence_transformer_ef = SentenceTransformerEmbeddingFunction(
            model_name=app.state.RAG_EMBEDDING_MODEL
        )
    else:
        app.state.sentence_transformer_ef = LiteralHashEmbeddingFunction()
    logger.debug(f"Update app.state.sentence_transformer_ef: {app.state.sentence_transformer_ef}")

    return {
        "status": True,
        "embedding_model": app.state.RAG_EMBEDDING_MODEL,
    }


@app.get("/config")
async def get_rag_config(user=Depends(get_admin_user)):
    return {
        "status": True,
        "pdf_extract_images": app.state.PDF_EXTRACT_IMAGES,
        "chunk": {
            "chunk_size": app.state.CHUNK_SIZE,
            "chunk_overlap": app.state.CHUNK_OVERLAP,
        },
    }


class ChunkParamUpdateForm(BaseModel):
    chunk_size: int
    chunk_overlap: int


class ConfigUpdateForm(BaseModel):
    pdf_extract_images: bool
    chunk: ChunkParamUpdateForm


@app.post("/config/update")
async def update_rag_config(form_data: ConfigUpdateForm, user=Depends(get_admin_user)):
    app.state.PDF_EXTRACT_IMAGES = form_data.pdf_extract_images
    app.state.CHUNK_SIZE = form_data.chunk.chunk_size
    app.state.CHUNK_OVERLAP = form_data.chunk.chunk_overlap

    return {
        "status": True,
        "pdf_extract_images": app.state.PDF_EXTRACT_IMAGES,
        "chunk": {
            "chunk_size": app.state.CHUNK_SIZE,
            "chunk_overlap": app.state.CHUNK_OVERLAP,
        },
    }


@app.get("/template")
async def get_rag_template(user=Depends(get_current_user)):
    return {
        "status": True,
        "template": app.state.RAG_TEMPLATE,
    }


@app.get("/query/settings")
async def get_query_settings(user=Depends(get_admin_user)):
    return {
        "status": True,
        "template": app.state.RAG_TEMPLATE,
        "k": app.state.TOP_K,
    }


class QuerySettingsForm(BaseModel):
    k: Optional[int] = None
    template: Optional[str] = None


@app.post("/query/settings/update")
async def update_query_settings(
        form_data: QuerySettingsForm, user=Depends(get_admin_user)
):
    app.state.RAG_TEMPLATE = form_data.template if form_data.template else RAG_TEMPLATE
    app.state.TOP_K = form_data.k if form_data.k else 4
    return {"status": True, "template": app.state.RAG_TEMPLATE}


class QueryDocForm(BaseModel):
    collection_name: str
    query: str
    k: Optional[int] = None


@app.post("/query/doc")
def query_doc_handler(
        form_data: QueryDocForm,
        user=Depends(get_current_user),
):
    try:
        return query_doc(
            collection_name=form_data.collection_name,
            query=form_data.query,
            k=form_data.k if form_data.k else app.state.TOP_K,
            embedding_function=app.state.sentence_transformer_ef,
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


class QueryCollectionsForm(BaseModel):
    collection_names: List[str]
    query: str
    k: Optional[int] = None


@app.post("/query/collection")
def query_collection_handler(form_data: QueryCollectionsForm, user=Depends(get_current_user)):
    """Query collection, default db is chroma."""
    return query_collection(
        collection_names=form_data.collection_names,
        query=form_data.query,
        k=form_data.k if form_data.k else app.state.TOP_K,
        embedding_function=app.state.sentence_transformer_ef,
    )


@app.post("/web")
def store_web(form_data: StoreWebForm, user=Depends(get_current_user)):
    """Get data from web and store in vector db."""
    try:
        # input is url, e.g. "https://www.gutenberg.org/files/1727/1727-h/1727-h.htm"
        loader = WebBaseLoader(form_data.url)
        try:
            data = loader.lazy_load()
        except NotImplementedError:
            data = loader.load()

        collection_name = form_data.collection_name
        if collection_name == "":
            collection_name = calculate_sha256_string(form_data.url)[:63]

        store_data_in_vector_db(data, collection_name, overwrite=True)
        return {
            "status": True,
            "collection_name": collection_name,
            "filename": form_data.url,
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


def get_loader(filename: str, file_content_type: str, file_path: str):
    """Get loader by file type."""
    file_ext = filename.split(".")[-1].lower()
    known_type = True

    known_source_ext = [
        "go",
        "py",
        "java",
        "sh",
        "bat",
        "ps1",
        "cmd",
        "js",
        "ts",
        "css",
        "cpp",
        "hpp",
        "h",
        "c",
        "cs",
        "sql",
        "log",
        "ini",
        "pl",
        "pm",
        "r",
        "dart",
        "dockerfile",
        "env",
        "php",
        "hs",
        "hsc",
        "lua",
        "nginxconf",
        "conf",
        "m",
        "mm",
        "plsql",
        "perl",
        "rb",
        "rs",
        "db2",
        "scala",
        "bash",
        "swift",
        "vue",
        "svelte",
    ]

    if file_ext == "pdf":
        loader = PyPDFLoader(file_path, extract_images=app.state.PDF_EXTRACT_IMAGES)
    elif file_ext == "csv":
        loader = CSVLoader(file_path)
    elif file_ext == "rst":
        loader = UnstructuredRSTLoader(file_path, mode="elements")
    elif file_ext == "xml":
        loader = UnstructuredXMLLoader(file_path)
    elif file_ext == "md":
        loader = UnstructuredMarkdownLoader(file_path)
    elif file_content_type == "application/epub+zip":
        loader = UnstructuredEPubLoader(file_path)
    elif (
            file_content_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            or file_ext in ["doc", "docx"]
    ):
        loader = Docx2txtLoader(file_path)
    elif file_content_type in [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ] or file_ext in ["xls", "xlsx"]:
        loader = UnstructuredExcelLoader(file_path)
    elif file_ext in known_source_ext or (
            file_content_type and file_content_type.find("text/") >= 0
    ):
        loader = TextLoader(file_path)
    else:
        loader = TextLoader(file_path)
        known_type = False

    return loader, known_type


@app.post("/doc")
def store_doc(
        collection_name: Optional[str] = Form(None),
        file: UploadFile = File(...),
        user=Depends(get_current_user),
):
    """Store doc in vector db, support csv, docx, epub, md, pdf, rst, xml, xls, xlsx, and text"""
    logger.debug(f"rag doc, file type: {file.content_type}")
    try:
        filename = file.filename
        file_path = f"{UPLOAD_DIR}/{filename}"
        contents = file.file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
            f.close()

        f = open(file_path, "rb")
        if collection_name is None:
            collection_name = calculate_sha256(f)[:63]
        f.close()

        loader, known_type = get_loader(file.filename, file.content_type, file_path)
        # Check if lazy_load is implemented
        try:
            data = loader.lazy_load()
        except NotImplementedError:
            data = loader.load()

        result = store_data_in_vector_db(data, collection_name)

        if result:
            return {
                "status": True,
                "collection_name": collection_name,
                "filename": filename,
                "known_type": known_type,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR_MESSAGES.DEFAULT(),
            )
    except Exception as e:
        logger.error(e)
        if "No pandoc was found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.PANDOC_NOT_INSTALLED,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT(e),
            )


@app.get("/scan")
def scan_docs_dir(user=Depends(get_admin_user)):
    """Scan docs dir and store in vector db, only for admin user."""
    for path in Path(DOCS_DIR).rglob("./**/*"):
        try:
            if path.is_file() and not path.name.startswith("."):
                tags = extract_folders_after_data_docs(path)
                filename = path.name
                file_content_type = mimetypes.guess_type(path)

                f = open(path, "rb")
                collection_name = calculate_sha256(f)[:63]
                f.close()

                loader, known_type = get_loader(
                    filename, file_content_type[0], str(path)
                )
                try:
                    data = loader.lazy_load()
                except NotImplementedError:
                    data = loader.load()

                result = store_data_in_vector_db(data, collection_name)

                if result:
                    sanitized_filename = sanitize_filename(filename)
                    doc = Documents.get_doc_by_name(sanitized_filename)

                    if doc is None:
                        doc = Documents.insert_new_doc(
                            user.id,
                            DocumentForm(
                                **{
                                    "name": sanitized_filename,
                                    "title": filename,
                                    "collection_name": collection_name,
                                    "filename": filename,
                                    "content": (
                                        json.dumps(
                                            {
                                                "tags": list(
                                                    map(
                                                        lambda name: {"name": name},
                                                        tags,
                                                    )
                                                )
                                            }
                                        )
                                        if len(tags)
                                        else "{}"
                                    ),
                                }
                            ),
                        )

        except Exception as e:
            logger.error(e)

    return True


@app.get("/reset/db")
def reset_vector_db(user=Depends(get_admin_user)):
    CHROMA_CLIENT.reset()


@app.get("/reset")
def reset(user=Depends(get_admin_user)) -> bool:
    folder = f"{UPLOAD_DIR}"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error("Failed to delete %s. Reason: %s" % (file_path, e))

    try:
        CHROMA_CLIENT.reset()
    except Exception as e:
        logger.error(e)

    return True
