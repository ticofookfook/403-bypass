## 🚀 Funcionalidades

- **Múltiplos Métodos de Bypass**: Testa várias técnicas para contornar respostas 403 Forbidden
  - Técnicas de manipulação de caminhos
  - Falsificação de cabeçalhos HTTP
  - Manipulação de métodos HTTP
  - Alternância de User-Agent
- **Processamento Paralelo**: Execução rápida com suporte a multi-threading
- **Integração com Wayback Machine**: Verifica se a URL alvo foi arquivada com permissões potencialmente diferentes
- **Saída Colorida**: Resultados fáceis de ler com respostas codificadas por cores
- **Relatórios Detalhados**: Saída abrangente de tentativas bem-sucedidas de bypass
- **Personalizável**: Opções de configuração flexíveis através de argumentos de linha de comando

## 📋 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/403-bypass.git
cd 403-bypass

# Instale as dependências necessárias
pip install -r requirements.txt
```

## 🔧 Uso

### Uso Básico

```bash
python bypass.py http://exemplo.com/caminho-proibido
```

### Opções Avançadas

```bash
python bypass.py http://exemplo.com/admin -t 20 --user-agents --methods -v -o resultados.txt
```

### Argumentos de Linha de Comando

| Opção | Descrição |
|--------|-------------|
| `url` | URL alvo (obrigatório) |
| `-t, --threads` | Número de threads concorrentes (padrão: 10) |
| `-v, --verbose` | Exibe saída detalhada |
| `-o, --output` | Salva resultados em arquivo |
| `--timeout` | Tempo limite da requisição em segundos (padrão: 5) |
| `--no-color` | Desativa saída colorida |
| `--no-wayback` | Pula verificação no Wayback Machine |
| `--user-agents` | Testa diferentes user agents |
| `--methods` | Testa diferentes métodos HTTP |

## 🛡️ Técnicas de Bypass

### Manipulação de Caminhos

A ferramenta testa várias técnicas de manipulação de caminhos, incluindo:

- Barras duplas (`//caminho//`)
- Codificação de caminho (`%2e/caminho`)
- Caracteres finais (`caminho/`, `caminho/.`, `caminho?`, `caminho#`)
- Extensões de arquivo (`caminho.html`, `caminho.php`, `caminho.json`)
- Caracteres especiais (`caminho;/`, `caminho..;/`)
- Truques de codificação URL (`caminho%20`, `caminho%09`)
- E muitos mais!

### Cabeçalhos HTTP

Testa vários cabeçalhos HTTP que podem contornar controles de acesso:

- `X-Original-URL`
- `X-Rewrite-URL`
- `X-Forwarded-For`
- `X-Forwarded-Host`
- `X-Host`
- `X-Custom-IP-Authorization`
- Além de muitos outros que podem enganar o servidor, fazendo-o acreditar que a requisição está vindo de uma fonte autorizada

### Métodos HTTP

Testa métodos HTTP alternativos que podem ter diferentes controles de acesso:

- GET, POST, PUT, DELETE, PATCH
- OPTIONS, TRACE, CONNECT, HEAD
- PROPFIND (WebDAV)

### Falsificação de User-Agent

Testa diferentes user agents incluindo:

- Navegadores desktop (Chrome, Firefox, Safari)
- Navegadores móveis (iPhone, iPad)
- Crawlers de mecanismos de busca (Googlebot, Bingbot)
- Crawlers de redes sociais (Facebook)

## 📊 Exemplo de Saída

```
 _  _    ___ ____    ____               
| || |  / _ \___ \  |  _ \             
| || |_| | | |__) | | |_) |_   _ _ __  
|__   _| | | |__ <  |  _ <| | | | '_ \ 
   | | | |_| |__) | | |_) | |_| | | | |
   |_|  \___/____/  |____/ \__, |_| |_|
                           __/ |      
                          |___/       
    Ferramenta de Bypass 403 v2.0 - Encontre seu caminho!

[+] Alvo: http://exemplo.com/admin
[+] Iniciando testes de bypass com 10 threads...

Requisição inicial para http://exemplo.com/admin retornou: 403, 1528 bytes

http://exemplo.com/admin --> 403, 1528 bytes
http://exemplo.com/%2e/admin --> 404, 345 bytes
http://exemplo.com/admin/. --> 403, 1528 bytes
http://exemplo.com//admin// --> 200, 8721 bytes
http://exemplo.com/./admin/./ --> 403, 1528 bytes
...

[Wayback Machine] Arquivo encontrado:
{
  "url": "http://exemplo.com/admin",
  "timestamp": "20220315185642",
  "status": "200",
  "available": true
}

------------------------------------------------------------
Resumo: 7 tentativas de bypass bem-sucedidas de um total de 45 testes

Resultados salvos em resultados.txt
```

## 🔍 Aplicações Práticas

- **Testes de Segurança**: Teste aplicações web para vulnerabilidades de controle de acesso
- **Bug Bounty Hunting**: Identifique problemas de bypass 403 em programas de bug bounty
- **Teste de Penetração**: Avalie a segurança de configurações de servidores web
- **Pesquisa de Segurança**: Experimente com diferentes técnicas de bypass

## ⚠️ Aviso Legal

Esta ferramenta é fornecida apenas para fins educacionais e testes de segurança autorizados. Sempre obtenha permissão adequada antes de testar qualquer site ou aplicação. O autor não se responsabiliza por qualquer uso indevido ou dano causado por esta ferramenta.

## 📜 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 🤝 Contribuindo

Contribuições, problemas e solicitações de recursos são bem-vindos! Sinta-se à vontade para verificar a [página de issues](https://github.com/seu-usuario/403-bypass/issues).

1. Faça um fork do repositório
2. Crie sua branch de recurso (`git checkout -b recurso/recurso-incrivel`)
3. Faça commit de suas alterações (`git commit -m 'Adiciona um recurso incrível'`)
4. Faça push para a branch (`git push origin recurso/recurso-incrivel`)
5. Abra um Pull Request
