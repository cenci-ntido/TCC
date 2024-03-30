from openai import OpenAI
import fdb

con = fdb.connect(
    host='localhost',
    database='C:\BALLAGRO.fdb',
    user='VIASOFT',
    password='153'
)

cur = con.cursor()

cur.execute("SELECT tabela, COLUNA, DESCTEC AS descricao, TIPO  FROM pcolunas WHERE TABELA ='CONTAMOV'")



result_string = ""

for row in cur.fetchall():
    result_string += ", ".join(str(value) for value in row) + "\n"  # Adicionando uma quebra de linha no final de cada linha





client = OpenAI(api_key="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")

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content":  "Você é um interpretador de texto do usuário em SQL para Firebrid. Certifique-se que sua resposta seja possível de ser executada no Firebrid. Responda sempre somente com o código SQL em formato de texto. Considere a seguinte estrutura do banco de dados para montar o SQL: " + result_string},
        {"role": "user", "content": "Nome do cliente 123"}
    ]
)

cur.execute(completion.choices[0].message.content)
result_string2 = ""

for row in cur.fetchall():
    result_string2 += ", ".join(str(value) for value in row) + "\n"  # Adicionando uma quebra de linha no final de cada linha


print(result_string2)

cur.close()
con.close()
