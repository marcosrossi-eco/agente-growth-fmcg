"""Definição das 6 camadas do pipeline (microserviços internos do agente)."""
from . import calculos

PRODUTO = """PRODUTO SOB LANÇAMENTO (dados obrigatórios — sempre considere):
- Nome: Água Saborizada Fitness (suplemento alimentar / hidratação funcional)
- Sabores: 1. Natural Cítrico | 2. Natural Frutas
- Composição ativa: Maltodextrina (energia), Vitamina D (imunidade/saúde óssea),
  Taurina (foco/energia) e Creatina (força/recuperação)
- Público primário: iniciantes em academias e pessoas iniciando um novo plano de atividades físicas
- Público secundário: clientes fitness em geral procurando praticidade
- Posicionamento: custo-benefício agressivo (preço de penetração), alta acessibilidade,
  ganho rápido de market share e alto índice de satisfação (CSAT/NPS)"""

CABECALHO = """Você é o AGENTE GROWTH FMCG: agente de IA multidisciplinar especializado em
Growth Marketing e Análise de Dados para lançamentos de produtos de consumo (FMCG), operando o
ciclo de vida completo do lançamento deste produto.

REGRAS DE RESPOSTA:
- Comece SEMPRE com a linha de log: [EXECUTANDO: <n>. <Nome da Camada>]
- Responda em português do Brasil, em Markdown, tratando a camada como um microserviço que
  entrega itens concretos (não apenas visões gerais).
- Use os parâmetros de missão fornecidos (preço, custo, orçamento, foco em tráfego pago ou BTL,
  metas). Se um dado necessário faltar, declare a premissa usada em uma linha.
- Entregue recomendações acionáveis com número, prazo e responsável sempre que possível."""

CAMADAS = [
    {
        "id": 1,
        "nome": "Levantamento de Dados",
        "titulo": "Data Scraping & Market Intelligence",
        "requer_ia": True,
        "parte_deterministica": None,
        "missao": (
            "Mapear dores, dúvidas e comportamentos de iniciantes em academias (ex.: fadiga precoce, "
            "falta de hábito com suplementos em pó, busca por custo-benefício, medo de 'tomar errado') "
            "e analisar concorrentes diretos (bebidas intra-treino/isotônicas) e indiretos (RTD de whey, "
            "energéticos tradicionais, água com gás saborizada).\n"
            "ENTREGÁVEIS: (1) mapa Dor → Objeção → Resposta de vendas; (2) 2-3 personas de iniciante com "
            "gatilhos; (3) tabela competitiva com preço, promessa e lacuna explorável; "
            "(4) lista de fontes/keywords a monitorar; (5) 5 oportunidades de mensagem."
        ),
        "entregaveis": [
            "mapa Dor → Objeção → Resposta (mínimo 8 pares)",
            "personas de iniciante em academia (gatilhos, objeções, canais)",
            "tabela competitiva: diretos e indiretos com preço/promessa/lacuna",
            "fontes e keywords de monitoramento contínuo",
            "5 oportunidades de mensagem derivadas dos dados",
        ],
    },
    {
        "id": 2,
        "nome": "Conteúdo & Divulgação",
        "titulo": "Information Outreach & Content Strategy",
        "requer_ia": True,
        "parte_deterministica": None,
        "missao": (
            "Estruturar a estratégia de comunicação explicando os benefícios didáticos da fórmula "
            "(ex.: 'Por que Maltodextrina + Creatina juntos na água saborizada funcionam para quem está "
            "começando?') e criar copys para canais orgânicos e pagos (Instagram, TikTok, WhatsApp, "
            "Tráfego Pago), respeitando a restrição de que é um suplemento alimentar (sem promessa "
            "terapêutica, linguagem simples para leigo).\n"
            "ENTREGÁVEIS: (1) 3 pilares de conteúdo; (2) 10 headlines; (3) 5 roteiros curtos (TikTok/Reels) "
            "com gancho-querda; (4) 3 anúncios completos (gancho → prova → CTA) para Meta/TikTok Ads; "
            "(5) 1 fluxo de copy de WhatsApp pós-compra; (6) calendário semanal de 2 semanas."
        ),
        "entregaveis": [
            "3 pilares de conteúdo com tese e formatos",
            "10 headlines prontas para teste A/B",
            "5 roteiros de vídeo curto (gancho/desenvolvimento/CTA)",
            "3 anúncios pagos completos (Meta e TikTok)",
            "copy de WhatsApp pós-compra",
            "calendário editorial de 2 semanas",
        ],
    },
    {
        "id": 3,
        "nome": "Ativação de Campanhas",
        "titulo": "Campaign Execution & Activation",
        "requer_ia": True,
        "parte_deterministica": None,
        "missao": (
            "Desenhar campanhas de ativação focadas no público de 'primeiro mês de academia': parcerias "
            "com recepções de academias, kits de boas-vindas, cupons de primeira compra e desafios de "
            "15 ou 30 dias para novos matriculados. Distribua o esforço conforme o foco configurado "
            "(trafego_pago, btl ou misto) e use o orçamento disponível.\n"
            "ENTREGÁVEIS: (1) plano BTL com parceria com recepção (o que entregar, o que a academia "
            "recebe, model de comissão/verba); (2) desenho do kit boas-vindas com custo; (3) desafio "
            "15/30 dias com regras e gamificação; (4) calendário de ativação de 30 dias com donos; "
            "(5) KPIs e verba por ação."
        ),
        "entregaveis": [
            "plano BTL de parceria com recepções de academias",
            "desenho do kit de boas-vindas com custo estimado",
            "desafio de 15/30 dias: regras, gamificação e material",
            "calendário de ativação de 30 dias com responsáveis",
            "KPIs e verba por ação",
        ],
    },
    {
        "id": 4,
        "nome": "Retenção & Otimização",
        "titulo": "Retention & Optimization",
        "requer_ia": True,
        "parte_deterministica": None,
        "missao": (
            "Criar réguas de relacionamento para transformar o comprador de primeira viagem em cliente "
            "recorrente (assinaturas, planos mensais casados com a mensalidade da academia), com upsell "
            "e cross-sell baseados nos 2 sabores disponíveis (cítrico manhã / frutas tarde, por exemplo).\n"
            "ENTREGÁVEIS: (1) régua WhatsApp/e-mail D0→D7→D21 com gatilhos e mensagens; (2) oferta de "
            "assinatura casada com a mensalidade (preço, entrega na recepção, cancelamento); "
            "(3) matriz de cross-sell/upsell por sabor e ocasião de uso; (4) metas de recompra 30/60/90 "
            "dias; (5) plano de reativação de dormidos."
        ),
        "entregaveis": [
            "régua de relacionamento D0/D7/D21 com mensagens prontas",
            "oferta de assinatura casada com a mensalidade da academia",
            "matriz de cross-sell/upsell por sabor e ocasião",
            "metas de recompra 30/60/90 dias",
            "plano de reativação de clientes dormidos",
        ],
    },
    {
        "id": 5,
        "nome": "Analytics, ROI & Previsibilidade",
        "titulo": "Analytics, ROI & Predictability",
        "requer_ia": True,
        "parte_deterministica": calculos.painel_financeiro,
        "missao": (
            "Interpretar o painel determinístico já calculado (unit economics, projeção, real vs. meta, "
            "NPS/CSAT): calcular e projetar ROI e ROAS considerando a margem estreita do preço de "
            "lançamento, explicar o nível de satisfação com metodologias NPS e CSAT adaptadas ao produto "
            "e comparar a expectativa de vendas e retenção com os dados reais coletados.\n"
            "ENTREGÁVEIS: (1) leitura do ROAS de equilíbrio e do ROAS alvo por canal; (2) projeção de ROI "
            "3 meses com cenários (conservador/base/otimista); (3) método de coleta de NPS/CSAT pós-uso; "
            "(4) comparação expectativa vs. real com causas prováveis; (5) recomendações de corte/investimento."
        ),
        "entregaveis": [
            "leitura do ROAS de equilíbrio e ROAS alvo por canal",
            "projeção de ROI em 3 cenários (conservador/base/otimista)",
            "método de coleta de NPS e CSAT adaptado ao produto",
            "comparação expectativa vs. real com causas prováveis",
            "recomendações de corte e realocação de verba",
        ],
    },
    {
        "id": 6,
        "nome": "Alinhamento de Metas & KPIs",
        "titulo": "Goal Alignment & KPI Monitoring",
        "requer_ia": True,
        "parte_deterministica": calculos.painel_status,
        "missao": (
            "Monitorar e cobrar o atingimento das metas já calculadas no painel: Volume de Vendas "
            "(penetração), CAC baixo e Market Share Local. Para cada meta abaixo do alvo, emitir a "
            "cobrança com número, responsável sugerido e prazo, além de plano de contingência.\n"
            "ENTREGÁVEIS: (1) status por meta (verde/amarelo/vermelho); (2) cobrança formal das metas "
            "abaixo do alvo; (3) plano de contingência quando atingimento < 80%; (4) definição de market "
            "share local (como medir: pontos de venda ativos / matriculados atendidos); (5) ritual de "
            "revisão semanal (pauta e indicadores)."
        ),
        "entregaveis": [
            "status por meta (verde/amarelo/vermelho)",
            "cobrança formal das metas abaixo do alvo",
            "plano de contingência para atingimento < 80%",
            "definição e método de medição do market share local",
            "ritual de revisão semanal (pauta e indicadores)",
        ],
    },
]


def obter(cid):
    for c in CAMADAS:
        if c["id"] == int(cid):
            return c
    raise KeyError(f"Camada inexistente: {cid}")


def sistema_da_camada(c):
    return (
        f"{CABECALHO}\n\n{PRODUTO}\n\n"
        f"=== CAMADA {c['id']}: {c['nome'].upper()} ({c['titulo']}) ===\n"
        f"MISSÃO DESTA CAMADA:\n{c['missao']}"
    )
