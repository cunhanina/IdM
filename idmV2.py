import customtkinter as ctk
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime
from unidecode import unidecode
from tkinter import messagebox
import re

# --- Bosch Digital Design Palette ---
BOSCH_BLUE = "#005691"
BOSCH_RED = "#ED0007"
SUCCESS_GREEN = "#1F922B"
LIGHT_BG = "#EFF1F2"
WHITE = "#FFFFFF"
TEXT_MAIN = "#191919"
BORDER_GRAY = "#D1D5DB"

ctk.set_appearance_mode("light")

class MeasurementApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ETS - Instrument Management v3.0")
        self.geometry("1100x900")
        self.configure(fg_color=LIGHT_BG)

        self.file_path = "Instrumentos de medição.xlsx"
        self.available_sheets = []
        self.get_sheet_list()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_header()
        self.setup_main_area()

    def get_sheet_list(self):
        try:
            wb = load_workbook(self.file_path, read_only=True)
            self.available_sheets = wb.sheetnames
        except:
            self.available_sheets = ["Geral", "Perdidos"]

    def setup_header(self):
        self.header = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=BOSCH_BLUE)
        self.header.grid(row=0, column=0, sticky="ew")
        
        ctk.CTkLabel(
            self.header, 
            text="GESTÃO DE INSTRUMENTOS | ETS", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=WHITE
        ).pack(side="left", padx=30, pady=20)

    def setup_main_area(self):
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.show_dashboard()

    def normalize_kw(self, text):
        """Removes all non-numeric characters to make search flexible"""
        if not text: return ""
        return re.sub(r'[^0-9]', '', str(text))

    def show_dashboard(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        card = ctk.CTkFrame(self.main_container, fg_color=WHITE, corner_radius=12, border_width=1, border_color=BORDER_GRAY)
        card.pack(fill="x", pady=(10, 20))

        ctk.CTkLabel(card, text="Painel de Busca", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=25, pady=(20, 10))

        search_row = ctk.CTkFrame(card, fg_color="transparent")
        search_row.pack(fill="x", padx=20, pady=(0, 20))

        self.search_entry = ctk.CTkEntry(search_row, placeholder_text="Pesquise por Nome, Norma ou KW (Ex: 0325 ou 03/25)", height=48)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        self.search_btn = ctk.CTkButton(search_row, text="Buscar", fg_color=BOSCH_BLUE, height=48, width=140, 
                                        font=ctk.CTkFont(weight="bold"), command=self.perform_search)
        self.search_btn.pack(side="right")

        self.filter_var = ctk.StringVar(value="nome")
        filter_frame = ctk.CTkFrame(card, fg_color="transparent")
        filter_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        for text, mode in [("Nome", "nome"), ("Norma", "norma"), ("KW", "kw")]:
            ctk.CTkRadioButton(filter_frame, text=text, variable=self.filter_var, value=mode).pack(side="left", padx=(0, 25))

    def perform_search(self):
        query = self.search_entry.get().strip()
        mode = self.filter_var.get()
        if not query: return
        
        normalized_query = self.normalize_kw(query) if mode == "kw" else unidecode(query.lower())
        
        try:
            wb = load_workbook(self.file_path, data_only=True)
            results = []
            
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                rows = list(ws.iter_rows(values_only=True))
                if not rows: continue
                
                for idx, row in enumerate(rows[1:], start=2):
                    if not any(row): continue
                    match = False
                    
                    if mode == "nome" and len(row) > 2:
                        if normalized_query in unidecode(str(row[2]).lower()): match = True
                    elif mode == "norma" and len(row) > 4:
                        if query in str(row[4]): match = True
                    elif mode == "kw" and len(row) > 7:
                        # Flexible KW match: Compare only numbers
                        if normalized_query in self.normalize_kw(row[7]): match = True

                    if match:
                        results.append({"data": row, "sheet": sheet_name, "row_idx": idx})

            self.render_results(results)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao acessar base de dados: {e}")

    def render_results(self, results):
        for widget in self.main_container.winfo_children()[1:]:
            widget.destroy()

        if not results:
            ctk.CTkLabel(self.main_container, text="Nenhum resultado encontrado para este critério.", text_color="gray60").pack(pady=50)
            return

        for res in results:
            data = res["data"]
            card = ctk.CTkFrame(self.main_container, fg_color=WHITE, corner_radius=10, border_width=1, border_color="#E5E7EB")
            card.pack(fill="x", pady=6)

            # --- Left: Meta & Identity ---
            left_pane = ctk.CTkFrame(card, fg_color="transparent")
            left_pane.pack(side="left", padx=20, pady=15)

            # Dropdown for Sheet Tag
            sheet_var = ctk.StringVar(value=res['sheet'])
            tag_color = BOSCH_RED if "Perdido" in res['sheet'] else "#D1E9FF"
            
            sheet_dropdown = ctk.CTkOptionMenu(
                left_pane, values=self.available_sheets, variable=sheet_var,
                width=110, height=24, font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=tag_color, text_color=BOSCH_BLUE if tag_color != BOSCH_RED else WHITE,
                button_color=tag_color, button_hover_color=tag_color,
                command=lambda new_sheet, r=res: self.change_instrument_sheet(r, new_sheet)
            )
            sheet_dropdown.pack(anchor="w")

            ctk.CTkLabel(left_pane, text=f"{data[2]}", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(5, 0))
            ctk.CTkLabel(left_pane, text=f"Norma: {data[4]} | ID: {data[0]}", font=ctk.CTkFont(size=12), text_color="gray50").pack(anchor="w")

            # --- Right: KW Controls ---
            right_pane = ctk.CTkFrame(card, fg_color="transparent")
            right_pane.pack(side="right", padx=20)

            kw_text = str(data[7]) if len(data) > 7 else "Sem KW"
            kw_color = BOSCH_RED if "Sem" in kw_text else "#1F2937"
            
            ctk.CTkLabel(right_pane, text=kw_text, text_color=kw_color, font=ctk.CTkFont(family="Courier", size=15, weight="bold")).pack(side="left", padx=20)
            
            ctk.CTkButton(right_pane, text="Atualizar KW", width=110, fg_color=BOSCH_BLUE, 
                          command=lambda r=res: self.update_kw(r)).pack(side="right")

    def change_instrument_sheet(self, res, target_sheet):
        """Moves a row from one sheet to another"""
        if res['sheet'] == target_sheet: return
        
        if messagebox.askyesno("Confirmar Mudança", f"Mover este instrumento para a aba '{target_sheet}'?"):
            try:
                wb = load_workbook(self.file_path)
                source_ws = wb[res['sheet']]
                target_ws = wb[target_sheet]
                
                # Copy data to new sheet
                row_data = [cell.value for cell in source_ws[res['row_idx']]]
                target_ws.append(row_data)
                
                # Remove from old sheet
                source_ws.delete_rows(res['row_idx'])
                
                wb.save(self.file_path)
                messagebox.showinfo("Sucesso", "Localização atualizada.")
                self.perform_search() # Refresh
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao mover: {e}")

    def update_kw(self, res):
        dialog = ctk.CTkInputDialog(text="Novo KW (WW/YY):", title="Atualizar Validade")
        new_kw = dialog.get_input()

        if new_kw:
            # Simple validation check
            if not re.match(r"^[0-9]{2}/[0-9]{2}$", new_kw) and not re.match(r"^[0-9]{4}$", new_kw):
                messagebox.showwarning("Aviso", "Formato sugerido: WW/YY")
            
            try:
                wb = load_workbook(self.file_path)
                ws = wb[res["sheet"]]
                ws.cell(row=res["row_idx"], column=8).value = new_kw
                ws.cell(row=res["row_idx"], column=7).value = datetime.now().strftime("%d/%m/%Y %H:%M")
                wb.save(self.file_path)
                self.perform_search()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

if __name__ == "__main__":
    app = MeasurementApp()
    app.mainloop()