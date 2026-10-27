---
name: tribunal
description: Coloca uma ideia (de negócio, produto, conteúdo ou roteiro de reel) em julgamento no estilo tribunal brasileiro — acusação, defesa, júri de personagens e juiz — e entrega um veredito honesto com placar e o que mudar. Use quando o usuário digitar /tribunal, pedir para "julgar", "testar", "colocar à prova" ou receber uma opinião sincera sobre uma ideia, ou quando quiser saber se um roteiro de vídeo vai segurar.
---

# Tribunal — sua ideia no banco dos réus

O Claude tende a concordar com o usuário. Esta skill força o contrário: a ideia é julgada por lados opostos e por um júri de pessoas muito diferentes, cada um votando sozinho. O objetivo é uma resposta honesta e útil, não um "parabéns".

## Como chamar
- `/tribunal <ideia>` — julgamento completo (12 jurados)
- `/tribunal --rapido <ideia>` — 6 jurados (gasta bem menos limite)
- `/tribunal --reel <roteiro ou ideia de vídeo>` — modo criador: julga se o vídeo vai prender e converter
- `/tribunal --jurados N <ideia>` — júri de 3 a 12

Se o usuário não escreveu a ideia, peça em uma frase: "Qual ideia vai a julgamento? Me conta o que é, pra quem é e como ganha dinheiro (ou o roteiro do vídeo)."
Se faltar algo essencial (público, preço, canal), pergunte no máximo 2 coisas e siga. Nunca invente números como se fossem fatos; quando assumir algo, escreva "PRESSUPOSTO:".

## Regras do julgamento
1. **Todo mundo fala português do Brasil**, direto, sem enrolação.
2. **Ninguém vê o voto do outro.** Cada jurado é um subagente separado (use a ferramenta de subagentes/Task quando disponível; sem ela, gere cada voto de forma independente, sem reler os votos anteriores).
3. **Julga a ideia como foi descrita**, não uma versão melhorada dela.
4. **Proibido elogio vazio.** Todo argumento precisa de um motivo concreto.

## Etapas

### 1. Autos do processo
Escreva um resumo neutro de 5 linhas: o que é, pra quem, como ganha dinheiro/atenção, o que precisa ser verdade pra dar certo, e os pressupostos.

### 2. Acusação (Promotoria)
Um subagente monta o caso MAIS FORTE de que a ideia vai dar errado como está. Máx. 5 acusações, cada uma com: a acusação em 1 frase, a evidência/raciocínio, e a gravidade (leve / séria / fatal).

### 3. Defesa
Outro subagente, sem ver a acusação, monta o caso MAIS FORTE de que a ideia vai dar certo. Máx. 5 argumentos, com motivo concreto.

### 4. Réplica e tréplica
Cada lado recebe o texto do outro e responde em até 5 linhas: o que cai, o que se mantém.

### 5. Júri
Cada jurado recebe os autos + acusação + defesa + réplicas e responde SOZINHO:
- Voto: **CULPADO** (do jeito que está, não funciona) ou **INOCENTE** (pode seguir)
- Motivo em 1 frase, na voz do personagem
- A única coisa que mudaria o voto dele

**Júri padrão (12):**
1. **O cliente** — quem pagaria por isso. "Eu compraria? Por quanto?"
2. **O dono do comércio da esquina** — prático, sem paciência pra modinha
3. **O investidor** — margem, escala, risco
4. **O concorrente** — "como eu copio ou derrubo isso em um mês?"
5. **A mãe** — entende o que é em uma frase? confiaria?
6. **O contador** — conta fecha? imposto, custo escondido
7. **O influencer do nicho** — isso viraliza? dá pra falar sobre?
8. **O cético do grupo da família** — "isso é golpe?"
9. **O primeiro funcionário** — dá pra executar com o que existe hoje?
10. **O cliente que já se decepcionou** — o que vai dar errado na entrega?
11. **O advogado** — risco legal, LGPD, direitos, promessa exagerada
12. **O usuário de 19 anos** — usaria? acha chato?

**Júri `--rapido` (6):** cliente, investidor, concorrente, mãe, contador, cético do grupo da família.

**Júri `--reel` (troca o júri inteiro):**
1. Quem está só rolando o feed (para nos 2 primeiros segundos?)
2. O seguidor fiel
3. O cliente ideal do criador
4. O hater dos comentários
5. O editor de vídeo
6. O algoritmo (retenção, salvamento, envio)
7. O concorrente do nicho
8. Quem vê sem som
9. O especialista no assunto (tem erro?)
10. A pessoa que nunca ouviu falar do criador
11. O comprador cético
12. O amigo sincero
No modo reel, a acusação ataca gancho, ritmo, clareza, promessa e CTA; a defesa defende os mesmos pontos.

### 6. Juiz
Um último subagente lê tudo e decide:
- **Placar** (ex.: CULPADO por 8 a 4)
- **Acusações que se sustentaram** (as que mais de um jurado citou)
- **O que a defesa acertou**
- **Condições para absolvição:** de 3 a 5 mudanças concretas e em ordem de prioridade
- **Veredito final em 1 frase**

## Saída
Mostre na conversa o placar, o veredito e as condições para absolvição. Salve o processo completo em `tribunal/VEREDITO-<aaaa-mm-dd>-<tema-curto>.md` com: autos, acusação, defesa, réplicas, tabela do júri (jurado | voto | motivo | o que mudaria), sentença do juiz.
Não altere nenhum outro arquivo do projeto.

## Fecho
Termine com: "Quer rejulgar depois de aplicar as mudanças? É só mandar a versão nova com /tribunal."

---
Criado por Akira · Ghost Labs. Licença MIT.
