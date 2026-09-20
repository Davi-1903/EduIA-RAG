import os
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from pinecone import Pinecone

from constants import CONVERTED_PATH, HEADERS_TO_SPLIT_ON
from converter import get_paths


def generate_langchain_documents(files: list[Path]) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(HEADERS_TO_SPLIT_ON, strip_headers=False)
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=['\n\n', '\n', ' ', ''],
    )
    documents: list[Document] = []
    for file in files:
        chunks = header_splitter.split_text(file.read_text(encoding='utf-8'))
        for idx, doc in enumerate(recursive_splitter.split_documents(chunks)):
            doc.metadata['source'] = file.name
            doc.id = str(uuid5(NAMESPACE_URL, f'{file.name}:{idx}'))
            documents.append(doc)
    return documents


def main():
    if (pinecone_api_key := os.getenv('PINECONE_API_KEY')) is None:
        raise RuntimeError('A variável de ambiente "PINECONE_API_KEY" está vazia ou não foi definida')

    embeddings = HuggingFaceEmbeddings(
        model_name='Qwen/Qwen3-Embedding-0.6B',
        encode_kwargs={'normalize_embeddings': True},
    )

    files = get_paths(CONVERTED_PATH)
    documents = generate_langchain_documents(files)
    print(f'{len(documents)} documentos criados')

    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index('eduia-rag')
    vector_store = PineconeVectorStore(embedding=embeddings, index=index)

    vector_store.add_documents(documents=documents)
    print(f'{len(documents)} documentos adicionados com sucesso')


if __name__ == '__main__':
    main()
