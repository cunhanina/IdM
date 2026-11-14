"""Bosch Digital Design System color palette and styling helpers."""

from typing import Tuple
from idm.i18n import t
from idm.models import CalibrationStatus, Instrument

# --- Bosch Digital Design Palette ---
BOSCH_BLUE = "#005691"
BOSCH_BLUE_DARK = "#003E6B"
BOSCH_BLUE_LIGHT = "#E1F0FA"
BOSCH_RED = "#ED0007"
BOSCH_RED_LIGHT = "#FDE8E9"
SUCCESS_GREEN = "#1F922B"
SUCCESS_GREEN_LIGHT = "#E6F6E8"
WARNING_AMBER = "#D97706"
WARNING_AMBER_LIGHT = "#FEF3C7"
INFO_PURPLE = "#6D28D9"
INFO_PURPLE_LIGHT = "#EDE9FE"
NEUTRAL_GRAY = "#4B5563"
NEUTRAL_GRAY_LIGHT = "#F3F4F6"

LIGHT_BG = "#EFF1F2"
WHITE = "#FFFFFF"
TEXT_MAIN = "#191919"
TEXT_MUTED = "#6B7280"
BORDER_GRAY = "#D1D5DB"
CARD_BORDER = "#E5E7EB"


def get_sheet_tag_colors(sheet_name: str) -> Tuple[str, str]:
    """Return (bg_color, text_color) for a worksheet dropdown badge."""
    lower = sheet_name.lower()
    if "perdido" in lower:
        return BOSCH_RED, WHITE
    if "sucateado" in lower:
        return NEUTRAL_GRAY, WHITE
    return BOSCH_BLUE_LIGHT, BOSCH_BLUE


def get_status_badge_style(inst: Instrument) -> Tuple[str, str, str]:
    """Return (badge_text, bg_color, text_color) for an instrument's calibration status."""
    delta_suffix = ""
    if inst.weeks_delta is not None and inst.status != CalibrationStatus.INACTIVE:
        if inst.weeks_delta > 0:
            delta_suffix = f" ({t('weeks_remaining', weeks=inst.weeks_delta)})"
        elif inst.weeks_delta == 0:
            delta_suffix = f" ({t('weeks_current')})"
        else:
            delta_suffix = f" ({t('weeks_overdue', weeks=abs(inst.weeks_delta))})"

    if inst.status == CalibrationStatus.VALID:
        return f"● {t('status_valid')}{delta_suffix}", SUCCESS_GREEN_LIGHT, SUCCESS_GREEN
    if inst.status == CalibrationStatus.DUE_SOON:
        return f"▲ {t('status_due_soon')}{delta_suffix}", WARNING_AMBER_LIGHT, WARNING_AMBER
    if inst.status == CalibrationStatus.EXPIRED:
        return f"✖ {t('status_expired')}{delta_suffix}", BOSCH_RED_LIGHT, BOSCH_RED
    if inst.status == CalibrationStatus.IN_CALIBRATION:
        return f"⟳ {t('status_in_calibration')}", INFO_PURPLE_LIGHT, INFO_PURPLE
    if inst.status == CalibrationStatus.INACTIVE:
        return f"■ {t('status_inactive')}", NEUTRAL_GRAY_LIGHT, NEUTRAL_GRAY
    return f"○ {t('status_missing_kw')}", NEUTRAL_GRAY_LIGHT, NEUTRAL_GRAY
