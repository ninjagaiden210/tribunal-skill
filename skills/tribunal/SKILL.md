---
name: tribunal
description: Coloca uma ideia (de negócio, produto, conteúdo ou roteiro de reel) em julgamento no estilo tribunal brasileiro — acusação, defesa, júri de personagens e juiz — e entrega um veredito honesto com placar e o que mudar. Use quando o usuário digitar /tribunal, pedir para "julgar", "testar", "colocar à prova" ou receber uma opinião sincera sobre uma ideia, ou quando quiser saber se um roteiro de vídeo vai segurar.
---

# Tribunal — sua ideia no banco dos réus

O Claude tende a concordar com o usuário. Esta skill força o contrário: a ideia é julgada por lados opostos e por um júri de pessoas muito diferentes, cada um votando sozinho.

**Você (o Claude principal) só coordena.** Você não acusa, não defende, não vota, não conta votos e não escreve a sentença. Quem faz isso são subagentes separados. Quem confere os formatos, conta os votos e monta o veredito é o script `tribunal.py`, que fica na mesma pasta deste SKILL.md. O placar que vale é sempre o que o script imprimir.

## Como chamar
- `/tribunal <ideia>` — julgamento completo (12 jurados)
- `/tribunal --rapido <ideia>` — 6 jurados (gasta bem menos limite)
- `/tribunal --reel <roteiro ou ideia de vídeo>` — modo criador: júri de espectadores julga se o vídeo prende e converte
- `/tribunal --jurados N <ideia>` — júri de 3 a 12 (sorteados; `--semente S` repete o mesmo sorteio)

Se o usuário não escreveu a ideia, peça em uma frase: "Qual ideia vai a julgamento? Me conta o que é, pra quem é e como ganha dinheiro (ou o roteiro do vídeo)."
Se faltar algo essencial (público, preço, canal), pergunte no máximo 2 coisas e siga.

Um julgamento completo dispara 17 subagentes (2 aberturas, 2 réplicas, 12 jurados, 1 juiz) e o `--rapido` dispara 11. Avise o usuário disso uma vez, numa linha, antes de começar o completo.

## Antes de tudo: o Python
Rode os comandos a partir da pasta do projeto do usuário, chamando o script pelo caminho completo:
`python "<pasta desta skill>/tribunal.py" <comando>`
Descubra o comando do Python uma vez: tente `python3 --version`, depois `python --version` e depois `py --version` (Windows), e use o primeiro que responder Python 3. Se nenhum funcionar, diga ao usuário que a skill precisa do Python 3 (python.org) e pare.

## Passo a passo (siga na ordem, sem pular)

**1. Abrir**
`tribunal.py abrir --tema "<tema curto>" [--modo padrao|rapido|reel] [--jurados N] [--semente S]`

**2. Autos.** Escreva no `autos.md` que o script indicar um resumo neutro de 5 linhas: o que é, pra quem, como ganha dinheiro ou atenção, o que precisa ser verdade pra dar certo, e os pressupostos (marque cada um com PRESSUPOSTO:). Copie também, abaixo do resumo, a ideia ou o roteiro do usuário exatamente como ele escreveu. Julga-se a ideia como foi descrita, não uma versão melhorada.

**3. Para cada fase, na ordem `abertura` → `replica` → `juri` → `juiz`:**
1. `tribunal.py briefing <fase>`: o script cria um brief por agente e lista brief e saída de cada um.
2. Dispare um subagente por brief, todos em paralelo, com o prompt: `Leia o arquivo <brief> e siga exatamente o que ele diz.` Não passe mais nenhum contexto: tudo o que o agente precisa está no brief. Se não houver ferramenta de subagentes, pare e diga ao usuário que esta skill precisa do Claude Code.
3. `tribunal.py checar <fase>`
   - Se aprovar, siga para a próxima fase.
   - Se reprovar, dispare de novo **só** os agentes que o script listar, com o mesmo brief. Nunca corrija nem escreva você mesmo o arquivo de um agente. Depois de 2 tentativas reprovadas do mesmo agente, pare e mostre o erro ao usuário.
4. Depois de `checar juri` aprovado, rode `tribunal.py contar` antes de `briefing juiz`.

Entre as fases, avise o usuário em uma linha do que está acontecendo (por exemplo: "Os 12 jurados estão votando, cada um sem ver o voto dos outros.").

**4. Veredito**
`tribunal.py veredito`: o script monta `tribunal/VEREDITO-<data>-<tema>.md` e imprime o resumo. Mostre ao usuário o resumo do jeito que o script imprimiu (placar, veredito e condições para absolvição). Você pode acrescentar 1 ou 2 linhas de contexto, mas nunca mude o placar, o resultado nem as condições.

## Regras
- Tudo em português do Brasil, direto.
- Não altere nenhum arquivo do projeto além do que fica dentro de `tribunal/`.
- Se o usuário pedir para "ajustar" o resultado, explique que o placar é do júri. O caminho é aplicar as condições e rejulgar.

## Fecho
Termine com: "Quer rejulgar depois de aplicar as mudanças? É só mandar a versão nova com /tribunal."

---
Criado por Akira · Ghost Labs. Inspirada no /court de Alex Chen (@nocodealex). Licença MIT.
