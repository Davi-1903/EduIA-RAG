from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter

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
            documents += markdown_splitter.split_text(content)

    return documents


def main():
    embeddings = HuggingFaceEmbeddings(model_name='Qwen/Qwen3-Embedding-0.6B')

    files = get_paths('./docs/converted')
    documents = generate_langchain_documents(files)
    print(f'{len(documents)} documentos criados')

    # Salvo em memória, apenas para testes
    vector_store = Chroma(
        collection_name='eduia_rag',
        embedding_function=embeddings,
        persist_directory='./chroma',
    )
    vector_store.add_documents(
        documents=documents,
        ids=[f'id{n}' for n in range(1, len(documents) + 1)],
    )


if __name__ == '__main__':
    main()
