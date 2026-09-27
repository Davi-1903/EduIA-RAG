from os import getenv
from pathlib import Path

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from loguru import logger
from pinecone import Pinecone


try:
    logger.remove(0)
except ValueError:
    pass


def setup_logger(name: str, filepath: str | Path, rotation: str = '1 MB'):
    logger.add(
        filepath,
        format='{level:<8} | {time:DD/MM/YYYY HH:mm} | {name} - {message}',
        rotation=rotation,
        filter=lambda record, _name=name: record['name'] == _name,
    )


def get_env(key: str, default: str | None = None) -> str:
    value = getenv(key)
    if value is not None:
        return value
    if default is not None:
        return default
    raise RuntimeError(f'A variável de ambiente "{key}" não foi estabelecida ou está vazia')


def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=get_env('HF_EMBEDDING_MODEL'),
        encode_kwargs={'normalize_embeddings': True},
    )


def get_vector_store():
    embeddings = get_embedding_model()

    try:
        pc = Pinecone(api_key=get_env('PINECONE_API_KEY'))
        index = pc.Index(get_env('INDEX_NAME'))
    except Exception as err:
        raise RuntimeError(f'Não foi possível se conectar ao pinecone: {err}') from err

    return index, PineconeVectorStore(embedding=embeddings, index=index)


def get_llm() -> ChatHuggingFace:
    llm_endpoint = HuggingFaceEndpoint(
        model=get_env('HF_MODEL'),
        max_new_tokens=int(get_env('MAX_TOKENS')),
        temperature=0.1,
        top_p=0.9,
        provider='auto',
    )
    return ChatHuggingFace(llm=llm_endpoint)
