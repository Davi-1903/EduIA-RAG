from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import torch
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from tqdm import tqdm

from constants import CONVERTED_PATH, HEADERS_TO_SPLIT_ON
from converter import get_paths
from utils import get_env, get_vector_store


load_dotenv()


def build_chunk_id(file: Path, idx: int) -> str:
    return str(uuid5(NAMESPACE_URL, f'{file.name}:{idx}'))


def delete_old_chunks(index, file: Path, current_chunk_count: int):
    candidate_ids = [build_chunk_id(file, idx) for idx in range(current_chunk_count + int(get_env('DELETE_BUFFER')))]
    for n in range(0, len(candidate_ids), 1000):
        index.delete(ids=candidate_ids[n : n + 1000])


def add_documents_in_batches(vector_store: PineconeVectorStore, documents: list[Document]):
    for n in tqdm(
        range(0, len(documents), int(get_env('BATCH_SIZE'))),
        desc='Indexando lotes',
        unit='embedding',
        leave=True,
    ):
        vector_store.add_documents(documents=documents[n : n + int(get_env('BATCH_SIZE'))])


def get_device_kwargs() -> dict[str, str]:
    return {'device': 'cuda'} if torch.cuda.is_available() else {'device': 'cpu'}


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
        doc.id = build_chunk_id(file, idx)
        documents.append(doc)
        idx += 1

    return documents


def main():
    index, vector_store = get_vector_store()

    files = get_paths(CONVERTED_PATH)
    total_documents = 0

    for file in tqdm(files, desc='Gerando embeddings', unit='arquivo'):
        documents = generate_langchain_documents(file)
        if not documents:
            print(f'Nenhum chunk válido gerado para "{file.name}", pulando...')
            continue

        delete_old_chunks(index, file, len(documents))
        add_documents_in_batches(vector_store, documents)
        vector_store.add_documents(documents=documents)
        total_documents += len(documents)

    print(f'{total_documents} documento(s) adicionado(s) com sucesso em {len(files)} arquivo(s)')


if __name__ == '__main__':
    main()
