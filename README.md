# ⚖️ Tribunal — skill do Claude em português

Pare de perguntar pro Claude se a sua ideia é boa. **Coloque ela em julgamento.**

Uma acusação tenta provar que a ideia vai dar errado, uma defesa tenta provar que vai dar certo, um júri de 12 personagens bem brasileiros vota sem ver o voto um do outro, e um juiz te entrega o placar e **o que mudar**.

## Instalar (escolha um jeito)
**1. Pedindo pro Claude Code:** cole o link deste repositório e diga "instala essa skill".

**2. Manual:**
```
git clone https://github.com/ninjagaiden210/tribunal-skill.git
cp -r tribunal-skill/skills/tribunal ~/.claude/skills/
```

## Usar
```
/tribunal quero abrir uma agência de social media só pra dentistas
/tribunal --rapido vender curso de fotografia com celular por R$ 97
/tribunal --reel <cole aqui o roteiro do seu reel>
```
- `--rapido`: 6 jurados (gasta menos limite)
- `--reel`: júri de espectadores — julga se o vídeo prende e converte
- `--jurados N`: de 3 a 12

O processo completo fica salvo em `tribunal/VEREDITO-....md`.

## O júri
O cliente · o dono do comércio da esquina · o investidor · o concorrente · a mãe · o contador · o influencer do nicho · o cético do grupo da família · o primeiro funcionário · o cliente que já se decepcionou · o advogado · o usuário de 19 anos.

## Aviso
Cada jurado é uma chamada separada do Claude, então um julgamento completo consome uma parte boa do seu limite de uso. Use `--rapido` pra testar.

---
Feito por **Akira · Ghost Labs** 👻 · Licença MIT · Inspirado na ideia de "júri de agentes" que viralizou na comunidade do Claude.
