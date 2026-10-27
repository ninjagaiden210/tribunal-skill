"""Testes do tribunal.py. Rode: python -m unittest discover -s tests"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tribunal"))
import tribunal as t  # noqa: E402

ACUSACAO = """## Acusação 1
ACUSAÇÃO: Não tem diferencial.
EVIDÊNCIA: Todo concorrente se diz artesanal.
GRAVIDADE: séria

## Acusação 2
**ACUSAÇÃO:** A conta não fecha.
**EVIDÊNCIA:** Comissão do app come a margem.
**GRAVIDADE:** fatal
"""

DEFESA = """## Argumento 1
ARGUMENTO: Sem salão, o risco é menor.
MOTIVO: Aluguel e equipe menores.
"""

JUIZ_OK = """## Acusações que se sustentaram
Sem diferencial (4 jurados).

## O que a defesa acertou
Risco baixo.

## Condições para absolvição
1. Fechar a conta por pedido.
2. Criar um burger que ninguém tem.
3. Rodar um piloto de 100 pedidos.

## Veredito
Do jeito que está, é só mais uma hamburgueria no app.
"""


def rodar(*args):
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(saida):
        try:
            codigo = t.main(list(args))
        except SystemExit as e:
            codigo = e.code
    return codigo, saida.getvalue()


class TestFluxo(unittest.TestCase):
    def setUp(self):
        self.antes = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.antes)
        self.tmp.cleanup()

    def processo(self):
        return t.Processo.atual()

    def test_julgamento_completo(self):
        codigo, out = rodar("abrir", "--tema", "Hamburgueria delivery em Santos", "--modo", "rapido")
        self.assertEqual(codigo, 0, out)
        p = self.processo()
        self.assertEqual(len(p.jurados), 6)

        # sem autos, não abre a fase
        codigo, out = rodar("briefing", "abertura")
        self.assertEqual(codigo, 1)

        t.escrever(p.autos, "O que é: hamburgueria\nPra quem: Santos\nComo ganha: iFood\n")
        self.assertEqual(rodar("briefing", "abertura")[0], 0)

        # não pula fase
        self.assertEqual(rodar("briefing", "juri")[0], 1)

        t.escrever(p.saida("acusacao"), ACUSACAO)
        t.escrever(p.saida("defesa"), DEFESA)
        codigo, out = rodar("checar", "abertura")
        self.assertEqual(codigo, 0, out)

        rodar("briefing", "replica")
        t.escrever(p.saida("replica-acusacao"), "A defesa não respondeu à conta.")
        t.escrever(p.saida("treplica-defesa"), "O piloto resolve a conta.")
        self.assertEqual(rodar("checar", "replica")[0], 0)

        rodar("briefing", "juri")
        votos = ["CULPADO", "**CULPADO**", "culpado", "INOCENTE", "Culpado.", "INOCENTE"]
        for j, v in zip(p.jurados, votos):
            t.escrever(p.saida("jurado-" + j["id"]), f"VOTO: {v}\nMOTIVO: motivo de {j['id']}\nMUDARIA: algo\n")
        self.assertEqual(rodar("checar", "juri")[0], 0)

        codigo, out = rodar("contar")
        self.assertEqual(codigo, 0, out)
        placar = json.loads(t.ler(p.placar_json))
        self.assertEqual((placar["culpado"], placar["inocente"], placar["resultado"]), (4, 2, "CULPADO"))

        rodar("briefing", "juiz")
        t.escrever(p.saida("juiz"), JUIZ_OK)
        codigo, out = rodar("checar", "juiz")
        self.assertEqual(codigo, 0, out)

        codigo, out = rodar("veredito")
        self.assertEqual(codigo, 0, out)
        self.assertIn("CULPADO por 4 a 2", out)
        arquivos = list(Path("tribunal").glob("VEREDITO-*.md"))
        self.assertEqual(len(arquivos), 1)
        texto = arquivos[0].read_text(encoding="utf-8")
        self.assertIn("| O cliente | CULPADO |", texto)
        self.assertIn("Fechar a conta por pedido", texto)

    def test_voto_invalido_reprova(self):
        rodar("abrir", "--tema", "x", "--jurados", "3", "--semente", "7")
        p = self.processo()
        self.assertEqual(len(p.jurados), 3)
        p.dados["fases_ok"] = ["abertura", "replica"]
        p.salvar()
        for i, j in enumerate(p.jurados):
            voto = "TALVEZ" if i == 0 else "INOCENTE"
            t.escrever(p.saida("jurado-" + j["id"]), f"VOTO: {voto}\nMOTIVO: m\nMUDARIA: n\n")
        codigo, out = rodar("checar", "juri")
        self.assertEqual(codigo, 2)
        self.assertIn("TALVEZ", out)
        self.assertEqual(rodar("contar")[0], 1)

    def test_jurado_faltando_reprova(self):
        rodar("abrir", "--tema", "x", "--modo", "rapido")
        p = self.processo()
        p.dados["fases_ok"] = ["abertura", "replica"]
        p.salvar()
        for j in p.jurados[:-1]:
            t.escrever(p.saida("jurado-" + j["id"]), "VOTO: CULPADO\nMOTIVO: m\nMUDARIA: n\n")
        codigo, out = rodar("checar", "juri")
        self.assertEqual(codigo, 2)
        self.assertIn("não foi criado", out)

    def test_empate_favorece_reu(self):
        votos = [{"voto": "CULPADO"}] * 3 + [{"voto": "INOCENTE"}] * 3
        placar = t.contar_votos(votos)
        self.assertEqual(placar["resultado"], "INOCENTE")
        self.assertIn("empate", placar["nota"])

    def test_juiz_nao_mexe_no_placar(self):
        placar = {"culpado": 4, "inocente": 2, "resultado": "CULPADO"}
        erros = t.checar_juiz(JUIZ_OK.replace("Do jeito", "Condenado por 5 a 1. Do jeito"), placar)
        self.assertTrue(any("placar" in e for e in erros))
        self.assertEqual(t.checar_juiz(JUIZ_OK, placar), [])
        # "de 3 a 5" e valores em reais não contam como placar
        self.assertEqual(t.checar_juiz(JUIZ_OK + "\nTeste de 3 a 5 semanas, R$ 10 a 16.\n", placar), [])

    def test_juiz_poucas_condicoes(self):
        ruim = JUIZ_OK.replace("3. Rodar um piloto de 100 pedidos.\n", "").replace("2. Criar um burger que ninguém tem.\n", "")
        self.assertTrue(any("condições" in e for e in t.checar_juiz(ruim, None)))

    def test_acusacao_formato(self):
        self.assertEqual(t.checar_acusacao(ACUSACAO), [])
        self.assertTrue(t.checar_acusacao("## Acusação 1\nACUSAÇÃO: x\nEVIDÊNCIA: y\nGRAVIDADE: média\n"))
        seis = "".join(f"## Acusação {i}\nACUSAÇÃO: x\nEVIDÊNCIA: y\nGRAVIDADE: leve\n" for i in range(6))
        self.assertTrue(t.checar_acusacao(seis))

    def test_reel_troca_juri(self):
        rodar("abrir", "--tema", "roteiro", "--modo", "reel")
        p = self.processo()
        self.assertEqual(p.jurados[0]["id"], "rolando-feed")
        rodar_ok = rodar
        t.escrever(p.autos, "a\nb\nc\n")
        rodar_ok("briefing", "abertura")
        self.assertIn("reel", t.ler(p.brief("acusacao")))


if __name__ == "__main__":
    unittest.main()
