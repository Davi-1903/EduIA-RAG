from os import getenv

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


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
