from pathlib import Path

from markitdown import MarkItDown, MarkItDownException
from tqdm import tqdm

from constants import CONVERTED_PATH, RAW_PATH


def get_paths(path: Path) -> list[Path]:
    return [file for file in path.glob('*') if file.is_file() and not file.name.startswith('.')]


def convert_to_markdown(path: Path) -> str | None:
    md = MarkItDown(enable_plugins=False)

    try:
        result = md.convert(path)
        return result.markdown

    except MarkItDownException:
        print(f'Ocorreu um erro ao converter o arquivo "{path.name}"')


def save_file(file: Path, content: str):
    try:
        with open(file, mode='w+', encoding='utf-8') as f:
            f.write(content)

    except OSError:
        print(f'O arquivo "{file.name}" já existe')


def main():
    raw_files = get_paths(RAW_PATH)
    for file in tqdm(raw_files, desc='Convertendo arquivos', unit='arquivo'):
        content = convert_to_markdown(file)
        if content is not None:
            save_file(CONVERTED_PATH / f'{file.name}.md', content)


if __name__ == '__main__':
    main()
