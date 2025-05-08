import fdb
import time
from flask import Flask, request, jsonify
from google import genai

# === CONFIGURAÇÃO DA API KEY DA GOOGLE ===
client = genai.Client(api_key="AIzaSyB2uqBIZol3eQds7uxboI4WxlG0KXh8s7Y")  # substitua pela sua chave real

# === CONEXÃO COM BANCO FIREBIRD ===
def conectar_banco():
    return fdb.connect(
        host='localhost',
        database='C:\\Users\\Tiago\\Downloads\\BANCO_AGRO_VIASOFT\\BALLAGRO.FDB',
        user='SYSDBA',
        password='masterkey'
    )

def consultar_sql(query):
    con = conectar_banco()
    cur = con.cursor()
    cur.execute(query)
    result_string = "\n".join(",".join(str(value) for value in row) for row in cur.fetchall())
    cur.close()
    con.close()
    return result_string

# === FUNÇÃO DE COMPLETAR CONVERSA USANDO GEMINI ===
def completar_conversa(mensagens):
    prompt = "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in mensagens])
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

# === FUNÇÃO QUE PROCESSA O PEDIDO DO USUÁRIO ===
def receber_texto():
    user_request = request.data.decode("utf-8")

    estrutura_inicio = time.time()
    sql_structure = consultar_sql("""
        SELECT tabela, COLUNA, DESCTEC AS descricao, TIPO
        FROM pcolunas
        WHERE TABELA IN (
            'ITEMAGRO', 'CONTAMOV', 'CONFREAGE', 'AGROSYSCFG',
            'ABASTECOMPLETO', 'PEDCAB'
        )
    """)
    estrutura_tempo = time.time() - estrutura_inicio

    gerar_sql_inicio = time.time()
    sql_gerado = completar_conversa([
        {
            "role": "system",
            "content": f"""Você é um interpretador de texto do usuário em SQL para Firebird.
Sua resposta será executada diretamente no banco Firebird.
Não use crases (```) nem 'sql'. Apenas o SQL puro, sem formatação Markdown.
Use apenas as tabelas da seguinte estrutura: {sql_structure}.
Se o pedido não fizer sentido, ou você não entender, ou peça algum dado que não tem no banco, diga apenas: Não posso responder."""
        },
        {
            "role": "user",
            "content": user_request
        }
    ])
    gerar_sql_tempo = time.time() - gerar_sql_inicio

    # Limpar blocos de código (caso existam)
    sql_gerado = sql_gerado.strip().removeprefix("```sql").removesuffix("```").strip()

    executar_sql_inicio = time.time()
    try:
        resultado_sql = consultar_sql(sql_gerado)
        resultado_legivel = resultado_sql if resultado_sql else "Nenhum resultado encontrado para a consulta."
    except Exception as e:
        resultado_sql = ""
        resultado_legivel = f"Erro ao executar SQL: {e}"
    executar_sql_tempo = time.time() - executar_sql_inicio

    resposta_inicio = time.time()
    mensagem_final = completar_conversa([
        {
            "role": "system",
            "content": """Você é um montador de respostas amigáveis ao usuário, porém diretas e sem perguntas, super formal, não fale nada a mais do que a resposta diretamente.
Você irá receber uma solicitação de um usuário, um SQL executado e o resultado. Gere uma resposta direta com base nisso. Se o SQL gerado for: Não posso responder, responda o mesmo: Não posso responder"""
        },
        {
            "role": "user",
            "content": f"""
O usuário solicitou: {user_request}.
O SQL executado foi: {sql_gerado}.
O resultado foi: {resultado_legivel}
"""
        }
    ])
    resposta_tempo = time.time() - resposta_inicio

    return jsonify({
        "sql_gerado": sql_gerado,
        "tempo_sql_gerado": round(gerar_sql_tempo, 3),
        "resultado_sql": resultado_sql,
        "tempo_execucao_sql": round(executar_sql_tempo, 3),
        "mensagem_ia": mensagem_final,
        "tempo_mensagem_ia": round(resposta_tempo, 3),
        "tempo_carregar_estrutura": round(estrutura_tempo, 3)
    })

# === FLASK APP ===
app = Flask(__name__)

@app.route('/receber_texto', methods=['POST'])
def receber_texto_route():
    return receber_texto()

if __name__ == '__main__':
    app.run(debug=True)
