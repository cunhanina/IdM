"""Unit tests for idm.validators and idm.i18n."""

from datetime import date
import pytest

from idm.i18n import get_language, set_language, t, toggle_language
from idm.models import CalibrationStatus
from idm.validators import (
    evaluate_calibration_status,
    format_date_cell,
    kw_weeks_delta,
    normalize_kw_digits,
    normalize_norm,
    normalize_norm_search,
    normalize_text,
    parse_and_validate_kw,
)


class TestKWValidation:
    def test_valid_standard_formats(self):
        assert parse_and_validate_kw("03/27") == (True, "03/27")
        assert parse_and_validate_kw("3/27") == (True, "03/27")
        assert parse_and_validate_kw("0327") == (True, "03/27")
        assert parse_and_validate_kw("03-27") == (True, "03/27")
        assert parse_and_validate_kw("52/26") == (True, "52/26")

    def test_iso_week_53_validation(self):
        # 2026 has 53 ISO weeks; 2025 only has 52 ISO weeks
        assert parse_and_validate_kw("53/26") == (True, "53/26")
        assert parse_and_validate_kw("53/25") == (False, "")

    def test_invalid_kw_rejected(self):
        assert parse_and_validate_kw("") == (False, "")
        assert parse_and_validate_kw(None) == (False, "")
        assert parse_and_validate_kw("00/26") == (False, "")
        assert parse_and_validate_kw("54/26") == (False, "")
        assert parse_and_validate_kw("99/99") == (False, "")
        assert parse_and_validate_kw("Sem KW") == (False, "")
        assert parse_and_validate_kw("12/2026") == (False, "")


class TestCalibrationStatusAndWeeksDelta:
    def test_weeks_delta_calculation(self):
        # 2026-11-13 is in ISO week 46 of 2026 (46/26)
        ref = date(2026, 11, 13)
        assert kw_weeks_delta("46/26", ref_date=ref) == 0
        assert kw_weeks_delta("48/26", ref_date=ref) == 2
        assert kw_weeks_delta("44/26", ref_date=ref) == -2

    def test_status_classification(self):
        ref = date(2026, 11, 13)  # KW 46/26

        status, delta = evaluate_calibration_status("05/27", "Geral", ref_date=ref)
        assert status == CalibrationStatus.VALID
        assert delta > 4

        status, delta = evaluate_calibration_status("48/26", "Geral", ref_date=ref)
        assert status == CalibrationStatus.DUE_SOON
        assert delta == 2

        status, delta = evaluate_calibration_status("30/26", "Geral", ref_date=ref)
        assert status == CalibrationStatus.EXPIRED
        assert delta < 0

        status, _ = evaluate_calibration_status("", "Geral", ref_date=ref)
        assert status == CalibrationStatus.MISSING_KW

        status, _ = evaluate_calibration_status(
            "30/26",
            "Geral",
            checkout_date_str="12/11/2026 10:00",
            return_date_str="01/01/2026 09:00",
            ref_date=ref,
        )
        assert status == CalibrationStatus.IN_CALIBRATION

        status, _ = evaluate_calibration_status("05/27", "Perdidos", ref_date=ref)
        assert status == CalibrationStatus.INACTIVE


class TestNormalizationAndFormatting:
    def test_accent_and_case_normalization(self):
        assert normalize_text("Paquímetro Analógico  ") == "paquimetro analogico"
        assert normalize_text("RETÍFICA CILÍNDRICA 21") == "retifica cilindrica 21"

    def test_norm_cleaning(self):
        assert normalize_norm("4738340019- 370693       ") == "4738340019-370693"
        assert normalize_norm_search("4738340019- 370693") == "4738340019370693"

    def test_kw_digits(self):
        assert normalize_kw_digits("03/27") == "0327"
        assert normalize_kw_digits("KW 12-26") == "1226"

    def test_date_formatting(self):
        assert format_date_cell(date(2026, 3, 15)) == "15/03/2026"
        assert format_date_cell("2024-02-01 00:00:00") == "01/02/2024"


class TestI18n:
    def test_language_switching(self):
        set_language("pt")
        assert get_language() == "pt"
        assert "Buscar" in t("btn_search")

        toggle_language()
        assert get_language() == "en"
        assert "Search" in t("btn_search")

        set_language("pt")
        with pytest.raises(ValueError):
            set_language("fr")
