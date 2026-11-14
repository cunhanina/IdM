"""Modal dialogs for creating/editing instruments and viewing the Audit Log."""

from tkinter import messagebox
from typing import Callable, List, Optional
import customtkinter as ctk

from idm.i18n import t
from idm.models import Instrument
from idm.repository import InstrumentRepository
from idm.ui.theme import (
    BORDER_GRAY,
    BOSCH_BLUE,
    BOSCH_BLUE_LIGHT,
    CARD_BORDER,
    LIGHT_BG,
    NEUTRAL_GRAY,
    TEXT_MAIN,
    TEXT_MUTED,
    WHITE,
)
from idm.validators import parse_and_validate_kw


class InstrumentFormDialog(ctk.CTkToplevel):
    """Modal dialog to create a new instrument or edit an existing instrument."""

    def __init__(
        self,
        parent: ctk.CTk,
        repo: InstrumentRepository,
        available_sheets: List[str],
        available_locations: List[str],
        on_saved: Callable[[], None],
        instrument: Optional[Instrument] = None,
    ) -> None:
        super().__init__(parent)
        self.repo = repo
        self.available_sheets = available_sheets or ["Geral", "Perdidos", "Sucateados"]
        self.available_locations = available_locations
        self.on_saved = on_saved
        self.instrument = instrument

        is_edit = instrument is not None
        self.title(t("modal_edit_title") if is_edit else t("modal_new_title"))
        self.geometry("520x540")
        self.configure(fg_color=LIGHT_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_form()

    def _build_form(self) -> None:
        card = ctk.CTkFrame(
            self,
            fg_color=WHITE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_GRAY,
        )
        card.pack(fill="both", expand=True, padx=20, pady=20)

        title_text = t("modal_edit_title") if self.instrument else t("modal_new_title")
        ctk.CTkLabel(
            card,
            text=title_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=BOSCH_BLUE,
        ).pack(anchor="w", padx=24, pady=(18, 12))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24)
        form.grid_columnconfigure(1, weight=1)

        # 1. Sheet selector (only editable when creating a new instrument)
        ctk.CTkLabel(form, text=t("field_sheet"), font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", pady=8, padx=(0, 12)
        )
        self.sheet_var = ctk.StringVar(
            value=self.instrument.sheet if self.instrument else self.available_sheets[0]
        )
        self.sheet_menu = ctk.CTkOptionMenu(
            form,
            values=self.available_sheets,
            variable=self.sheet_var,
            fg_color=BOSCH_BLUE,
            state="disabled" if self.instrument else "normal",
        )
        self.sheet_menu.grid(row=0, column=1, sticky="ew", pady=8)

        # 2. Physical Location (ComboBox allowing existing or new location)
        ctk.CTkLabel(form, text=t("field_location"), font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=0, sticky="w", pady=8, padx=(0, 12)
        )
        loc_values = self.available_locations or ["ARMÁRIO 35", "BANCADA 1", "CNC 40"]
        self.location_combo = ctk.CTkComboBox(form, values=loc_values)
        self.location_combo.set(self.instrument.location if self.instrument else loc_values[0])
        self.location_combo.grid(row=1, column=1, sticky="ew", pady=8)

        # 3. Description / Name
        ctk.CTkLabel(form, text=t("field_name"), font=ctk.CTkFont(weight="bold")).grid(
            row=2, column=0, sticky="w", pady=8, padx=(0, 12)
        )
        self.name_entry = ctk.CTkEntry(
            form, placeholder_text="Ex: Paquímetro Digital 150mm"
        )
        if self.instrument:
            self.name_entry.insert(0, self.instrument.name)
        self.name_entry.grid(row=2, column=1, sticky="ew", pady=8)

        # 4. Brand
        ctk.CTkLabel(form, text=t("field_brand"), font=ctk.CTkFont(weight="bold")).grid(
            row=3, column=0, sticky="w", pady=8, padx=(0, 12)
        )
        self.brand_entry = ctk.CTkEntry(form, placeholder_text="Ex: MITUTOYO")
        if self.instrument and self.instrument.brand != "-":
            self.brand_entry.insert(0, self.instrument.brand)
        self.brand_entry.grid(row=3, column=1, sticky="ew", pady=8)

        # 5. Norm / Serial Number
        ctk.CTkLabel(form, text=t("field_norm"), font=ctk.CTkFont(weight="bold")).grid(
            row=4, column=0, sticky="w", pady=8, padx=(0, 12)
        )
        self.norm_entry = ctk.CTkEntry(form, placeholder_text="Ex: 4738440078-009304")
        if self.instrument and self.instrument.norm != "-":
            self.norm_entry.insert(0, self.instrument.norm)
        self.norm_entry.grid(row=4, column=1, sticky="ew", pady=8)

        # 6. Letter / Code
        ctk.CTkLabel(form, text=t("field_letter"), font=ctk.CTkFont(weight="bold")).grid(
            row=5, column=0, sticky="w", pady=8, padx=(0, 12)
        )
        self.letter_entry = ctk.CTkEntry(form, placeholder_text="Ex: A, B (opcional)")
        if self.instrument and self.instrument.letter:
            self.letter_entry.insert(0, self.instrument.letter)
        self.letter_entry.grid(row=5, column=1, sticky="ew", pady=8)

        # 7. Calibration KW
        ctk.CTkLabel(form, text=t("field_kw"), font=ctk.CTkFont(weight="bold")).grid(
            row=6, column=0, sticky="w", pady=8, padx=(0, 12)
        )
        self.kw_entry = ctk.CTkEntry(form, placeholder_text="WW/YY (Ex: 14/27)")
        if self.instrument and self.instrument.kw:
            self.kw_entry.insert(0, self.instrument.kw)
        self.kw_entry.grid(row=6, column=1, sticky="ew", pady=8)

        # Footer Buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(12, 20))

        ctk.CTkButton(
            btn_row,
            text=t("btn_cancel"),
            fg_color=NEUTRAL_GRAY,
            width=120,
            command=self.destroy,
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            btn_row,
            text=t("btn_save"),
            fg_color=BOSCH_BLUE,
            font=ctk.CTkFont(weight="bold"),
            width=140,
            command=self._handle_save,
        ).pack(side="right")

    def _handle_save(self) -> None:
        loc = self.location_combo.get().strip()
        name = self.name_entry.get().strip()
        brand = self.brand_entry.get().strip()
        norm = self.norm_entry.get().strip()
        letter = self.letter_entry.get().strip()
        raw_kw = self.kw_entry.get().strip()

        if not loc or not name or not norm:
            messagebox.showwarning(t("error_title"), t("validation_required"), parent=self)
            return

        if raw_kw:
            is_valid, _ = parse_and_validate_kw(raw_kw)
            if not is_valid:
                messagebox.showerror(
                    t("kw_invalid_title"),
                    t("kw_invalid_msg", value=raw_kw),
                    parent=self,
                )
                return

        try:
            if self.instrument:
                self.repo.edit_instrument(
                    inst=self.instrument,
                    location=loc,
                    letter=letter,
                    name=name,
                    brand=brand,
                    norm=norm,
                    kw=raw_kw,
                )
            else:
                self.repo.add_instrument(
                    sheet=self.sheet_var.get(),
                    location=loc,
                    letter=letter,
                    name=name,
                    brand=brand,
                    norm=norm,
                    kw=raw_kw,
                )
            messagebox.showinfo("OK", t("save_success_msg"), parent=self)
            self.on_saved()
            self.destroy()
        except Exception as exc:
            messagebox.showerror(t("error_title"), str(exc), parent=self)


class AuditLogDialog(ctk.CTkToplevel):
    """Modal window displaying the Audit_Log history from the Excel database."""

    def __init__(self, parent: ctk.CTk, repo: InstrumentRepository) -> None:
        super().__init__(parent)
        self.repo = repo
        self.title(t("audit_modal_title"))
        self.geometry("860x540")
        self.configure(fg_color=LIGHT_BG)
        self.transient(parent)
        self.grab_set()

        self._build_view()

    def _build_view(self) -> None:
        header = ctk.CTkFrame(self, fg_color=BOSCH_BLUE, corner_radius=0, height=56)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text=t("audit_modal_title"),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=WHITE,
        ).pack(side="left", padx=24, pady=14)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        entries = self.repo.get_audit_log(limit=100)
        if not entries:
            ctk.CTkLabel(
                scroll,
                text=t("audit_empty"),
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=14),
            ).pack(pady=40)
            return

        for entry in entries:
            row_card = ctk.CTkFrame(
                scroll,
                fg_color=WHITE,
                corner_radius=8,
                border_width=1,
                border_color=CARD_BORDER,
            )
            row_card.pack(fill="x", pady=4)

            top_line = ctk.CTkFrame(row_card, fg_color="transparent")
            top_line.pack(fill="x", padx=14, pady=(8, 2))

            ctk.CTkLabel(
                top_line,
                text=entry.action,
                fg_color=BOSCH_BLUE_LIGHT,
                text_color=BOSCH_BLUE,
                corner_radius=6,
                font=ctk.CTkFont(size=11, weight="bold"),
                padx=8,
                pady=2,
            ).pack(side="left")

            ctk.CTkLabel(
                top_line,
                text=f"  {entry.instrument_name} ({entry.norm})",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=TEXT_MAIN,
            ).pack(side="left")

            ctk.CTkLabel(
                top_line,
                text=entry.timestamp,
                font=ctk.CTkFont(family="Courier", size=12),
                text_color=TEXT_MUTED,
            ).pack(side="right")

            detail_text = (
                f"[{entry.source_sheet} → {entry.target_sheet}]   "
                f"{entry.old_value}  ➔  {entry.new_value}"
            )
            ctk.CTkLabel(
                row_card,
                text=detail_text,
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
            ).pack(anchor="w", padx=14, pady=(0, 8))
