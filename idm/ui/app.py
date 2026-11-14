"""Main CustomTkinter application window for the IdM System."""

import math
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import List, Optional, Union
import customtkinter as ctk

from idm.i18n import t, toggle_language
from idm.models import CalibrationStatus, Instrument
from idm.repository import InstrumentRepository
from idm.ui.dialogs import AuditLogDialog, InstrumentFormDialog
from idm.ui.theme import (
    BORDER_GRAY,
    BOSCH_BLUE,
    BOSCH_BLUE_DARK,
    BOSCH_BLUE_LIGHT,
    BOSCH_RED,
    CARD_BORDER,
    INFO_PURPLE,
    LIGHT_BG,
    NEUTRAL_GRAY,
    SUCCESS_GREEN,
    TEXT_MAIN,
    TEXT_MUTED,
    WARNING_AMBER,
    WHITE,
    get_sheet_tag_colors,
    get_status_badge_style,
)
from idm.validators import parse_and_validate_kw

ctk.set_appearance_mode("light")

PAGE_SIZE = 25


class MeasurementApp(ctk.CTk):
    """Main application window for tracking and validating measurement instruments."""

    def __init__(self, file_path: Union[str, Path] = "Instrumentos de medição.xlsx") -> None:
        super().__init__()

        self.repo = InstrumentRepository(file_path=file_path)
        self.all_instruments: List[Instrument] = []
        self.filtered_instruments: List[Instrument] = []
        self.available_sheets: List[str] = []
        self.available_locations: List[str] = []

        # Active filter state
        self.current_query: str = ""
        self.current_mode: str = "all"
        self.current_sheet_filter: str = "all"
        self.current_location_filter: str = "all"
        self.current_status_filter: str = "all"
        self.current_page: int = 1

        self.geometry("1220x920")
        self.minsize(1020, 720)
        self.configure(fg_color=LIGHT_BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._reload_database()
        self._build_ui()

    def _reload_database(self) -> None:
        """Load instruments, sheets, and unique locations from the Excel repository."""
        try:
            self.available_sheets = self.repo.get_instrument_sheets()
            self.all_instruments = self.repo.load_all_instruments()
            self.available_locations = self.repo.get_unique_locations(self.all_instruments)
        except Exception as exc:
            messagebox.showerror(t("error_title"), t("db_error_msg", error=exc))
            self.available_sheets = ["Geral", "Perdidos", "Sucateados"]
            self.all_instruments = []
            self.available_locations = []

    def _build_ui(self) -> None:
        """Build or rebuild the entire interface (supports live PT/EN language toggle)."""
        self.title(t("app_title"))
        for child in self.winfo_children():
            child.destroy()

        self._setup_header()
        self._setup_main_container()
        self.apply_filters(reset_page=False)

    def _setup_header(self) -> None:
        self.header = ctk.CTkFrame(self, height=76, corner_radius=0, fg_color=BOSCH_BLUE)
        self.header.grid(row=0, column=0, sticky="ew")

        title_box = ctk.CTkFrame(self.header, fg_color="transparent")
        title_box.pack(side="left", padx=28, pady=12)

        ctk.CTkLabel(
            title_box,
            text=t("header_title"),
            font=ctk.CTkFont(size=21, weight="bold"),
            text_color=WHITE,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text=t("header_subtitle"),
            font=ctk.CTkFont(size=12),
            text_color=BOSCH_BLUE_LIGHT,
        ).pack(anchor="w")

        # Right-hand toolbar buttons
        actions_box = ctk.CTkFrame(self.header, fg_color="transparent")
        actions_box.pack(side="right", padx=24, pady=16)

        stats = self.repo.compute_stats(self.all_instruments)
        ctk.CTkLabel(
            actions_box,
            text=t("current_kw_badge", kw=stats.current_kw_str),
            fg_color=BOSCH_BLUE_DARK,
            text_color=WHITE,
            corner_radius=6,
            font=ctk.CTkFont(family="Courier", size=12, weight="bold"),
            padx=12,
            pady=6,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            actions_box,
            text=t("btn_new_instrument"),
            fg_color=SUCCESS_GREEN,
            hover_color="#177321",
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._open_new_instrument_modal,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions_box,
            text=t("btn_audit_log"),
            fg_color=BOSCH_BLUE_DARK,
            hover_color="#002B4D",
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._open_audit_modal,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions_box,
            text=t("btn_export_csv"),
            fg_color=BOSCH_BLUE_DARK,
            hover_color="#002B4D",
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._export_current_view,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions_box,
            text=t("lang_toggle"),
            fg_color=WHITE,
            text_color=BOSCH_BLUE,
            hover_color=BOSCH_BLUE_LIGHT,
            width=90,
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._handle_toggle_language,
        ).pack(side="left", padx=(8, 0))

    def _setup_main_container(self) -> None:
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=28, pady=16)

        # 1. KPI Summary Strip
        self.kpi_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.kpi_frame.pack(fill="x", pady=(0, 14))
        for col in range(6):
            self.kpi_frame.grid_columnconfigure(col, weight=1)
        self._render_kpi_cards()

        # 2. Search & Filter Card
        self._setup_search_and_filter_card()

        # 3. Results Header + Cards Container + Pagination Footer
        self.results_header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.results_header_frame.pack(fill="x", pady=(4, 6))

        self.results_list_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.results_list_frame.pack(fill="x")

        self.pagination_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=(12, 20))

    def _render_kpi_cards(self) -> None:
        for widget in self.kpi_frame.winfo_children():
            widget.destroy()

        stats = self.repo.compute_stats(self.all_instruments)
        kpi_specs = [
            ("all", t("kpi_all"), stats.total, BOSCH_BLUE),
            (CalibrationStatus.VALID.value, t("kpi_valid"), stats.valid, SUCCESS_GREEN),
            (CalibrationStatus.DUE_SOON.value, t("kpi_due_soon"), stats.due_soon, WARNING_AMBER),
            (CalibrationStatus.EXPIRED.value, t("kpi_expired"), stats.expired, BOSCH_RED),
            (
                "in_calibration_or_missing",
                t("kpi_in_calibration"),
                stats.in_calibration_or_missing,
                INFO_PURPLE,
            ),
            (CalibrationStatus.INACTIVE.value, t("kpi_inactive"), stats.inactive, NEUTRAL_GRAY),
        ]

        for idx, (status_key, label, value, accent_color) in enumerate(kpi_specs):
            is_selected = self.current_status_filter == status_key
            card = ctk.CTkFrame(
                self.kpi_frame,
                fg_color=WHITE,
                corner_radius=10,
                border_width=2 if is_selected else 1,
                border_color=accent_color if is_selected else BORDER_GRAY,
                cursor="hand2",
            )
            card.grid(row=0, column=idx, sticky="nsew", padx=5)

            val_lbl = ctk.CTkLabel(
                card,
                text=str(value),
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=accent_color,
            )
            val_lbl.pack(anchor="w", padx=14, pady=(12, 2))

            title_lbl = ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_MUTED,
            )
            title_lbl.pack(anchor="w", padx=14, pady=(0, 12))

            for clickable in (card, val_lbl, title_lbl):
                clickable.bind(
                    "<Button-1>",
                    lambda _e, sk=status_key: self._on_kpi_card_clicked(sk),
                )

    def _setup_search_and_filter_card(self) -> None:
        card = ctk.CTkFrame(
            self.main_container,
            fg_color=WHITE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_GRAY,
        )
        card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            card,
            text=t("search_panel_title"),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_MAIN,
        ).pack(anchor="w", padx=22, pady=(16, 8))

        # Search input row
        search_row = ctk.CTkFrame(card, fg_color="transparent")
        search_row.pack(fill="x", padx=20, pady=(0, 12))

        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text=t("search_placeholder"),
            height=42,
        )
        if self.current_query:
            self.search_entry.insert(0, self.current_query)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda _e: self.perform_search())

        ctk.CTkButton(
            search_row,
            text=t("btn_clear"),
            fg_color=NEUTRAL_GRAY,
            height=42,
            width=95,
            command=self._reset_all_filters,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            search_row,
            text=t("btn_search"),
            fg_color=BOSCH_BLUE,
            height=42,
            width=125,
            font=ctk.CTkFont(weight="bold"),
            command=self.perform_search,
        ).pack(side="right")

        # Filter controls row (Field mode radio buttons + Sheet, Location & Status dropdowns)
        controls_row = ctk.CTkFrame(card, fg_color="transparent")
        controls_row.pack(fill="x", padx=22, pady=(0, 16))

        self.filter_var = ctk.StringVar(value=self.current_mode)
        ctk.CTkLabel(
            controls_row,
            text=t("filter_mode_label"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=(0, 8))

        for label_text, mode_val in [
            (t("mode_all"), "all"),
            (t("mode_nome"), "nome"),
            (t("mode_norma"), "norma"),
            (t("mode_local"), "local"),
            (t("mode_kw"), "kw"),
        ]:
            ctk.CTkRadioButton(
                controls_row,
                text=label_text,
                variable=self.filter_var,
                value=mode_val,
                command=self.perform_search,
            ).pack(side="left", padx=(0, 14))

        # Right-aligned Dropdown Filters
        dropdown_box = ctk.CTkFrame(controls_row, fg_color="transparent")
        dropdown_box.pack(side="right")

        # Sheet filter
        sheet_display_map = {t("sheet_all"): "all"}
        for s in self.available_sheets:
            sheet_display_map[s] = s
        self._sheet_map = sheet_display_map
        inv_sheet = {v: k for k, v in sheet_display_map.items()}
        self.sheet_filter_var = ctk.StringVar(
            value=inv_sheet.get(self.current_sheet_filter, t("sheet_all"))
        )
        ctk.CTkOptionMenu(
            dropdown_box,
            values=list(sheet_display_map.keys()),
            variable=self.sheet_filter_var,
            width=135,
            height=30,
            fg_color=BOSCH_BLUE_LIGHT,
            text_color=BOSCH_BLUE,
            button_color=BOSCH_BLUE_LIGHT,
            command=lambda _val: self.perform_search(),
        ).pack(side="left", padx=5)

        # Location filter
        loc_display_map = {t("location_all"): "all"}
        for loc in self.available_locations:
            loc_display_map[loc] = loc
        self._loc_map = loc_display_map
        inv_loc = {v: k for k, v in loc_display_map.items()}
        self.loc_filter_var = ctk.StringVar(
            value=inv_loc.get(self.current_location_filter, t("location_all"))
        )
        ctk.CTkOptionMenu(
            dropdown_box,
            values=list(loc_display_map.keys()),
            variable=self.loc_filter_var,
            width=175,
            height=30,
            fg_color=BOSCH_BLUE_LIGHT,
            text_color=BOSCH_BLUE,
            button_color=BOSCH_BLUE_LIGHT,
            command=lambda _val: self.perform_search(),
        ).pack(side="left", padx=5)

        # Status filter
        status_display_map = {
            t("status_all"): "all",
            t("status_valid"): CalibrationStatus.VALID.value,
            t("status_due_soon"): CalibrationStatus.DUE_SOON.value,
            t("status_expired"): CalibrationStatus.EXPIRED.value,
            t("kpi_in_calibration"): "in_calibration_or_missing",
            t("status_inactive"): CalibrationStatus.INACTIVE.value,
        }
        self._status_map = status_display_map
        inv_status = {v: k for k, v in status_display_map.items()}
        self.status_filter_var = ctk.StringVar(
            value=inv_status.get(self.current_status_filter, t("status_all"))
        )
        ctk.CTkOptionMenu(
            dropdown_box,
            values=list(status_display_map.keys()),
            variable=self.status_filter_var,
            width=165,
            height=30,
            fg_color=BOSCH_BLUE_LIGHT,
            text_color=BOSCH_BLUE,
            button_color=BOSCH_BLUE_LIGHT,
            command=lambda _val: self.perform_search(),
        ).pack(side="left", padx=(5, 0))

    def _on_kpi_card_clicked(self, status_key: str) -> None:
        self.current_status_filter = status_key
        if status_key == CalibrationStatus.INACTIVE.value:
            self.current_sheet_filter = "all"
        inv_status = {v: k for k, v in self._status_map.items()}
        self.status_filter_var.set(inv_status.get(status_key, t("status_all")))
        self.apply_filters(reset_page=True)

    def _reset_all_filters(self) -> None:
        self.current_query = ""
        self.current_mode = "all"
        self.current_sheet_filter = "all"
        self.current_location_filter = "all"
        self.current_status_filter = "all"
        self.search_entry.delete(0, "end")
        self.filter_var.set("all")
        self.sheet_filter_var.set(t("sheet_all"))
        self.loc_filter_var.set(t("location_all"))
        self.status_filter_var.set(t("status_all"))
        self.apply_filters(reset_page=True)

    def perform_search(self) -> None:
        """Read current search & filter widget states and refresh the results list."""
        self.current_query = self.search_entry.get().strip()
        self.current_mode = self.filter_var.get()
        self.current_sheet_filter = self._sheet_map.get(self.sheet_filter_var.get(), "all")
        self.current_location_filter = self._loc_map.get(self.loc_filter_var.get(), "all")
        self.current_status_filter = self._status_map.get(self.status_filter_var.get(), "all")
        self.apply_filters(reset_page=True)

    def apply_filters(self, reset_page: bool = True) -> None:
        """Filter in-memory instruments and render current page."""
        if reset_page:
            self.current_page = 1

        self.filtered_instruments = self.repo.search_and_filter(
            query=self.current_query,
            mode=self.current_mode,
            sheet_filter=self.current_sheet_filter,
            location_filter=self.current_location_filter,
            status_filter=self.current_status_filter,
            instruments=self.all_instruments,
        )
        self._render_kpi_cards()
        self.render_results(self.filtered_instruments)

    def render_results(self, results: List[Instrument]) -> None:
        """Render the current page of matching Instrument cards and pagination controls."""
        for widget in self.results_header_frame.winfo_children():
            widget.destroy()
        for widget in self.results_list_frame.winfo_children():
            widget.destroy()
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()

        total = len(results)
        if total == 0:
            ctk.CTkLabel(
                self.results_list_frame,
                text=t("results_empty"),
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=14),
            ).pack(pady=45)
            return

        total_pages = max(1, math.ceil(total / PAGE_SIZE))
        self.current_page = max(1, min(self.current_page, total_pages))

        start_idx = (self.current_page - 1) * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total)
        page_items = results[start_idx:end_idx]

        # Results count header
        ctk.CTkLabel(
            self.results_header_frame,
            text=t("results_Showing", start=start_idx + 1, end=end_idx, total=total),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=4)

        for inst in page_items:
            self._render_instrument_card(inst)

        # Pagination footer
        if total_pages > 1:
            ctk.CTkButton(
                self.pagination_frame,
                text=t("btn_prev_page"),
                width=110,
                height=32,
                fg_color=BOSCH_BLUE if self.current_page > 1 else BORDER_GRAY,
                state="normal" if self.current_page > 1 else "disabled",
                command=self._prev_page,
            ).pack(side="left")

            ctk.CTkLabel(
                self.pagination_frame,
                text=t("page_indicator", page=self.current_page, total_pages=total_pages),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT_MAIN,
            ).pack(side="left", expand=True)

            ctk.CTkButton(
                self.pagination_frame,
                text=t("btn_next_page"),
                width=110,
                height=32,
                fg_color=BOSCH_BLUE if self.current_page < total_pages else BORDER_GRAY,
                state="normal" if self.current_page < total_pages else "disabled",
                command=self._next_page,
            ).pack(side="right")

    def _render_instrument_card(self, inst: Instrument) -> None:
        card = ctk.CTkFrame(
            self.results_list_frame,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=CARD_BORDER,
        )
        card.pack(fill="x", pady=5)

        # --- Left Pane: Sheet Tag, Status Badge, Name & Metadata ---
        left_pane = ctk.CTkFrame(card, fg_color="transparent")
        left_pane.pack(side="left", fill="x", expand=True, padx=18, pady=12)

        badges_row = ctk.CTkFrame(left_pane, fg_color="transparent")
        badges_row.pack(anchor="w")

        sheet_var = ctk.StringVar(value=inst.sheet)
        tag_bg, tag_fg = get_sheet_tag_colors(inst.sheet)
        sheet_dropdown = ctk.CTkOptionMenu(
            badges_row,
            values=self.available_sheets,
            variable=sheet_var,
            width=115,
            height=24,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=tag_bg,
            text_color=tag_fg,
            button_color=tag_bg,
            button_hover_color=tag_bg,
            command=lambda new_sheet, item=inst: self.change_instrument_sheet(item, new_sheet),
        )
        sheet_dropdown.pack(side="left", padx=(0, 8))

        badge_text, badge_bg, badge_fg = get_status_badge_style(inst)
        ctk.CTkLabel(
            badges_row,
            text=badge_text,
            fg_color=badge_bg,
            text_color=badge_fg,
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            padx=10,
            pady=2,
        ).pack(side="left")

        title_str = inst.name
        if inst.brand and inst.brand not in ("-", "?", "NÃO TEM"):
            title_str = f"{inst.name}  ·  {inst.brand}"

        ctk.CTkLabel(
            left_pane,
            text=title_str,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_MAIN,
        ).pack(anchor="w", pady=(6, 2))

        meta_parts = [
            f"📍 {t('card_location')}: {inst.location}",
            f"🔖 {t('card_norm')}: {inst.norm}",
        ]
        if inst.letter:
            meta_parts.append(f"{t('card_letter')}: {inst.letter}")
        if inst.checkout_date:
            meta_parts.append(f"📤 {t('card_checkout')}: {inst.checkout_date}")
        if inst.return_date:
            meta_parts.append(f"📥 {t('card_return')}: {inst.return_date}")

        ctk.CTkLabel(
            left_pane,
            text="   |   ".join(meta_parts),
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        # --- Right Pane: KW Readout & Action Buttons ---
        right_pane = ctk.CTkFrame(card, fg_color="transparent")
        right_pane.pack(side="right", padx=18, pady=12)

        kw_display = f"KW {inst.kw}" if inst.has_kw else t("card_no_kw")
        kw_color = BOSCH_RED if not inst.has_kw or inst.status == CalibrationStatus.EXPIRED else TEXT_MAIN

        ctk.CTkLabel(
            right_pane,
            text=kw_display,
            text_color=kw_color,
            font=ctk.CTkFont(family="Courier", size=15, weight="bold"),
            width=95,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            right_pane,
            text=t("btn_update_kw"),
            width=115,
            height=32,
            fg_color=BOSCH_BLUE,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda item=inst: self.update_kw(item),
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            right_pane,
            text=t("btn_checkout"),
            width=130,
            height=32,
            fg_color=BOSCH_BLUE_LIGHT,
            text_color=BOSCH_BLUE,
            hover_color="#C5E2F6",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda item=inst: self.record_checkout(item),
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            right_pane,
            text=t("btn_edit"),
            width=70,
            height=32,
            fg_color=NEUTRAL_GRAY,
            font=ctk.CTkFont(size=12),
            command=lambda item=inst: self._open_edit_instrument_modal(item),
        ).pack(side="left", padx=(4, 0))

    def _prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self.render_results(self.filtered_instruments)

    def _next_page(self) -> None:
        self.current_page += 1
        self.render_results(self.filtered_instruments)

    def change_instrument_sheet(self, inst: Instrument, target_sheet: str) -> None:
        """Move an instrument row to another worksheet after user confirmation."""
        if inst.sheet == target_sheet:
            return

        confirmed = messagebox.askyesno(
            t("confirm_move_title"),
            t(
                "confirm_move_msg",
                name=inst.name,
                norm=inst.norm,
                old_sheet=inst.sheet,
                new_sheet=target_sheet,
            ),
        )
        if not confirmed:
            self.render_results(self.filtered_instruments)
            return

        try:
            self.repo.move_instrument_sheet(inst, target_sheet)
            messagebox.showinfo(
                t("move_success_title"),
                t("move_success_msg", sheet=target_sheet),
            )
            self._reload_and_refresh()
        except Exception as exc:
            messagebox.showerror(t("error_title"), str(exc))
            self.render_results(self.filtered_instruments)

    def update_kw(self, inst: Instrument) -> None:
        """Prompt user for a new KW, strictly validate WW/YY, and update database."""
        dialog = ctk.CTkInputDialog(
            text=t("kw_dialog_prompt"),
            title=t("kw_dialog_title"),
        )
        raw_kw = dialog.get_input()
        if raw_kw is None or not raw_kw.strip():
            return

        is_valid, canonical_kw = parse_and_validate_kw(raw_kw)
        if not is_valid:
            messagebox.showerror(
                t("kw_invalid_title"),
                t("kw_invalid_msg", value=raw_kw),
            )
            return

        try:
            saved_kw = self.repo.update_kw(inst, canonical_kw)
            messagebox.showinfo("OK", t("kw_updated_msg", kw=saved_kw))
            self._reload_and_refresh()
        except Exception as exc:
            messagebox.showerror(t("error_title"), str(exc))

    def record_checkout(self, inst: Instrument) -> None:
        """Record checkout date (DATA DE RETIRADA) when sending an instrument to calibration."""
        if not messagebox.askyesno(
            t("checkout_confirm_title"),
            t("checkout_confirm_msg", name=inst.name, norm=inst.norm),
        ):
            return
        try:
            self.repo.record_checkout(inst)
            messagebox.showinfo("OK", t("checkout_success_msg"))
            self._reload_and_refresh()
        except Exception as exc:
            messagebox.showerror(t("error_title"), str(exc))

    def _open_new_instrument_modal(self) -> None:
        InstrumentFormDialog(
            parent=self,
            repo=self.repo,
            available_sheets=self.available_sheets,
            available_locations=self.available_locations,
            on_saved=self._reload_and_refresh,
            instrument=None,
        )

    def _open_edit_instrument_modal(self, inst: Instrument) -> None:
        InstrumentFormDialog(
            parent=self,
            repo=self.repo,
            available_sheets=self.available_sheets,
            available_locations=self.available_locations,
            on_saved=self._reload_and_refresh,
            instrument=inst,
        )

    def _open_audit_modal(self) -> None:
        AuditLogDialog(parent=self, repo=self.repo)

    def _export_current_view(self) -> None:
        target_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="relatorio_instrumentos_idm.csv",
        )
        if not target_path:
            return
        try:
            out = self.repo.export_to_csv(self.filtered_instruments, target_path)
            messagebox.showinfo(
                t("export_success_title"),
                t("export_success_msg", count=len(self.filtered_instruments), path=out),
            )
        except Exception as exc:
            messagebox.showerror(t("error_title"), str(exc))

    def _handle_toggle_language(self) -> None:
        toggle_language()
        self._build_ui()

    def _reload_and_refresh(self) -> None:
        self._reload_database()
        self.apply_filters(reset_page=False)
