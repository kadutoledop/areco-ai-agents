# Arquitetura e decisões

Frontend HTML/CSS/JS → POST `/api/chat` → roteador Python → um dos agentes especializados → resposta com fontes. Financeiro: CSV + `Decimal` (sem SQL dinâmico). Ouvidoria: correspondência exata por protocolo, regras de referência. Interno: recuperação lexical de Markdown/FAQ, com origem citada. O classificador retorna `fora_de_escopo` quando não encontra domínio. Log JSONL de metadados, sem perguntas completas.

## Limitações
Este MVP **não** usa LLM, embeddings, ChromaDB ou PostgreSQL. A recuperação é lexical, não RAG semântico completo. O roteador pode falhar em linguagem indireta e consultas financeiras arbitrárias. Não há autenticação ou controle de acesso; usar apenas com dados sintéticos em ambiente de demonstração. Para produção: autenticação, autorização por documento, banco de dados, classificador LLM com saída estruturada, busca vetorial, observabilidade, testes de regressão e proteção contra prompt injection.
