"""Jogo de Adivinhação de Números com interface gráfica.

    python adivinhacao.py
"""

from __future__ import annotations

import platform
import tkinter as tk
from tkinter import ttk

from jogo import NIVEIS, Partida, Placar, Resultado, temperatura

CORES = {
    "fundo": "#0f172a",
    "painel": "#1e293b",
    "borda": "#334155",
    "texto": "#e2e8f0",
    "texto_suave": "#94a3b8",
    "destaque": "#38bdf8",
    "verde": "#22c55e",
    "vermelho": "#ef4444",
    "ambar": "#f59e0b",
}
CORES_TEMPERATURA = {"Fervendo": "#ef4444", "Quente": "#f97316", "Morno": "#f59e0b", "Frio": "#38bdf8",
                     "Acertou!": "#22c55e"}

WINDOWS = platform.system() == "Windows"
FONTE = "Segoe UI" if WINDOWS else "Helvetica"
FONTE_MONO = "Consolas" if WINDOWS else "DejaVu Sans Mono"


def configurar_estilo(raiz: tk.Tk) -> None:
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    sem_borda = dict(bordercolor=CORES["painel"], lightcolor=CORES["painel"], darkcolor=CORES["painel"])
    estilo.configure(".", background=CORES["fundo"], foreground=CORES["texto"], font=(FONTE, 10))
    estilo.configure("Painel.TFrame", background=CORES["painel"])
    estilo.configure("Painel.TLabel", background=CORES["painel"])
    estilo.configure("PainelSuave.TLabel", background=CORES["painel"], foreground=CORES["texto_suave"])
    estilo.configure("Suave.TLabel", foreground=CORES["texto_suave"])
    estilo.configure("Titulo.TLabel", background=CORES["painel"], foreground=CORES["destaque"],
                     font=(FONTE, 11, "bold"))
    estilo.configure("TButton", background=CORES["borda"], foreground=CORES["texto"], borderwidth=0,
                     padding=(14, 7), font=(FONTE, 10, "bold"))
    estilo.map("TButton", background=[("disabled", CORES["painel"]), ("active", "#475569")],
               foreground=[("disabled", CORES["texto_suave"])])
    estilo.configure("Destaque.TButton", background=CORES["destaque"], foreground=CORES["fundo"],
                     font=(FONTE, 11, "bold"), padding=(18, 8))
    estilo.map("Destaque.TButton", background=[("disabled", CORES["painel"]), ("active", "#0ea5e9")])
    estilo.configure("Verde.TButton", background=CORES["verde"], foreground="#052e16")
    estilo.map("Verde.TButton", background=[("disabled", CORES["painel"]), ("active", "#16a34a")])
    estilo.configure("TRadiobutton", background=CORES["painel"], foreground=CORES["texto"],
                     indicatorbackground=CORES["fundo"], indicatorforeground=CORES["destaque"],
                     upperbordercolor=CORES["borda"], lowerbordercolor=CORES["borda"])
    estilo.map("TRadiobutton", background=[("active", CORES["painel"])],
               indicatorbackground=[("selected", CORES["fundo"]), ("!selected", CORES["fundo"])],
               indicatorforeground=[("selected", CORES["destaque"]), ("!selected", CORES["fundo"])])
    campo = dict(fieldbackground=CORES["fundo"], foreground=CORES["texto"], insertcolor=CORES["texto"],
                 bordercolor=CORES["borda"], lightcolor=CORES["fundo"], darkcolor=CORES["fundo"])
    estilo.configure("TEntry", **campo)
    estilo.configure("Treeview", background=CORES["painel"], fieldbackground=CORES["painel"],
                     foreground=CORES["texto"], borderwidth=0, rowheight=26, **sem_borda)
    estilo.configure("Treeview.Heading", background=CORES["borda"], foreground=CORES["texto_suave"],
                     borderwidth=0, font=(FONTE, 9, "bold"))
    estilo.map("Treeview", background=[("selected", CORES["borda"])])


class Aplicativo(tk.Tk):
    LARGURA_BARRA = 460

    def __init__(self) -> None:
        super().__init__()
        self.title("Jogo de Adivinhação")
        self.geometry("940x600")
        self.minsize(900, 580)
        self.configure(bg=CORES["fundo"])
        configurar_estilo(self)

        self.placar = Placar.carregar()
        self.partida: Partida | None = None
        self.var_nome = tk.StringVar()
        self.var_nivel = tk.StringVar(value="Médio")
        self.var_palpite = tk.StringVar()

        self._montar()
        self.novo_jogo()

    # ------------------------------------------------------------------ tela

    def _montar(self) -> None:
        lateral = ttk.Frame(self, style="Painel.TFrame", padding=16)
        lateral.pack(side="left", fill="y", padx=(16, 0), pady=16)
        ttk.Label(lateral, text="Jogador", style="Titulo.TLabel").pack(anchor="w")
        ttk.Entry(lateral, textvariable=self.var_nome, width=22).pack(anchor="w", pady=(6, 16), ipady=3)
        ttk.Label(lateral, text="Nível", style="Titulo.TLabel").pack(anchor="w")
        for nome, nivel in NIVEIS.items():
            ttk.Radiobutton(lateral, text=nome, value=nome, variable=self.var_nivel,
                            command=self._trocar_nivel).pack(anchor="w", pady=(8, 0))
            ttk.Label(lateral, text=nivel.descricao, style="PainelSuave.TLabel",
                      font=(FONTE, 9)).pack(anchor="w", padx=(22, 0))
        ttk.Button(lateral, text="Novo jogo", style="Verde.TButton", command=self.novo_jogo).pack(
            fill="x", pady=(20, 0))

        ttk.Label(lateral, text="Ranking", style="Titulo.TLabel").pack(anchor="w", pady=(24, 6))
        self.tbl_ranking = ttk.Treeview(lateral, columns=("pos", "nome", "tent", "tempo"), show="headings",
                                        height=7, selectmode="none")
        for chave, titulo, largura, ancora in (("pos", "#", 28, "center"), ("nome", "Jogador", 92, "w"),
                                               ("tent", "Tent.", 44, "center"), ("tempo", "Tempo", 54, "e")):
            self.tbl_ranking.heading(chave, text=titulo, anchor=ancora)
            self.tbl_ranking.column(chave, width=largura, anchor=ancora, stretch=False)
        self.tbl_ranking.tag_configure("novo", foreground=CORES["verde"])
        self.tbl_ranking.pack(anchor="w")

        # Área do jogo
        jogo = ttk.Frame(self, padding=(24, 20))
        jogo.pack(side="left", fill="both", expand=True)
        self.lbl_enunciado = tk.Label(jogo, font=(FONTE, 15), bg=CORES["fundo"], fg=CORES["texto"])
        self.lbl_enunciado.pack(pady=(4, 2))
        self.lbl_tentativas = ttk.Label(jogo, style="Suave.TLabel")
        self.lbl_tentativas.pack()

        self.barra = tk.Canvas(jogo, width=self.LARGURA_BARRA + 40, height=70, bg=CORES["fundo"],
                               highlightthickness=0)
        self.barra.pack(pady=(18, 6))

        entrada_linha = ttk.Frame(jogo)
        entrada_linha.pack(pady=10)
        self.entrada = ttk.Entry(entrada_linha, textvariable=self.var_palpite, width=8, justify="center",
                                 font=(FONTE_MONO, 24))
        self.entrada.pack(side="left", ipady=4)
        self.entrada.bind("<Return>", lambda _e: self.palpitar())
        self.btn_chutar = ttk.Button(entrada_linha, text="Chutar", style="Destaque.TButton",
                                     command=self.palpitar)
        self.btn_chutar.pack(side="left", padx=(12, 0), ipady=6)

        self.lbl_resposta = tk.Label(jogo, font=(FONTE, 22, "bold"), bg=CORES["fundo"], fg=CORES["texto"])
        self.lbl_resposta.pack(pady=(10, 0))
        self.lbl_dica = tk.Label(jogo, font=(FONTE, 11), bg=CORES["fundo"], fg=CORES["texto_suave"])
        self.lbl_dica.pack()

        ttk.Label(jogo, text="Seus palpites", style="Suave.TLabel").pack(pady=(18, 4))
        self.historico = tk.Text(jogo, height=3, width=52, bg=CORES["painel"], fg=CORES["texto"], relief="flat",
                                 font=(FONTE_MONO, 11), padx=10, pady=8, highlightthickness=0, state="disabled",
                                 wrap="word")
        self.historico.tag_configure("maior", foreground=CORES["destaque"])
        self.historico.tag_configure("menor", foreground=CORES["ambar"])
        self.historico.tag_configure("acertou", foreground=CORES["verde"])
        self.historico.pack()

    # ------------------------------------------------------------------ jogo

    def _trocar_nivel(self) -> None:
        if self.partida and self.partida.tentativas and not self.partida.terminou:
            self.lbl_dica.configure(text="Nível alterado: começando uma nova partida.", fg=CORES["texto_suave"])
        self.novo_jogo()

    def novo_jogo(self) -> None:
        self.unbind("<Return>")
        nivel = NIVEIS[self.var_nivel.get()]
        self.partida = Partida(nivel)
        self.var_palpite.set("")
        self.lbl_enunciado.configure(text=f"Estou pensando num número de {nivel.minimo} a {nivel.maximo}.")
        self.lbl_resposta.configure(text="Qual é o seu palpite?", fg=CORES["texto"])
        melhor = self.placar.melhor(nivel.nome)
        recorde = (f"Recorde do nível: {melhor.tentativas} tentativa(s), de {melhor.jogador}" if melhor
                   else "Ainda não há recorde neste nível. É sua vez de começar!")
        self.lbl_dica.configure(text=recorde, fg=CORES["texto_suave"])
        self.historico.configure(state="normal")
        self.historico.delete("1.0", "end")
        self.historico.configure(state="disabled")
        self.entrada.state(["!disabled"])
        self.btn_chutar.state(["!disabled"])
        self.entrada.focus_set()
        self._atualizar_contador()
        self._desenhar_barra()
        self._atualizar_ranking()

    def palpitar(self) -> None:
        partida = self.partida
        if partida is None or partida.terminou:
            return
        texto = self.var_palpite.get()
        self.var_palpite.set("")
        try:
            resultado = partida.palpitar(texto)
        except ValueError as erro:
            self.lbl_resposta.configure(text="Ops!", fg=CORES["vermelho"])
            self.lbl_dica.configure(text=str(erro), fg=CORES["vermelho"])
            return

        numero = int(texto)
        if resultado is Resultado.REPETIDO:
            self.lbl_resposta.configure(text=f"Você já chutou {numero}", fg=CORES["ambar"])
            self.lbl_dica.configure(text="Esse palpite não contou. Tente outro número.", fg=CORES["texto_suave"])
            return

        calor = temperatura(numero, partida.segredo, partida.nivel)
        if resultado is Resultado.ACERTOU:
            self._registrar_historico(numero, "acertou", "✔")
            self._vitoria()
        else:
            maior = resultado is Resultado.MAIOR
            self._registrar_historico(numero, "maior" if maior else "menor", "↑" if maior else "↓")
            self.lbl_resposta.configure(text="É maior! ↑" if maior else "É menor! ↓",
                                        fg=CORES["destaque"] if maior else CORES["ambar"])
            self.lbl_dica.configure(text=f"{calor}  ·  está entre {partida.menor_possivel} e {partida.maior_possivel}",
                                    fg=CORES_TEMPERATURA[calor])
            if partida.perdeu:
                self._derrota()
        self._atualizar_contador()
        self._desenhar_barra()

    def _vitoria(self) -> None:
        partida = self.partida
        nome = self.var_nome.get().strip() or "Jogador"
        posicao = self.placar.registrar(partida.nivel.nome, nome, partida)
        try:
            self.placar.salvar()
        except OSError:
            pass
        plural = "tentativa" if partida.tentativas == 1 else "tentativas"
        self.lbl_resposta.configure(text=f"Excelente, {nome}! Você acertou!", fg=CORES["verde"])
        if posicao == 1:
            extra = "Novo recorde do nível! 🏆"
        elif posicao:
            extra = f"{posicao}º lugar no ranking."
        else:
            extra = "Não entrou no ranking desta vez."
        self.lbl_dica.configure(text=f"O número era {partida.segredo}: {partida.tentativas} {plural} em "
                                     f"{partida.segundos():.0f}s. {extra}", fg=CORES["verde"])
        self._fim_de_jogo()
        self._atualizar_ranking(destaque=posicao)

    def _derrota(self) -> None:
        partida = self.partida
        self.lbl_resposta.configure(text="Fim das tentativas!", fg=CORES["vermelho"])
        self.lbl_dica.configure(text=f"O número era {partida.segredo}. Clique em Novo jogo para tentar de novo.",
                                fg=CORES["texto_suave"])
        self._fim_de_jogo()

    def _fim_de_jogo(self) -> None:
        self.entrada.state(["disabled"])
        self.btn_chutar.state(["disabled"])
        self.bind("<Return>", lambda _e: self.novo_jogo())  # Enter começa outra partida

    # ------------------------------------------------------------------ desenho

    def _atualizar_contador(self) -> None:
        p = self.partida
        if p.restantes is None:
            texto = f"Tentativas: {p.tentativas}"
        else:
            texto = f"Tentativa {min(p.tentativas + 1, p.nivel.max_tentativas)} de {p.nivel.max_tentativas}"
            if p.terminou:
                texto = f"Tentativas usadas: {p.tentativas} de {p.nivel.max_tentativas}"
        self.lbl_tentativas.configure(text=texto)

    def _x(self, valor: float) -> float:
        nivel = self.partida.nivel
        return 20 + (valor - nivel.minimo) / (nivel.maximo - nivel.minimo) * self.LARGURA_BARRA

    def _desenhar_barra(self) -> None:
        p = self.partida
        c = self.barra
        c.delete("all")
        topo, base = 22, 40
        c.create_rectangle(20, topo, 20 + self.LARGURA_BARRA, base, fill=CORES["painel"], outline="")
        cor = CORES["verde"] if p.venceu else CORES["destaque"]
        x1 = self._x(p.menor_possivel - 0.5) if p.menor_possivel > p.nivel.minimo else 20
        x2 = self._x(p.maior_possivel + 0.5) if p.maior_possivel < p.nivel.maximo else 20 + self.LARGURA_BARRA
        if p.perdeu:
            cor = CORES["vermelho"]
            x1, x2 = self._x(p.segredo) - 3, self._x(p.segredo) + 3
        c.create_rectangle(max(20, x1), topo, min(20 + self.LARGURA_BARRA, x2), base, fill=cor, outline="")
        for palpite in p.palpites:
            x = self._x(palpite)
            c.create_line(x, topo - 4, x, base + 4, fill=CORES["texto_suave"], width=1)
        c.create_text(20, base + 16, text=str(p.nivel.minimo), fill=CORES["texto_suave"], anchor="w",
                      font=(FONTE, 9))
        c.create_text(20 + self.LARGURA_BARRA, base + 16, text=str(p.nivel.maximo), fill=CORES["texto_suave"],
                      anchor="e", font=(FONTE, 9))
        if p.terminou:
            legenda = f"{p.segredo}"
        elif p.menor_possivel == p.maior_possivel:
            legenda = f"só pode ser {p.menor_possivel}!"
        else:
            legenda = f"faixa possível: {p.menor_possivel} a {p.maior_possivel}"
        c.create_text(20 + self.LARGURA_BARRA / 2, topo - 12, text=legenda, fill=cor, font=(FONTE, 10, "bold"))

    def _registrar_historico(self, numero: int, tag: str, seta: str) -> None:
        self.historico.configure(state="normal")
        self.historico.insert("end", f"{numero}{seta}  ", tag)
        self.historico.see("end")
        self.historico.configure(state="disabled")

    def _atualizar_ranking(self, destaque: int | None = None) -> None:
        self.tbl_ranking.delete(*self.tbl_ranking.get_children())
        for posicao, recorde in enumerate(self.placar.ranking(self.var_nivel.get()), start=1):
            minutos, segundos = divmod(int(recorde.segundos), 60)
            tempo = f"{minutos}:{segundos:02d}"
            self.tbl_ranking.insert("", "end", tags=("novo",) if posicao == destaque else (),
                                    values=(posicao, recorde.jogador[:14], recorde.tentativas, tempo))


def main() -> None:
    Aplicativo().mainloop()


if __name__ == "__main__":
    main()
