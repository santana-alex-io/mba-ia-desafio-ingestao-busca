from search import search_prompt


def main():
    try:
        chain = search_prompt()
    except Exception as error:
        print(f"Não foi possível iniciar o chat: {error}")
        return

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Faça sua pergunta (ou digite 'sair' para encerrar):")

    while True:
        try:
            question = input("\nPERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nChat encerrado.")
            break

        if question.lower() in {"sair", "exit", "quit"}:
            print("Chat encerrado.")
            break
        if not question:
            continue

        try:
            answer = chain(question)
            print(f"RESPOSTA: {answer}")
        except Exception as error:
            print(f"ERRO: Não foi possível responder à pergunta: {error}")


if __name__ == "__main__":
    main()