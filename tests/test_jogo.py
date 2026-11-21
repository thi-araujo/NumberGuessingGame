import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jogo import NIVEIS, Partida, Placar, Resultado, temperatura  # noqa: E402

FACIL, MEDIO, DIFICIL = NIVEIS["Fácil"], NIVEIS["Médio"], NIVEIS["Difícil"]


class TestPartida(unittest.TestCase):
    def test_sorteio_dentro_da_faixa(self):
        gerador = random.Random(42)
        for nivel in NIVEIS.values():
            for _ in range(200):
                segredo = Partida(nivel, gerador).segredo
                self.assertTrue(nivel.minimo <= segredo <= nivel.maximo)

    def test_dicas_e_faixa_possivel(self):
        p = Partida(MEDIO, segredo=42)
        self.assertEqual(p.palpitar(50), Resultado.MENOR)
        self.assertEqual((p.menor_possivel, p.maior_possivel), (1, 49))
        self.assertEqual(p.palpitar("25"), Resultado.MAIOR)
        self.assertEqual((p.menor_possivel, p.maior_possivel), (26, 49))
        self.assertEqual(p.palpitar(" 42 "), Resultado.ACERTOU)
        self.assertTrue(p.venceu and p.terminou and not p.perdeu)
        self.assertEqual(p.tentativas, 3)
        self.assertIsNotNone(p.fim)

    def test_palpite_invalido_nao_conta(self):
        p = Partida(FACIL, segredo=5)
        for valor in ("abc", "", "3.5", 0, 11):
            with self.assertRaises(ValueError):
                p.palpitar(valor)
        self.assertEqual(p.tentativas, 0)

    def test_repetido_nao_conta(self):
        p = Partida(FACIL, segredo=5)
        p.palpitar(3)
        self.assertEqual(p.palpitar(3), Resultado.REPETIDO)
        self.assertEqual(p.tentativas, 1)

    def test_perde_ao_esgotar_tentativas(self):
        p = Partida(MEDIO, segredo=100)
        for chute in range(1, 11):
            p.palpitar(chute)
        self.assertTrue(p.perdeu and p.terminou)
        self.assertEqual(p.restantes, 0)
        with self.assertRaises(RuntimeError):
            p.palpitar(100)

    def test_acertar_na_ultima_tentativa_e_vitoria(self):
        p = Partida(MEDIO, segredo=10)
        for chute in range(1, 11):
            p.palpitar(chute)
        self.assertTrue(p.venceu)
        self.assertFalse(p.perdeu)

    def test_facil_sem_limite(self):
        p = Partida(FACIL, segredo=10)
        for chute in range(1, 10):
            p.palpitar(chute)
        self.assertIsNone(p.restantes)
        self.assertFalse(p.terminou)

    def test_busca_binaria_sempre_vence_no_dificil(self):
        # Com a estratégia ideal, 1000 números precisam de no máximo 10 palpites (limite: 12).
        for segredo in (1, 500, 777, 1000):
            p = Partida(DIFICIL, segredo=segredo)
            while not p.terminou:
                p.palpitar((p.menor_possivel + p.maior_possivel) // 2)
            self.assertTrue(p.venceu, segredo)
            self.assertLessEqual(p.tentativas, 10)

    def test_segredo_fora_da_faixa(self):
        with self.assertRaises(ValueError):
            Partida(FACIL, segredo=11)


class TestTemperatura(unittest.TestCase):
    def test_relativa_ao_nivel(self):
        self.assertEqual(temperatura(50, 50, MEDIO), "Acertou!")
        self.assertEqual(temperatura(48, 50, MEDIO), "Fervendo")
        self.assertEqual(temperatura(42, 50, MEDIO), "Quente")
        self.assertEqual(temperatura(30, 50, MEDIO), "Morno")
        self.assertEqual(temperatura(1, 50, MEDIO), "Frio")
        self.assertEqual(temperatura(480, 500, DIFICIL), "Fervendo")


class TestPlacar(unittest.TestCase):
    def vitoria(self, tentativas, nivel=MEDIO):
        p = Partida(nivel, segredo=nivel.maximo)
        for chute in range(nivel.minimo, nivel.minimo + tentativas - 1):
            p.palpitar(chute)
        p.palpitar(nivel.maximo)
        return p

    def test_ranking_ordena_por_tentativas(self):
        placar = Placar()
        self.assertEqual(placar.registrar("Médio", "Ana", self.vitoria(5)), 1)
        self.assertEqual(placar.registrar("Médio", "Bia", self.vitoria(3)), 1)
        self.assertEqual(placar.registrar("Médio", "  ", self.vitoria(8)), 3)
        self.assertEqual([r.jogador for r in placar.ranking("Médio")], ["Bia", "Ana", "Jogador"])
        self.assertEqual(placar.melhor("Médio").tentativas, 3)
        self.assertIsNone(placar.melhor("Difícil"))

    def test_ranking_limitado(self):
        placar = Placar()
        for _ in range(10):
            placar.registrar("Médio", "Bom", self.vitoria(2))
        self.assertIsNone(placar.registrar("Médio", "Pior", self.vitoria(9)))
        self.assertEqual(len(placar.ranking("Médio")), 10)

    def test_salvar_e_carregar(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "placar.json"
            placar = Placar()
            placar.registrar("Fácil", "Thiago", self.vitoria(2, FACIL))
            placar.salvar(arquivo)
            self.assertEqual(Placar.carregar(arquivo), placar)
            arquivo.write_text("{quebrado", encoding="utf-8")
            self.assertEqual(Placar.carregar(arquivo), Placar())


if __name__ == "__main__":
    unittest.main()
