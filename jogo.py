"""Regras do Jogo de Adivinhação e placar, sem interface gráfica.

O computador sorteia um número e o jogador tenta adivinhar. A cada palpite,
o jogo diz se o número secreto é maior ou menor. Nos níveis Médio e Difícil
há limite de tentativas.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

ARQUIVO_PLACAR = Path.home() / ".jogo_adivinhacao.json"
TAMANHO_RANKING = 10


@dataclass(frozen=True)
class Nivel:
    nome: str
    minimo: int
    maximo: int
    max_tentativas: int | None  # None = sem limite

    @property
    def descricao(self) -> str:
        limite = f"{self.max_tentativas} tentativas" if self.max_tentativas else "tentativas livres"
        return f"{self.minimo} a {self.maximo}, {limite}"


NIVEIS = {
    "Fácil": Nivel("Fácil", 1, 10, None),
    "Médio": Nivel("Médio", 1, 100, 10),
    "Difícil": Nivel("Difícil", 1, 1000, 12),
}


class Resultado(Enum):
    ACERTOU = "acertou"
    MAIOR = "maior"        # o número secreto é maior que o palpite
    MENOR = "menor"        # o número secreto é menor que o palpite
    REPETIDO = "repetido"  # palpite já feito: não conta tentativa


def temperatura(palpite: int, segredo: int, nivel: Nivel) -> str:
    """Dica de proximidade, relativa ao tamanho da faixa do nível."""
    distancia = abs(palpite - segredo) / (nivel.maximo - nivel.minimo + 1)
    if distancia == 0:
        return "Acertou!"
    if distancia <= 0.03:
        return "Fervendo"
    if distancia <= 0.10:
        return "Quente"
    if distancia <= 0.25:
        return "Morno"
    return "Frio"


class Partida:
    def __init__(self, nivel: Nivel, sorteio: random.Random | None = None, segredo: int | None = None) -> None:
        self.nivel = nivel
        gerador = sorteio or random.Random()
        self.segredo = segredo if segredo is not None else gerador.randint(nivel.minimo, nivel.maximo)
        if not nivel.minimo <= self.segredo <= nivel.maximo:
            raise ValueError("número secreto fora da faixa do nível")
        self.palpites: list[int] = []
        self.menor_possivel = nivel.minimo
        self.maior_possivel = nivel.maximo
        self.inicio = datetime.now()
        self.fim: datetime | None = None

    @property
    def tentativas(self) -> int:
        return len(self.palpites)

    @property
    def venceu(self) -> bool:
        return bool(self.palpites) and self.palpites[-1] == self.segredo

    @property
    def perdeu(self) -> bool:
        limite = self.nivel.max_tentativas
        return not self.venceu and limite is not None and self.tentativas >= limite

    @property
    def terminou(self) -> bool:
        return self.venceu or self.perdeu

    @property
    def restantes(self) -> int | None:
        if self.nivel.max_tentativas is None:
            return None
        return self.nivel.max_tentativas - self.tentativas

    def segundos(self) -> float:
        return ((self.fim or datetime.now()) - self.inicio).total_seconds()

    def palpitar(self, valor: int | str) -> Resultado:
        """Registra um palpite. Levanta ValueError se não for um número da faixa."""
        if self.terminou:
            raise RuntimeError("a partida já terminou")
        try:
            numero = int(str(valor).strip())
        except ValueError:
            raise ValueError("Digite um número inteiro.") from None
        if not self.nivel.minimo <= numero <= self.nivel.maximo:
            raise ValueError(f"Escolha um número entre {self.nivel.minimo} e {self.nivel.maximo}.")
        if numero in self.palpites:
            return Resultado.REPETIDO

        self.palpites.append(numero)
        if numero == self.segredo:
            resultado = Resultado.ACERTOU
            self.menor_possivel = self.maior_possivel = numero
        elif numero < self.segredo:
            resultado = Resultado.MAIOR
            self.menor_possivel = max(self.menor_possivel, numero + 1)
        else:
            resultado = Resultado.MENOR
            self.maior_possivel = min(self.maior_possivel, numero - 1)
        if self.terminou:
            self.fim = datetime.now()
        return resultado


# --------------------------------------------------------------------------
# Placar
# --------------------------------------------------------------------------

@dataclass
class Recorde:
    jogador: str
    tentativas: int
    segundos: float
    data: str  # "AAAA-MM-DD HH:MM"


@dataclass
class Placar:
    rankings: dict[str, list[Recorde]] = field(default_factory=dict)

    def ranking(self, nivel: str) -> list[Recorde]:
        return self.rankings.get(nivel, [])

    def melhor(self, nivel: str) -> Recorde | None:
        ranking = self.ranking(nivel)
        return ranking[0] if ranking else None

    def registrar(self, nivel: str, jogador: str, partida: Partida) -> int | None:
        """Adiciona uma vitória e devolve a posição no ranking (1 = primeiro),
        ou None se não entrou entre os melhores."""
        recorde = Recorde(jogador.strip() or "Jogador", partida.tentativas, round(partida.segundos(), 1),
                          datetime.now().strftime("%Y-%m-%d %H:%M"))
        ranking = self.rankings.setdefault(nivel, [])
        ranking.append(recorde)
        ranking.sort(key=lambda r: (r.tentativas, r.segundos))
        del ranking[TAMANHO_RANKING:]
        for posicao, item in enumerate(ranking, start=1):
            if item is recorde:
                return posicao
        return None

    def salvar(self, caminho: Path = ARQUIVO_PLACAR) -> None:
        dados = {nivel: [asdict(r) for r in lista] for nivel, lista in self.rankings.items()}
        caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def carregar(cls, caminho: Path = ARQUIVO_PLACAR) -> "Placar":
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            rankings = {}
            for nivel, lista in dados.items():
                if nivel not in NIVEIS:
                    continue
                recordes = [Recorde(str(r["jogador"]), int(r["tentativas"]), float(r["segundos"]), str(r["data"]))
                            for r in lista]
                recordes.sort(key=lambda r: (r.tentativas, r.segundos))
                rankings[nivel] = recordes[:TAMANHO_RANKING]
            return cls(rankings)
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            return cls()
