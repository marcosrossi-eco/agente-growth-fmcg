"""Parâmetros de missão (metas) e registro de resultados reais — metas.json."""
import json
import os

from . import RAIZ

CAMINHO = os.path.join(RAIZ, "metas.json")


def carregar():
    if not os.path.isfile(CAMINHO):
        return {}
    with open(CAMINHO, encoding="utf-8") as f:
        return json.load(f)


def salvar(dados):
    with open(CAMINHO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return CAMINHO


def _coagir(valor):
    if valor.lower() in ("true", "false"):
        return valor.lower() == "true"
    try:
        return int(valor)
    except ValueError:
        pass
    try:
        return float(valor)
    except ValueError:
        return valor


def aplicar(dados, pares):
    """Define caminhos anotados, ex.: unit.preco_venda=5.99"""
    alterados = []
    for par in pares:
        if "=" not in par:
            raise ValueError(f"Parâmetro inválido (esperado chave=valor): {par}")
        caminho, valor = par.split("=", 1)
        alvo = dados
        partes = caminho.strip().split(".")
        for p in partes[:-1]:
            alvo = alvo.setdefault(p, {})
        alvo[partes[-1]] = _coagir(valor.strip())
        alterados.append(caminho.strip())
    return alterados


def aplicar_resultado(dados, mes, pares):
    """Registra resultado real do mês, ex.: 1 unidades=3800 investimento=6100."""
    registro = dados.setdefault("resultados", {}).setdefault(str(int(mes)), {})
    return aplicar(registro, pares)


def _brl(x):
    s = f"{x:,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return f"R$ {s}"


def mostrar_texto(d):
    u = d.get("unit", {})
    inv = d.get("investimento", {})
    linhas = [
        "[METAS ATIVAS]",
        f"  Preço unitário: {_brl(u.get('preco_venda', 0))} | Custo: {_brl(u.get('custo_unitario', 0))}",
    ]
    if u.get("preco_caixa"):
        linhas.append(f"  Caixa ({u.get('unidades_por_caixa', '?')} un): {_brl(u['preco_caixa'])}")
    linhas.append(
        f"  Orçamento mensal: {_brl(inv.get('orcamento_mensal', 0))} | Foco: {inv.get('foco', 'não definido')}"
    )
    linhas.append("  Metas por mês:")
    for m in d.get("meses", []):
        linhas.append(
            f"    Mês {m['mes']}: {m.get('unidades', '-')} un | CAC máx {_brl(m['cac_max'])}"
            f" | recompra30 {int(m.get('recompra30', 0) * 100)}% | PDV {m.get('pontos_venda', '-')}"
        )
    if d.get("resultados"):
        linhas.append("  Resultados registrados: mês " + ", ".join(sorted(d["resultados"], key=int)))
    else:
        linhas.append("  Resultados registrados: nenhum (use --resultado)")
    return "\n".join(linhas)


def resumo_para_prompt(d):
    u = d.get("unit", {})
    inv = d.get("investimento", {})
    linhas = [
        f"- Preço de venda: {_brl(u.get('preco_venda', 0))}; custo unitário: {_brl(u.get('custo_unitario', 0))}",
        f"- Orçamento mensal de marketing: {_brl(inv.get('orcamento_mensal', 0))}; foco: {inv.get('foco', 'a definir')}",
    ]
    for m in d.get("meses", []):
        linhas.append(
            f"- Meta mês {m['mes']}: {m.get('unidades', '?')} unidades, CAC máximo {_brl(m.get('cac_max', 0))}, "
            f"recompra 30d {int(m.get('recompra30', 0) * 100)}%, {m.get('pontos_venda', '?')} pontos de venda"
        )
    return "\n".join(linhas)
