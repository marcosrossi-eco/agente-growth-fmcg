# Agente Growth FMCG — Água Saborizada Fitness

Agente de linha de comando com pipeline de **6 camadas** para gerenciar o ciclo de vida completo do
lançamento de uma água saborizada fitness (suplemento alimentar): de levantamento de dados a
monitoramento de metas.

## Camadas

| # | Camada | O que entrega |
|---|--------|---------------|
| 1 | Levantamento de Dados | dores do iniciante, personas, mapa de concorrência |
| 2 | Conteúdo & Divulgação | pilares, headlines, roteiros, anúncios, WhatsApp |
| 3 | Ativação de Campanhas | plano BTL em academias, kit boas-vindas, desafio 15/30 dias |
| 4 | Retenção & Otimização | régua D0/D7/D21, assinatura, cross-sell de sabores |
| 5 | Analytics, ROI & Previsibilidade | cálculos de margem, ROAS de equilíbrio, ROI, NPS/CSAT |
| 6 | Alinhamento de Metas & KPIs | painel meta vs. real, CAC, cobrança de metas |

As camadas 5 e 6 são **determinísticas** (matemática em código, funcionam sem IA); as camadas 1–4
usam o modelo de IA quando a chave está configurada.

## Requisitos

- Python 3.10+ (sem dependências externas)
- Chave da API compatível com OpenAI: https://freebuff.com/account/api

## Configuração

```bash
cp .env.example .env      # cole sua chave: OPENAI_API_KEY=...
```

Enquanto a chave não existir, o agente roda em modo determinístico/estrutural (cálculos + estrutura
de entregáveis), sem fingir saída de IA.

## Uso

```bash
python3 agente.py                       # menu interativo
python3 agente.py --camada 5            # executa a camada 5 (ROI/ROAS)
python3 agente.py --camada 3 "foco BTL" # camada com contexto livre
python3 agente.py --visao-geral         # executa 1..6 em sequência
python3 agente.py --status              # painel meta vs. real

# Parâmetros de missão (preço, custo, orçamento, foco, metas):
python3 agente.py --metas
python3 agente.py --definir unit.preco_venda=5.99 investimento.foco=btl

# Alimentar o painel com resultados reais:
python3 agente.py --resultado 1 unidades=3800 investimento=6100 novos_clientes=405 pontos_venda=22
python3 agente.py --resultado 1 nps.promotores=60 nps.neutros=25 nps.detratores=15
python3 agente.py --resultado 1 csat.soma=432 csat.respostas=96
```

No menu interativo: digite `1`..`6` (com contexto opcional), `metas`, `status`, `geral` ou `sair`.

## Arquivos

- `agente.py` — entrypoint CLI e orquestração
- `core/pipeline.py` — definição das 6 camadas (missão, prompts, entregáveis)
- `core/calculos.py` — margem, ROAS de equilíbrio, ROI, CAC, NPS/CSAT, cobrança de metas
- `core/llm.py` — cliente da API compatível com OpenAI (Freebuff)
- `core/metas.py` — parâmetros de missão e registro de resultados
- `metas.json` — preço, custo, orçamento, foco, metas por mês e resultados reais
- `entregaveis/` — um `.markdown` por execução de camada (gerado automaticamente)
