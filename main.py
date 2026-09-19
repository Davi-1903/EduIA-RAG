from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter


def get_documents() -> list[Document]:
    with open('./resume.md', encoding='utf-8') as f:
        content = f.read()

        headers_to_split_on = [
            ('#', 'Header 1'),
            ('##', 'Header 2'),
            ('###', 'Header 3'),
            ('####', 'Header 4'),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
        md_header_splits = markdown_splitter.split_text(content)
        return md_header_splits


def main():
    embeddings = HuggingFaceEmbeddings(model_name='Qwen/Qwen3-Embedding-0.6B')

    documents = get_documents()
    vector_store = InMemoryVectorStore(embedding=embeddings)
    vector_store.add_documents(
        documents=documents,
        ids=[f'id{n}' for n in range(1, len(documents) + 1)],
    )

    phrase = 'Base de dados relacional'
    documents = vector_store.similarity_search(query=phrase, k=1)
    print(f'Frase: {phrase}')
    for doc in documents:
        print(doc)


if __name__ == '__main__':
    main()
