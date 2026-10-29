"""Cliente da API de IA compatível com OpenAI (Freebuff).

A chave fica apenas em .env (nunca no código nem no terminal).
Sem chave, o agente continua funcional no modo determinístico/estrutural.
"""
import json
import os
import urllib.error
import urllib.request

URL_PADRAO = "https://freebuff.com/api/v1/paid"
MODELO_PADRAO = "gpt-5.1"


class SemChave(Exception):
    """OPENAI_API_KEY não configurada."""


class ErroIA(Exception):
    """Falha de rede ou de API ao chamar o modelo."""


def carregar_env(caminho):
    """Lê .env simples (CHAVE=valor) sem dependências externas."""
    if not os.path.isfile(caminho):
        return
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


def chave():
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("FREEBUFF_API_KEY")


def configurada():
    return bool(chave())


def base():
    return (os.environ.get("FREEBUFF_API_BASE") or URL_PADRAO).rstrip("/")


_modelo_cache = None


def modelo():
    """Modelo configurado ou descoberto via GET /models (compatível com OpenAI)."""
    global _modelo_cache
    if _modelo_cache:
        return _modelo_cache
    definido = os.environ.get("FREEBUFF_MODEL")
    if definido:
        _modelo_cache = definido
        return _modelo_cache
    try:
        req = urllib.request.Request(
            base() + "/models",
            headers={"Authorization": "Bearer " + (chave() or "")},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            dados = json.load(r)
        ids = [x.get("id") for x in dados.get("data", []) if x.get("id")]
        preferidos = [
            i for i in ids
            if any(p in i.lower() for p in ("gpt-5", "gpt-4o", "gpt-4", "claude", "gemini"))
        ] or ids
        if preferidos:
            _modelo_cache = preferidos[0]
            return _modelo_cache
    except Exception:
        pass
    _modelo_cache = MODELO_PADRAO
    return _modelo_cache


def chat(mensagens, temperatura=0.7, timeout=180):
    """Chama /chat/completions e devolve o texto da resposta."""
    if not configurada():
        raise SemChave("OPENAI_API_KEY ausente.")
    corpo = json.dumps({
        "model": modelo(),
        "messages": mensagens,
        "temperature": temperatura,
    }).encode("utf-8")
    req = urllib.request.Request(
        base() + "/chat/completions",
        data=corpo,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + chave(),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            dados = json.load(r)
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode("utf-8", "replace")[:400]
        raise ErroIA(f"HTTP {e.code} na API: {detalhe}") from e
    except urllib.error.URLError as e:
        raise ErroIA(f"Falha de rede na API: {e.reason}") from e
    try:
        return dados["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise ErroIA("Resposta inesperada da API: " + json.dumps(dados)[:400]) from e


def cartao_configuracao():
    return (
        "[IA: NÃO CONFIGURADA]\n"
        "  1. Gere sua chave em https://freebuff.com/account/api\n"
        "  2. Crie o arquivo .env na raiz do projeto (use .env.example como modelo)\n"
        "  3. Adicione: OPENAI_API_KEY=sua_chave_aqui\n"
        "  Enquanto isso, as camadas seguem no modo determinístico (cálculos e estrutura)."
    )
