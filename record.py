import json

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import BaseTool, tool
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langgraph.graph.state import CompiledStateGraph
from tqdm import tqdm


load_dotenv()


def get_questions() -> list[str]:
    with open('./questions.json', encoding='utf-8') as f:
        questions = json.load(f)
        return [question['pergunta'] for question in questions]


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

        # Filtrar por disciplina
        result = vector_store.similarity_search(query, k=10)

        if not result:
            return 'Nenhum resultado encontrado nos documentos indexados.'

        return '\n\n---\n\n'.join(
            f'Fonte: {doc.metadata.get("source", "desconhecida")}\n{doc.page_content}' for doc in result
        )

    return search_documentation


def generate_answer(question: str, agent: CompiledStateGraph) -> str:
    result = agent.invoke({'messages': [HumanMessage(question)]})
    return result['messages'][-1].content


def save_answer(answer: str):
    with open('./answers.txt', 'a+', encoding='utf-8') as f:
        f.write(answer + '\n\n---\n\n')


def main():
    # if (pinecone_api_key := os.getenv('PINECONE_API_KEY')) is None:
    #     raise RuntimeError('A variável de ambiente "PINECONE_API_KEY" está vazia ou não foi definida')

    SYSTEM_PROMPT = 'Você é um assistente que responde perguntas usando os materiais de estudo indexados. Use a ferramenta search_documentation para buscar contexto antes de responder. Se a resposta não estiver nos documentos, diga isso claramente em vez de inventar'

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
        system_prompt=SYSTEM_PROMPT,
    )

    for question in tqdm(get_questions(), desc='Gerando respostas', unit='pergunta'):
        answer = generate_answer(question, agent)
        save_answer(answer)


if __name__ == '__main__':
    main()
