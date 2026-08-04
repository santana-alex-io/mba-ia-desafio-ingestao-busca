import os
from pathlib import Path
from typing import Callable

from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_postgres import PGVector


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

FALLBACK_ANSWER = "Não tenho informações necessárias para responder sua pergunta."

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"A variável de ambiente {name} não foi configurada.")
    return value


def search_prompt(question: str | None = None) -> Callable[[str], str] | str:
    google_api_key = required_env("GOOGLE_API_KEY")
    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001"),
        google_api_key=google_api_key,
    )
    vector_store = PGVector(
        embeddings=embeddings,
        connection=required_env("DATABASE_URL"),
        collection_name=required_env("PG_VECTOR_COLLECTION_NAME"),
        use_jsonb=True,
    )
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite"),
        google_api_key=google_api_key,
        temperature=0,
    )

    def answer(user_question: str) -> str:
        results = vector_store.similarity_search_with_score(
            user_question,
            k=10,
        )
        if not results:
            return FALLBACK_ANSWER

        context = "\n\n".join(document.page_content for document, _ in results)
        prompt = PROMPT_TEMPLATE.format(
            contexto=context,
            pergunta=user_question,
        )
        response = llm.invoke(prompt)
        content = response.content

        if isinstance(content, str):
            return content.strip()

        text_parts = [
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("text")
        ]
        return "\n".join(text_parts).strip() or FALLBACK_ANSWER

    if question is not None:
        return answer(question)
    return answer