from pathlib import Path

from loguru import logger
from markitdown import MarkItDown, MarkItDownException
from openai import OpenAI
from tqdm import tqdm

from pipeline.constants import CONVERTED_PATH, RAW_PATH
from pipeline.utils import get_env, setup_logger


setup_logger(__name__, 'logs/conversions.log')


def get_paths(path: Path) -> list[Path]:
    return [file for file in path.glob('*') if file.is_file() and not file.name.startswith('.')]


def convert_to_markdown(path: Path) -> str | None:
    client = OpenAI(base_url='https://huggingface.co', api_key=get_env('HUGGINGFACEHUB_API_TOKEN'))

    md = MarkItDown(
        enable_plugins=True,
        llm_client=client,
        llm_model=get_env('HF_VISION_MODEL'),
        llm_prompt='Extract all the content and organize it using Markdown headings. Describe the images and the content of the tables.',
    )

    try:
        result = md.convert(path)
        return result.markdown

    except MarkItDownException as err:
        print(f'Ocorreu um erro ao converter o arquivo "{path.name}": {err}')


def save_file(file: Path, content: str):
    try:
        with open(file, mode='w', encoding='utf-8') as f:
            f.write(content)

    except OSError as err:
        print(f'O arquivo "{file.name}" já existe: {err}')


def main():
    logger.debug('Iniciando a conversão dos materiais')

    raw_files = get_paths(RAW_PATH)
    for file in tqdm(raw_files, desc='Convertendo arquivos', unit='arquivo'):
        content = convert_to_markdown(file)
        if content is not None:
            save_file(CONVERTED_PATH / f'{file.name}.md', content)
            logger.info(f'"{file.name}" convertido')
        else:
            logger.error(f'"{file.name}" não foi convertido')

    logger.success(f'Finalizado a conversão de {len(raw_files)} materiais')


if __name__ == '__main__':
    main()
