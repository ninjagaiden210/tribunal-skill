# ⚖️ Tribunal — skill do Claude

Pare de perguntar pro Claude se a sua ideia é boa. **Coloque ela em julgamento.**

Uma acusação tenta provar que a ideia vai dar errado, uma defesa tenta provar que vai dar certo, um júri de 12 personagens bem brasileiros vota sem ver o voto um do outro, e um juiz te entrega o placar e **o que mudar**.

## Precisa de
- Claude Code
- Python 3 ([python.org](https://www.python.org/downloads/)), que confere os formatos e conta os votos

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

## À prova de erro
O Claude só coordena. Quem acusa, defende, vota e julga são agentes separados, e nenhum jurado vê o voto do outro.
O script `tribunal.py` faz a parte que não pode errar:
- monta a tarefa de cada agente
- confere se cada resposta veio no formato certo e manda refazer a que vier errada
- conta os votos (empate = a favor do réu)
- barra o juiz se ele citar um placar diferente do contado
- monta o arquivo do veredito

Testes: `python -m unittest discover -s tests`

## O júri
O cliente · o dono do comércio da esquina · o investidor · o concorrente · a mãe · o contador · o influencer do nicho · o cético do grupo da família · o primeiro funcionário · o cliente que já se decepcionou · o advogado · o usuário de 19 anos.

## Aviso
Cada agente é uma chamada separada do Claude (17 no completo, 11 no `--rapido`), então um julgamento completo consome uma parte boa do seu limite de uso. Use `--rapido` pra testar.

O júri é formado por modelos de linguagem: é uma segunda opinião estruturada, não aconselhamento jurídico, financeiro ou profissional.

---
Feito por **Akira · Ghost Labs** 👻 · Licença MIT · Inspirada no [/court](https://github.com/alexyc9381/court-skill) de Alex Chen (@nocodealex).
