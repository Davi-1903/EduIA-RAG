from pathlib import Path
from time import sleep

from dotenv import load_dotenv
from groq import RateLimitError
from langchain_groq import ChatGroq
from loguru import logger
from markitdown import MarkItDown, MarkItDownException
from tqdm import tqdm

from pipeline.constants import CONVERTED_PATH, RAW_PATH
from pipeline.utils import get_llm, setup_logger


load_dotenv()
setup_logger(__name__, 'logs/conversions.log')


def get_paths(path: Path) -> list[Path]:
    return [file for file in path.glob('*') if file.is_file() and not file.name.startswith('.')]


def convert_to_markdown(converter: MarkItDown, model: ChatGroq, path: Path) -> str | None:
    for _ in range(5):
        try:
            result = converter.convert(path)
            markdown = model.invoke(
                'Organize as informações desse material e retorne um markdown. Use níveis de títulos, organize as ideiais, '
                'conceitos e descarte o que julgar desnecessário ao conteúdo em questão. Descreva tabelas e listas/tópicos em texto corrido '
                'para manter a semântica do conteúdo, ou seja, não use `|` (barras verticiais) das tabelas ou `-` (hífens), `*` (asteríscos) '
                f'e números das listas/tópicos. Não invente informações novas, use apenas as informações fornecidas no material abaixo:\n\n{result.markdown}'
            ).content
            if isinstance(markdown, str):
                return markdown

        except MarkItDownException as err:
            logger.error(f'Ocorreu um erro ao converter o arquivo "{path.name}": {err}')
            return

        except RateLimitError:
            logger.warning('Rate limit atingido... Esperando 5 segundos para continuar')
            sleep(5)


def save_file(file: Path, content: str):
    with open(file, mode='w', encoding='utf-8') as f:
        f.write(content)


def main():
    converter = MarkItDown()
    llm = get_llm()

    logger.debug('Iniciando a conversão dos materiais')

    raw_files = get_paths(RAW_PATH)
    converted_materials = 0
    for file in tqdm(raw_files, desc='Convertendo arquivos', unit='arquivo'):
        content = convert_to_markdown(converter, llm, file)
        if content is not None:
            save_file(CONVERTED_PATH / f'{file.name}.md', content)
            logger.info(f'"{file.name}" convertido')
            converted_materials += 1
        else:
            logger.error(f'"{file.name}" não foi convertido')

    logger.success(f'Finalizado a conversão de {converted_materials} materiais')


if __name__ == '__main__':
    main()
