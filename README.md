<div align="center">

  # IdM - Instrument Management System (v3.1)

  ![Python](https://img.shields.io/badge/Python-3.11+-007BC0?style=flat&logo=python&logoColor=white)
  ![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blue?style=flat)
  ![Excel](https://img.shields.io/badge/Database-Excel_(.xlsx)-217346?logo=microsoftexcel&logoColor=white)
  ![Tests](https://img.shields.io/badge/Tests-Pytest_Passing-success?style=flat&logo=pytest)
  ![I18n](https://img.shields.io/badge/Language-PT--BR_%7C_EN-informational?style=flat)

  **An industrial-grade metrology dashboard for tracking, validating, and auditing measurement instrument lifecycles (`KW` calibration windows) on the manufacturing shop floor.**
</div>

---

## 📖 Executive Summary

The **IdM (Instrumentos de Medição) System** is a quality-compliance desktop application designed to replace manual, error-prone spreadsheet editing in precision manufacturing and technical training environments (**ETS**).

* **The Problem:** Direct shop-floor editing of shared Excel files leads to malformed Calendar Week (`KW`) dates (e.g., invalid week numbers or inconsistent separators), lost checkout/return timestamps, and accidental data loss when moving instruments between *Active* (`Geral`), *Lost* (`Perdidos`), and *Scrapped* (`Sucateados`) worksheets.
* **The Solution:** A clean, modular validation and lifecycle management layer built with **Python** and **CustomTkinter** over the existing `.xlsx` workbook. It enforces ISO 8601 week rules (`WW/YY`), calculates real-time calibration expiration KPIs, automates cross-sheet row migration, and records an immutable audit trail (`Audit_Log`).

---

## ✨ Key Features

* **📊 Real-Time Calibration KPI Dashboard:** Automatically compares each instrument's `KW` (`WW/YY`) against the current ISO calendar week to classify the inventory into interactive KPI cards:
  * 🟢 **Calibrated (Valid):** More than 4 weeks remaining.
  * 🟡 **Due Soon:** Expiring within `≤ 4` weeks.
  * 🔴 **Expired (Overdue):** Past calibration `KW`.
  * 🟣 **In Calibration / Missing KW:** Checked out for calibration (`DATA DE RETIRADA`) or awaiting initial `KW`.
  * ⚪ **Inactive:** Located in `Perdidos` (Lost) or `Sucateados` (Scrapped).
* **🔍 Unified & Multi-Faceted Fuzzy Search:** Search across **Name**, **Norm/Serial**, **Physical Location** (`ARMÁRIO 35`, `CNC 42`, `BANCADA 1`), **Brand** (`MITUTOYO`, `STARRETT`, `MAHR`), and **KW** simultaneously. Automatically strips accents (`Paquímetro` $\leftrightarrow$ `paquimetro`), normalizes serial whitespace, and matches compact `KW` digits (`0327` $\leftrightarrow$ `03/27`).
* **🛡️ Strict ISO Calendar Week (`KW`) Validation:** Blocks invalid week entries (such as `00/27`, `54/27`, or `53/25` in 52-week years) before they touch the database, canonicalizing valid inputs (`3/27` or `0327` $\rightarrow$ `03/27`).
* **🔄 Complete Instrument Lifecycle (CRUD + Checkout/Return):**
  * **Check Out (`Registrar Retirada`):** Stamps `DATA DE RETIRADA` when sending an instrument to the metrology lab.
  * **Update KW & Return (`Atualizar KW`):** Validates the new `KW` and automatically stamps `DATA DE RETORNO`.
  * **Dynamic Sheet Migration:** Moving an instrument's dropdown tag between `Geral`, `Perdidos`, and `Sucateados` transfers the record and cleans up the source sheet.
  * **Create & Edit Modals:** Register new instruments or edit physical locations, brands, and serial norms in place.
* **📋 Automated Audit Trail (`Audit_Log`):** Every `CREATE`, `EDIT`, `CHECKOUT`, `UPDATE_KW`, and `MOVE_SHEET` operation is logged with a timestamp, old value, and new value in a dedicated `Audit_Log` worksheet viewable directly from the UI.
* **🌐 Bilingual Interface (`PT-BR` | `EN`) & CSV Export:** One-click live toggle between Portuguese and English, plus filtered CSV report export.

---

## 🏗 Project Architecture

```text
IdM/
├── idm/                          # Core application package
│   ├── __init__.py
│   ├── i18n.py                   # Bilingual (PT-BR / EN) translation dictionary & state
│   ├── models.py                 # Typed dataclasses: Instrument, AuditEntry, DashboardStats, CalibrationStatus
│   ├── validators.py             # ISO calendar week (KW) math, regex validation & string normalization
│   ├── repository.py             # Excel (.xlsx) CRUD repository, sheet migration & Audit_Log writer
│   └── ui/                       # CustomTkinter UI components
│       ├── theme.py              # Bosch Digital Design System palette & status badge styling
│       ├── dialogs.py            # Modal dialogs for New/Edit Instrument & Audit Trail history
│       └── app.py                # Main window with KPI cards, multi-filter bar & paginated cards
├── tests/                        # Automated Pytest suite
│   ├── test_validators.py        # Unit tests for ISO week math, KW bounds & normalization
│   └── test_repository.py        # Integration tests for Excel CRUD, sheet transfers & Audit_Log
├── Instrumentos de medição.xlsx  # Standardized Excel database (Geral, Perdidos, Sucateados, Audit_Log)
├── main.py                       # Main CLI & GUI entry point
├── idmV2.py                      # Legacy entry point (backward-compatible wrapper)
└── requirements.txt              # Project dependencies
```

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/cunhanina/IdM.git
cd IdM

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Launch the Desktop Application

```bash
# Launch in Portuguese (default)
python main.py

# Or launch directly in English
python main.py --lang en
```

### 3. CLI Reporting & Automated Tests

```bash
# Print live KPI calibration statistics to the terminal (headless)
python main.py --stats

# Export full inventory report to CSV from the command line
python main.py --export relatorio_idm.csv

# Run the automated test suite
pytest -v
```

---

<div align="center">

### Built with ❤️ by [Nina Cunha](https://github.com/cunhanina)

**Digital Transformation · Industrial Engineering**

[![LinkedIn](https://img.shields.io/badge/Connect-LinkedIn-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/nscunha/)
[![GitHub](https://img.shields.io/badge/Follow-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/cunhanina)

</div>
