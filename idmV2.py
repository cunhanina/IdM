"""Legacy entry point preserved for backward compatibility.

Delegates directly to the modular `idm` package (`main.py` / `idm.ui.app.MeasurementApp`).
"""

import sys
from idm.ui.app import MeasurementApp
from main import main

__all__ = ["MeasurementApp", "main"]

if __name__ == "__main__":
    sys.exit(main())