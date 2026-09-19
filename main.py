import os
from pathlib import Path
from uuid import uuid4

from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from pinecone import Pinecone

from converter import get_paths


def generate_langchain_documents(files: list[Path]) -> list[Document]:
    documents: list[Document] = []
    headers_to_split_on = [
        ('#', 'Header 1'),
        ('##', 'Header 2'),
        ('###', 'Header 3'),
        ('####', 'Header 4'),
        ('#####', 'Header 5'),
        ('######', 'Header 6'),
    ]

    for file in files:
        with open(file, encoding='utf-8') as f:
            content = f.read()

            markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
            chunks = markdown_splitter.split_text(content)

            recursive_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=150,
                separators=['\n\n', '\n', ' ', ''],
            )
            documents += recursive_splitter.split_documents(chunks)

    return documents


def main():
    embeddings = HuggingFaceEmbeddings(model_name='Qwen/Qwen3-Embedding-0.6B')

    files = get_paths('./docs/converted')
    documents = generate_langchain_documents(files)
    print(f'{len(documents)} documentos criados')

    if (pinecone_api_key := os.getenv('PINECONE_API_KEY')) is None:
        raise RuntimeError('A variável de ambiente "PINECONE_API_KEY" está vazia ou não foi definida')

    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index('eduia-rag')
    vector_store = PineconeVectorStore(embedding=embeddings, index=index)

    vector_store.add_documents(
        documents=documents,
        ids=[str(uuid4()) for _ in range(len(documents))],
    )
    print('Documentos adicionados com sucesso')


if __name__ == '__main__':
    main()
