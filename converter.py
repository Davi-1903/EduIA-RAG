from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from markitdown import MarkItDown, MarkItDownException


DOCS_PATH = Path('./docs')
RAW_PATH = DOCS_PATH / 'raw'
CONVERTED_PATH = DOCS_PATH / 'converted'


def get_files(path: str) -> list[Path]:
    return [file for file in Path(path).glob('*') if file.is_file() and file.name != '.gitkeep']


def generate_langchain_documents(files: list[Path]) -> list[Document]:
    documents: list[Document] = []

    for file in files:
        with open(file) as f:
            content = f.read()

            headers_to_split_on = [
                ('#', 'Header 1'),
                ('##', 'Header 2'),
                ('###', 'Header 3'),
                ('####', 'Header 4'),
                ('#####', 'Header 5'),
                ('######', 'Header 6'),
            ]
            markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
            documents.append(*markdown_splitter.split_text(content))

    return documents


def convert_to_markdown(path: Path) -> str | None:
    md = MarkItDown(enable_plugins=False)

    try:
        result = md.convert(path)
        return result.markdown

    except MarkItDownException:
        print(f'Ocorreu um erro ao converter o arquivo "{path.name}"')


def save_file(file: Path, content: str):
    try:
        with file.open(mode='w+', encoding='utf-8') as f:
            f.write(content)

    except FileExistsError:
        print(f'O arquivo "{file.name}" já existe')


def main():
    # Convert files
    raw_files = get_files('./docs/raw')
    for file in raw_files:
        content = convert_to_markdown(file)
        if content is not None:
            save_file(CONVERTED_PATH / f'{file.stem}.md', content)


if __name__ == '__main__':
    main()
