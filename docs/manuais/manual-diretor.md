# Manual do Diretor

Este manual explica, em linguagem simples, o que você pode fazer na
Plataforma Adaptativa como **Diretor** — o papel de maior privilégio na
sua instituição.

## O que você pode fazer

Como Diretor, você pode:

- Criar contas de **Coordenador**, **Professor** e **Aluno**
- Aprovar alunos que se cadastraram sozinhos
- Ver todas as turmas e todos os problemas da sua instituição
- Ver a lista completa de usuários da instituição

## 1. Entrando na plataforma

Acesse o endereço da plataforma no navegador e faça login com o e-mail e
senha da sua conta de Diretor.

> **Sua conta de Diretor não se cadastra sozinha.** Ela é criada por um
> comando de instalação (`scripts/seed_diretor.py`) executado por quem
> configurou a plataforma para a sua instituição — normalmente uma única
> vez, no começo. Se você ainda não tem uma senha, peça para quem cuida
> da instalação técnica.

## 2. Criando a conta de um Coordenador

1. No menu à esquerda, clique em **Usuários**.
2. Clique no botão **Novo usuário**, no canto superior direito.
3. Preencha:
   - **Nome completo**
   - **E-mail** (será o login da pessoa)
   - **Senha temporária** (peça para a pessoa trocar no primeiro acesso)
   - **Papel**: escolha **Coordenador**
4. Clique em **Criar usuário**. A conta já nasce ativa — a pessoa pode
   entrar imediatamente com o e-mail e a senha temporária.

O mesmo processo serve para criar Professores e Alunos diretamente,
trocando o campo **Papel**.

## 3. Aprovando um aluno que se cadastrou sozinho

Alunos também podem criar a própria conta pela tela de login ("Criar
conta de aluno"). Por segurança, essas contas **nascem inativas** e
precisam ser aprovadas por um Diretor, Coordenador ou Professor antes do
aluno conseguir entrar.

1. Vá em **Usuários**.
2. Alunos aguardando aprovação aparecem com a etiqueta amarela
   **"Aguardando aprovação"**.
3. Clique no botão **Aprovar** na linha da pessoa.

Pronto — o aluno já consegue fazer login.

## 4. Acompanhando a instituição

Na tela **Início** (a primeira tela depois do login), você vê um resumo:
quantas turmas, problemas e usuários existem na sua instituição. Cada
número é um atalho — clique para ver a lista completa.

## 5. Sua própria acessibilidade

O menu **Acessibilidade** (para qualquer papel, inclusive o seu) permite
ajustar tamanho de fonte, alto contraste, redução de animações e leitura
em voz alta. Essas preferências são suas, pessoais, e valem em qualquer
computador em que você entrar.
