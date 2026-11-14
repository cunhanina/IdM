"""Domain models and enums for the IdM Instrument Management System."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CalibrationStatus( str, Enum ):
    """Lifecycle and calibration validity state of a measurement instrument."""

    VALID = "valid"
    DUE_SOON = "due_soon"
    EXPIRED = "expired"
    IN_CALIBRATION = "in_calibration"
    MISSING_KW = "missing_kw"
    INACTIVE = "inactive"


@dataclass
class Instrument:
    """Represents a single measurement instrument row in the Excel workbook."""

    sheet: str
    row_idx: int
    location: str
    letter: str
    name: str
    brand: str
    norm: str
    checkout_date: str
    return_date: str
    kw: str
    status: CalibrationStatus = CalibrationStatus.MISSING_KW
    weeks_delta: Optional[int] = None

    @property
    def has_kw(self) -> bool:
        """Return True if the instrument has a valid KW string assigned."""
        return bool(self.kw and self.kw.lower() not in ("sem kw", "none", "-", "n/a"))


@dataclass
class AuditEntry:
    """Represents a single audit trail event stored in the Audit_Log sheet."""

    timestamp: str
    action: str
    instrument_name: str
    norm: str
    source_sheet: str
    target_sheet: str
    old_value: str
    new_value: str


@dataclass
class DashboardStats:
    """Aggregated KPI metrics across the instrument inventory."""

    total: int = 0
    valid: int = 0
    due_soon: int = 0
    expired: int = 0
    in_calibration_or_missing: int = 0
    inactive: int = 0
    current_kw_str: str = ""
