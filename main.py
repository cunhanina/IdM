"""Main entry point for the IdM - Instrument Management System."""

import argparse
import os
from pathlib import Path
import sys

# Silence macOS system Tk 8.5 deprecation notice
os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")

from idm.i18n import set_language
from idm.repository import InstrumentRepository


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="IdM - Measurement Instrument Management System (ETS)"
    )
    parser.add_argument(
        "--file",
        default="Instrumentos de medição.xlsx",
        help="Path to the Excel database file (default: Instrumentos de medição.xlsx)",
    )
    parser.add_argument(
        "--lang",
        choices=["pt", "en"],
        default="pt",
        help="Initial UI language ('pt' or 'en')",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print calibration KPI summary to stdout and exit (headless mode)",
    )
    parser.add_argument(
        "--export",
        metavar="CSV_PATH",
        help="Export all instruments to the specified CSV file and exit",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    set_language(args.lang)

    repo = InstrumentRepository(file_path=Path(args.file))

    if args.stats:
        instruments = repo.load_all_instruments()
        stats = repo.compute_stats(instruments)
        print(f"=== IdM Portfolio KPI Summary (Current KW: {stats.current_kw_str}) ===")
        print(f"  Total Inventory          : {stats.total}")
        print(f"  Calibrated (Valid)       : {stats.valid}")
        print(f"  Due Soon (<= 4 weeks)    : {stats.due_soon}")
        print(f"  Expired (Overdue KW)     : {stats.expired}")
        print(f"  In Calibration / No KW   : {stats.in_calibration_or_missing}")
        print(f"  Inactive (Lost/Scrapped) : {stats.inactive}")
        return 0

    if args.export:
        instruments = repo.load_all_instruments()
        out = repo.export_to_csv(instruments, args.export)
        print(f"Exported {len(instruments)} instruments to {out}")
        return 0

    import tkinter as tk
    if sys.platform == "darwin" and getattr(tk, "TkVersion", 8.6) < 8.6:
        print(
            "\n[!] AVISO macOS: Você está executando com o Python do sistema da Apple (Tcl/Tk 8.5 antigo),\n"
            "    que possui um bug conhecido de tela preta/cinza no macOS recente.\n"
            "    Se a janela ficar escura, use o Python 3.11+ do python.org ou Homebrew:\n"
            "      brew install python-tk\n"
        )

    from idm.ui.app import MeasurementApp

    app = MeasurementApp(file_path=args.file)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
