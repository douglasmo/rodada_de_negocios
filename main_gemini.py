import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
import threading
import random
import itertools
from PIL import Image # <- Importação da nova biblioteca

class RodadaNegociosApp:
    """
    Aplicação com interface gráfica para gerar e gerenciar rodadas de negócios.
    Versão com exportação de imagens para subpasta e compilação de PDF.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Rodadas de Negócios")
        self.root.geometry("450x350")

        style = ttk.Style(self.root)
        style.theme_use("clam")

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.entries = {}
        fields = {
            "Nº de Participantes (N):": "participantes",
            "Nº de Mesas (M):": "mesas",
            "Cadeiras por Mesa (C):": "cadeiras",
            "Nº de Rodadas (R):": "rodadas"
        }

        for i, (text, key) in enumerate(fields.items()):
            label = ttk.Label(main_frame, text=text)
            label.grid(row=i, column=0, padx=5, pady=10, sticky="w")
            
            entry = ttk.Entry(main_frame, width=15)
            entry.grid(row=i, column=1, padx=5, pady=10, sticky="ew")
            entry.bind("<KeyRelease>", self.validate_inputs)
            self.entries[key] = entry

        self.generate_button = ttk.Button(main_frame, text="Gerar Rodadas", command=self.run_generation_thread, state=tk.DISABLED)
        self.generate_button.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        self.progress_label = ttk.Label(main_frame, text="Status: Aguardando entrada...")
        self.progress_label.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="w")
        
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=len(fields) + 2, column=0, columnspan=2, sticky="ew", pady=(5,0))

        main_frame.columnconfigure(1, weight=1)
        self.validate_inputs()

    def validate_inputs(self, event=None):
        try:
            n = int(self.entries["participantes"].get() or 0)
            m = int(self.entries["mesas"].get() or 0)
            c = int(self.entries["cadeiras"].get() or 0)
            r = int(self.entries["rodadas"].get() or 0)

            valid_params = all(x > 0 for x in [n, m, c, r])
            valid_capacity = (n <= m * c)
            valid_chairs = (c >= 2)

            if not valid_params:
                self.progress_label.config(text="Status: Preencha todos os campos com inteiros positivos.")
                self.generate_button.config(state=tk.DISABLED)
            elif not valid_chairs:
                self.progress_label.config(text="Status: Erro! Cada mesa deve ter no mínimo 2 cadeiras.")
                self.generate_button.config(state=tk.DISABLED)
            elif not valid_capacity:
                self.progress_label.config(text=f"Status: Erro! Capacidade insuficiente ({m*c} lugares para {n} pessoas).")
                self.generate_button.config(state=tk.DISABLED)
            else:
                self.progress_label.config(text="Status: Pronto para gerar as rodadas.")
                self.generate_button.config(state=tk.NORMAL)
        except ValueError:
            self.progress_label.config(text="Status: Por favor, insira apenas números inteiros.")
            self.generate_button.config(state=tk.DISABLED)

    def run_generation_thread(self):
        self.generate_button.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0
        self.progress_label.config(text="Status: Gerando... Por favor, aguarde.")
        
        try:
            params = {key: int(val.get()) for key, val in self.entries.items()}
            thread = threading.Thread(target=self.generate_schedules, args=(params,))
            thread.start()
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")
            self.reset_ui()
            
    def update_progress(self, value, text):
        self.progress_bar["value"] = value
        self.progress_label.config(text=f"Status: {text}")
        self.root.update_idletasks()
    
    def reset_ui(self):
        self.validate_inputs()

    def generate_schedules(self, params):
        N = params["participantes"]
        M = params["mesas"]
        C = params["cadeiras"]
        R = params["rodadas"]
        
        total_slots = M * C
        participantes = [f"Participante {i+1}" for i in range(N)]
        vazios = ["Vazio"] * (total_slots - N)
        full_list = participantes + vazios
        
        all_rounds_schedules = []
        pairs_seen = set()
        
        fixed_participant = full_list[0]
        rotatable_list = full_list[1:]

        for r_idx in range(R):
            progress_val = (r_idx / (R + 3)) * 100
            self.root.after(0, self.update_progress, progress_val, f"Otimizando Rodada {r_idx + 1}/{R}...")
            
            best_round_schedule, min_collisions = None, float('inf')
            num_attempts = 100

            for _ in range(num_attempts):
                random.shuffle(rotatable_list)
                candidate_list = [fixed_participant] + rotatable_list
                current_schedule = [candidate_list[i*C : (i+1)*C] for i in range(M)]
                
                current_collisions = 0
                for table in current_schedule:
                    real_participants_in_table = [p for p in table if p != "Vazio"]
                    if len(real_participants_in_table) < 2: continue
                    for pair in itertools.combinations(real_participants_in_table, 2):
                        if tuple(sorted(pair)) in pairs_seen:
                            current_collisions += 1
                
                if current_collisions < min_collisions:
                    min_collisions, best_round_schedule = current_collisions, current_schedule
                if min_collisions == 0: break
            
            all_rounds_schedules.append(best_round_schedule)
            for table in best_round_schedule:
                real_participants_in_table = [p for p in table if p != "Vazio"]
                if len(real_participants_in_table) < 2: continue
                for pair in itertools.combinations(real_participants_in_table, 2):
                    pairs_seen.add(tuple(sorted(pair)))

        # --- NOVA ESTRUTURA DE PASTAS ---
        output_dir = Path.home() / "Downloads" / "rodada_de_negocio"
        images_dir = output_dir / "imagens"
        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        
        self.root.after(0, self.update_progress, 80, "Gerando arquivo Excel...")
        self.export_to_excel_pivot(all_rounds_schedules, participantes, R, output_dir)
        
        # --- GERA IMAGENS E OBTÉM OS CAMINHOS ---
        generated_image_paths = self.generate_participant_images(all_rounds_schedules, participantes, images_dir, R)

        # --- NOVA ETAPA: COMPILAR PDF ---
        self.root.after(0, self.update_progress, 95, "Compilando PDF com todas as agendas...")
        self.compile_images_to_pdf(generated_image_paths, output_dir)

        self.root.after(0, self.update_progress, 100, "Concluído com sucesso!")
        messagebox.showinfo("Sucesso", f"Rodadas geradas!\nArquivos (incluindo PDF) salvos em:\n{output_dir}")
        self.root.after(0, self.reset_ui)

    def export_to_excel_pivot(self, schedules, participantes_list, R, output_dir):
        flat_data = []
        for r_idx, round_schedule in enumerate(schedules):
            for m_idx, table in enumerate(round_schedule):
                for participante in table:
                    if participante in participantes_list:
                        flat_data.append({"Participante": participante, "Rodada": f"Rodada {r_idx + 1}", "Mesa": m_idx + 1})
        df_long = pd.DataFrame(flat_data)
        if not df_long.empty:
            pivot_df = df_long.pivot_table(index="Participante", columns="Rodada", values="Mesa")
            rodada_cols = [f"Rodada {i+1}" for i in range(R)]
            participante_index = [f"Participante {i+1}" for i in range(len(participantes_list))]
            pivot_df = pivot_df.reindex(index=participante_index, columns=rodada_cols)
            excel_path = output_dir / "resumo_rodadas_geral.xlsx"
            pivot_df.to_excel(excel_path, engine='openpyxl')

    def generate_participant_images(self, schedules, participantes_list, images_dir, R):
        """Gera imagens na pasta especificada e retorna uma lista de caminhos."""
        num_participantes = len(participantes_list)
        generated_paths = [] # Lista para armazenar os caminhos das imagens geradas
        
        for i, participante in enumerate(participantes_list):
            progress_val = 80 + (i / num_participantes) * 15 # Ajusta progresso para dar espaço ao PDF
            self.root.after(0, self.update_progress, progress_val, f"Gerando imagem para {participante}...")

            participante_schedule = []
            for r_idx, round_schedule in enumerate(schedules):
                for m_idx, table in enumerate(round_schedule):
                    if participante in table:
                        participante_schedule.append([f"Rodada {r_idx + 1}", f"Mesa {m_idx + 1}"])
                        break
            
            if not participante_schedule: continue

            fig_height = 2.0 + 0.4 * len(participante_schedule)
            fig, ax = plt.subplots(figsize=(5, fig_height))
            ax.axis('off')
            participante_num = participante.split(" ")[1]
            ax.set_title(f"Participante {participante_num}", fontsize=18, pad=10, weight='bold')

            table_data = plt.table(
                cellText=participante_schedule, colLabels=["Rodada", "Mesa"], loc='center',
                cellLoc='center', colWidths=[0.4, 0.4])
            table_data.auto_set_font_size(False); table_data.set_fontsize(12); table_data.scale(1.2, 1.4)
            plt.tight_layout(pad=1.0)
            
            image_filename = f"{participante.replace(' ', '_')}.png"
            image_path = images_dir / image_filename # Salva na pasta 'imagens'
            plt.savefig(image_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            generated_paths.append(image_path) # Adiciona o caminho à lista
        
        return generated_paths

    def compile_images_to_pdf(self, image_paths, output_dir):
        """Compila uma lista de imagens em um único arquivo PDF."""
        if not image_paths:
            return

        # Abre a primeira imagem e a converte para RGB (evita problemas com transparência)
        try:
            img1 = Image.open(image_paths[0]).convert('RGB')
            
            # Abre as imagens restantes
            other_imgs = [Image.open(p).convert('RGB') for p in image_paths[1:]]
            
            pdf_path = output_dir / "agendas_compiladas.pdf"
            
            # Salva o PDF com todas as imagens anexadas
            img1.save(
                pdf_path, 
                "PDF", 
                resolution=100.0, 
                save_all=True, 
                append_images=other_imgs
            )
        except Exception as e:
            messagebox.showwarning("Erro de PDF", f"Não foi possível criar o arquivo PDF.\nErro: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RodadaNegociosApp(root)
    root.mainloop()