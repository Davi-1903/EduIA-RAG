# EduIA-RAG

**RAG** do sistema [**EduIA**](https://github.com/Davi-1903/EduIA)

## Como executar

1. **Clone o repositório**

    ```bash
    git clone https://github.com/Davi-1903/EduIA-RAG.git
    ```

2. **Instale as dependências**

    ```bash
    pip install -r requirements.txt
    # or
    uv sync
    ```

3. **Execute o scripts**

    - [`converter.py`](./converter.py): Arquivo responsável por converter os [documentos](./docs) em markdown. [Estrutura dos documentos](.estrutura_dos_documentos)
    - [`main.py`](./main.py): Arquivo responsável por criar os embeddings e salvar

    ```bash
    python <arquivo.py>
    # or
    uv run <arquivo.py>
    ```

> [!TIP]
> Use ambiente virtual, pois são muitas dependências

## Disciplinas técnicas da antiga ementa

- [x] **Informática Básica**
- [x] **Fundamentos de Lógica e Algoritmo**
- [x] **Princípios de Design e Projeto Gráfico**
- [ ] **Programção Estrutura e Orientada a Objetos**
- [ ] **Design Web e Arquitetura da Informação**
- [ ] **Análise e Projeto Orientados a Objetos**
- [ ] **Programção de Sistemas para Internet**
- [ ] **Banco de dados**
- [ ] **Instalação e Configuração de Servidores**
- [ ] **Programção Estruturada e Orientada a Serviços**
- [ ] **Projeto de Desenvolvimento de Sistemas para Internet**

## Disciplinas técnicas da nova ementa

...

## Estrutura dos documentos

```bash
docs
├───converted  # Arquivos convertidos em markdown
└───raw        # Arquivos crus (até o momento PDFs)
```

## Pontos para melhorar

- [ ] **Usar modelo para descrever as imagens**
- [ ] **Especificar o uso de títulos em markdown**
- [ ] **Usar metadados útils nos documentos criados, como (`souce`, `title`, `section`, `discipine`, `file_name`, `page` ou `section_order`)**
- [ ] **Usar armazenamento na nuvem**
