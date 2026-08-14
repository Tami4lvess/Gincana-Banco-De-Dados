import os
import random
import sys
import time

import pyodbc


# ============================================================
# CONFIGURAÇÃO DO BANCO
# ============================================================

DADOS_CONEXAO = (
    r"Driver={ODBC Driver 17 for SQL Server};"
    r"Server=localhost\sqlexpress;"
    r"Database=biblioteca;"
    r"UID=sa;"
    r"PWD=1234;"
    r"TrustServerCertificate=yes;"
)


# ============================================================
# UTILITÁRIOS
# ============================================================

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def esperar(segundos=1):
    time.sleep(segundos)


def efeito_texto(texto, atraso=0.01):
    """Escreve texto com efeito de terminal."""
    for caractere in texto:
        sys.stdout.write(caractere)
        sys.stdout.flush()
        time.sleep(atraso)

    print()


def barra_carregamento(
    mensagem="PROCESSANDO DADOS",
    multiplicador_tempo=1.0
):
    sys.stdout.write(f"{mensagem} ")
    sys.stdout.flush()

    for _ in range(15):
        sys.stdout.write("█")
        sys.stdout.flush()
        time.sleep(0.04 * multiplicador_tempo)

    print(" [OK]")
    esperar(0.3 * multiplicador_tempo)


# ============================================================
# BANCO DE DADOS
# ============================================================

def conectar_banco():
    """Conecta ao SQL Server e retorna a conexão."""

    try:
        return pyodbc.connect(
            DADOS_CONEXAO,
            timeout=5
        )

    except pyodbc.Error as erro:

        print("\n[ERRO CRÍTICO] Não foi possível conectar ao SQL Server.")
        print(f"Detalhes: {erro}")

        print("\nVerifique:")
        print("  - O SQL Server está executando.")
        print("  - O SQL Server Express está em localhost\\SQLEXPRESS.")
        print("  - O banco 'biblioteca' existe.")
        print("  - O usuário e senha estão corretos.")
        print("  - O ODBC Driver 17 for SQL Server está instalado.")

        input("\nPressione ENTER para sair...")

        return None


def preparar_banco(conexao):
    """
    Garante que a tabela utilizada pelo ranking exista.

    As tabelas:
        alunos
        livros
        emprestimos

    continuam sendo responsabilidade do banco do projeto.
    """

    cursor = conexao.cursor()

    cursor.execute(
        """
        IF OBJECT_ID('dbo.historico_hacker', 'U') IS NULL
        BEGIN

            CREATE TABLE dbo.historico_hacker
            (
                id_historico INT IDENTITY(1,1) PRIMARY KEY,

                jogadores NVARCHAR(150) NOT NULL,

                tempo_segundos INT NOT NULL,

                pontuacao DECIMAL(10,2) NOT NULL,

                data_partida DATETIME2 NOT NULL
                    CONSTRAINT DF_historico_hacker_data
                    DEFAULT SYSDATETIME()
            )

        END
        """
    )

    conexao.commit()

    cursor.close()


# ============================================================
# MISSÕES
# ============================================================

def gerar_missao_por_dificuldade(cursor, nivel):
    """
    Escolhe um empréstimo existente no banco
    e transforma os dados em uma missão.
    """

    query = """
        SELECT
            e.id_emprestimo,
            e.id_livro,
            e.id_aluno,
            l.nome AS livro_nome,
            a.nome AS aluno_nome

        FROM emprestimos AS e

        INNER JOIN livros AS l
            ON e.id_livro = l.id_livro

        INNER JOIN alunos AS a
            ON e.id_aluno = a.id_aluno
    """

    try:

        cursor.execute(query)

        resultados = cursor.fetchall()

    except pyodbc.Error as erro:

        print(
            f"\n[ERRO] Não foi possível consultar "
            f"os empréstimos: {erro}"
        )

        return None

    if not resultados:
        return None

    row = random.choice(resultados)

    dados = {
        "id_emprestimo": str(row.id_emprestimo),
        "id_livro": str(row.id_livro),
        "id_aluno": str(row.id_aluno),
        "livro": str(row.livro_nome),
        "aluno": str(row.aluno_nome),
    }

    # --------------------------------------------------------
    # DIFICULDADE
    # --------------------------------------------------------

    if nivel == "facil":

        tipo_missao = random.choice((1, 4))
        pontos = 0.5

    elif nivel == "medio":

        tipo_missao = random.choice((2, 3))
        pontos = 1.0

    else:

        tipo_missao = random.choice((5, 6))
        pontos = 1.5

    return {
        "dados": dados,
        "tipo": tipo_missao,
        "pontos": pontos,
        "nivel": nivel,
    }


def apresentar_enunciado(missao, numero_fase):

    dados = missao["dados"]
    tipo = missao["tipo"]

    print("\n" + "=" * 70)

    print(
        f" DESAFIO {numero_fase} DE 2 | "
        f"NÍVEL: {missao['nivel'].upper()} | "
        f"{missao['pontos']:.1f} pts"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # MISSÃO 1
    # --------------------------------------------------------

    if tipo == 1:

        efeito_texto(
            f"[ALVO] Quem pegou o livro '{dados['livro']}'?"
        )

        print("       Digite o nome do aluno.")

    # --------------------------------------------------------
    # MISSÃO 2
    # --------------------------------------------------------

    elif tipo == 2:

        efeito_texto(
            f"[ALVO] O aluno '{dados['aluno']}' levou qual livro?"
        )

        print("       Digite o nome do livro.")

    # --------------------------------------------------------
    # MISSÃO 3
    # --------------------------------------------------------

    elif tipo == 3:

        efeito_texto(
            f"[ALVO] Qual o nome do livro cujo ID é "
            f"[ {dados['id_livro']} ]?"
        )

    # --------------------------------------------------------
    # MISSÃO 4
    # --------------------------------------------------------

    elif tipo == 4:

        efeito_texto(
            f"[ALVO] Quem é o aluno associado ao ID "
            f"[ {dados['id_aluno']} ]?"
        )

        print("       Digite o nome completo.")

    # --------------------------------------------------------
    # MISSÃO 5
    # --------------------------------------------------------

    elif tipo == 5:

        efeito_texto(
            f"[ALVO] Qual o ID do empréstimo associado "
            f"ao aluno '{dados['aluno']}' "
            f"e ao livro '{dados['livro']}'?"
        )

    # --------------------------------------------------------
    # MISSÃO 6
    # --------------------------------------------------------

    elif tipo == 6:

        efeito_texto(
            f"[ALVO CRÍTICO] Quais são o ALUNO e o LIVRO "
            f"no empréstimo ID [ {dados['id_emprestimo']} ]?"
        )

        print(
            "       Formato: Nome do Aluno, Nome do Livro"
        )

    print("=" * 70)


# ============================================================
# VALIDAÇÃO
# ============================================================

def normalizar(texto):
    """
    Remove espaços extras e ignora diferença
    entre letras maiúsculas/minúsculas.
    """

    return " ".join(
        texto.strip().casefold().split()
    )


def validar_resposta(chute, missao):

    tipo = missao["tipo"]
    dados = missao["dados"]

    chute = chute.strip()

    # --------------------------------------------------------
    # ALUNO
    # --------------------------------------------------------

    if tipo in (1, 4):

        return (
            normalizar(chute)
            ==
            normalizar(dados["aluno"])
        )

    # --------------------------------------------------------
    # LIVRO
    # --------------------------------------------------------

    if tipo in (2, 3):

        return (
            normalizar(chute)
            ==
            normalizar(dados["livro"])
        )

    # --------------------------------------------------------
    # ID DO EMPRÉSTIMO
    # --------------------------------------------------------

    if tipo == 5:

        return (
            chute.strip()
            ==
            dados["id_emprestimo"]
        )

    # --------------------------------------------------------
    # ALUNO + LIVRO
    # --------------------------------------------------------

    if tipo == 6:

        partes = [
            normalizar(parte)
            for parte in chute.split(",", 1)
        ]

        if len(partes) != 2:
            return False

        aluno_correto = normalizar(
            dados["aluno"]
        )

        livro_correto = normalizar(
            dados["livro"]
        )

        return (
            partes[0] == aluno_correto
            and
            partes[1] == livro_correto
        )

    return False


# ============================================================
# COMANDOS
# ============================================================

def mostrar_ajuda():

    print("\n--- COMANDOS DISPONÍVEIS ---")

    print(
        "  ajuda\n"
        "      Exibe este painel."
    )

    print(
        "\n  tabela alunos\n"
        "      Exibe ID e nome dos alunos."
    )

    print(
        "\n  tabela livros\n"
        "      Exibe ID e nome dos livros."
    )

    print(
        "\n  tabela emprestimos\n"
        "      Exibe ID do empréstimo, "
        "ID do livro e ID do aluno."
    )

    print(
        "\n  chutar [sua resposta]\n"
        "      Envia a resposta da missão."
    )

    print(
        "\n  sair\n"
        "      Aborta a missão atual."
    )

    print()


# ============================================================
# EXIBIR TABELAS
# ============================================================

def exibir_tabela(cursor, tabela):

    try:

        # ----------------------------------------------------
        # ALUNOS
        # ----------------------------------------------------

        if tabela == "alunos":

            barra_carregamento(
                "DUMPING TABLE: alunos"
            )

            cursor.execute(
                """
                SELECT id_aluno, nome
                FROM alunos
                ORDER BY id_aluno
                """
            )

            resultados = cursor.fetchall()

            print("\nID ALUNO   | NOME DO ALUNO")
            print("-" * 45)

            for row in resultados:

                print(
                    f"{str(row.id_aluno):<10} | "
                    f"{row.nome}"
                )

        # ----------------------------------------------------
        # LIVROS
        # ----------------------------------------------------

        elif tabela == "livros":

            barra_carregamento(
                "DUMPING TABLE: livros"
            )

            cursor.execute(
                """
                SELECT id_livro, nome
                FROM livros
                ORDER BY id_livro
                """
            )

            resultados = cursor.fetchall()

            print("\nID LIVRO   | NOME DO LIVRO")
            print("-" * 55)

            for row in resultados:

                print(
                    f"{str(row.id_livro):<10} | "
                    f"{row.nome}"
                )

        # ----------------------------------------------------
        # EMPRÉSTIMOS
        # ----------------------------------------------------

        elif tabela == "emprestimos":

            barra_carregamento(
                "DUMPING TABLE: emprestimos"
            )

            cursor.execute(
                """
                SELECT
                    id_emprestimo,
                    id_livro,
                    id_aluno

                FROM emprestimos

                ORDER BY id_emprestimo
                """
            )

            resultados = cursor.fetchall()

            print(
                "\nID EMPRÉSTIMO | ID LIVRO   | ID ALUNO"
            )

            print("-" * 45)

            for row in resultados:

                print(
                    f"{str(row.id_emprestimo):<13} | "
                    f"{str(row.id_livro):<10} | "
                    f"{row.id_aluno}"
                )

        else:

            print(
                "[ERRO] Tabela desconhecida."
            )

    except pyodbc.Error as erro:

        print(
            f"\n[ERRO DE BANCO] "
            f"Não foi possível consultar a tabela: {erro}"
        )


# ============================================================
# RANKING
# ============================================================

def exibir_ranking(cursor):

    limpar_tela()

    print("=" * 70)

    print(
        "              HACKNET V3.4 - RANKING"
    )

    print("=" * 70)

    try:

        cursor.execute(
            """
            SELECT TOP 10
                jogadores,
                tempo_segundos,
                pontuacao

            FROM historico_hacker

            ORDER BY
                tempo_segundos ASC,
                pontuacao DESC
            """
        )

        resultados = cursor.fetchall()

        if not resultados:

            print(
                "\n[!] Nenhuma partida registrada ainda."
            )

        else:

            print(
                "\nPOSIÇÃO | OPERADORES              "
                "| TEMPO (s) | PONTOS"
            )

            print("-" * 70)

            for rank, row in enumerate(
                resultados,
                start=1
            ):

                print(
                    f" #{rank:<6} | "
                    f"{str(row.jogadores)[:22]:<22} | "
                    f"{row.tempo_segundos:<9} | "
                    f"{float(row.pontuacao):.1f}"
                )

    except pyodbc.Error as erro:

        print(
            f"\n[ERRO] "
            f"Não foi possível carregar o ranking: {erro}"
        )

    print("=" * 70)

    input(
        "\nPressione ENTER para voltar ao lobby..."
    )


# ============================================================
# SALVAR RESULTADO
# ============================================================

def salvar_resultado(
    cursor,
    conexao,
    nomes_dupla,
    tempo_total,
    pontuacao
):

    try:

        cursor.execute(
            """
            INSERT INTO historico_hacker
                (
                    jogadores,
                    tempo_segundos,
                    pontuacao
                )

            VALUES (?, ?, ?)
            """,

            (
                nomes_dupla,
                tempo_total,
                pontuacao
            )
        )

        conexao.commit()

        return True

    except pyodbc.Error as erro:

        conexao.rollback()

        print(
            f"\n[ERRO DE BANCO] "
            f"Não foi possível salvar a partida: {erro}"
        )

        return False


# ============================================================
# EXECUTAR MISSÃO
# ============================================================

def executar_missao(cursor, conexao):

    limpar_tela()

    barra_carregamento(
        "INICIALIZANDO PROTOCOLO COOPERATIVO "
        "DE INFILTRAÇÃO",

        multiplicador_tempo=1.5
    )

    limpar_tela()

    efeito_texto(
        ">>> ACESSO LIBERADO AO TERMINAL SECRETO",
        atraso=0.02
    )

    print("-" * 55)

    nomes_dupla = input(
        "Identifiquem a dupla "
        "(Ex: Carlos e Amanda): "
    ).strip()

    if not nomes_dupla:

        nomes_dupla = (
            "Operadores Anônimos"
        )

    limpar_tela()

    barra_carregamento(
        "AUTENTICANDO CREDENCIAIS NA REDE",
        multiplicador_tempo=1.2
    )

    limpar_tela()

    efeito_texto(
        f">>> OPERAÇÃO INICIADA POR: "
        f"{nomes_dupla.upper()}",
        atraso=0.02
    )

    efeito_texto(
        ">>> O cronômetro foi disparado. "
        "Sejam rápidos e precisos!\n",
        atraso=0.01
    )

    esperar(0.5)

    # --------------------------------------------------------
    # GERAR MISSÕES
    # --------------------------------------------------------

    missao_1 = gerar_missao_por_dificuldade(
        cursor,
        "facil"
    )

    missao_2 = gerar_missao_por_dificuldade(
        cursor,
        random.choice(
            [
                "medio",
                "dificil"
            ]
        )
    )

    if missao_1 is None or missao_2 is None:

        print(
            "\n[ERRO] "
            "Não foi possível gerar as missões."
        )

        print(
            "Verifique se as tabelas "
            "alunos, livros e emprestimos "
            "possuem dados."
        )

        input(
            "\nPressione ENTER "
            "para voltar ao lobby..."
        )

        return True

    fases = [
        missao_1,
        missao_2
    ]

    pontuacao_total = 0.0

    tempo_inicio = time.time()

    # --------------------------------------------------------
    # EXECUTAR AS DUAS FASES
    # --------------------------------------------------------

    for numero_fase, missao in enumerate(
        fases,
        start=1
    ):

        apresentar_enunciado(
            missao,
            numero_fase
        )

        while True:

            comando = input(
                f"\n[{nomes_dupla}] SEC-CLI> "
            ).strip()

            comando_lower = (
                comando.casefold()
            )

            # ------------------------------------------------
            # SAIR
            # ------------------------------------------------

            if comando_lower == "sair":

                efeito_texto(
                    "Abortando missão e "
                    "limpando logs de acesso..."
                )

                return True

            # ------------------------------------------------
            # AJUDA
            # ------------------------------------------------

            if comando_lower == "ajuda":

                mostrar_ajuda()

                continue

            # ------------------------------------------------
            # TABELA ALUNOS
            # ------------------------------------------------

            if comando_lower == "tabela alunos":

                exibir_tabela(
                    cursor,
                    "alunos"
                )

                continue

            # ------------------------------------------------
            # TABELA LIVROS
            # ------------------------------------------------

            if comando_lower == "tabela livros":

                exibir_tabela(
                    cursor,
                    "livros"
                )

                continue

            # ------------------------------------------------
            # TABELA EMPRÉSTIMOS
            # ------------------------------------------------

            if (
                comando_lower
                ==
                "tabela emprestimos"
            ):

                exibir_tabela(
                    cursor,
                    "emprestimos"
                )

                continue

            # ------------------------------------------------
            # CHUTAR
            # ------------------------------------------------

            if comando_lower.startswith(
                "chutar"
            ):

                chute = comando[
                    6:
                ].strip()

                if not chute:

                    print(
                        "[ERRO] "
                        "Você precisa informar "
                        "uma resposta."
                    )

                    print(
                        "Exemplo: "
                        "chutar João da Silva"
                    )

                    continue

                barra_carregamento(
                    "TESTANDO EXPLOIT DE DADOS",
                    multiplicador_tempo=0.8
                )

                if validar_resposta(
                    chute,
                    missao
                ):

                    pontuacao_total += (
                        missao["pontos"]
                    )

                    efeito_texto(
                        f"\n[SUCESSO] "
                        f"Código aceito! "
                        f"+{missao['pontos']:.1f} "
                        f"pontos."
                    )

                    esperar(1)

                    limpar_tela()

                    break

                efeito_texto(
                    "\n[ALERTA] "
                    "FALHA NA QUEBRA! "
                    "Assinatura incorreta. "
                    "Tente novamente."
                )

                continue

            # ------------------------------------------------
            # COMANDO DESCONHECIDO
            # ------------------------------------------------

            print(
                "[ERRO] "
                "Comando desconhecido. "
                "Use 'ajuda' para verificar "
                "as opções."
            )

    # ========================================================
    # FINAL DA MISSÃO
    # ========================================================

    tempo_total = max(
        0,
        int(time.time() - tempo_inicio)
    )

    limpar_tela()

    print("=" * 70)

    efeito_texto(
        ">>> OPERAÇÃO FINALIZADA COM SUCESSO!",
        atraso=0.02
    )

    efeito_texto(
        ">>> SISTEMA DESCRIPTOGRAFADO!",
        atraso=0.02
    )

    print("=" * 70)

    print(
        f"Dupla Operacional : "
        f"{nomes_dupla}"
    )

    print(
        f"Tempo de Invasão  : "
        f"{tempo_total} segundos"
    )

    print(
        f"Pontuação Total   : "
        f"{pontuacao_total:.1f} pontos"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # SALVAR NO BANCO
    # --------------------------------------------------------

    if salvar_resultado(
        cursor,
        conexao,
        nomes_dupla,
        tempo_total,
        pontuacao_total
    ):

        efeito_texto(
            "[GRAVAÇÃO] "
            "Resultado salvo no ranking "
            "com sucesso."
        )

    input(
        "\nPressione ENTER para continuar..."
    )

    return True


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def iniciar_terminal():

    if os.name == "nt":
        os.system("color 0A")

    conexao = conectar_banco()

    if conexao is None:
        return

    cursor = None

    try:

        preparar_banco(conexao)

        cursor = conexao.cursor()

        # ====================================================
        # LOBBY
        # ====================================================

        while True:

            limpar_tela()

            print("=" * 60)

            print(
                "       SISTEMA HACKNET OPERACIONAL V3.4"
            )

            print(
                "       MINIGAME: INFILTRAÇÃO BIBLIOTECA"
            )

            print("=" * 60)

            print(
                "  [1] Iniciar Nova Missão em Dupla"
            )

            print(
                "  [2] Ver Ranking dos Mais Rápidos"
            )

            print(
                "  [3] Desconectar / Sair"
            )

            print("=" * 60)

            opcao = input(
                "\nSEC-LOBBY> "
            ).strip()

            # ------------------------------------------------
            # NOVA MISSÃO
            # ------------------------------------------------

            if opcao == "1":

                continuar = executar_missao(
                    cursor,
                    conexao
                )

                if not continuar:
                    break

            # ------------------------------------------------
            # RANKING
            # ------------------------------------------------

            elif opcao == "2":

                exibir_ranking(
                    cursor
                )

            # ------------------------------------------------
            # SAIR
            # ------------------------------------------------

            elif opcao == "3":

                limpar_tela()

                efeito_texto(
                    "Fechando conexões seguras. "
                    "Até logo, operador."
                )

                break

            # ------------------------------------------------
            # OPÇÃO INVÁLIDA
            # ------------------------------------------------

            else:

                efeito_texto(
                    "[ERRO] "
                    "Opção inválida no lobby."
                )

                esperar(1)

    except KeyboardInterrupt:

        print(
            "\n\n[!] Interrupção detectada. "
            "Encerrando com segurança..."
        )

    except pyodbc.Error as erro:

        print(
            f"\n[ERRO DE BANCO] {erro}"
        )

        input(
            "\nPressione ENTER para sair..."
        )

    finally:

        if cursor is not None:
            cursor.close()

        conexao.close()


# ============================================================
# INÍCIO
# ============================================================

if __name__ == "__main__":
    iniciar_terminal()