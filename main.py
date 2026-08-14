import os
import random
import sys
import time
import pyodbc

# Configuração da conexão com o banco de dados (Ajuste servidor, usuário e senha)
DADOS_CONEXAO = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=.\SQLEXPRESS;"
    "Database=biblioteca;"
    "UID=sa;"
    "PWD=1234;"
)


def limpar_tela():
    """Limpa a tela do terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def efeito_texto(texto, atraso=0.015):
    """Escreve o texto letra por letra no estilo terminal."""
    for caractere in texto:
        sys.stdout.write(caractere)
        sys.stdout.flush()
        time.sleep(atraso)
    print()


def barra_carregamento(mensagem="PROCESSANDO DADOS"):
    """Exibe uma barra de carregamento interativa."""
    sys.stdout.write(f"{mensagem} ")
    sys.stdout.flush()
    for _ in range(15):
        sys.stdout.write("█")
        sys.stdout.flush()
        time.sleep(0.03)
    print(" [OK]")
    time.sleep(0.2)


def conectar_banco():
    """Estabelece conexão com o SQL Server."""
    try:
        return pyodbc.connect(DADOS_CONEXAO)
    except Exception as e:
        print(f"Erro crítico de conexão: {e}")
        sys.exit(1)


def gerar_missao_aleatoria(cursor):
    """Sorteia um empréstimo e seleciona um dos 6 tipos de perguntas avançadas."""
    query = """
        SELECT e.id_emprestimo, e.id_livro, e.id_aluno, 
               l.nome AS livro_nome, a.nome AS aluno_nome 
        FROM emprestimos e
        JOIN livros l ON e.id_livro = l.id_livro
        JOIN alunos a ON e.id_aluno = a.id_aluno
    """
    cursor.execute(query)
    resultados = cursor.fetchall()
    if not resultados:
        return None

    row = random.choice(resultados)
    dado_completo = {
        "id_emprestimo": str(row.id_emprestimo),
        "id_livro": str(row.id_livro),
        "id_aluno": str(row.id_aluno),
        "livro": row.livro_nome,
        "aluno": row.aluno_nome,
    }

    tipo_missao = random.randint(1, 6)
    return {"dados": dado_completo, "tipo": tipo_missao}


def mostrar_ajuda():
    """Exibe os comandos disponíveis no terminal."""
    print("\n--- COMANDOS DO TERMINAL DE HACKING ---")
    print("  ajuda                           - Exibe esta lista")
    print("  tabela alunos                   - Lista IDs e nomes de alunos")
    print("  tabela livros                   - Lista IDs e nomes de livros")
    print("  tabela emprestimos              - Lista os registros de empréstimos")
    print("  chutar [Sua Resposta]           - Envia a resposta (se forem 2 valores, use virgula)")
    print("  sair                            - Encerra o terminal\n")


def apresentar_enunciado(missao, numero_missao):
    """Imprime o enunciado do desafio com base no tipo sorteado."""
    t = missao["tipo"]
    d = missao["dados"]
    print("\n" + "=" * 65)
    print(f" DESAFIO {numero_missao} DE 2")
    print("=" * 65)
    if t == 1:
        efeito_texto(f"[ALVO #1] Quem é o aluno com ID [ {d['id_aluno']} ]? (Digite o nome do aluno)")
    elif t == 2:
        efeito_texto(f"[ALVO #2] Quem é o aluno que pegou o livro '{d['livro']}'? (Digite o nome do aluno)")
    elif t == 3:
        efeito_texto(f"[ALVO #3] Quais são o NOME DO ALUNO e o NOME DO LIVRO atrelados ao empréstimo ID [ {d['id_emprestimo']} ]?")
        efeito_texto("-> Responda no formato exato: Nome do Aluno, Nome do Livro")
    elif t == 4:
        efeito_texto(f"[ALVO #4] Qual o ID do livro que possui o nome '{d['livro']}'? (Digite o ID numérico)")
    elif t == 5:
        efeito_texto(f"[ALVO #5] Qual o ID do empréstimo associado ao aluno '{d['aluno']}' e livro '{d['livro']}'?")
    elif t == 6:
        efeito_texto(f"[ALVO #6] Qual o nome do livro que possui o ID [ {d['id_livro']} ]?")
    print("=" * 65)


def validar_resposta(chute, missao):
    """Valida o texto digitado de acordo com o tipo de missão."""
    t = missao["tipo"]
    d = missao["dados"]
    chute = chute.strip()

    if t == 1:
        return chute.lower() == d["aluno"].lower()
    elif t == 2:
        return chute.lower() == d["aluno"].lower()
    elif t == 3:
        partes = [p.strip().lower() for p in chute.split(",")]
        if len(partes) >= 2:
            return partes[0] == d["aluno"].lower() and partes[1] == d["livro"].lower()
        return False
    elif t == 4:
        return chute == d["id_livro"]
    elif t == 5:
        return chute == d["id_emprestimo"]
    elif t == 6:
        return chute.lower() == d["livro"].lower()
    return False


def iniciar_terminal():
    os.system("color 0A")
    conexao = conectar_banco()
    cursor = conexao.cursor()

    while True:
        limpar_tela()
        barra_carregamento("INICIALIZANDO DESAFIO EM DUPLA")
        time.sleep(0.3)
        limpar_tela()

        efeito_texto(">>> INFILTRAÇÃO EM DUPLA INICIADA. COMPLETEM AS 2 MISSÕES.")
        efeito_texto(">>> Digite 'ajuda' para listar as ferramentas de varredura.\n")

        missoes_completadas = 0
        
        while missoes_completadas < 2:
            missao_atual = gerar_missao_aleatoria(cursor)
            if not missao_atual:
                efeito_texto("[ERRO CRÍTICO] Base de dados vazia.")
                return

            apresentar_enunciado(missao_atual, missoes_completadas + 1)
            fase_resolvida = False

            while not fase_resolvida:
                comando = input("\nSEC-CLI> ").strip()

                if comando.lower() == "sair":
                    efeito_texto("Desconectando e abortando missão...")
                    cursor.close()
                    conexao.close()
                    return

                elif comando.lower() == "ajuda":
                    mostrar_ajuda()

                elif comando.lower() == "tabela alunos":
                    barra_carregamento("LENDO TABELA [alunos]")
                    cursor.execute("SELECT id_aluno, nome FROM alunos")
                    print("\nID ALUNO   | NOME")
                    print("-" * 35)
                    for row in cursor.fetchall():
                        print(f"{row.id_aluno:<10} | {row.nome}")
                    print()

                elif comando.lower() == "tabela livros":
                    barra_carregamento("LENDO TABELA [livros]")
                    cursor.execute("SELECT id_livro, nome FROM livros")
                    print("\nID LIVRO   | NOME")
                    print("-" * 35)
                    for row in cursor.fetchall():
                        print(f"{row.id_livro:<10} | {row.nome}")
                    print()

                elif comando.lower() == "tabela emprestimos":
                    barra_carregamento("LENDO TABELA [emprestimos]")
                    cursor.execute("SELECT id_emprestimo, id_livro, id_aluno FROM emprestimos")
                    print("\nID EMPRÉSTIMO | ID LIVRO   | ID ALUNO")
                    print("-" * 42)
                    for row in cursor.fetchall():
                        print(f"{row.id_emprestimo:<13} | {row.id_livro:<10} | {row.id_aluno}")
                    print()

                elif comando.lower().startswith("chutar "):
                    chute = comando[7:].strip()
                    barra_carregamento("VALIDANDO CHAVE DE CRIPTOGRAFIA")

                    if validar_resposta(chute, missao_atual):
                        efeito_texto(f"\n[SUCESSO] Desafio {missoes_completadas + 1} superado com êxito!")
                        missoes_completadas += 1
                        fase_resolvida = True
                        time.sleep(1.5)
                        limpar_tela()
                    else:
                        efeito_texto("\n[ALERTA] ACESSO NEGADO! Chute incorreto. Tentem novamente.")

                else:
                    efeito_texto("[ERRO] Comando desconhecido. Digite 'ajuda' para verificar.")

        print("=" * 65)
        efeito_texto("🎉 PARABÉNS À DUPLA! O servidor BIBLIOTECA foi totalmente hackeado!")
        print("=" * 65)
        
        jogar_de_novo = input("\nDesejam iniciar um novo desafio em dupla? (S/N): ").strip().upper()
        if jogar_de_novo != "S":
            efeito_texto("\nEncerrando terminal. Até a próxima operação.")
            break

    cursor.close()
    conexao.close()


if __name__ == "__main__":
    iniciar_terminal()
