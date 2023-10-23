from flask import Flask, request
import openai
import psycopg2

app = Flask(__name__)

openai.api_key = "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"

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="01thiago",
    host="localhost"
)

cur = conn.cursor()
def getDatabaseDictionary():
    curTables = conn.cursor()
    curTables.execute("select * from dicionario_tabelas")
    resultsTables = curTables.fetchall()

    curCampos = conn.cursor()
    curCampos.execute("select * from dicionario_campos")
    resultsFields = curCampos.fetchall()

    return f'Tabelas {resultsTables} e Campos das tabelas: {resultsFields}'

prompt_sistema = """
Você é um interpetador de texto do usuário em SQL para Postgres. Responda sempre somente com o código SQL.
Considere a estrutura do banco de dados: 
""" + getDatabaseDictionary()

@app.route('/receber_texto', methods=['POST'])
def receber_texto():
    try:
        prompt_usuario = request.data.decode("utf-8")
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": prompt_sistema
                },
                {
                    "role": "user",
                    "content": prompt_usuario
                }
            ],
            temperature=0.7,
            max_tokens=50,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Obtém a consulta SQL gerada
        sql_query = resposta.choices[0].message.content

        # Execute a consulta SQL no banco de dados
        cur.execute(sql_query)

        # Recupere os resultados da consulta
        results = cur.fetchall()

        return f'Resposta do SQL: {results}'
    except Exception as e:
        return f'Erro: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)

conn.close()




