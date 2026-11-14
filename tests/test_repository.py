"""Integration and unit tests for InstrumentRepository (Excel CRUD, search, migration, audit log)."""

from datetime import date
from pathlib import Path
import pytest

from idm.models import CalibrationStatus
from idm.repository import InstrumentRepository


@pytest.fixture
def temp_repo(tmp_path: Path) -> InstrumentRepository:
    excel_file = tmp_path / "test_idm.xlsx"
    repo = InstrumentRepository(file_path=excel_file, ref_date=date(2026, 11, 13))
    repo.ensure_workbook_exists()
    return repo


class TestInstrumentRepository:
    def test_add_and_load_instrument(self, temp_repo: InstrumentRepository):
        created = temp_repo.add_instrument(
            sheet="Geral",
            location="armário 35",
            letter="a",
            name="Paquímetro Digital 150mm",
            brand="mitutoyo",
            norm="4738440078- 009304",
            kw="12/27",
        )
        assert created.location == "ARMÁRIO 35"
        assert created.brand == "MITUTOYO"
        assert created.norm == "4738440078-009304"
        assert created.kw == "12/27"
        assert created.status == CalibrationStatus.VALID

        all_items = temp_repo.load_all_instruments()
        assert len(all_items) == 1
        assert all_items[0].name == "Paquímetro Digital 150mm"

    def test_update_kw_blocks_invalid_and_logs_audit(self, temp_repo: InstrumentRepository):
        inst = temp_repo.add_instrument(
            sheet="Geral",
            location="BANCADA 1",
            letter="",
            name="Micrômetro Externo 0-25mm",
            brand="MITUTOYO",
            norm="4738450004-002011",
            kw="30/26",
        )
        assert inst.status == CalibrationStatus.EXPIRED

        # Invalid KW must raise ValueError and not corrupt Excel
        with pytest.raises(ValueError):
            temp_repo.update_kw(inst, "99/99")

        # Valid compact KW '0827' is normalized to '08/27'
        saved_kw = temp_repo.update_kw(inst, "0827")
        assert saved_kw == "08/27"

        reloaded = temp_repo.load_all_instruments()[0]
        assert reloaded.kw == "08/27"
        assert reloaded.return_date != ""
        assert reloaded.status == CalibrationStatus.VALID

        logs = temp_repo.get_audit_log()
        assert any(entry.action == "UPDATE_KW" and entry.new_value == "08/27" for entry in logs)

    def test_checkout_and_sheet_migration(self, temp_repo: InstrumentRepository):
        inst = temp_repo.add_instrument(
            sheet="Geral",
            location="CNC 42",
            letter="",
            name="Relógio Comparador",
            brand="MAHR",
            norm="353278",
            kw="",
        )
        ts = temp_repo.record_checkout(inst)
        assert ts != ""

        checked_out = temp_repo.load_all_instruments()[0]
        assert checked_out.checkout_date != ""
        assert checked_out.status == CalibrationStatus.IN_CALIBRATION

        # Move from Geral to Perdidos
        temp_repo.move_instrument_sheet(checked_out, "Perdidos")
        after_move = temp_repo.load_all_instruments()
        assert len(after_move) == 1
        assert after_move[0].sheet == "Perdidos"
        assert after_move[0].status == CalibrationStatus.INACTIVE

        logs = temp_repo.get_audit_log()
        assert any(entry.action == "MOVE_SHEET" and entry.target_sheet == "Perdidos" for entry in logs)

    def test_unified_search_and_csv_export(self, temp_repo: InstrumentRepository, tmp_path: Path):
        temp_repo.add_instrument("Geral", "ARMÁRIO 35", "", "Paquímetro Digital", "MITUTOYO", "4738-001", "03/27")
        temp_repo.add_instrument("Geral", "CNC 40", "", "Esquadro de Precisão", "STARRETT", "9912-002", "47/26")
        temp_repo.add_instrument("Perdidos", "BANCADA 11", "", "Imicro", "COSA", "1111-003", "")

        # Accent-insensitive name search
        res_name = temp_repo.search_and_filter(query="paquimetro", mode="nome")
        assert len(res_name) == 1

        # Whitespace/hyphen-tolerant norm search
        res_norm = temp_repo.search_and_filter(query="4738001", mode="norma")
        assert len(res_norm) == 1

        # Flexible KW search ('0327' matches '03/27')
        res_kw = temp_repo.search_and_filter(query="0327", mode="kw")
        assert len(res_kw) == 1

        # Status filter
        res_due = temp_repo.search_and_filter(status_filter=CalibrationStatus.DUE_SOON.value)
        assert len(res_due) == 1
        assert res_due[0].name == "Esquadro de Precisão"

        # CSV export
        csv_path = tmp_path / "export.csv"
        all_items = temp_repo.load_all_instruments()
        temp_repo.export_to_csv(all_items, csv_path)
        assert csv_path.exists()
        content = csv_path.read_text(encoding="utf-8-sig")
        assert "Paquímetro Digital" in content
        assert "Esquadro de Precisão" in content
