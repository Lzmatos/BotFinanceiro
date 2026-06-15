# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 12:02:29 2026

@author: CS377260
"""

import sqlite3

# ==========================
# BANCO DE DADOS
# ==========================

conn = sqlite3.connect("financeiro.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    beneficiario TEXT,
    valor REAL,
    vencimento TEXT,
    mensal INTEGER,
    categoria TEXT,
    forma_pagamento TEXT,
    status TEXT
)
""")

conn.commit()


# ==========================
# TRATAR VALOR
# ==========================

def tratar_valor(valor):

    valor = str(valor).strip()

    valor = valor.replace("R$", "")
    valor = valor.replace(" ", "")

    if "," in valor and "." in valor:

        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

    elif "," in valor:

        valor = valor.replace(",", ".")

    return float(valor)


# ==========================
# LISTAR CONTAS
# ==========================

def listar_contas_filtro():

    print("\n1 - Em Aberto")
    print("2 - Pagas")
    print("3 - Vencidas")
    print("4 - Canceladas")
    print("5 - Todas")

    opcao = input("Escolha: ")

    if opcao == "1":

        cursor.execute("""
        SELECT *
        FROM contas
        WHERE status='ABERTO'
        ORDER BY id
        """)

    elif opcao == "2":

        cursor.execute("""
        SELECT *
        FROM contas
        WHERE status='PAGO'
        ORDER BY id
        """)

    elif opcao == "3":

        cursor.execute("""
        SELECT *
        FROM contas
        WHERE status='VENCIDO'
        ORDER BY id
        """)

    elif opcao == "4":

        cursor.execute("""
        SELECT *
        FROM contas
        WHERE status='CANCELADO'
        ORDER BY id
        """)

    else:

        cursor.execute("""
        SELECT *
        FROM contas
        ORDER BY id
        """)

    contas = cursor.fetchall()

    if not contas:

        print(
            "\nNenhuma conta encontrada."
        )

        return []

    print("\n===== CONTAS =====\n")

    for conta in contas:

        mensal = (
            "SIM"
            if conta[4] == 1
            else "NÃO"
        )

        print(
            f"ID:{conta[0]} | "
            f"{conta[1]} | "
            f"R${conta[2]:.2f} | "
            f"Venc: {conta[3]} | "
            f"Categoria: {conta[5]} | "
            f"Forma: {conta[6]} | "
            f"Mensal: {mensal} | "
            f"Status: {conta[7]}"
        )

    return contas


# ==========================
# BUSCAR POR ID
# ==========================

def buscar_conta_por_id(id_conta):

    cursor.execute(
        "SELECT * FROM contas WHERE id=?",
        (id_conta,)
    )

    return cursor.fetchone()


# ==========================
# CADASTRAR
# ==========================

def cadastrar():

    print(
        "\n===== CADASTRAR CONTA ====="
    )

    beneficiario = input(
        "Beneficiário: "
    )

    try:

        valor = tratar_valor(
            input("Valor: ")
        )

    except:

        print("Valor inválido.")
        return

    vencimento = input(
        "Data Vencimento (dd/mm/aaaa): "
    )

    mensal = input(
        "Mensal? (S/N): "
    ).upper()

    print("\nCategorias")

    print("1 - Construção")
    print("2 - Combustível")
    print("3 - Mercado")
    print("4 - Energia")
    print("5 - Água")
    print("6 - Internet")
    print("7 - Ajuda Eclesiástica")
    print("8 - Ajuda Construção")
    print("9 - Outros")

    opcao_categoria = input(
        "\nEscolha a categoria: "
    )

    categorias = {

        "1": "Construção",
        "2": "Combustível",
        "3": "Mercado",
        "4": "Energia",
        "5": "Água",
        "6": "Internet",
        "7": "Ajuda Eclesiástica",
        "8": "Ajuda Construção",
        "9": "Outros"

    }

    categoria = categorias.get(
        opcao_categoria,
        "Outros"
    )

    print("\nForma de Pagamento")

    print("1 - PIX")
    print("2 - Dinheiro")
    print("3 - Cartão")
    print("4 - Transferência")
    print("5 - Boleto")
    print("6 - Cheque")
    print("7 - Outros")

    opcao_forma = input(
        "\nEscolha: "
    )

    formas = {

        "1": "PIX",
        "2": "Dinheiro",
        "3": "Cartão",
        "4": "Transferência",
        "5": "Boleto",
        "6": "Cheque",
        "7": "Outros"

    }

    forma = formas.get(
        opcao_forma,
        "Outros"
    )

    mensalidade = (
        1
        if mensal == "S"
        else 0
    )

    cursor.execute("""

    INSERT INTO contas (

        beneficiario,
        valor,
        vencimento,
        mensal,
        categoria,
        forma_pagamento,
        status

    )

    VALUES

    (?, ?, ?, ?, ?, ?, ?)

    """,
    (
        beneficiario,
        valor,
        vencimento,
        mensalidade,
        categoria,
        forma,
        "ABERTO"
    ))

    conn.commit()

    print(
        "\n✅ Conta cadastrada com sucesso!"
    )
    
    # ==========================
# CONSULTAR
# ==========================

def consultar():

    listar_contas_filtro()


# ==========================
# ALTERAR STATUS
# ==========================

def alterar_status():

    contas = listar_contas_filtro()

    if not contas:
        return

    id_conta = input(
        "\nInforme o ID da conta: "
    )

    conta = buscar_conta_por_id(
        id_conta
    )

    if not conta:

        print(
            "\n❌ Conta não encontrada."
        )

        return

    print(
        "\n===== CONTA SELECIONADA ====="
    )

    print(f"ID: {conta[0]}")
    print(f"Beneficiário: {conta[1]}")
    print(f"Valor: R${conta[2]:.2f}")
    print(f"Categoria: {conta[5]}")
    print(f"Forma: {conta[6]}")
    print(f"Status Atual: {conta[7]}")

    while True:

        novo_status = input(

            "\nNovo Status "
            "(ABERTO/PAGO/VENCIDO/CANCELADO): "

        ).upper()

        if novo_status in [

            "ABERTO",
            "PAGO",
            "VENCIDO",
            "CANCELADO"

        ]:

            break

        print(
            "\nStatus inválido."
        )

    cursor.execute(

        """
        UPDATE contas
        SET status=?
        WHERE id=?
        """,

        (
            novo_status,
            id_conta
        )

    )

    conn.commit()

    print(
        "\n✅ Status atualizado com sucesso."
    )


# ==========================
# DELETAR
# ==========================

def deletar():

    contas = listar_contas_filtro()

    if not contas:
        return

    id_conta = input(

        "\nInforme o ID da conta "
        "para exclusão: "

    )

    conta = buscar_conta_por_id(
        id_conta
    )

    if not conta:

        print(
            "\n❌ Conta não encontrada."
        )

        return

    print(
        "\n===== CONTA SELECIONADA ====="
    )

    print(f"ID: {conta[0]}")
    print(f"Beneficiário: {conta[1]}")
    print(f"Valor: R${conta[2]:.2f}")
    print(f"Vencimento: {conta[3]}")
    print(f"Categoria: {conta[5]}")
    print(f"Forma: {conta[6]}")
    print(f"Status: {conta[7]}")

    confirmar = input(

        "\nConfirma exclusão? "
        "(S/N): "

    ).upper()

    if confirmar != "S":

        print(
            "\nOperação cancelada."
        )

        return

    cursor.execute(

        """
        DELETE FROM contas
        WHERE id=?
        """,

        (id_conta,)

    )

    conn.commit()

    print(
        "\n✅ Conta removida com sucesso."
    )
    
    # ==========================
# RELATÓRIO
# ==========================

def relatorio():

    cursor.execute("""
    SELECT COUNT(*), SUM(valor)
    FROM contas
    WHERE status='ABERTO'
    """)

    aberto = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*), SUM(valor)
    FROM contas
    WHERE status='PAGO'
    """)

    pago = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*), SUM(valor)
    FROM contas
    WHERE status='VENCIDO'
    """)

    vencido = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*), SUM(valor)
    FROM contas
    WHERE status='CANCELADO'
    """)

    cancelado = cursor.fetchone()

    total_aberto = aberto[1] if aberto[1] else 0
    total_pago = pago[1] if pago[1] else 0
    total_vencido = vencido[1] if vencido[1] else 0
    total_cancelado = cancelado[1] if cancelado[1] else 0

    print("\n===== RELATÓRIO FINANCEIRO =====")

    print(f"\nContas em Aberto: {aberto[0]}")
    print(f"Valor em Aberto: R${total_aberto:.2f}")

    print(f"\nContas Pagas: {pago[0]}")
    print(f"Valor Pago: R${total_pago:.2f}")

    print(f"\nContas Vencidas: {vencido[0]}")
    print(f"Valor Vencido: R${total_vencido:.2f}")

    print(f"\nContas Canceladas: {cancelado[0]}")
    print(f"Valor Cancelado: R${total_cancelado:.2f}")

    print(
        f"\nTotal Geral: "
        f"R${(total_aberto + total_pago + total_vencido):.2f}"
    )


# ==========================
# MENU
# ==========================

def menu():

    while True:

        print("\n========================")
        print("      BOT FINANCEIRO")
        print("========================")
        print("1 - Cadastrar Conta")
        print("2 - Consultar Contas")
        print("3 - Alterar Status")
        print("4 - Deletar Conta")
        print("5 - Relatórios")
        print("0 - Sair")

        opcao = input("\nEscolha: ")

        if opcao == "1":

            cadastrar()

        elif opcao == "2":

            consultar()

        elif opcao == "3":

            alterar_status()

        elif opcao == "4":

            deletar()

        elif opcao == "5":

            relatorio()

        elif opcao == "0":

            print(
                "\nEncerrando sistema..."
            )

            break

        else:

            print(
                "\nOpção inválida."
            )


# ==========================
# INÍCIO
# ==========================

menu()

conn.close()