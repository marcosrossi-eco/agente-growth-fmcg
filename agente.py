#!/usr/bin/env python3
"""Agente Growth FMCG — CLI do pipeline de 6 camadas para lançamento de
Água Saborizada Fitness (suplemento alimentar).

Uso:
  python3 agente.py                       # menu interativo
  python3 agente.py --camada 5            # executa uma camada
  python3 agente.py --camada 3 "foco BTL" # com contexto livre
  python3 agente.py --visao-geral         # executa 1..6 em sequência
  python3 agente.py --metas               # mostra parâmetros de missão
  python3 agente.py --definir unit.preco_venda=5.99
  python3 agente.py --resultado 1 unidades=3800 investimento=6100
  python3 agente.py --status              # painel meta vs. real
"""
import argparse
import datetime
import os
import sys

from core import llm
from core import calculos
from core.metas import (RAIZ, carregar, aplicar, aplicar_resultado,
                        mostrar_texto, resumo_para_prompt, salvar)
from core.pipeline import CAMADAS, obter, sistema_da_camada

ENTREGAVEIS = os.path.join(RAIZ, "entregaveis")


def log_execucao(c):
    print(f"\n[EXECUTANDO: {c['id']}. {c['nome']}]")


def _salvar_entrega(c, contexto, corpo):
    os.makedirs(ENTREGAVEIS, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    caminho = os.path.join(ENTREGAVEIS, f"camada{c['id']}-{ts}.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(
            f"[EXECUTANDO: {c['id']}. {c['nome']}]\n\n"
            f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"Contexto: {contexto or '(padrão da camada)'}\n\n{corpo}\n"
        )
    return caminho


def executar_camada(cid, contexto="", usar_ia=True, dados=None):
    c = obter(cid)
    dados = dados if dados is not None else carregar()
    log_execucao(c)

    partes = []
    if c["parte_deterministica"]:
        texto = c["parte_deterministica"](dados)
        print(texto)
        partes.append(texto)

    if c["requer_ia"]:
        if usar_ia and llm.configurada():
            print(f"\n[IA] gerando análise da camada com modelo '{llm.modelo()}' ...")
            user = contexto or (
                f"Execute agora a Camada {c['id']} ({c['nome']}), entregando todos os itens "
                "listados na missão em ordem numerada."
            )
            if partes:
                user += "\n\nPAINEL DETERMINÍSTICO JÁ CALCULADO (use como base, não recalcie):\n" + partes[0]
            mensagens = [
                {"role": "system", "content": sistema_da_camada(c)},
                {"role": "user", "content": user + "\n\nPARÂMETROS DE MISSÃO ATUAIS:\n" + resumo_para_prompt(dados)},
            ]
            try:
                resposta = llm.chat(mensagens)
                print("\n" + resposta)
                partes.append(resposta)
            except llm.ErroIA as e:
                print(f"\n[IA: ERRO] {e}")
        else:
            if not usar_ia:
                print("[IA] desativada por --sem-ia; entregando estrutura determinística.")
            elif not llm.configurada():
                print(llm.cartao_configuracao())
            estrutura = (
                f"Estrutura de entregáveis da Camada {c['id']} (geração por IA indisponível):\n"
                + "\n".join(f"  - {i}" for i in c["entregaveis"])
            )
            print("\n" + estrutura)
            partes.append(estrutura)

    corpo = "\n\n".join(partes) or "(sem conteúdo gerado)"
    caminho = _salvar_entrega(c, contexto, corpo)
    print(f"\n[ENTREGA] {caminho}")
    return caminho


def visao_geral(contexto="", usar_ia=True):
    print("=" * 70)
    print("VISÃO GERAL DO PLANO DE LANÇAMENTO — PIPELINE COMPLETO (1..6)")
    print("=" * 70)
    dados = carregar()
    caminhos = []
    for c in CAMADAS:
        caminhos.append(executar_camada(c["id"], contexto, usar_ia, dados))
    print("\n[PIPELINE CONCLUÍDO] entregáveis em " + ENTREGAVEIS)
    return caminhos


def menu():
    dados = carregar()
    print("=" * 70)
    print(" AGENTE GROWTH FMCG — ÁGUA SABORIZADA FITNESS | pipeline de 6 camadas")
    print("=" * 70)
    if llm.configurada():
        print(f"[IA: configurada] modelo '{llm.modelo()}' ativo.")
    else:
        print(llm.cartao_configuracao())
    print("\nParâmetros de missão atuais:")
    print(mostrar_texto(dados))
    print("\nComandos: 1..6 [contexto] | metas | status | geral | sair")
    while True:
        try:
            linha = input("\nagente> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[SAINDO]")
            break
        if not linha:
            continue
        if linha.lower() in ("sair", "exit", "q"):
            print("[SAINDO]")
            break
        if linha.lower() == "metas":
            print(mostrar_texto(carregar()))
            continue
        if linha.lower() == "status":
            print(calculos.painel_status(carregar()))
            continue
        if linha.lower() == "geral":
            visao_geral()
            continue
        partes = linha.split(maxsplit=1)
        if partes[0].isdigit() and 1 <= int(partes[0]) <= 6:
            contexto = partes[1] if len(partes) > 1 else ""
            executar_camada(int(partes[0]), contexto)
        else:
            print("Comando inválido. Use: 1..6 [contexto] | metas | status | geral | sair")


def main():
    llm.carregar_env(os.path.join(RAIZ, ".env"))

    p = argparse.ArgumentParser(
        description="Agente Growth FMCG — pipeline de 6 camadas para lançamento de água saborizada fitness.")
    p.add_argument("--camada", type=int, choices=range(1, 7), help="executar uma camada (1..6)")
    p.add_argument("--visao-geral", action="store_true", help="executar as 6 camadas em sequência")
    p.add_argument("--sem-ia", action="store_true", help="não chamar o modelo de IA")
    p.add_argument("--metas", action="store_true", help="mostrar parâmetros de missão")
    p.add_argument("--status", action="store_true", help="painel meta vs. real (camada 6)")
    p.add_argument("--definir", nargs="*", metavar="chave=valor",
                   help="definir parâmetros, ex.: unit.preco_venda=5.99")
    p.add_argument("--resultado", nargs="+", metavar="valor",
                   help="registrar resultado real: <mês> unidades=... investimento=...")
    p.add_argument("contexto", nargs="*", help="contexto livre para a camada")
    args = p.parse_args()

    try:
        if args.definir is not None:
            dados = carregar()
            alterados = aplicar(dados, args.definir)
            salvar(dados)
            print("[METAS] atualizado: " + ", ".join(alterados))
            print(mostrar_texto(dados))
            return

        if args.resultado:
            dados = carregar()
            mes, pares = args.resultado[0], args.resultado[1:]
            if not pares:
                p.error("--resultado requer pares chave=valor após o mês")
            aplicar_resultado(dados, int(mes), pares)
            salvar(dados)
            print(f"[RESULTADO] mês {mes} registrado.")
            print(calculos.painel_status(dados))
            return

        if args.metas:
            print(mostrar_texto(carregar()))
            return

        if args.status:
            print(calculos.painel_status(carregar()))
            return

        contexto = " ".join(args.contexto)

        if args.visao_geral:
            visao_geral(contexto, usar_ia=not args.sem_ia)
            return

        if args.camada:
            executar_camada(args.camada, contexto, usar_ia=not args.sem_ia)
            return

        if args.contexto:
            p.error("contexto informado sem --camada; use: python3 agente.py --camada 2 seu contexto")
        menu()
    except ValueError as e:
        print(f"[ERRO] {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INTERRUPIDO]")
        sys.exit(130)


if __name__ == "__main__":
    main()
