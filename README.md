# Desafio MBA Engenharia de Software com IA - Full Cycle

Aplicação de RAG que ingere um PDF no PostgreSQL com pgVector e responde
perguntas no terminal usando LangChain e Gemini.

## Pré-requisitos

- Python 3.10 ou superior
- Docker e Docker Compose
- Chave da API do Google Gemini

## Configuração

Crie o ambiente virtual na raiz do projeto.

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Copie o template de configuração:

Linux/macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Preencha `GOOGLE_API_KEY` no arquivo `.env`. Os demais valores padrão já
apontam para o PostgreSQL do `docker-compose.yml` e para `document.pdf`.

## Banco de dados

Inicie o PostgreSQL e aguarde o healthcheck. O serviço auxiliar cria a extensão
`vector` automaticamente.

```bash
docker compose up -d
docker compose ps
```

## Ingestão

Execute a ingestão a partir da raiz do projeto:

```bash
python src/ingest.py
```

O PDF é dividido em chunks de 1000 caracteres com overlap de 150. Cada
execução recria a collection configurada em `PG_VECTOR_COLLECTION_NAME`, o que
evita documentos duplicados.

## Chat

```bash
python src/chat.py
```

Exemplo:

```text
Faça sua pergunta (ou digite 'sair' para encerrar):

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.
```

Para encerrar, digite `sair` ou pressione `Ctrl+C`.

Perguntas cuja resposta não esteja no contexto recuperado devem retornar:

```text
Não tenho informações necessárias para responder sua pergunta.
```

Para parar o banco:

```bash
docker compose down
```