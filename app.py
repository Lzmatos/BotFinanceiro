# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 13:22:40 2026

@author: CS377260
"""

import re
from datetime import datetime
from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)


@app.route("/")
def home():

    conn = sqlite3.connect("financeiro.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM contas
    ORDER BY id DESC
    """)

    contas = cursor.fetchall()

    conn.close()

    html = """
    <h1>Bot Financeiro Igreja</h1>

    <h3>Contas Cadastradas</h3>

    <table border='1' cellpadding='5'>
        <tr>
            <th>ID</th>
            <th>Beneficiário</th>
            <th>Valor</th>
            <th>Vencimento</th>
            <th>Categoria</th>
            <th>Status</th>
        </tr>
    """

    for conta in contas:

        html += f"""
        <tr>
            <td>{conta[0]}</td>
            <td>{conta[1]}</td>
            <td>R$ {conta[2]:.2f}</td>
            <td>{conta[3]}</td>
            <td>{conta[5]}</td>
            <td>{conta[7]}</td>
        </tr>
        """

    html += "</table>"

    return html

@app.route("/api/contas")
def api_contas():

    conn = sqlite3.connect("financeiro.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        beneficiario,
        valor,
        vencimento,
        categoria,
        forma_pagamento,
        status
    FROM contas
    ORDER BY id DESC
    """)

    contas = cursor.fetchall()

    conn.close()

    resultado = []

    for conta in contas:

        resultado.append({

            "id": conta[0],
            "beneficiario": conta[1],
            "valor": conta[2],
            "vencimento": conta[3],
            "categoria": conta[4],
            "forma_pagamento": conta[5],
            "status": conta[6]

        })

    return jsonify(resultado)

@app.route("/api/cadastrar", methods=["POST"])
def api_cadastrar():

    dados = request.json

    beneficiario = dados.get("beneficiario")
    valor = dados.get("valor")
    vencimento = dados.get("vencimento")

    categoria = dados.get(
        "categoria",
        "Outros"
    )

    forma = dados.get(
        "forma_pagamento",
        "PIX"
    )

    conn = sqlite3.connect(
        "financeiro.db"
    )

    cursor = conn.cursor()

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
        0,
        categoria,
        forma,
        "ABERTO"

    ))

    conn.commit()
    conn.close()

    return jsonify({

        "sucesso": True,
        "mensagem":
        "Conta cadastrada"

    })
        
@app.route("/api/mensagem", methods=["POST"])
def api_mensagem():

    dados = request.json

    mensagem = dados.get(
        "mensagem",
        ""
    )

    numeros = re.findall(
        r'\d+[.,]?\d*',
        mensagem
    )

    if len(numeros) == 0:

        return jsonify({
            "sucesso": False,
            "mensagem":
            "Não encontrei valor."
        })

    valor = numeros[0]

    valor = valor.replace(
        ".",
        ""
    ).replace(
        ",",
        "."
    )

    valor = float(valor)

    palavras = mensagem.split()

    beneficiario = palavras[0]

    hoje = datetime.now()

    vencimento = hoje.strftime(
        "%d/%m/%Y"
    )

    categoria = "Outros"

    texto = mensagem.lower()

    if "cpfl" in texto:
        categoria = "Energia"

    elif "mercado" in texto:
        categoria = "Mercado"

    elif "internet" in texto:
        categoria = "Internet"

    conn = sqlite3.connect(
        "financeiro.db"
    )

    cursor = conn.cursor()

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
        0,
        categoria,
        "PIX",
        "ABERTO"

    ))

    conn.commit()
    conn.close()

    return jsonify({

        "sucesso": True,

        "beneficiario":
        beneficiario,

        "valor":
        valor,

        "categoria":
        categoria

    }) 
        
@app.route("/api/perguntar", methods=["POST"])
def api_perguntar():

    dados = request.json

    mensagem = dados.get(
        "mensagem",
        ""
    ).lower()

    conn = sqlite3.connect(
        "financeiro.db"
    )

    cursor = conn.cursor()

    # =====================
    # TOTAL EM ABERTO
    # =====================

    if "quanto tenho em aberto" in mensagem \
    or "quanto devo" in mensagem:

        cursor.execute("""
        SELECT
            COUNT(*),
            SUM(valor)
        FROM contas
        WHERE status='ABERTO'
        """)

        resultado = cursor.fetchone()

        conn.close()

        return jsonify({

            "tipo": "consulta",

            "quantidade":
            resultado[0],

            "total":
            resultado[1] or 0

        })

    # =====================
    # MOSTRAR CONTAS
    # =====================

    elif "mostrar contas" in mensagem:

        if "pagas" in mensagem:

            status = "PAGO"

        elif "vencidas" in mensagem:

            status = "VENCIDO"

        elif "canceladas" in mensagem:

            status = "CANCELADO"

        else:

            status = "ABERTO"

        cursor.execute("""
        SELECT
            id,
            beneficiario,
            valor,
            vencimento
        FROM contas
        WHERE status=?
        ORDER BY id
        """,
        (status,)
        )

        contas = cursor.fetchall()

        conn.close()

        lista = []

        for conta in contas:

            lista.append({

                "id": conta[0],
                "beneficiario": conta[1],
                "valor": conta[2],
                "vencimento": conta[3]

            })

        return jsonify({

            "tipo": "lista",
            "status": status,
            "contas": lista

        })

    # =====================
    # PAGUEI
    # =====================

    elif mensagem.startswith("paguei"):

        numeros = re.findall(
            r'\d+',
            mensagem
        )

        if len(numeros) == 0:

            conn.close()

            return jsonify({

                "erro":
                "Informe o ID"

            })

        id_conta = numeros[0]

        cursor.execute("""
        UPDATE contas
        SET status='PAGO'
        WHERE id=?
        """,
        (id_conta,)
        )

        conn.commit()

        conn.close()

        return jsonify({

            "sucesso": True,

            "mensagem":
            f"Conta {id_conta} marcada como PAGA"

        })

    # =====================
    # CANCELAR
    # =====================

    elif mensagem.startswith("cancelar"):

        numeros = re.findall(
            r'\d+',
            mensagem
        )

        if len(numeros) == 0:

            conn.close()

            return jsonify({

                "erro":
                "Informe o ID"

            })

        id_conta = numeros[0]

        cursor.execute("""
        UPDATE contas
        SET status='CANCELADO'
        WHERE id=?
        """,
        (id_conta,)
        )

        conn.commit()

        conn.close()

        return jsonify({

            "sucesso": True,

            "mensagem":
            f"Conta {id_conta} cancelada"

        })

    conn.close()

    return jsonify({

        "mensagem":
        "Comando não reconhecido"

    })        

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )