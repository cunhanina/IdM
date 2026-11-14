"""Validation, normalization, and ISO calendar week (KW) calculation utilities."""

from datetime import date, datetime
import re
from typing import Optional, Tuple
import unicodedata

try:
    from unidecode import unidecode as _unidecode
except ImportError:
    def _unidecode(text: str) -> str:
        return (
            unicodedata.normalize("NFKD", text)
            .encode("ascii", "ignore")
            .decode("ascii")
        )

from idm.models import CalibrationStatus

INACTIVE_SHEET_KEYWORDS = ("perdido", "sucateado", "lost", "scrap")


def normalize_text(value: object) -> str:
    """Return lowercase, accent-stripped, single-spaced text for fuzzy search."""
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    ascii_str = _unidecode(raw).lower()
    return re.sub(r"\s+", " ", ascii_str)


def normalize_norm(value: object) -> str:
    """Clean norm/serial strings for display (e.g., '4738340019- 370693   ' -> '4738340019-370693')."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = re.sub(r"\s*-\s*", "-", text)
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_norm_search(value: object) -> str:
    """Return alphanumeric lowercase string with all spaces and hyphens removed for norm matching."""
    if value is None:
        return ""
    return re.sub(r"[\s\-_/]", "", _unidecode(str(value)).lower())


def normalize_kw_digits(value: object) -> str:
    """Remove all non-numeric characters from a KW string for flexible search."""
    if value is None:
        return ""
    return re.sub(r"[^0-9]", "", str(value))


def format_date_cell(value: object) -> str:
    """Format an Excel cell value (datetime, date, or string) into DD/MM/YYYY or DD/MM/YYYY HH:MM."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        if value.hour == 0 and value.minute == 0 and value.second == 0:
            return value.strftime("%d/%m/%Y")
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    text = str(value).strip()
    if not text or text.lower() in ("none", "nat", "-"):
        return ""
    # Normalize legacy DD-MM-YYYY HH:MM:SS format if present
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            dt = datetime.strptime(text, fmt)
            if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
                return dt.strftime("%d/%m/%Y")
            return dt.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            continue
    return text


def parse_and_validate_kw(raw_input: object) -> Tuple[bool, str]:
    """Validate and canonicalize a Calendar Week input into 'WW/YY'.

    Accepts formats such as:
      - '03/27', '3/27', '03-27', '03.27'
      - '0327' (4 digits: 2-digit week + 2-digit year)
    Enforces ISO week bounds (01 <= WW <= 53) and 2-digit year (00 <= YY <= 99).

    Returns:
      (is_valid, canonical_kw_or_empty)
    """
    if raw_input is None:
        return False, ""
    cleaned = str(raw_input).strip()
    if not cleaned:
        return False, ""

    # Match WW/YY, W/YY, WW-YY, WW.YY
    sep_match = re.match(r"^(\d{1,2})\s*[/\-\.]\s*(\d{2})$", cleaned)
    if sep_match:
        week = int(sep_match.group(1))
        year = int(sep_match.group(2))
    else:
        # Match 4 compact digits WWYY
        compact_match = re.match(r"^(\d{2})(\d{2})$", cleaned)
        if not compact_match:
            return False, ""
        week = int(compact_match.group(1))
        year = int(compact_match.group(2))

    if not (1 <= week <= 53):
        return False, ""
    if not (0 <= year <= 99):
        return False, ""

    # Verify if week 53 actually exists in 2000 + year
    full_year = 2000 + year
    if week == 53:
        # Dec 28 is always in the last ISO week of its year
        last_iso_week = date(full_year, 12, 28).isocalendar()[1]
        if last_iso_week < 53:
            return False, ""

    return True, f"{week:02d}/{year:02d}"


def get_current_iso_kw(ref_date: Optional[date] = None) -> Tuple[int, int, str]:
    """Return (iso_week, two_digit_year, formatted_'WW/YY') for ref_date (or today)."""
    target = ref_date or date.today()
    iso_year, iso_week, _ = target.isocalendar()
    yy = iso_year % 100
    return iso_week, yy, f"{iso_week:02d}/{yy:02d}"


def kw_weeks_delta(kw_str: object, ref_date: Optional[date] = None) -> Optional[int]:
    """Compute the signed difference in weeks between target KW and ref_date's ISO week.

    Returns:
      - Positive integer: weeks remaining in the future
      - 0: due this week
      - Negative integer: weeks overdue
      - None: if kw_str is not a valid KW
    """
    is_valid, canonical = parse_and_validate_kw(kw_str)
    if not is_valid:
        return None

    target_week = int(canonical[:2])
    target_year = 2000 + int(canonical[3:5])

    ref = ref_date or date.today()
    try:
        # Monday of the target ISO week vs Monday of the reference ISO week
        target_monday = date.fromisocalendar(target_year, target_week, 1)
        ref_iso_year, ref_iso_week, _ = ref.isocalendar()
        ref_monday = date.fromisocalendar(ref_iso_year, ref_iso_week, 1)
        return (target_monday - ref_monday).days // 7
    except ValueError:
        return None


def _parse_date_Rough(date_str: str) -> Optional[datetime]:
    """Best-effort parse of formatted date strings for comparing checkout vs return."""
    if not date_str:
        return None
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def is_inactive_sheet(sheet_name: str) -> bool:
    """Return True if the sheet represents lost or scrapped instruments."""
    norm_sheet = normalize_text(sheet_name)
    return any(keyword in norm_sheet for keyword in INACTIVE_SHEET_KEYWORDS)


def evaluate_calibration_status(
    kw_str: object,
    sheet_name: str,
    checkout_date_str: str = "",
    return_date_str: str = "",
    ref_date: Optional[date] = None,
    due_soon_weeks: int = 4,
) -> Tuple[CalibrationStatus, Optional[int]]:
    """Determine the CalibrationStatus and weeks_delta for an instrument."""
    if is_inactive_sheet(sheet_name):
        return CalibrationStatus.INACTIVE, kw_weeks_delta(kw_str, ref_date=ref_date)

    # Check if currently checked out for calibration (checkout_date > return_date, or checkout without return & no valid future KW)
    dt_out = _parse_date_Rough(checkout_date_str)
    dt_ret = _parse_date_Rough(return_date_str)

    delta = kw_weeks_delta(kw_str, ref_date=ref_date)
    if delta is None:
        if dt_out and not dt_ret:
            return CalibrationStatus.IN_CALIBRATION, None
        return CalibrationStatus.MISSING_KW, None

    if dt_out and dt_ret and dt_out > dt_ret:
        return CalibrationStatus.IN_CALIBRATION, delta

    if delta < 0:
        return CalibrationStatus.EXPIRED, delta
    if delta <= due_soon_weeks:
        return CalibrationStatus.DUE_SOON, delta
    return CalibrationStatus.VALID, delta
