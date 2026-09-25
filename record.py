import csv

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import BaseTool, tool
from langchain_chroma import Chroma
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface.embeddings import HuggingFaceEmbeddings


load_dotenv()


def get_questions(path: str) -> list[list[str]]:
    with open(path, encoding='utf-8') as f:
        questions = csv.reader(f, delimiter=';')
        next(questions)
        return list(questions)


def build_search_tool(vector_store: Chroma) -> BaseTool:
    @tool(parse_docstring=True)
    def search_documentation(query: str) -> str:
        """Busca trechos relevantes nos materiais de estudo indexados para responder
        à pergunta do usuário. Use sempre que precisar de informação dos documentos
        antes de responder.

        Args:
            query: Pergunta realizada pelo usuário

        Returns:
            String com contendo o conteúdo dos materiais encontrados e a fonte
        """

        result = vector_store.similarity_search(
            query,
            # filter={'discipline': None},
            k=10,
        )

        if not result:
            return 'Nenhum resultado encontrado nos documentos indexados.'

        return '\n\n---\n\n'.join(
            f'Fonte: {doc.metadata.get("source", "desconhecida")}\n{doc.page_content}' for doc in result
        )

    return search_documentation


def main():
    # if (pinecone_api_key := os.getenv('PINECONE_API_KEY')) is None:
    #     raise RuntimeError('A variável de ambiente "PINECONE_API_KEY" está vazia ou não foi definida')

    embeddings = HuggingFaceEmbeddings(
        model_name='Qwen/Qwen3-Embedding-0.6B', encode_kwargs={'normalize_embeddings': True}
    )
    vector_store = Chroma(
        collection_name='eduia-rag', embedding_function=embeddings, persist_directory='./chroma_eduia_rag'
    )
    llm_endpoint = HuggingFaceEndpoint(
        model='Qwen/Qwen2.5-72B-Instruct', max_new_tokens=3000, temperature=0.1, top_p=0.9, provider='auto'
    )
    llm = ChatHuggingFace(llm=llm_endpoint)
    agent = create_agent(
        model=llm,
        tools=[build_search_tool(vector_store)],
        system_prompt='Você é um assistente que responde perguntas usando os materiais de estudo indexados. Use a ferramenta search_documentation para buscar contexto antes de responder. Se a resposta não estiver nos documentos, diga isso claramente em vez de inventar',
    )

    result = agent.invoke(
        {'messages': [{'role': 'user', 'content': 'Qual a diferença entre Docker Máquinas virtuais?'}]}
    )
    print(f'\nResposta: {result["messages"][-1].content}')


if __name__ == '__main__':
    main()
