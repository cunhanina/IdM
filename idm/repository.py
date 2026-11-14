"""Excel (.xlsx) repository and data access layer for the IdM system."""

import csv
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional, Union
from openpyxl import Workbook, load_workbook

from idm.models import AuditEntry, CalibrationStatus, DashboardStats, Instrument
from idm.validators import (
    evaluate_calibration_status,
    format_date_cell,
    get_current_iso_kw,
    normalize_kw_digits,
    normalize_norm,
    normalize_norm_search,
    normalize_text,
    parse_and_validate_kw,
)

AUDIT_SHEET_NAME = "Audit_Log"
STANDARD_HEADERS = [
    "LOCALIZAÇÃO",
    "LETRA",
    "DENOMINAÇÃO",
    "MARCA",
    "NORMA/SÉRIE",
    "DATA DE RETIRADA",
    "DATA DE RETORNO",
    "KW",
]
AUDIT_HEADERS = [
    "TIMESTAMP",
    "ACTION",
    "INSTRUMENT",
    "NORM_SERIAL",
    "SOURCE_SHEET",
    "TARGET_SHEET",
    "OLD_VALUE",
    "NEW_VALUE",
]
DEFAULT_INSTRUMENT_SHEETS = ["Geral", "Perdidos", "Sucateados"]


class InstrumentRepository:
    """Data access layer managing measurement instruments and audit logs in Excel."""

    def __init__(
        self,
        file_path: Union[str, Path] = "Instrumentos de medição.xlsx",
        ref_date: Optional[date] = None,
    ) -> None:
        self.file_path = Path(file_path)
        self.ref_date = ref_date

    def ensure_workbook_exists(self) -> None:
        """Create a properly structured Excel workbook if it does not exist yet."""
        if self.file_path.exists():
            return
        wb = Workbook()
        default_ws = wb.active
        default_ws.title = "Geral"
        default_ws.append(STANDARD_HEADERS)
        for sheet_name in ("Perdidos", "Sucateados"):
            ws = wb.create_sheet(title=sheet_name)
            ws.append(STANDARD_HEADERS)
        audit_ws = wb.create_sheet(title=AUDIT_SHEET_NAME)
        audit_ws.append(AUDIT_HEADERS)
        wb.save(self.file_path)

    def get_instrument_sheets(self) -> List[str]:
        """Return all worksheet names excluding the internal Audit_Log sheet."""
        if not self.file_path.exists():
            return list(DEFAULT_INSTRUMENT_SHEETS)
        try:
            wb = load_workbook(self.file_path, read_only=True)
            sheets = [name for name in wb.sheetnames if name != AUDIT_SHEET_NAME]
            wb.close()
            return sheets or list(DEFAULT_INSTRUMENT_SHEETS)
        except Exception:
            return list(DEFAULT_INSTRUMENT_SHEETS)

    def _row_to_instrument(self, sheet_name: str, row_idx: int, row: tuple) -> Instrument:
        """Convert a raw Excel tuple row into a typed Instrument model."""
        padded = list(row) + [None] * max(0, 8 - len(row))

        location = str(padded[0]).strip() if padded[0] is not None else "N/A"
        letter = str(padded[1]).strip() if padded[1] is not None else ""
        name = str(padded[2]).strip() if padded[2] is not None else "Sem Denominação"
        brand = str(padded[3]).strip() if padded[3] is not None else "-"
        norm = normalize_norm(padded[4]) if padded[4] is not None else "-"
        checkout_str = format_date_cell(padded[5])
        return_str = format_date_cell(padded[6])

        raw_kw = str(padded[7]).strip() if padded[7] is not None else ""
        is_valid_kw, canonical_kw = parse_and_validate_kw(raw_kw)
        kw_display = canonical_kw if is_valid_kw else ""

        status, weeks_delta = evaluate_calibration_status(
            kw_str=kw_display,
            sheet_name=sheet_name,
            checkout_date_str=checkout_str,
            return_date_str=return_str,
            ref_date=self.ref_date,
        )

        return Instrument(
            sheet=sheet_name,
            row_idx=row_idx,
            location=location,
            letter=letter,
            name=name,
            brand=brand,
            norm=norm,
            checkout_date=checkout_str,
            return_date=return_str,
            kw=kw_display,
            status=status,
            weeks_delta=weeks_delta,
        )

    def load_all_instruments(self) -> List[Instrument]:
        """Load all non-empty instrument rows across all instrument worksheets."""
        self.ensure_workbook_exists()
        wb = load_workbook(self.file_path, data_only=True)
        instruments: List[Instrument] = []
        try:
            for sheet_name in wb.sheetnames:
                if sheet_name == AUDIT_SHEET_NAME:
                    continue
                ws = wb[sheet_name]
                rows = list(ws.iter_rows(values_only=True))
                if not rows:
                    continue
                for idx, row in enumerate(rows[1:], start=2):
                    if not row or not any(cell is not None and str(cell).strip() != "" for cell in row):
                        continue
                    instruments.append(self._row_to_instrument(sheet_name, idx, row))
        finally:
            wb.close()
        return instruments

    def get_unique_locations(self, instruments: Optional[List[Instrument]] = None) -> List[str]:
        """Return sorted list of unique physical locations across all instruments."""
        items = instruments if instruments is not None else self.load_all_instruments()
        locs = {inst.location for inst in items if inst.location and inst.location != "N/A"}
        return sorted(locs)

    def compute_stats(self, instruments: Optional[List[Instrument]] = None) -> DashboardStats:
        """Calculate portfolio-wide KPI statistics for the dashboard."""
        items = instruments if instruments is not None else self.load_all_instruments()
        _, _, current_kw_str = get_current_iso_kw(self.ref_date)
        stats = DashboardStats(total=len(items), current_kw_str=current_kw_str)
        for inst in items:
            if inst.status == CalibrationStatus.VALID:
                stats.valid += 1
            elif inst.status == CalibrationStatus.DUE_SOON:
                stats.due_soon += 1
            elif inst.status == CalibrationStatus.EXPIRED:
                stats.expired += 1
            elif inst.status in (CalibrationStatus.IN_CALIBRATION, CalibrationStatus.MISSING_KW):
                stats.in_calibration_or_missing += 1
            elif inst.status == CalibrationStatus.INACTIVE:
                stats.inactive += 1
        return stats

    def search_and_filter(
        self,
        query: str = "",
        mode: str = "all",
        sheet_filter: str = "all",
        location_filter: str = "all",
        status_filter: str = "all",
        instruments: Optional[List[Instrument]] = None,
    ) -> List[Instrument]:
        """Filter instruments by text query, field mode, sheet, location, and calibration status."""
        items = instruments if instruments is not None else self.load_all_instruments()
        q_raw = query.strip()
        q_norm = normalize_text(q_raw)
        q_norm_serial = normalize_norm_search(q_raw)
        q_digits = normalize_kw_digits(q_raw)

        filtered: List[Instrument] = []
        for inst in items:
            # 1. Sheet filter
            if sheet_filter and sheet_filter != "all" and inst.sheet != sheet_filter:
                continue

            # 2. Location filter
            if location_filter and location_filter != "all" and inst.location != location_filter:
                continue

            # 3. Status filter
            if status_filter and status_filter != "all":
                if status_filter == "in_calibration_or_missing":
                    if inst.status not in (CalibrationStatus.IN_CALIBRATION, CalibrationStatus.MISSING_KW):
                        continue
                elif inst.status.value != status_filter:
                    continue

            # 4. Text query match
            if q_raw:
                match = False
                if mode == "nome":
                    match = q_norm in normalize_text(inst.name) or q_norm in normalize_text(inst.brand)
                elif mode == "norma":
                    match = bool(q_norm_serial and q_norm_serial in normalize_norm_search(inst.norm))
                elif mode == "local":
                    match = q_norm in normalize_text(inst.location) or q_norm in normalize_text(inst.letter)
                elif mode == "kw":
                    match = bool(q_digits and q_digits in normalize_kw_digits(inst.kw))
                else:
                    # Unified 'all' search across Name, Norm/Serial, Location, Brand, Letter, and KW
                    if q_norm in normalize_text(inst.name):
                        match = True
                    elif q_norm_serial and q_norm_serial in normalize_norm_search(inst.norm):
                        match = True
                    elif q_norm in normalize_text(inst.location):
                        match = True
                    elif q_norm in normalize_text(inst.brand):
                        match = True
                    elif q_digits and len(q_digits) >= 2 and q_digits in normalize_kw_digits(inst.kw):
                        match = True

                if not match:
                    continue

            filtered.append(inst)

        return filtered

    def _append_audit_log(
        self,
        wb: Workbook,
        action: str,
        instrument_name: str,
        norm: str,
        source_sheet: str,
        target_sheet: str,
        old_value: str,
        new_value: str,
        timestamp: Optional[str] = None,
    ) -> None:
        """Append a structured audit trail row to the Audit_Log worksheet."""
        if AUDIT_SHEET_NAME not in wb.sheetnames:
            audit_ws = wb.create_sheet(title=AUDIT_SHEET_NAME)
            audit_ws.append(AUDIT_HEADERS)
        else:
            audit_ws = wb[AUDIT_SHEET_NAME]

        ts = timestamp or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        audit_ws.append(
            [
                ts,
                action,
                instrument_name,
                norm,
                source_sheet,
                target_sheet,
                old_value,
                new_value,
            ]
        )

    def update_kw(self, inst: Instrument, raw_kw: str) -> str:
        """Validate and update an instrument's KW and Return Date, logging to Audit_Log.

        Raises ValueError if raw_kw is not a valid ISO WW/YY calendar week.
        Returns the canonical 'WW/YY' string saved.
        """
        is_valid, canonical_kw = parse_and_validate_kw(raw_kw)
        if not is_valid:
            raise ValueError(f"Invalid KW format: {raw_kw!r}")

        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        wb = load_workbook(self.file_path)
        try:
            ws = wb[inst.sheet]
            old_kw = str(ws.cell(row=inst.row_idx, column=8).value or "Sem KW").strip()
            ws.cell(row=inst.row_idx, column=8).value = canonical_kw
            ws.cell(row=inst.row_idx, column=7).value = now_str

            self._append_audit_log(
                wb=wb,
                action="UPDATE_KW",
                instrument_name=inst.name,
                norm=inst.norm,
                source_sheet=inst.sheet,
                target_sheet=inst.sheet,
                old_value=old_kw,
                new_value=canonical_kw,
            )
            wb.save(self.file_path)
        finally:
            wb.close()

        return canonical_kw

    def record_checkout(self, inst: Instrument) -> str:
        """Record current timestamp in DATA DE RETIRADA (column 6) and log to Audit_Log."""
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        wb = load_workbook(self.file_path)
        try:
            ws = wb[inst.sheet]
            old_checkout = format_date_cell(ws.cell(row=inst.row_idx, column=6).value) or "-"
            ws.cell(row=inst.row_idx, column=6).value = now_str

            self._append_audit_log(
                wb=wb,
                action="CHECKOUT",
                instrument_name=inst.name,
                norm=inst.norm,
                source_sheet=inst.sheet,
                target_sheet=inst.sheet,
                old_value=old_checkout,
                new_value=now_str,
            )
            wb.save(self.file_path)
        finally:
            wb.close()
        return now_str

    def move_instrument_sheet(self, inst: Instrument, target_sheet: str) -> None:
        """Move an instrument row from its current sheet to target_sheet and log to Audit_Log."""
        if inst.sheet == target_sheet:
            return

        wb = load_workbook(self.file_path)
        try:
            if target_sheet not in wb.sheetnames:
                new_ws = wb.create_sheet(title=target_sheet)
                new_ws.append(STANDARD_HEADERS)

            source_ws = wb[inst.sheet]
            target_ws = wb[target_sheet]

            row_cells = [cell.value for cell in source_ws[inst.row_idx]]
            padded_row = (row_cells + [None] * 8)[:8]
            target_ws.append(padded_row)
            source_ws.delete_rows(inst.row_idx)

            self._append_audit_log(
                wb=wb,
                action="MOVE_SHEET",
                instrument_name=inst.name,
                norm=inst.norm,
                source_sheet=inst.sheet,
                target_sheet=target_sheet,
                old_value=inst.sheet,
                new_value=target_sheet,
            )
            wb.save(self.file_path)
        finally:
            wb.close()

    def add_instrument(
        self,
        sheet: str,
        location: str,
        letter: str,
        name: str,
        brand: str,
        norm: str,
        kw: str = "",
    ) -> Instrument:
        """Add a new instrument to the specified sheet and record in Audit_Log."""
        loc_clean = location.strip().upper()
        name_clean = name.strip()
        norm_clean = normalize_norm(norm)
        if not loc_clean or not name_clean or not norm_clean:
            raise ValueError("Location, Name, and Norm/Serial are required.")

        canonical_kw = ""
        if kw and kw.strip():
            is_valid, canonical_kw = parse_and_validate_kw(kw)
            if not is_valid:
                raise ValueError(f"Invalid KW format: {kw!r}")

        self.ensure_workbook_exists()
        wb = load_workbook(self.file_path)
        try:
            if sheet not in wb.sheetnames:
                ws = wb.create_sheet(title=sheet)
                ws.append(STANDARD_HEADERS)
            else:
                ws = wb[sheet]

            now_str = datetime.now().strftime("%d/%m/%Y %H:%M") if canonical_kw else None
            new_row = [
                loc_clean,
                letter.strip().upper() or None,
                name_clean,
                brand.strip().upper() or "-",
                norm_clean,
                None,
                now_str,
                canonical_kw or None,
            ]
            ws.append(new_row)
            new_row_idx = ws.max_row

            self._append_audit_log(
                wb=wb,
                action="CREATE",
                instrument_name=name_clean,
                norm=norm_clean,
                source_sheet=sheet,
                target_sheet=sheet,
                old_value="-",
                new_value=f"{loc_clean} | KW: {canonical_kw or 'N/A'}",
            )
            wb.save(self.file_path)
        finally:
            wb.close()

        return self._row_to_instrument(sheet, new_row_idx, tuple(new_row))

    def edit_instrument(
        self,
        inst: Instrument,
        location: str,
        letter: str,
        name: str,
        brand: str,
        norm: str,
        kw: str = "",
    ) -> None:
        """Update an existing instrument's metadata and optional KW in place."""
        loc_clean = location.strip().upper()
        name_clean = name.strip()
        norm_clean = normalize_norm(norm)
        if not loc_clean or not name_clean or not norm_clean:
            raise ValueError("Location, Name, and Norm/Serial are required.")

        canonical_kw = ""
        if kw and kw.strip():
            is_valid, canonical_kw = parse_and_validate_kw(kw)
            if not is_valid:
                raise ValueError(f"Invalid KW format: {kw!r}")

        wb = load_workbook(self.file_path)
        try:
            ws = wb[inst.sheet]
            ws.cell(row=inst.row_idx, column=1).value = loc_clean
            ws.cell(row=inst.row_idx, column=2).value = letter.strip().upper() or None
            ws.cell(row=inst.row_idx, column=3).value = name_clean
            ws.cell(row=inst.row_idx, column=4).value = brand.strip().upper() or "-"
            ws.cell(row=inst.row_idx, column=5).value = norm_clean

            if canonical_kw != inst.kw:
                ws.cell(row=inst.row_idx, column=8).value = canonical_kw or None
                if canonical_kw:
                    ws.cell(row=inst.row_idx, column=7).value = datetime.now().strftime("%d/%m/%Y %H:%M")

            self._append_audit_log(
                wb=wb,
                action="EDIT",
                instrument_name=name_clean,
                norm=norm_clean,
                source_sheet=inst.sheet,
                target_sheet=inst.sheet,
                old_value=f"{inst.location} | {inst.name} | KW:{inst.kw or '-'}",
                new_value=f"{loc_clean} | {name_clean} | KW:{canonical_kw or '-'}",
            )
            wb.save(self.file_path)
        finally:
            wb.close()

    def get_audit_log(self, limit: int = 100) -> List[AuditEntry]:
        """Return the most recent AuditEntry records (newest first)."""
        if not self.file_path.exists():
            return []
        wb = load_workbook(self.file_path, data_only=True, read_only=True)
        entries: List[AuditEntry] = []
        try:
            if AUDIT_SHEET_NAME not in wb.sheetnames:
                return []
            ws = wb[AUDIT_SHEET_NAME]
            rows = list(ws.iter_rows(values_only=True))
            for row in reversed(rows[1:]):
                if not row or not any(row):
                    continue
                padded = list(row) + [""] * max(0, 8 - len(row))
                entries.append(
                    AuditEntry(
                        timestamp=str(padded[0] or ""),
                        action=str(padded[1] or ""),
                        instrument_name=str(padded[2] or ""),
                        norm=str(padded[3] or ""),
                        source_sheet=str(padded[4] or ""),
                        target_sheet=str(padded[5] or ""),
                        old_value=str(padded[6] or ""),
                        new_value=str(padded[7] or ""),
                    )
                )
                if len(entries) >= limit:
                    break
        finally:
            wb.close()
        return entries

    def export_to_csv(self, instruments: List[Instrument], output_path: Union[str, Path]) -> Path:
        """Export the given list of Instrument objects to a UTF-8 CSV file."""
        out = Path(output_path)
        with out.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "ABA",
                    "LOCALIZAÇÃO",
                    "LETRA",
                    "DENOMINAÇÃO",
                    "MARCA",
                    "NORMA/SÉRIE",
                    "DATA DE RETIRADA",
                    "DATA DE RETORNO",
                    "KW",
                    "STATUS",
                ]
            )
            for inst in instruments:
                writer.writerow(
                    [
                        inst.sheet,
                        inst.location,
                        inst.letter,
                        inst.name,
                        inst.brand,
                        inst.norm,
                        inst.checkout_date,
                        inst.return_date,
                        inst.kw or "Sem KW",
                        inst.status.value,
                    ]
                )
        return out
