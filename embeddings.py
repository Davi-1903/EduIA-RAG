import os
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from tqdm import tqdm

from constants import CONVERTED_PATH, HEADERS_TO_SPLIT_ON
from converter import get_paths


load_dotenv()


def get_env(key: str, default: str | None = None) -> str:
    value = os.getenv(key)
    if value is not None:
        return value
    if default is not None:
        return default
    raise RuntimeError(f'A variável de ambiente "{key}" não foi estabelecida ou está vazia')


def add_headers_context(doc: Document) -> Document:
    path = ' > '.join(doc.metadata[name] for _, name in HEADERS_TO_SPLIT_ON if name in doc.metadata)
    if path:
        doc.page_content = f'{path}\n\n{doc.page_content}'
    return doc


def generate_langchain_documents(file: Path) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(HEADERS_TO_SPLIT_ON, strip_headers=True)
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=['\n\n', '\n', ' ', ''],
    )

    chunks = header_splitter.split_text(file.read_text(encoding='utf-8'))
    split_docs = recursive_splitter.split_documents(chunks)
    documents: list[Document] = []
    idx = 0

    for doc in split_docs:
        if len(doc.page_content.strip()) < int(get_env('MIN_CHUNKS_LENGTH')):
            continue

        # Adicionar disciplina no metadata
        doc = add_headers_context(doc)
        doc.metadata['source'] = file.name
        doc.id = str(uuid5(NAMESPACE_URL, f'{file.name}:{idx}'))
        documents.append(doc)
        idx += 1

    return documents


def main():
    embeddings = HuggingFaceEmbeddings(
        model_name=get_env('HF_EMBEDDING_MODEL'),
        encode_kwargs={'normalize_embeddings': True},
    )

    # try:
    #     pc = Pinecone(api_key=get_env('PINECONE_API_KEY'))
    #     index = pc.Index(get_env('INDEX_NAME'))
    # except Exception as e:
    #     raise RuntimeError(f'Não foi possível se conectar ao pinecone: {e}') from e

    # vector_store = PineconeVectorStore(embedding=embeddings, index=index)

    vector_store = Chroma(
        collection_name=get_env('HF_MODEL'),
        embedding_function=embeddings,
        persist_directory='./chroma_eduia_rag',
    )

    files = get_paths(CONVERTED_PATH)
    for file in tqdm(files, desc='Gerando embeddings', unit='arquivo'):
        documents = generate_langchain_documents(file)
        vector_store.add_documents(documents=documents)


if __name__ == '__main__':
    main()
