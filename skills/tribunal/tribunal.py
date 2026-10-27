#!/usr/bin/env python3
"""Tribunal: a parte burocrática do julgamento.

O Claude coordena. Este script monta a tarefa de cada agente, confere se cada
resposta veio no formato certo, conta os votos e escreve o veredito.
Ninguém além do script mexe no placar.

Uso (rode a partir da pasta do projeto):
  python tribunal.py abrir --tema "hamburgueria delivery" [--modo padrao|rapido|reel] [--jurados N] [--semente S]
  python tribunal.py briefing abertura|replica|juri|juiz
  python tribunal.py checar   abertura|replica|juri|juiz
  python tribunal.py contar
  python tribunal.py veredito
  python tribunal.py status

Só usa a biblioteca padrão do Python 3.8+.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = Path("tribunal")
PROCESSOS = RAIZ / ".processo"
ATUAL = PROCESSOS / "ATUAL"
CREDITO = "Criado por Akira · Ghost Labs — github.com/ninjagaiden210/tribunal-skill"

FASES = ["abertura", "replica", "juri", "juiz"]
GRAVIDADES = {"leve", "seria", "fatal"}


class Falha(Exception):
    """Erro que o Claude precisa corrigir antes de seguir."""


# ---------------------------------------------------------------- utilidades

def _saida_utf8() -> None:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def sem_acento(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def slugify(texto: str) -> str:
    base = sem_acento(texto).lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return (base or "ideia")[:40].strip("-")


def ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


def escrever(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def linhas_cheias(texto: str) -> list[str]:
    return [l for l in texto.splitlines() if l.strip()]


def limpar_valor(valor: str) -> str:
    return valor.replace("*", "").replace("_", "").strip()


def carregar_jurados() -> dict:
    return json.loads((AQUI / "jurados.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- processo

class Processo:
    def __init__(self, pasta: Path):
        self.pasta = pasta
        self.dados = json.loads(ler(pasta / "processo.json"))

    # caminhos
    @property
    def autos(self) -> Path:
        return self.pasta / "autos.md"

    def brief(self, nome: str) -> Path:
        return self.pasta / "briefs" / f"{nome}.md"

    def saida(self, nome: str) -> Path:
        return self.pasta / "saidas" / f"{nome}.md"

    @property
    def placar_json(self) -> Path:
        return self.pasta / "placar.json"

    def salvar(self) -> None:
        escrever(self.pasta / "processo.json", json.dumps(self.dados, ensure_ascii=False, indent=2))

    @property
    def jurados(self) -> list[dict]:
        return self.dados["jurados"]

    @classmethod
    def atual(cls) -> "Processo":
        if not ATUAL.exists():
            raise Falha("Nenhum julgamento aberto. Rode primeiro: python tribunal.py abrir --tema \"...\"")
        pasta = PROCESSOS / ler(ATUAL).strip()
        if not (pasta / "processo.json").exists():
            raise Falha(f"Processo não encontrado em {pasta}. Abra um novo julgamento.")
        return cls(pasta)


def escolher_jurados(modo: str, quantidade: int | None, semente: int) -> list[dict]:
    tabela = carregar_jurados()
    if modo == "reel":
        base = tabela["reel"]
    else:
        base = tabela["padrao"]
    if modo == "rapido" and quantidade is None:
        ids = tabela["rapido"]
        return [j for j in base if j["id"] in ids]
    if quantidade is None:
        return list(base)
    if not 3 <= quantidade <= 12:
        raise Falha("O júri precisa ter de 3 a 12 jurados.")
    sorteados = set(j["id"] for j in random.Random(semente).sample(base, quantidade))
    return [j for j in base if j["id"] in sorteados]


def cmd_abrir(args) -> None:
    data = _dt.date.today().isoformat()
    slug = slugify(args.tema)
    nome = f"{data}-{slug}"
    pasta = PROCESSOS / nome
    n = 2
    while pasta.exists():
        nome = f"{data}-{slug}-{n}"
        pasta = PROCESSOS / nome
        n += 1
    jurados = escolher_jurados(args.modo, args.jurados, args.semente)
    dados = {
        "tema": args.tema,
        "slug": slug,
        "data": data,
        "modo": args.modo,
        "semente": args.semente,
        "jurados": jurados,
        "fases_ok": [],
    }
    (pasta / "briefs").mkdir(parents=True)
    (pasta / "saidas").mkdir(parents=True)
    escrever(pasta / "processo.json", json.dumps(dados, ensure_ascii=False, indent=2))
    escrever(ATUAL, nome)
    print(f"Julgamento aberto: {pasta}")
    print(f"Modo: {args.modo} · {len(jurados)} jurados: " + ", ".join(j["nome"] for j in jurados))
    print()
    print(f"PRÓXIMO PASSO: escreva os autos em {pasta / 'autos.md'} e depois rode: briefing abertura")


# ---------------------------------------------------------------- briefs

REGRAS_GERAIS = (
    "Regras: escreva em português do Brasil, direto. Julgue a ideia exatamente como está nos autos, "
    "não uma versão melhorada. Nada de elogio vazio: todo ponto precisa de um motivo concreto. "
    "Não invente números como se fossem fatos; quando assumir algo, escreva PRESSUPOSTO:. "
    "Não leia nenhum arquivo além dos indicados aqui. Não mexa em nenhum outro arquivo."
)

FOCO_REEL = (
    "Este é um julgamento de vídeo curto (reel). Avalie gancho, ritmo, clareza, promessa e CTA."
)


def _foco(p: Processo) -> str:
    return FOCO_REEL + "\n\n" if p.dados["modo"] == "reel" else ""


def brief_acusacao(p: Processo) -> str:
    return f"""# Você é a ACUSAÇÃO (Promotoria)

{_foco(p)}Leia os autos em: {p.autos}

Monte o caso MAIS FORTE e honesto de que a ideia vai dar errado do jeito que está.
De 1 a 5 acusações. {REGRAS_GERAIS}

Escreva sua resposta no arquivo: {p.saida('acusacao')}
Use EXATAMENTE este formato (repita o bloco para cada acusação):

## Acusação 1
ACUSAÇÃO: <a acusação em 1 frase>
EVIDÊNCIA: <o raciocínio ou a evidência>
GRAVIDADE: <leve | séria | fatal>

Depois de salvar, responda só: pronto.
"""


def brief_defesa(p: Processo) -> str:
    return f"""# Você é a DEFESA

{_foco(p)}Leia os autos em: {p.autos}

Monte o caso MAIS FORTE e honesto de que a ideia vai dar certo. Você não sabe o que a acusação disse.
De 1 a 5 argumentos. {REGRAS_GERAIS}

Escreva sua resposta no arquivo: {p.saida('defesa')}
Use EXATAMENTE este formato (repita o bloco para cada argumento):

## Argumento 1
ARGUMENTO: <o argumento em 1 frase>
MOTIVO: <por que se sustenta>

Depois de salvar, responda só: pronto.
"""


def brief_replica(p: Processo, lado: str) -> str:
    if lado == "acusacao":
        titulo, leia, saida = "a ACUSAÇÃO, na réplica", "defesa", "replica-acusacao"
        sua = "acusacao"
    else:
        titulo, leia, saida = "a DEFESA, na tréplica", "acusacao", "treplica-defesa"
        sua = "defesa"
    return f"""# Você é {titulo}

Leia os autos em: {p.autos}
Seu texto original: {p.saida(sua)}
O texto do outro lado: {p.saida(leia)}

Responda ao outro lado em NO MÁXIMO 5 linhas: o que cai, o que se mantém. {REGRAS_GERAIS}

Escreva no arquivo: {p.saida(saida)}
Depois de salvar, responda só: pronto.
"""


def brief_jurado(p: Processo, jurado: dict) -> str:
    return f"""# Você é um JURADO: {jurado['nome']}

Seu olhar: {jurado['olhar']}
{_foco(p)}
Leia, nesta ordem:
- Autos: {p.autos}
- Acusação: {p.saida('acusacao')}
- Defesa: {p.saida('defesa')}
- Réplica da acusação: {p.saida('replica-acusacao')}
- Tréplica da defesa: {p.saida('treplica-defesa')}

Vote SOZINHO. Não leia o voto de nenhum outro jurado. {REGRAS_GERAIS}
CULPADO = do jeito que está, não funciona. INOCENTE = pode seguir.

Escreva no arquivo: {p.saida('jurado-' + jurado['id'])}
Use EXATAMENTE estas 3 linhas, nada mais:

VOTO: <CULPADO ou INOCENTE>
MOTIVO: <1 frase, na voz do personagem>
MUDARIA: <a única coisa que mudaria o seu voto>

Depois de salvar, responda só: pronto.
"""


def brief_juiz(p: Processo, placar: dict) -> str:
    tabela = "\n".join(
        f"- {v['nome']}: {v['voto']} — {v['motivo']} (mudaria: {v['mudaria']})" for v in placar["votos"]
    )
    return f"""# Você é o JUIZ

Leia:
- Autos: {p.autos}
- Acusação: {p.saida('acusacao')}
- Defesa: {p.saida('defesa')}
- Réplica: {p.saida('replica-acusacao')}
- Tréplica: {p.saida('treplica-defesa')}

O júri já votou e o placar foi contado. Ele é final e você não pode mudá-lo:
RESULTADO: {placar['resultado']} — {placar['culpado']} culpado x {placar['inocente']} inocente{placar['nota']}

Votos:
{tabela}

{REGRAS_GERAIS}
Não escreva o placar de novo e não conte votos: isso já está feito.

Escreva no arquivo: {p.saida('juiz')}
Use EXATAMENTE estes títulos, nesta ordem:

## Acusações que se sustentaram
<as que mais de um jurado citou, com quantos citaram>

## O que a defesa acertou
<pontos>

## Condições para absolvição
1. <mudança concreta, a mais importante primeiro>
2. ...
(de 3 a 5 itens numerados)

## Veredito
<1 frase>

Depois de salvar, responda só: pronto.
"""


def cmd_briefing(args) -> None:
    p = Processo.atual()
    fase = args.fase
    exigir_anteriores(p, fase)
    tarefas: list[tuple[str, Path, Path]] = []
    if fase == "abertura":
        checar_autos(p)
        escrever(p.brief("acusacao"), brief_acusacao(p))
        escrever(p.brief("defesa"), brief_defesa(p))
        tarefas = [("Acusação", p.brief("acusacao"), p.saida("acusacao")),
                   ("Defesa", p.brief("defesa"), p.saida("defesa"))]
    elif fase == "replica":
        escrever(p.brief("replica-acusacao"), brief_replica(p, "acusacao"))
        escrever(p.brief("treplica-defesa"), brief_replica(p, "defesa"))
        tarefas = [("Réplica da acusação", p.brief("replica-acusacao"), p.saida("replica-acusacao")),
                   ("Tréplica da defesa", p.brief("treplica-defesa"), p.saida("treplica-defesa"))]
    elif fase == "juri":
        for j in p.jurados:
            nome = "jurado-" + j["id"]
            escrever(p.brief(nome), brief_jurado(p, j))
            tarefas.append((j["nome"], p.brief(nome), p.saida(nome)))
    elif fase == "juiz":
        if not p.placar_json.exists():
            raise Falha("Conte os votos antes: python tribunal.py contar")
        placar = json.loads(ler(p.placar_json))
        escrever(p.brief("juiz"), brief_juiz(p, placar))
        tarefas = [("Juiz", p.brief("juiz"), p.saida("juiz"))]
    print(f"Fase {fase}: dispare {len(tarefas)} subagente(s) em paralelo, um por linha.")
    print("Prompt de cada um: \"Leia o arquivo <brief> e siga exatamente o que ele diz.\"")
    print()
    for rotulo, b, s in tarefas:
        print(f"- {rotulo}\n    brief: {b}\n    saída: {s}")
    print()
    print(f"Quando todos responderem: python tribunal.py checar {fase}")


# ---------------------------------------------------------------- checagens

def checar_autos(p: Processo) -> None:
    if len(linhas_cheias(ler(p.autos))) < 3:
        raise Falha(f"Os autos estão vazios ou curtos demais. Escreva o resumo em {p.autos}.")


def exigir_anteriores(p: Processo, fase: str) -> None:
    for anterior in FASES[: FASES.index(fase)]:
        if anterior not in p.dados["fases_ok"]:
            raise Falha(f"A fase '{anterior}' ainda não passou na checagem. Rode: python tribunal.py checar {anterior}")


def _blocos(texto: str, titulo: str) -> list[str]:
    partes = re.split(rf"^##\s*{titulo}\b.*$", texto, flags=re.MULTILINE | re.IGNORECASE)
    return [b for b in partes[1:]]


def _campo(bloco: str, nome: str) -> str | None:
    padrao = re.compile(rf"^\W*{nome}\W*:\s*(.+)$", flags=re.IGNORECASE)
    for linha in bloco.splitlines():
        if padrao.match(sem_acento(linha).strip()):
            valor = limpar_valor(linha.split(":", 1)[1])
            return valor or None
    return None


def checar_acusacao(texto: str) -> list[str]:
    erros = []
    blocos = _blocos(sem_acento(texto), "Acusacao")
    if not 1 <= len(blocos) <= 5:
        erros.append(f"acusação: precisa de 1 a 5 blocos '## Acusação N' (veio {len(blocos)})")
    for i, b in enumerate(blocos, 1):
        for campo in ("ACUSACAO", "EVIDENCIA", "GRAVIDADE"):
            if not _campo(b, campo):
                erros.append(f"acusação {i}: falta a linha {campo}:")
        g = _campo(b, "GRAVIDADE")
        if g and sem_acento(g).lower().strip(" .") not in GRAVIDADES:
            erros.append(f"acusação {i}: GRAVIDADE precisa ser leve, séria ou fatal (veio '{g}')")
    return erros


def checar_defesa(texto: str) -> list[str]:
    erros = []
    blocos = _blocos(sem_acento(texto), "Argumento")
    if not 1 <= len(blocos) <= 5:
        erros.append(f"defesa: precisa de 1 a 5 blocos '## Argumento N' (veio {len(blocos)})")
    for i, b in enumerate(blocos, 1):
        for campo in ("ARGUMENTO", "MOTIVO"):
            if not _campo(b, campo):
                erros.append(f"defesa {i}: falta a linha {campo}:")
    return erros


def checar_replica(texto: str, rotulo: str) -> list[str]:
    n = len(linhas_cheias(texto))
    if n == 0:
        return [f"{rotulo}: arquivo vazio ou não foi criado"]
    if n > 5:
        return [f"{rotulo}: passou de 5 linhas (veio {n})"]
    return []


def ler_voto(texto: str) -> dict:
    voto = _campo(texto, "VOTO")
    motivo = _campo(texto, "MOTIVO")
    mudaria = _campo(texto, "MUDARIA")
    erros = []
    if voto is None:
        erros.append("falta a linha VOTO:")
    else:
        voto = sem_acento(voto).upper().strip(" .!")
        if voto not in ("CULPADO", "INOCENTE"):
            erros.append(f"VOTO precisa ser CULPADO ou INOCENTE (veio '{voto}')")
    if not motivo:
        erros.append("falta a linha MOTIVO:")
    if not mudaria:
        erros.append("falta a linha MUDARIA:")
    return {"voto": voto, "motivo": motivo, "mudaria": mudaria, "erros": erros}


def checar_juiz(texto: str, placar: dict | None) -> list[str]:
    erros = []
    base = sem_acento(texto).lower()
    for titulo in ("acusacoes que se sustentaram", "o que a defesa acertou",
                   "condicoes para absolvicao", "veredito"):
        if not re.search(rf"^##\s*{titulo}", base, flags=re.MULTILINE):
            erros.append(f"juiz: falta o título '## {titulo}'")
    m = re.search(r"^##\s*condicoes para absolvicao.*?$(.*?)(?=^##|\Z)", base, flags=re.MULTILINE | re.DOTALL)
    if m:
        itens = re.findall(r"^\s*\d+[.)]\s+\S", m.group(1), flags=re.MULTILINE)
        if not 3 <= len(itens) <= 5:
            erros.append(f"juiz: precisa de 3 a 5 condições numeradas (veio {len(itens)})")
    if placar:
        citados = re.findall(r"\bpor\s+(\d{1,2})\s*(?:a|x)\s*(\d{1,2})\b", base)
        citados += re.findall(r"\b(\d{1,2})\s*(?:x|×)\s*(\d{1,2})\b", base)
        for a, b in citados:
            par = {int(a), int(b)}
            if par != {placar["culpado"], placar["inocente"]}:
                erros.append(f"juiz: citou um placar ({a} a {b}) diferente do contado. Ele não pode mexer no placar.")
        outro = "inocente" if placar["resultado"] == "CULPADO" else "culpado"
        m2 = re.search(r"^##\s*veredito.*?$(.*)", base, flags=re.MULTILINE | re.DOTALL)
        if m2 and re.search(rf"\b(reu|ideia)\s+(e\s+)?(declarad[oa]\s+)?{outro}\b", m2.group(1)):
            erros.append("juiz: o veredito contradiz o resultado do júri.")
    return erros


def cmd_checar(args) -> None:
    p = Processo.atual()
    fase = args.fase
    exigir_anteriores(p, fase)
    erros: list[str] = []
    refazer: list[str] = []
    if fase == "abertura":
        for nome, fn in (("acusacao", checar_acusacao), ("defesa", checar_defesa)):
            texto = ler(p.saida(nome))
            e = [f"{nome}: arquivo não foi criado"] if not texto.strip() else fn(texto)
            if e:
                refazer.append(nome)
            erros += e
    elif fase == "replica":
        for nome in ("replica-acusacao", "treplica-defesa"):
            e = checar_replica(ler(p.saida(nome)), nome)
            if e:
                refazer.append(nome)
            erros += e
    elif fase == "juri":
        for j in p.jurados:
            nome = "jurado-" + j["id"]
            texto = ler(p.saida(nome))
            e = ["arquivo não foi criado"] if not texto.strip() else ler_voto(texto)["erros"]
            if e:
                refazer.append(nome)
                erros += [f"{j['nome']}: {x}" for x in e]
    elif fase == "juiz":
        placar = json.loads(ler(p.placar_json)) if p.placar_json.exists() else None
        texto = ler(p.saida("juiz"))
        erros = ["juiz: arquivo não foi criado"] if not texto.strip() else checar_juiz(texto, placar)
        if erros:
            refazer.append("juiz")
    if erros:
        print(f"REPROVADO na fase {fase}:")
        for e in erros:
            print(f"  - {e}")
        print()
        print("Refaça SÓ estes agentes, com o mesmo brief (não corrija o texto você mesmo):")
        for r in refazer:
            print(f"  - {p.brief(r)}")
        sys.exit(2)
    if fase not in p.dados["fases_ok"]:
        p.dados["fases_ok"].append(fase)
        p.salvar()
    proximo = {
        "abertura": "python tribunal.py briefing replica",
        "replica": "python tribunal.py briefing juri",
        "juri": "python tribunal.py contar",
        "juiz": "python tribunal.py veredito",
    }[fase]
    print(f"APROVADO: fase {fase}. Próximo: {proximo}")


# ---------------------------------------------------------------- contagem

def contar_votos(votos: list[dict]) -> dict:
    culpado = sum(1 for v in votos if v["voto"] == "CULPADO")
    inocente = sum(1 for v in votos if v["voto"] == "INOCENTE")
    if culpado > inocente:
        resultado, nota = "CULPADO", ""
    elif inocente > culpado:
        resultado, nota = "INOCENTE", ""
    else:
        resultado, nota = "INOCENTE", " (empate: na dúvida, a favor do réu)"
    return {"culpado": culpado, "inocente": inocente, "resultado": resultado, "nota": nota, "votos": votos}


def cmd_contar(args) -> None:
    p = Processo.atual()
    if "juri" not in p.dados["fases_ok"]:
        raise Falha("O júri ainda não passou na checagem. Rode: python tribunal.py checar juri")
    votos = []
    for j in p.jurados:
        v = ler_voto(ler(p.saida("jurado-" + j["id"])))
        if v["erros"]:
            raise Falha(f"Voto inválido de {j['nome']}: {v['erros']}")
        votos.append({"id": j["id"], "nome": j["nome"], "voto": v["voto"],
                      "motivo": v["motivo"], "mudaria": v["mudaria"]})
    placar = contar_votos(votos)
    escrever(p.placar_json, json.dumps(placar, ensure_ascii=False, indent=2))
    print(f"PLACAR: {placar['resultado']} — {placar['culpado']} culpado x {placar['inocente']} inocente{placar['nota']}")
    print("Próximo: python tribunal.py briefing juiz")


# ---------------------------------------------------------------- veredito

def _secao(texto: str, titulo: str) -> str:
    base = sem_acento(texto).lower()
    m = re.search(rf"^##\s*{titulo}.*?$", base, flags=re.MULTILINE)
    if not m:
        return ""
    inicio = m.end()
    prox = re.search(r"^##\s", base[inicio:], flags=re.MULTILINE)
    fim = inicio + prox.start() if prox else len(texto)
    return texto[inicio:fim].strip()


def montar_veredito(p: Processo, placar: dict) -> str:
    juiz = ler(p.saida("juiz"))
    linhas_tabela = "\n".join(
        f"| {v['nome']} | {v['voto']} | {v['motivo']} | {v['mudaria']} |" for v in placar["votos"]
    )
    cabecalho = (
        f"# Tribunal: {p.dados['tema']}\n\n"
        f"**Data:** {p.dados['data']} · **Modo:** {p.dados['modo']} · **Júri:** {len(p.jurados)}\n\n"
        f"## ⚖️ Veredito: {placar['resultado']} por {max(placar['culpado'], placar['inocente'])} a "
        f"{min(placar['culpado'], placar['inocente'])}{placar['nota']}\n\n"
        f"{_secao(juiz, 'veredito')}\n"
    )
    return (
        cabecalho
        + "\n## Condições para absolvição\n\n" + _secao(juiz, "condicoes para absolvicao") + "\n"
        + "\n## Acusações que se sustentaram\n\n" + _secao(juiz, "acusacoes que se sustentaram") + "\n"
        + "\n## O que a defesa acertou\n\n" + _secao(juiz, "o que a defesa acertou") + "\n"
        + "\n## Júri\n\n| Jurado | Voto | Motivo | O que mudaria |\n|---|---|---|---|\n" + linhas_tabela + "\n"
        + "\n---\n\n# Processo completo\n"
        + "\n## Autos\n\n" + ler(p.autos).strip() + "\n"
        + "\n## Acusação\n\n" + ler(p.saida("acusacao")).strip() + "\n"
        + "\n## Defesa\n\n" + ler(p.saida("defesa")).strip() + "\n"
        + "\n## Réplica da acusação\n\n" + ler(p.saida("replica-acusacao")).strip() + "\n"
        + "\n## Tréplica da defesa\n\n" + ler(p.saida("treplica-defesa")).strip() + "\n"
        + f"\n---\n\n_O júri é formado por modelos de linguagem: é uma segunda opinião estruturada, "
        f"não aconselhamento jurídico, financeiro ou profissional._\n\n{CREDITO}\n"
    )


def cmd_veredito(args) -> None:
    p = Processo.atual()
    exigir_anteriores(p, "juiz")
    if "juiz" not in p.dados["fases_ok"]:
        raise Falha("A sentença do juiz ainda não passou na checagem. Rode: python tribunal.py checar juiz")
    placar = json.loads(ler(p.placar_json))
    destino = RAIZ / f"VEREDITO-{p.dados['data']}-{p.dados['slug']}.md"
    n = 2
    while destino.exists():
        destino = RAIZ / f"VEREDITO-{p.dados['data']}-{p.dados['slug']}-{n}.md"
        n += 1
    escrever(destino, montar_veredito(p, placar))
    juiz = ler(p.saida("juiz"))
    print("MOSTRE ISTO AO USUÁRIO, SEM ALTERAR O PLACAR:")
    print()
    print(f"⚖️ Veredito: {placar['resultado']} por {max(placar['culpado'], placar['inocente'])} a "
          f"{min(placar['culpado'], placar['inocente'])}{placar['nota']}")
    print()
    print(_secao(juiz, "veredito"))
    print()
    print("Condições para absolvição:")
    print(_secao(juiz, "condicoes para absolvicao"))
    print()
    print(f"Processo completo: {destino}")


def cmd_status(args) -> None:
    p = Processo.atual()
    print(f"Processo: {p.pasta}")
    print(f"Tema: {p.dados['tema']} · modo {p.dados['modo']} · {len(p.jurados)} jurados")
    print(f"Fases aprovadas: {', '.join(p.dados['fases_ok']) or 'nenhuma'}")
    pendentes = [f for f in FASES if f not in p.dados["fases_ok"]]
    print(f"Próxima fase: {pendentes[0] if pendentes else 'veredito'}")


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    _saida_utf8()
    ap = argparse.ArgumentParser(prog="tribunal", description="A parte burocrática do Tribunal.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("abrir")
    a.add_argument("--tema", required=True)
    a.add_argument("--modo", choices=["padrao", "rapido", "reel"], default="padrao")
    a.add_argument("--jurados", type=int)
    a.add_argument("--semente", type=int, default=0)
    a.set_defaults(fn=cmd_abrir)
    for nome, fn in (("briefing", cmd_briefing), ("checar", cmd_checar)):
        s = sub.add_parser(nome)
        s.add_argument("fase", choices=FASES)
        s.set_defaults(fn=fn)
    sub.add_parser("contar").set_defaults(fn=cmd_contar)
    sub.add_parser("veredito").set_defaults(fn=cmd_veredito)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    args = ap.parse_args(argv)
    try:
        args.fn(args)
    except Falha as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
