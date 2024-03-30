from openai import OpenAI
from flask import Flask, request
import fdb

def conectar_banco():
    return fdb.connect(
        host='localhost',
        database=r'C:\BALLAGRO.fdb',
        user='VIASOFT',
        password='153'
    )

def consultar_sql(query):
    con = conectar_banco()
    cur = con.cursor()
    cur.execute(query)
    result_string = "\n".join(", ".join(str(value) for value in row) for row in cur.fetchall())
    cur.close()
    con.close()
    return result_string

def completar_conversa(messages):
    client = OpenAI(api_key="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")
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    return completion.choices[0].message.content

def receber_texto():
    result_string = consultar_sql("SELECT tabela, COLUNA, DESCTEC AS descricao, TIPO FROM pcolunas WHERE TABELA ='CONTAMOV'")
    user_request = request.data.decode("utf-8")

    sql_response = completar_conversa([
        {"role": "system", "content": f"Você é um interpretador de texto do usuário em SQL para Firebird. Certifique-se de que sua resposta seja possível de ser executada no Firebird. Responda sempre somente com o código SQL em formato de texto. Considere a seguinte estrutura do banco de dados para montar o SQL: {result_string}"},
        {"role": "user", "content": user_request}
    ])

    sql_result = consultar_sql(sql_response)

    user_message = completar_conversa([
        {"role": "system", "content": "Você é um montador de respostas amigáveis ao usuário, porém diretas e sem perguntas, super formal, não fale nada a mais do que a resposta diretamente. Você irá receber uma solicitação de um usuário e uma resposta de um assistente de forma crua. Você deve retornar uma mensagem amigável ao usuário com a resposta obtida do assistente. Enviarei todo o texto que você responder diretamente ao usuário!"},
        {"role": "user", "content": f"O usuário solicitou: {user_request}, O assistente obteve a resposta: {sql_result}"}
    ])

    return user_message

app = Flask(__name__)

@app.route('/receber_texto', methods=['POST'])
def receber_texto_route():
    return receber_texto()

if __name__ == '__main__':
    app.run(debug=True)
