# Registro de desenvolvimento com IA

## Sessão inicial — 23/10/2026
- **Solicitação:** construir MVP do desafio técnico Areco a partir do pacote `arquivos.rar`, com FastAPI, frontend, orquestrador, agentes, Docker, testes e documentação.
- **Ferramenta:** ChatGPT (assistência de geração de código e planejamento).
- **Proposta aceita:** implementação local determinística para respostas verificáveis, sem exigir chave de API; roteamento por regras; consulta às políticas por pontuação lexical e FAQ; agregações com `Decimal`; protocolos por correspondência exata.
- **Decisão e trade-off:** reduzir dependências e tempo de setup; não afirmar que há LLM/RAG semântico vetorial implementado. A recuperação interna é lexical e documental, uma aproximação de recuperação fundamentada.
- **Dados:** pacote sintético da Aurora Serviços Digitais S.A.; arquivo MATLAB preservado, mas fora do escopo dos agentes.
- **Limitações:** classificador baseado em palavras-chave, perguntas financeiras complexas fora do conjunto coberto e sem geração natural por LLM.
- **Validação:** executar `pytest -q` e testar `/api/health` e `/api/chat`; anotar os resultados efetivamente obtidos antes da entrega.
- **Histórico completo:** anexar exportação da conversa de desenvolvimento quando possível; este registro é resumo, não substitui exportação.
