import requests
import time

URL = "http://127.0.0.1:5000/receber_texto"
HEADERS = {"Content-Type": "text/plain"}
BODY = "Pessoa CPF 11145766978 está cadastrada?"

tempos = []

for i in range(10):
    inicio = time.time()
    response = requests.post(URL, headers=HEADERS, data=BODY)
    fim = time.time()

    duracao = fim - inicio
    tempos.append(duracao)

    print(f"[{i+1}] Tempo de execução: {duracao:.3f}s | Status: {response.status_code}")

media = sum(tempos) / len(tempos)
print(f"\nMédia de tempo de execução: {media:.3f}s")
