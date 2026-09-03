"""Servico de foto de perfil enviada pelo proprio usuario (upload real).

Isolado num pacote proprio - e nao espalhado por app/models, app/api,
app/repositories como o resto da aplicacao - porque lida com um tipo de
dado bem diferente (arquivo binario em disco) e pode um dia trocar de
storage (S3 etc.) sem tocar em nada fora daqui.

Complementa, e nao substitui, o avatar de icone em app/models/avatar.py:
aquele foi desenhado de proposito para nao exigir foto real (privacidade
e reducao de ansiedade social). Aqui o aluno/usuario que preferir pode
enviar uma foto propria."""
