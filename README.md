# EduIA-RAG

Pipeline de **RAG** (_Retrieval-Augmented Generation_, ou Geração Aumentada por Recuperação) do sistema [**EduIA**](https://github.com/Davi-1903/EduIA). O projeto converte documentos em Markdown, gera _embeddings_ a partir deles e os armazena em um banco vetorial no [**Pinecone**](https://www.pinecone.io/).

## Sumário

- [Como executar](#como-executar)
- [Estrutura dos documentos](#estrutura-dos-documentos)
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

    # Com uv
    uv sync
    ```

3. **Crie as variáveis de ambiente**

    Recomendo criar um arquivo `.env` na raiz do projeto:

    ```env
    PINECONE_API_KEY="<SUA-CHAVE-DE-API-DO-PINECONE>"
    ```

4. **Adicione os documentos a serem convertidos**

    Coloque os arquivos no diretório [`docs/raw/`](./docs/raw/). Veja a [estrutura dos documentos](#estrutura-dos-documentos).

5. **Execute os scripts**
    1. Execute o script [`converter.py`](./converter.py) para transformar os documentos de [`docs/raw/`](./docs/raw/) em Markdown. Os arquivos convertidos serão criados em [`docs/converted/`](./docs/converted/).
    2. Execute o script [`embeddings.py`](./embeddings.py) para criar os _embeddings_ e adicioná-los ao banco vetorial do Pinecone.

    ```bash
    # Com pip
    python converter.py
    python embeddings.py

    # Com uv
    uv run converter.py
    uv run embeddings.py
    ```

## Estrutura dos documentos

```text
docs/
├───converted/  # Arquivos convertidos em Markdown
└───raw/        # Arquivos brutos (até o momento, apenas PDFs)
```

## Observações

- **Reexecutar o `embeddings.py` não duplica vetores.** O ID de cada _chunk_ é gerado a partir do nome do arquivo e da posição do trecho, então uma nova execução sobrescreve os mesmos registros. Se um documento for alterado e passar a gerar menos _chunks_, os registros antigos permanecem no índice e precisam ser removidos manualmente.
- **O nome do índice (`eduia-rag`) está fixo no código.** Para usar outro índice, altere o `embeddings.py`.
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
- [ ] Adicionar testes com IA para validar qualidade dos embeddings gerados
- [ ] Explorar a estratégia Parent-Child

## Licença

**MIT License**. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.
