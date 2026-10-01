# EduIA-RAG

Pipeline de **RAG** (_Retrieval-Augmented Generation_, ou Geração Aumentada por Recuperação) do sistema [**EduIA**](https://github.com/Davi-1903/EduIA). O projeto converte documentos em Markdown, gera _embeddings_ a partir deles e os armazena em um banco vetorial no [**Pinecone**](https://www.pinecone.io/).

## Sumário

- [Como executar](#como-executar)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Observações](#observações)
- [Disciplinas do curso de Informática para Internet](#disciplinas-do-curso-de-informática-para-internet)
- [Melhorias futuras](#melhorias-futuras)
- [Licença](#licença)

## Como executar

> [!TIP]
> Use um ambiente virtual, pois há muitas dependências. Com o **uv**, o ambiente é criado automaticamente pelo `uv sync`.

1. **Clone o repositório**

    ```bash
    git clone https://github.com/Davi-1903/EduIA-RAG.git
    cd EduIA-RAG
    ```

2. **Instale as dependências**

    ```bash
    # Com pip
    python -m venv .venv
    source .venv/bin/activate  # No Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    pip install -e .

    # Com uv
    uv sync
    ```

    > O `pip install -e .` (ou o `uv sync`, que já cuida disso automaticamente) instala o próprio projeto em modo editável, disponibilizando os comandos `convert`, `embed` e `record` usados mais abaixo.

3. **Crie as variáveis de ambiente**

    Recomendo criar um arquivo `.env` na raiz do projeto:

    ```env
    # ========================< API KEYS >========================
    PINECONE_API_KEY="<SUA-CHAVE-DE-API-DO-PINECONE>"
    HUGGINGFACEHUB_API_TOKEN="<SUA-CHAVE-DE-API-DO-HUGGING-FACE>"

    # ===========================< IA >===========================
    HF_EMBEDDING_MODEL="<MODELO-DE-EMBEDDING>"
    HF_VISION_MODEL="<MODELO-PARA-OCR>"
    HF_MODEL="<MODELO-DE-IA>"
    MAX_TOKENS=3000
    INDEX_NAME="eduia-rag"
    MIN_CHUNKS_LENGTH=50
    DELETE_BUFFER=50
    BATCH_SIZE=100
    ```

4. **Adicione os documentos a serem convertidos**

    Coloque os arquivos no diretório [`docs/raw/`](./docs/raw/). Veja a [estrutura dos documentos](#estrutura-dos-documentos).

5. **Converta os documentos**

    Execute o script [`converter.py`](./src/pipeline/ingestion/converter.py) para transformar os documentos de [`docs/raw/`](./docs/raw/) em Markdown. Os arquivos convertidos serão criados em [`docs/converted/`](./docs/converted/).

    ```bash
    # Com pip
    convert

    # Com uv
    uv run convert
    ```

6. **Gere os embeddings**

    Execute o script [`embeddings.py`](./src/pipeline/ingestion/embeddings.py) para criar os _embeddings_ e adicioná-los ao banco vetorial do Pinecone. Adicione a flag `--discipline` ou `-d` e especifique a matéria dos materiais

    ```bash
    # Com pip
    embed -d "<disciplina>"

    # Com uv
    uv run embed -d "<disciplina>"
    ```

7. **Testar RAG**

    Para avaliar a qualidade das respostas é necessário criar possíveis perguntas e as respostas esperadas
    1. **Adicione as perguntas e respostas no arquivo [`questions.json`](./data/questions.json)**

        ```json
        [
        	{
        		"id": 1,
        		"question": "Qual problema o docker soluciona?",
        		"answer": "O docker foi criado para ..."
        	}
        ]
        ```

        > Outras perguntas e respostas seguindo o mesmo formato

    2. **Execute o script [`record.py`](./src/pipeline/cli/record.py)**

        O script `record.py` usa o **RAG** para responder as perguntas ([`questions.json`](./data/questions.json)) as armazenar em [`answers.json`](./data/answers.json), após isso o modelo comparará a resposta gerada pela **IA** com as respostas corretas, gerando uma nota de 0 a 10 para cada uma delas. Especifique de qual matéria são as perguntas

        ```bash
        # Com pip
        record -d "<disciplina>"

        # Com uv
        uv run record -d "<disciplina>"
        ```

## Estrutura do projeto

```text
EduIA-RAG
├───data/
│       answers.json
│       questions.json     # Perguntas e respostas (editado manualmente)
│
├───docs/
│   ├───converted/         # Arquivos convertidos em Markdown
│   └───raw/               # Arquivos brutos
│
└───src/
    └───pipeline/
        │   constants.py
        │   utils.py
        │
        ├───cli/
        │       record.py
        │
        └───ingestion/
                converter.py
                embeddings.py
```

## Observações

- **A dimensão do índice deve ser igual à do modelo de _embeddings_.** Ao trocar o modelo, é preciso criar um novo índice, pois a dimensão não pode ser alterada depois da criação.
- **Consultas:** o `Qwen3-Embedding` rende melhor quando as perguntas usam o _prompt_ de instrução do modelo, enquanto os documentos são indexados sem ele.

## Disciplinas do curso de Informática para Internet

Os materiais do curso de Informática para Internet serão adicionados primeiro. Marque as disciplinas cujos materiais já foram adicionados ao banco vetorial.

- [ ] **Filosofia, Ciência e Tecnologia**
- [ ] **Sociologia do Trabalho**
- [ ] **Qualidade de Vida e Trabalho**
- [ ] **Gestão Organizacional**
- [ ] **Fundamentos de Lógica e Algoritmo**
- [ ] **Análise e Projeto Orientados a Objetos**
- [ ] **Projeto de Desenvolvimento de Sistemas para Internet**
- [ ] **Princípios de Design e Projeto Gráfico**
- [ ] **Design Web e Arquitetura da Informação**
- [ ] **Programação Estruturada e Orientada a Objetos**
- [ ] **Banco de Dados**
- [ ] **Programação de Sistemas para Internet**
- [ ] **Instalação e Configuração de Servidores**
- [ ] **Projeto de Interface do Usuário**
- [ ] **Programação Orientada a Serviços**

## Melhorias futuras

- [ ] Usar um modelo da OpenAI para descrever as imagens e tabelas
- [ ] Especificar o uso de títulos em Markdown e preservar a estrutura dos documentos durante a conversão
- [ ] Diversificar estratégia de chunk splitting para diferentes tipos de materiais (listas, slides, textos, etc...)
- [x] Adicionar disciplina no metadata dos _embeddings_ criados
- [x] Adicionar testes com IA para validar qualidade dos embeddings gerados
- [ ] Adicionar testes variando os mateiriais criados, questões, quizzes, flashcards
- [ ] Explorar a estratégia Parent-Child
- [x] Adicionar logs

## Licença

**MIT License**. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.
