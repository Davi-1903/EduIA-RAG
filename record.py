import json

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import BaseTool, tool
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace
from langchain_pinecone import PineconeVectorStore
from langgraph.graph.state import CompiledStateGraph
from tabulate import tabulate
from tqdm import tqdm

from utils import get_llm, get_vector_store


load_dotenv()


def get_questions() -> list[str]:
    with open('./questions.json', encoding='utf-8') as f:
        questions = json.load(f)
        return [question['question'] for question in questions]


def build_search_tool(vector_store: PineconeVectorStore) -> BaseTool:
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


def save_answer(question: str, answer: str):
    with open('./answers.json', encoding='utf-8') as f:
        answers: list[dict] = json.load(f)
        answers.append({'id': len(answers) + 1, 'question': question, 'answer': answer})

    with open('./answers.json', 'w', encoding='utf-8') as f:
        json.dump(answers, f, indent=2)


def answer_questions(agent: CompiledStateGraph):
    for question in tqdm(get_questions(), desc='Gerando respostas', unit='pergunta'):
        answer = generate_answer(question, agent)
        save_answer(question, answer)


def compare_answers(llm: ChatHuggingFace):
    prompt = PromptTemplate(
        template="""Realize uma avaliação entre a primeira resposta (resposta obtida) em relação à segunda resposta (resposta esperada), fornecendo uma nota entre 0 e 5
        Formato da resposta:
            - A resposta deve conter apenas a nota (float);
            - Não explique o raciocínio;
        Resposta obtida:
            {resposta_obtida}
        Resposta esperada:
            {resposta_esperada}
        """,
        input_variables=['resposta_esperada', 'resposta_obtida'],
    )

    with open('./questions.json', encoding='utf-8') as f:
        correct_answers = json.load(f)

    with open('./answers.json', encoding='utf-8') as f:
        ai_responses = json.load(f)
        ai_responses = [answer['answer'] for answer in ai_responses]

    results = []
    for correct, ai in tqdm(
        zip(correct_answers, ai_responses),
        total=len(correct_answers),
        desc='Avaliando respostas',
        unit='resposta',
    ):
        response = llm.invoke(
            prompt.format(
                resposta_esperada=correct['answer'],
                resposta_obtida=ai,
            )
        )
        results.append(response.content)

    data = [[str(idx), result] for idx, result in enumerate(results, 1)]
    media = sum(float(result) for result in results) / len(results)
    print(tabulate(data, headers=['Id da pergunta', 'Avaliação'], tablefmt='pretty'))
    print(f'Média: {media}')


def main():
    SYSTEM_PROMPT = """Você é um assistente que responde perguntas usando os materiais de
    estudo indexados. Use a ferramenta search_documentation para buscar contexto antes de
    responder. Se a resposta não estiver nos documentos, diga isso claramente em vez de inventar"""

    _, vector_store = get_vector_store()
    llm = get_llm()
    agent = create_agent(
        model=llm,
        tools=[build_search_tool(vector_store)],
        system_prompt=SYSTEM_PROMPT,
    )

    answer_questions(agent)
    compare_answers(llm)


if __name__ == '__main__':
    main()
