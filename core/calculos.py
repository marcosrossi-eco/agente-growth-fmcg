"""Cálculos determinísticos: margens, ROI, ROAS, CAC, NPS e CSAT.

Toda a matemática é feita em código (não pelo modelo), para que as camadas
5 (Analytics/ROI) e 6 (Metas/KPIs) funcionem mesmo sem chave de IA.
"""
from .metas import carregar  # noqa: F401  (reexportado por conveniência)


def brl(x):
    s = f"{x:,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return f"R$ {s}"


def pct(x, casas=1):
    return f"{x * 100:.{casas}f}%".replace(".", ",")


def economia(d):
    """Unit economics a partir de metas.json."""
    u = d.get("unit", {})
    preco = float(u.get("preco_venda", 0))
    custo = float(u.get("custo_unitario", 0))
    margem = round(preco - custo, 2)
    margem_pct = (margem / preco) if preco else 0.0
    roas_eq = round(preco / margem, 2) if margem > 0 else None
    caixa = u.get("preco_caixa")
    und_caixa = u.get("unidades_por_caixa")
    economia_caixa = None
    if caixa and und_caixa and preco:
        avulso = preco * int(und_caixa)
        economia_caixa = (avulso - float(caixa)) / avulso
    return {
        "preco": preco, "custo": custo, "margem": margem, "margem_pct": margem_pct,
        "roas_equilibrio": roas_eq, "economia_caixa": economia_caixa,
        "caixa": float(caixa) if caixa else None, "und_caixa": int(und_caixa) if und_caixa else None,
    }


def projecao(d):
    """Projeção dos primeiros meses com o orçamento configurado."""
    eco = economia(d)
    inv = d.get("investimento", {})
    orc = float(inv.get("orcamento_mensal", 0))
    upc = float(inv.get("unidades_por_cliente", 1.5)) or 1.5
    linhas = []
    for m in d.get("meses", []):
        unidades = float(m.get("unidades", 0))
        faturamento = unidades * eco["preco"]
        contribuicao = unidades * eco["margem"]
        clientes = unidades / upc
        cac = (orc / clientes) if clientes else None
        roi = ((contribuicao - orc) / orc) if orc else None
        linhas.append({
            "mes": m.get("mes"), "unidades": unidades, "faturamento": faturamento,
            "contribuicao": contribuicao, "cac_planejado": cac, "roi": roi,
            "cac_max": m.get("cac_max"), "recompra30": m.get("recompra30"),
            "pontos_venda": m.get("pontos_venda"),
        })
    return {"eco": eco, "orcamento": orc, "foco": inv.get("foco", "não definido"), "linhas": linhas}


def _veredito(atingimento):
    if atingimento is None:
        return "SEM DADO"
    if atingimento >= 1:
        return "ATINGIDA"
    if atingimento >= 0.8:
        return "EM RISCO"
    return "CRÍTICA"


def status(d):
    """Meta vs. real por mês + lista de cobrança (KPIs da camada 6)."""
    eco = economia(d)
    inv = d.get("investimento", {})
    orc = float(inv.get("orcamento_mensal", 0))
    metas_por_mes = {}
    for m in d.get("meses", []):
        metas_por_mes[str(m.get("mes"))] = m

    linhas, cobrancas = [], []
    for chave in sorted(d.get("resultados", {}), key=int):
        res = d["resultados"][chave]
        meta = metas_por_mes.get(chave, {})
        un_real = res.get("unidades")
        un_meta = meta.get("unidades")
        atingimento = (float(un_real) / float(un_meta)) if un_real is not None and un_meta else None

        invest = float(res.get("investimento", orc))
        faturamento = res.get("faturamento")
        if faturamento is None and un_real is not None:
            faturamento = float(un_real) * eco["preco"]
        roas = (float(faturamento) / invest) if faturamento and invest else None

        clientes = res.get("novos_clientes")
        cac = (invest / float(clientes)) if clientes else None
        cac_max = meta.get("cac_max")

        pdv = res.get("pontos_venda", meta.get("pontos_venda"))

        linhas.append({
            "mes": chave, "un_real": un_real, "un_meta": un_meta,
            "atingimento": atingimento, "faturamento": faturamento,
            "investimento": invest, "roas": roas, "cac": cac, "cac_max": cac_max,
            "pdv": pdv, "veredito": _veredito(atingimento),
        })

        # Cobrança de metas (camada 6)
        if atingimento is not None and atingimento < 1:
            faltam = float(un_meta) - float(un_real)
            cobrancas.append(
                f"Mês {chave}: faltam {faltam:,.0f} un para a meta — ritmo necessário de "
                f"{faltam / 30:,.0f} un/dia (30 dias)".replace(",", ".")
            )
        if cac is not None and cac_max is not None and float(cac) > float(cac_max):
            cobrancas.append(
                f"Mês {chave}: CAC real {brl(cac)} acima do teto {brl(float(cac_max))} — revisar criativos/segmentação"
            )
        if roas is not None and eco["roas_equilibrio"] and roas < eco["roas_equilibrio"]:
            cobrancas.append(
                f"Mês {chave}: ROAS real {roas:.2f}x abaixo do equilíbrio "
                f"({eco['roas_equilibrio']:.2f}x) — cada R$1 em anúncio devolve menos que o custo"
            )

    # NPS e CSAT por mês
    pesquisas = []
    for chave in sorted(d.get("resultados", {}), key=int):
        res = d["resultados"][chave]
        meta = metas_por_mes.get(chave, {})
        nps = _nps_de(res)
        csat = _csat_de(res)
        if nps is None and csat is None:
            continue
        linha = {"mes": chave, "nps": nps, "csat": csat,
                 "nps_meta": meta.get("nps_meta"), "csat_meta": meta.get("csat_meta")}
        pesquisas.append(linha)
        if nps is not None and meta.get("nps_meta") is not None and nps < meta["nps_meta"]:
            cobrancas.append(f"Mês {chave}: NPS {nps:.0f} abaixo da meta {meta['nps_meta']} — investigar detratores")
        if csat is not None and meta.get("csat_meta") is not None and csat < meta["csat_meta"]:
            cobrancas.append(f"Mês {chave}: CSAT {csat:.1f} abaixo da meta {meta['csat_meta']:.1f}")

    if not linhas:
        cobrancas.append("Nenhum resultado real registrado — use --resultado <mês> chave=valor ... para alimentar o painel")

    return {"eco": eco, "orcamento": orc, "foco": inv.get("foco", "não definido"),
            "linhas": linhas, "pesquisas": pesquisas, "cobrancas": cobrancas}


def _nps_de(res):
    n = res.get("nps")
    if not n:
        return None
    p, nt, d = n.get("promotores", 0), n.get("neutros", 0), n.get("detratores", 0)
    total = p + nt + d
    return (p - d) * 100.0 / total if total else None


def _csat_de(res):
    c = res.get("csat")
    if not c:
        return None
    soma, respostas = c.get("soma", 0), c.get("respostas", 0)
    return (float(soma) / float(respostas)) if respostas else None


def _tabela(cols, linhas):
    linhas = [[str(v) for v in l] for l in linhas]
    larg = [len(c) for c in cols]
    for l in linhas:
        for i, v in enumerate(l):
            larg[i] = max(larg[i], len(v))
    out = [" | ".join(c.ljust(larg[i]) for i, c in enumerate(cols)),
           "-+-".join("-" * w for w in larg)]
    out += [" | ".join(v.ljust(larg[i]) for i, v in enumerate(l)) for l in linhas]
    return "\n".join(out)


def painel_financeiro(d=None):
    """Texto do painel da Camada 5 (Analytics, ROI & Previsibilidade)."""
    d = d if d is not None else carregar()
    eco = economia(d)
    proj = projecao(d)
    out = []

    out.append("=== UNIT ECONOMICS ===")
    out.append(f"Preço unitário: {brl(eco['preco'])} | Custo: {brl(eco['custo'])} | "
               f"Margem bruta: {brl(eco['margem'])} ({pct(eco['margem_pct'])})")
    if eco["roas_equilibrio"]:
        out.append(f"ROAS de equilíbrio: {eco['roas_equilibrio']:.2f}x — é o piso: abaixo disso o anúncio "
                   "come a margem (crítico com preço de penetração).")
    if eco["economia_caixa"] is not None:
        out.append(f"Caixa {eco['und_caixa']} un por {brl(eco['caixa'])} vs. {brl(eco['preco'] * eco['und_caixa'])} avulso "
                   f"→ economia de {pct(eco['economia_caixa'])} (alavanca de upsell/cross-sell entre sabores).")

    out.append("")
    out.append(f"=== PROJEÇÃO (orçamento {brl(proj['orcamento'])}/mês | foco: {proj['foco']}) ===")
    if proj["linhas"]:
        rows = []
        for l in proj["linhas"]:
            rows.append([
                f"Mês {l['mes']}", f"{l['unidades']:,.0f}".replace(",", "."),
                brl(l["faturamento"]), brl(l["contribuicao"]),
                brl(l["cac_planejado"]) if l["cac_planejado"] else "-",
                pct(l["roi"], 0) if l["roi"] is not None else "-",
            ])
        out.append(_tabela(["Período", "Unidades", "Faturamento", "Contribuição", "CAC planejado", "ROI"], rows))
        tot_un = sum(l["unidades"] for l in proj["linhas"])
        tot_fat = sum(l["faturamento"] for l in proj["linhas"])
        out.append(f"Total 3 meses: {tot_un:,.0f}".replace(",", ".") + f" un | {brl(tot_fat)} faturados")

    st = status(d)
    out.append("")
    out.append("=== REAL vs META ===")
    if st["linhas"]:
        rows = []
        for l in st["linhas"]:
            rows.append([
                f"Mês {l['mes']}",
                f"{l['un_real']:,.0f}".replace(",", ".") if l["un_real"] is not None else "-",
                f"{l['un_meta']:,.0f}".replace(",", ".") if l["un_meta"] is not None else "-",
                pct(l["atingimento"], 0) if l["atingimento"] is not None else "-",
                f"{l['roas']:.2f}x" if l["roas"] else "-",
                brl(l["cac"]) if l["cac"] else "-",
                l["veredito"],
            ])
        out.append(_tabela(["Mes", "Real", "Meta", "% ating.", "ROAS", "CAC", "Veredito"], rows))
    else:
        out.append("(sem resultados registrados — a projeção acima é a expectativa)")

    if st["cobrancas"]:
        out.append("")
        out.append("=== ALERTAS / COBRANÇA ===")
        for c in st["cobrancas"]:
            out.append(f"  ! {c}")

    if st["pesquisas"]:
        out.append("")
        out.append("=== SATISFAÇÃO (NPS/CSAT) ===")
        rows = []
        for p in st["pesquisas"]:
            rows.append([
                f"Mês {p['mes']}",
                f"{p['nps']:.0f}" if p["nps"] is not None else "-",
                str(p["nps_meta"] or "-"),
                f"{p['csat']:.2f}".replace(".", ",") if p["csat"] is not None else "-",
                str(p["csat_meta"] or "-"),
            ])
        out.append(_tabela(["Mes", "NPS", "Meta NPS", "CSAT", "Meta CSAT"], rows))

    return "\n".join(out)


def painel_status(d=None):
    """Texto do painel da Camada 6 (Alinhamento de Metas & KPI Monitoring)."""
    d = d if d is not None else carregar()
    st = status(d)
    eco = st["eco"]
    out = ["=== PAINEL DE METAS — VOLUME / CAC / MARKET SHARE ==="]

    if st["linhas"]:
        rows = []
        for l in st["linhas"]:
            rows.append([
                f"Mês {l['mes']}",
                pct(l["atingimento"], 0) if l["atingimento"] is not None else "-",
                brl(l["faturamento"]) if l["faturamento"] else "-",
                f"{l['roas']:.2f}x" if l["roas"] else "-",
                brl(l["cac"]) if l["cac"] else "-",
                brl(float(l["cac_max"])) if l["cac_max"] else "-",
                str(l["pdv"] or "-"),
                l["veredito"],
            ])
        out.append(_tabela(
            ["Mes", "% meta", "Faturamento", "ROAS", "CAC real", "CAC teto", "PDV", "Status"], rows))
    else:
        out.append("Nenhum resultado registrado ainda. Alimente com:")
        out.append("  python3 agente.py --resultado 1 unidades=3800 investimento=6100 novos_clientes=405 pontos_venda=22")

    out.append("")
    out.append("=== COBRANÇA DO ATRIBUIDO ===")
    if st["cobrancas"]:
        for i, c in enumerate(st["cobrancas"], 1):
            out.append(f"  {i}. {c}")
    else:
        out.append("  Todas as metas registradas estão sendo atingidas.")

    out.append("")
    out.append(f"Piso de rentabilidade: ROAS ≥ {eco['roas_equilibrio']:.2f}x | margem {pct(eco['margem_pct'])}"
               if eco["roas_equilibrio"] else "Piso de rentabilidade: margem não definida (configure unit.*)")
    return "\n".join(out)
