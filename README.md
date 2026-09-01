# Monitor Sísmico Global

Pipeline de dados end-to-end que coleta, combina e visualiza eventos sísmicos do Brasil e do mundo, atualizando automaticamente todos os dias sem intervenção manual.

Esse projeto nasceu de uma pergunta simples: dá pra montar, sozinho, um pipeline de dados completo, com fontes públicas reais, hospedagem em nuvem e atualização automática, do jeito que se faz em produção? A resposta foi sim, e este repositório é o resultado.

## O que o projeto faz

1. Busca eventos sísmicos em duas fontes públicas: **USGS** (catálogo global) e **Centro de Sismologia da USP** (cobertura mais fina no Brasil, incluindo eventos pequenos que não aparecem no catálogo global).
2. Normaliza os dois formatos de resposta (JSON e texto delimitado) para um schema único.
3. Identifica e marca eventos duplicados comparando proximidade de tempo e localização.
4. Carrega tudo num banco Postgres (Supabase), preservando o dado bruto e criando uma view já filtrada para consumo.
5. Roda sozinho, todo dia, via GitHub Actions.
6. Alimenta um dashboard no Power BI com mapa interativo, filtro de magnitude e período, e indicadores de atividade sísmica.

## Por que duas fontes, e por que filtros diferentes em cada uma

O USGS cobre dados sísmicos do mundo inteiro, mas inclui uma quantidade enorme de microssismos pouco relevantes fora de zonas de fronteira de placas. Já o Brasil, por ser uma região intraplaca de sismicidade baixa, tem nos eventos pequenos (magnitude entre 1 e 2) justamente o dado mais interessante. Filtrar isso teria descartado o diferencial do projeto.

Por isso: **magnitude mínima de 2.5 só no USGS**, reduzindo o ruído global, e a **USP sem filtro nenhum**, preservando a granularidade fina no Brasil.

## Arquitetura

```
USGS API + USP/FDSN    Python (coleta, normalização, deduplicação)
                       Postgres / Supabase (bronze + view gold)
                       GitHub Actions (agendamento diário)
                       Power BI (mapa, filtros, indicadores)
```

- **Ingestão**: `src/fetch_usgs.py` e `src/fetch_usp.py` — um módulo por fonte, cada um lidando com as particularidades do formato de resposta da respectiva API.
- **Orquestração local**: `src/ingest.py` — combina as duas fontes, aplica a deduplicação e dispara a carga no banco.
- **Persistência**: `src/load_postgres.py` — grava os eventos na tabela `bronze_eventos_sismicos`, com `ON CONFLICT DO NOTHING` garantindo que rodar o pipeline várias vezes não duplica dado.
- **Automação**: `.github/workflows/ingest.yml` — roda `ingest.py` todos os dias, buscando uma janela com sobreposição de 3 dias, protegendo proteção contra falhas ou atrasos numa execução isolada.

### Modelo de dados

A tabela `bronze_eventos_sismicos` guarda todos os dados, inclusive os eventos identificados como duplicata (marcados no campo `duplicata_de`, referenciando o evento "original"). A view `gold_eventos_sismicos` filtra essas duplicatas, e é a única fonte que o Power BI consome — mantendo o dado bruto sempre rastreável, sem nunca apagar nada.

## Stack

| Camada | Tecnologia |
|---|---|
| Coleta de dados | Python (`requests`) |
| Banco de dados | PostgreSQL (Supabase) |
| Automação | GitHub Actions (cron diário) |
| Visualização | Power BI Desktop |

## Como rodar localmente

```bash
git clone https://github.com/danillobarcelos/projeto-dados-sismicos.git
cd projeto-dados-sismicos
pip install -r requirements.txt
```

Copie `config_exemplo.py` para `src/config.py` e preencha com sua própria connection string do Postgres (não há a necessidade de commitar este arquivo, ele já está no `.gitignore`).

```bash
python src/ingest.py
```

## Automação (GitHub Actions)

O workflow em `.github/workflows/ingest.yml` roda todos os dias às 06:17 UTC, buscando os últimos 3 dias de eventos em cada fonte e carregando no Postgres. A credencial do banco fica guardada como Secret do repositórioe não está exposta no código.

## Autor

**Danillo Barcelos** — [github.com/danillobarcelos](https://github.com/danillobarcelos) — [linkedin.com/in/danillobarcelos](https://www.linkedin.com/in/danillobarcelos/) 

Projeto construído como parte da minha transição de carreira para Engenharia/Análise de Dados.