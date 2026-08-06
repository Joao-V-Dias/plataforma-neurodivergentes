"""Camada de integracao com o provedor de LLM (Groq) - o motor de IA
adaptativa da Parte 6.

Isolamento deliberado: nada fora deste pacote e de
app/services/dica_service.py sabe que existe um provedor de IA por tras
das dicas. Nenhum router importa `app.ai` diretamente - so o service, que
aplica as regras de negocio (progressao de nivel, guardrails, auditoria)
antes de qualquer chamada e depois de qualquer resposta."""
