from enum import Enum
from os import getenv
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import ConvertPipelineOptions, PictureDescriptionApiOptions, VlmPipelineOptions
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat
from docling.document_converter import DocumentConverter, PdfFormatOption, PowerpointFormatOption, WordFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from loguru import logger
from pinecone import Pinecone

from pipeline.constants import HF_URL


try:
    logger.remove(0)
except ValueError:
    pass


class Discipline(str, Enum):
    filosofia_ciencia_e_tecnologia = 'Filosofia, Ciência e Tecnologia'
    sociologia_do_trabalho = 'Sociologia do Trabalho'
    qualidade_de_vida_e_trabalho = 'Qualidade de Vida e Trabalho'
    gestao_organizacional = 'Gestão Organizacional'
    fundamentos_de_logica_e_algoritmo = 'Fundamentos de Lógica e Algoritmo'
    analise_e_projeto_orientados_a_objetos = 'Análise e Projeto Orientados a Objetos'
    projeto_de_desenvolvimento_de_sistemas_para_internet = 'Projeto de Desenvolvimento de Sistemas para Internet'
    principios_de_design_e_projeto_grafico = 'Princípios de Design e Projeto Gráfico'
    design_web_e_arquitetura_da_informacao = 'Design Web e Arquitetura da Informação'
    programacao_estruturada_e_orientada_a_objetos = 'Programação Estruturada e Orientada a Objetos'
    banco_de_dados = 'Banco de Dados'
    programacao_de_sistemas_para_internet = 'Programação de Sistemas para Internet'
    instalacao_e_configuracao_de_servidores = 'Instalação e Configuração de Servidores'
    projeto_de_interface_do_usuario = 'Projeto de Interface do Usuário'
    programacao_orientada_a_servicos = 'Programação Orientada a Serviços'


def setup_logger(name: str, filepath: str | Path, rotation: str = '1 MB'):
    logger.add(
        filepath,
        format='{level:<8} | {time:DD/MM/YYYY HH:mm} | {name} - {message}',
        rotation=rotation,
        filter=lambda record, _name=name: record['name'] == _name,
    )


def get_env(key: str, default: str | None = None) -> str:
    value = getenv(key)
    if value is not None:
        return value
    if default is not None:
        return default
    raise RuntimeError(f'A variável de ambiente "{key}" não foi estabelecida ou está vazia')


def get_converter() -> DocumentConverter:
    headers = {'Authorization': f'Bearer {get_env("HUGGINGFACEHUB_API_TOKEN")}'}
    base = {
        'model': get_env('HF_VISION_MODEL'),
        'temperature': 0,
    }

    pdf_opts = VlmPipelineOptions(
        enable_remote_services=True,
        vlm_options=ApiVlmOptions(
            url=HF_URL,
            headers=headers,
            params={**base, 'max_tokens': 4096},
            prompt=(
                'Transcreva fielmente todo o texto da página em português, '
                'com títulos em Markdown. Descreva imagens e tabelas.'
            ),
            timeout=120,
            scale=2.0,
            response_format=ResponseFormat.MARKDOWN,
        ),
    )

    pic_opts = PictureDescriptionApiOptions(
        url=HF_URL,
        headers=headers,
        params={**base, 'max_tokens': 300},
        prompt='Descreva a imagem em português, em até 3 frases.',
        timeout=90,
    )

    office_opts = ConvertPipelineOptions(
        enable_remote_services=True,
        do_picture_description=True,
        picture_description_options=pic_opts,
    )

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_cls=VlmPipeline, pipeline_options=pdf_opts),
            InputFormat.DOCX: WordFormatOption(pipeline_options=office_opts),
            InputFormat.PPTX: PowerpointFormatOption(pipeline_options=office_opts),
        }
    )


def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=get_env('HF_EMBEDDING_MODEL'),
        encode_kwargs={'normalize_embeddings': True},
    )


def get_vector_store():
    embeddings = get_embedding_model()

    try:
        pc = Pinecone(api_key=get_env('PINECONE_API_KEY'))
        index = pc.Index(get_env('INDEX_NAME'))
    except Exception as err:
        raise RuntimeError(f'Não foi possível se conectar ao pinecone: {err}') from err

    return index, PineconeVectorStore(embedding=embeddings, index=index)


def get_llm() -> ChatHuggingFace:
    llm_endpoint = HuggingFaceEndpoint(
        model=get_env('HF_MODEL'),
        max_new_tokens=int(get_env('MAX_TOKENS')),
        temperature=0.1,
        top_p=0.9,
        provider='auto',
    )
    return ChatHuggingFace(llm=llm_endpoint)
