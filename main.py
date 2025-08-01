#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Rodadas de Negócios – v2
-----------------------------------
• Aloca participantes em mesas minimizando repetições de pares.
• Exporta:
   - PNG por participante (~/Downloads/rodada_de_negocio)
   - Excel resumo (cronograma.xlsx) na mesma pasta
• Interface: Tkinter
"""

import random
import itertools
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
import matplotlib
matplotlib.use("Agg")              # backend não-GUI
import matplotlib.pyplot as plt


# ------------------------------------------------------------------
#  ALGORITMO DE GERAÇÃO DAS MESAS
# ------------------------------------------------------------------
def generate_schedule(n_participants: int,
                      n_tables: int,
                      chairs: int,
                      n_rounds: int,
                      seed: int = 42):
    """Retorna lista[rodada] -> lista[mesa] -> lista[pessoas ou None]."""
    random.seed(seed)
    participants = [f"Participante {i+1}" for i in range(n_participants)]

    capacity = n_tables * chairs
    pad = capacity - n_participants
    previous_pairs = set()
    schedule = []

    for _ in range(n_rounds):
        attempts = 0
        while attempts < 1000:
            random.shuffle(participants)
            padded = participants + [None] * pad
            tables = [padded[i*chairs:(i+1)*chairs] for i in range(n_tables)]

            # colisões?
            valid = True
            new_pairs = set()
            for tbl in tables:
                pessoas = [p for p in tbl if p]
                for pair in itertools.combinations(pessoas, 2):
                    if pair in previous_pairs:
                        valid = False
                        break
                    new_pairs.add(pair)
                if not valid:
                    break
            if valid:
                schedule.append(tables)
                previous_pairs.update(new_pairs)
                break
            attempts += 1
        else:  # não encontrou sem colisão
            padded = participants + [None] * pad
            tables = [padded[i*chairs:(i+1)*chairs] for i in range(n_tables)]
            schedule.append(tables)
            for tbl in tables:
                pessoas = [p for p in tbl if p]
                previous_pairs.update(itertools.combinations(pessoas, 2))

    return schedule


# ------------------------------------------------------------------
#  EXPORTA PLANILHA EXCEL
# ------------------------------------------------------------------
def export_excel(schedule, output_dir: Path):
    n_rounds = len(schedule)
    mapping = {}  # participante -> list de mesas

    long_rows = []  # para aba Detalhado

    for r_idx, tables in enumerate(schedule, start=1):
        for t_idx, tbl in enumerate(tables, start=1):
            for p in tbl:
                if not p:
                    continue
                mapping.setdefault(p, []).append(t_idx)
                long_rows.append({"Rodada": r_idx, "Mesa": t_idx, "Participante": p})

    # Aba "Geral"
    df_geral = pd.DataFrame(mapping).T
    df_geral.columns = [f"Rodada {i}" for i in range(1, n_rounds + 1)]
    df_geral.index.name = "Participante"

    # Aba "Detalhado"
    df_long = pd.DataFrame(long_rows)

    dest = output_dir / "cronograma.xlsx"
    with pd.ExcelWriter(dest, engine="openpyxl", mode="w") as writer:
        df_geral.to_excel(writer, sheet_name="Geral")
        df_long.to_excel(writer, sheet_name="Detalhado", index=False)


# ------------------------------------------------------------------
#  EXPORTA IMAGENS
# ------------------------------------------------------------------
def export_images(schedule, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    n_rounds = len(schedule)
    mapping = {}

    for r_idx, tables in enumerate(schedule, start=1):
        for t_idx, tbl in enumerate(tables, start=1):
            for p in tbl:
                if not p:
                    continue
                mapping.setdefault(p, []).append(t_idx)

    for participant, mesas in mapping.items():
        linhas = [f"Rodada {r} | Mesa {m}" for r, m in enumerate(mesas, start=1)]

        fig_h = max(2.5, 0.55 * (n_rounds + 1))
        fig, ax = plt.subplots(figsize=(4, fig_h))
        ax.axis('off')

        # título
        ax.text(0.5, 1.0, participant, ha='center', va='top',
                fontsize=12, fontweight='bold', transform=ax.transAxes)

        # linhas
        for idx, txt in enumerate(linhas):
            y = 0.9 - idx * 0.08
            ax.text(0.5, y, txt, ha='center', va='center', fontsize=10, transform=ax.transAxes)

        fig.tight_layout()
        fname = output_dir / f"{participant.lower().replace(' ', '_')}.png"
        fig.savefig(fname, dpi=300, bbox_inches='tight')
        plt.close(fig)


# ------------------------------------------------------------------
#  INTERFACE TKINTER
# ------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Rodadas de Negócios")
        self.geometry("370x300")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        ttk.Style(self).theme_use("clam")
        self.entries = {}
        params = [
            ("Participantes", "30"),
            ("Mesas", "5"),
            ("Cadeiras por mesa", "6"),
            ("Rodadas", "4")
        ]
        for idx, (label, default) in enumerate(params):
            ttk.Label(self, text=f"{label}:").grid(row=idx, column=0, padx=12, pady=6, sticky="e")
            ent = ttk.Entry(self, width=10)
            ent.insert(0, default)
            ent.grid(row=idx, column=1, sticky="w")
            self.entries[label] = ent

        self.btn_generate = ttk.Button(self, text="Gerar Rodadas", command=self.on_generate)
        self.btn_generate.grid(row=len(params), column=0, columnspan=2, pady=12)

        self.status = tk.StringVar(value="Preencha os parâmetros e clique em Gerar")
        ttk.Label(self, textvariable=self.status, wraplength=330, anchor="center")\
            .grid(row=len(params)+1, column=0, columnspan=2, pady=4, padx=10)

    # --------------------------------------------------------------
    def on_generate(self):
        try:
            n = int(self.entries["Participantes"].get())
            m = int(self.entries["Mesas"].get())
            c = int(self.entries["Cadeiras por mesa"].get())
            r = int(self.entries["Rodadas"].get())
        except ValueError:
            messagebox.showerror("Erro", "Todos os campos devem ser números inteiros.")
            return

        if any(x <= 0 for x in (n, m, c, r)):
            messagebox.showerror("Erro", "Valores precisam ser maiores que zero.")
            return
        if n > m * c:
            messagebox.showerror("Erro",
                                 f"Capacidade insuficiente: {n} participantes para {m*c} lugares.")
            return
        if c < 2:
            messagebox.showerror("Erro", "Cada mesa deve ter pelo menos 2 cadeiras.")
            return

        self.status.set("Gerando cronograma, aguarde…")
        self.update_idletasks()

        schedule = generate_schedule(n, m, c, r)
        destino = Path.home() / "Downloads" / "rodada_de_negocio"
        export_images(schedule, destino)
        export_excel(schedule, destino)

        self.status.set(f"Concluído! Arquivos salvos em: {destino}")
        messagebox.showinfo("Sucesso", "Rodadas geradas e exportadas com êxito!")


# ------------------------------------------------------------------
if __name__ == "__main__":
    App().mainloop()
