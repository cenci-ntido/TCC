from flask import Flask, request
import openai
import psycopg2

openai.api_key = "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"

def enviaGPT(prompt_sistema, prompt_usuario):
    return openai.ChatCompletion.create(
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

def receber_texto():
    try:
        with psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="01thiago",
                host="localhost"
        ) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_schema = %s and table_name = %s;",
                ('public', 'dicionario_campos'))
            resultColumns = cur.fetchall()
            cur.execute("SELECT * FROM dicionario_campos;")
            resultsFields = cur.fetchall()
            dicionario = f'Estrutura: {resultColumns}  Dados: {resultsFields}'

            prompt_sistema = """
            Você é um interpretador de texto do usuário em SQL para Postgres.
            Certifique-se que sua resposta seja possível de ser executada no Postgres.
            Use apenas cláusulas SELECT, SUM, COUNT, JOIN e WHERE. Sem ORDER ou LIMIT ou GROUP BY.
            Responda sempre somente com o código SQL.
            Considere a estrutura do banco de dados: 
            """ + str(dicionario)

            prompt_usuario = request.data.decode("utf-8")
            sql_query = enviaGPT(prompt_sistema, prompt_usuario).choices[0].message.content
            cur.execute(sql_query)
            results = cur.fetchall()

            prompt_sistema_tratamento = (f'Você é um montador de respostas amigáveis ao usuário'
                                         f'Você irá receber uma solicitação de um usuário e uma resposta de um assistente de forma crua '
                                         f'Você deve retornar uma mensagem amigável ao usuário com a resposta obtida do assistente.'
                                         f'Enviarei todo o texto que você responder diretamente ao usuário!')
            prompt_usuário_tratamento = (f'O usuário solicitou: {prompt_usuario},'
                                         f'O assistente obteve a resposta: {results} ')
            retornoTratado = enviaGPT(prompt_sistema_tratamento, prompt_usuário_tratamento).choices[0].message.content
            return f'{retornoTratado}'
    except Exception as e:
        return f'Erro: {str(e)}'


app = Flask(__name__)


@app.route('/receber_texto', methods=['POST'])
def receber_texto_route():
    return receber_texto()


if __name__ == '__main__':
    app.run(debug=True)


