import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"A variável de ambiente {name} não foi configurada.")
    return value


def ingest_pdf() -> None:
    pdf_path = Path(required_env("PDF_PATH")).expanduser()
    if not pdf_path.is_absolute():
        pdf_path = PROJECT_ROOT / pdf_path
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")

    database_url = required_env("DATABASE_URL")
    collection_name = required_env("PG_VECTOR_COLLECTION_NAME")
    google_api_key = required_env("GOOGLE_API_KEY")
    embedding_model = os.getenv(
        "GOOGLE_EMBEDDING_MODEL", "models/embedding-001"
    )

    documents = PyPDFLoader(str(pdf_path)).load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(documents)
    if not chunks:
        raise ValueError(f"Nenhum conteúdo foi extraído do PDF: {pdf_path}")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=embedding_model,
        google_api_key=google_api_key,
    )
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        connection=database_url,
        collection_name=collection_name,
        pre_delete_collection=True,
        use_jsonb=True,
    )

    print(
        f"Ingestão concluída: {len(documents)} página(s), "
        f"{len(chunks)} chunk(s), collection '{collection_name}'."
    )


if __name__ == "__main__":
    ingest_pdf()