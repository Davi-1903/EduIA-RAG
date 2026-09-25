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

from constants import CONVERTED_PATH, HEADERS_TO_SPLIT_ON, MIN_CHUNKS_LENGTH
from converter import get_paths


load_dotenv()


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
        if len(doc.page_content.strip()) < MIN_CHUNKS_LENGTH:
            continue

        # Adicionar disciplina no metadata
        doc = add_headers_context(doc)
        doc.metadata['source'] = file.name
        doc.id = str(uuid5(NAMESPACE_URL, f'{file.name}:{idx}'))
        documents.append(doc)
        idx += 1

    return documents


def main():
    # if (pinecone_api_key := os.getenv('PINECONE_API_KEY')) is None:
    #     raise RuntimeError('A variável de ambiente "PINECONE_API_KEY" está vazia ou não foi definida')

    embeddings = HuggingFaceEmbeddings(
        model_name='Qwen/Qwen3-Embedding-0.6B',
        encode_kwargs={'normalize_embeddings': True},
    )

    # try:
    #     pc = Pinecone(api_key=pinecone_api_key)
    #     index = pc.Index('eduia-rag')
    # except Exception as e:
    #     raise RuntimeError(f'Não foi possível se conectar ao pinecone: {e}') from e

    # vector_store = PineconeVectorStore(embedding=embeddings, index=index)

    vector_store = Chroma(
        collection_name='eduia-rag',
        embedding_function=embeddings,
        persist_directory='./chroma_eduia_rag',
    )

    files = get_paths(CONVERTED_PATH)
    for file in tqdm(files, desc='Gerando embeddings', unit='arquivo'):
        documents = generate_langchain_documents(file)
        vector_store.add_documents(documents=documents)


if __name__ == '__main__':
    main()
