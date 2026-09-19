from pathlib import Path

from markitdown import MarkItDown, MarkItDownException


DOCS_PATH = Path('./docs')
RAW_PATH = DOCS_PATH / 'raw'
CONVERTED_PATH = DOCS_PATH / 'converted'


def get_paths(path: str) -> list[Path]:
    return [file for file in Path(path).glob('*') if file.is_file() and file.name != '.gitkeep']


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
    raw_files = get_paths('./docs/raw')
    for file in raw_files:
        content = convert_to_markdown(file)
        if content is not None:
            save_file(CONVERTED_PATH / f'{file.stem}.md', content)


if __name__ == '__main__':
    main()
