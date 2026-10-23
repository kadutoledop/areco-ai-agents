# Areco — Assistente Multiagente (MVP)

Protótipo funcional para o desafio técnico. **Não requer chave de API**. Utiliza os dados sintéticos fornecidos, com três agentes e roteamento por regras. Consulte `docs/architecture.md` para limitações (sem LLM nem busca vetorial).

## Executar com Docker

```bash
docker compose up --build
```

Acesse `http://localhost:8000`. API documentada em `http://localhost:8000/docs`.

## Executar sem Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Testes

```bash
pytest -q
```

## Exemplos de perguntas

- Como solicito férias?
- Qual o prazo para pedir reembolso?
- Quais são as aprovações para uma compra de R$ 12.000?
- Quanto foi gasto em despesas pagas no período de janeiro a março de 2025?
- Qual departamento tem maior orçamento em janeiro de 2026?
- Qual o status do protocolo OUV-0002?
- Existe o protocolo OUV-9999?

## Arquivos

- `app/main.py`: API, roteamento e agentes.
- `frontend/`: interface.
- `data/`: dados sintéticos fornecidos no desafio, inclusive fixtures de avaliação.
- `logs/interactions.jsonl`: criado durante consultas, com metadados e sem pergunta completa.
- `AGENTS.md`, `docs/development_log.md`: orientações e decisões de desenvolvimento com IA.
- `docs/architecture.md`: arquitetura, limitações e melhorias.

## Requisição de exemplo

```bash
curl -X POST http://localhost:8000/api/chat -H 'Content-Type: application/json' -d '{"question":"Como solicito férias?"}'
```

## Entrega

Publicar no GitHub com `git init`, `git add .`, `git commit -m "MVP multiagente"` e `git push` para um repositório criado pelo candidato. Exportar também o histórico da conversa com IA, quando possível, removendo informações sensíveis. Não publicar `.env` nem logs privados.
