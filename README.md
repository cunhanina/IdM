<div align="center">

  # IdM — Instrument Management System

  ![Python](https://img.shields.io/badge/Python-3.11+-007BC0?style=flat&logo=python&logoColor=white)
  ![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-005691?style=flat)
  ![Excel](https://img.shields.io/badge/Database-Excel_(.xlsx)-217346?logo=microsoftexcel&logoColor=white)
  ![Tests](https://img.shields.io/badge/Tests-14_Passed_(Pytest)-1F922B?style=flat&logo=pytest)
  ![I18n](https://img.shields.io/badge/Language-PT--BR_%7C_EN-informational?style=flat)
  ![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=flat)

  **An industrial-grade metrology management system for tracking calibration validity (`KW`), physical locations, checkout/return workflows, and lifecycle states on the manufacturing shop floor.**
</div>

---

## 📖 Executive Summary

In high-precision manufacturing and technical training environments (**ETS**), ensuring that every measurement instrument—such as micrometers, calipers, dial indicators, and gauge blocks—remains within its valid calibration window (**KW / ISO Calendar Week**) is essential for quality compliance and ISO traceability.

* **The Problem:** Direct manual editing of shared Excel spreadsheets on the shop floor frequently leads to malformed `KW` dates (invalid week numbers or inconsistent separators), missing checkout/return timestamps, broken formulas, and accidental data loss when transferring rows between *Active* (`Geral`), *Lost* (`Perdidos`), and *Scrapped* (`Sucateados`) worksheets.
* **The Solution:** **IdM** acts as a dedicated **Validation & Lifecycle Layer** over the Excel workbook. Built with a modular Python architecture and a Bosch-inspired **CustomTkinter** interface, it enforces strict ISO 8601 week validation, surfaces real-time calibration KPIs, automates cross-sheet row migration, and logs every change to an immutable `Audit_Log` worksheet.

---

## ✨ Key Capabilities

### 📊 1. Real-Time Calibration Intelligence (KPI Dashboard)
Upon startup, IdM parses every instrument's `KW` (`WW/YY`) against the current ISO calendar week and categorizes the inventory into interactive KPI filter cards:
* **🟢 Calibrated (Valid):** Calibration window is valid with more than 4 weeks remaining.
* **🟡 Due Soon (`≤ 4 wks`):** Approaching calibration expiration within the next 4 weeks.
* **🔴 Expired (Overdue KW):** Calibration window has passed and requires immediate recall.
* **🟣 In Calibration / Missing KW:** Currently checked out to the metrology lab (`DATA DE RETIRADA`) or awaiting initial `KW` assignment.
* **⚪ Inactive (`Perdidos` / `Sucateados`):** Instruments marked as lost or decommissioned/scrapped.

### 🔍 2. Unified Multi-Faceted Fuzzy Search
* **Single-Bar Omnisearch:** Search simultaneously across **Name**, **Norm/Serial Number**, **Physical Location** (`ARMÁRIO 35`, `CNC 42`, `BANCADA 1`), **Brand** (`MITUTOYO`, `STARRETT`, `MAHR`), and **KW**.
* **Operator-Friendly Normalization:** Automatically strips accents (`Paquímetro` $\leftrightarrow$ `paquimetro`), normalizes serial number whitespace/hyphens (`4738440078- 009304` $\leftrightarrow$ `4738440078009304`), and matches compact `KW` digits (`0327` $\leftrightarrow$ `03/27`).
* **Combinable Filters:** Filter by **Worksheet** (`Geral`, `Perdidos`, `Sucateados`), **Physical Location**, and **Calibration Status** in one click.

### 🛡️ 3. Strict ISO 8601 Calendar Week (`KW`) Validation
* Enforces valid ISO week bounds (`01 <= WW <= 53`) and verifies whether week `53` actually exists in the target calendar year (e.g., `53/26` is valid because 2026 has 53 ISO weeks, whereas `53/25` is rejected).
* Automatically canonicalizes shorthand inputs (`3/27`, `03-27`, or `0327` $\rightarrow$ `03/27`) and blocks invalid inputs before they can corrupt the Excel workbook.

### 🔄 4. Complete Instrument Lifecycle & Audit Trail
* **Calibration Checkout (`Registrar Retirada`):** Stamps `DATA DE RETIRADA` when an instrument is sent out for calibration.
* **Calibration Return (`Atualizar KW`):** Validates the new `KW` and automatically stamps `DATA DE RETORNO`.
* **Dynamic Sheet Migration:** Changing an instrument's sheet tag (e.g., `Geral` $\rightarrow$ `Perdidos`) atomically appends the record to the destination sheet and deletes the source row.
* **CRUD Modals:** Register new instruments or edit physical locations, brands, letters, and serial norms via dedicated dialogs.
* **Automated Audit Trail (`Audit_Log`):** Every `CREATE`, `EDIT`, `CHECKOUT`, `UPDATE_KW`, and `MOVE_SHEET` action records a timestamp, actor action, source/target sheet, old value, and new value in the `Audit_Log` sheet, viewable directly inside the app.
* **🌐 Bilingual UI (`PT-BR` | `EN`) & CSV Export:** Switch live between Portuguese and English at any time, and export filtered views to UTF-8 CSV reports.

---

## 🛠 Tech Stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Core Language** | Python 3.11+ | Application logic, dataclasses, and CLI |
| **UI Framework** | CustomTkinter | Modernized Bosch Digital Design System desktop interface |
| **Data Persistence** | OpenPyXL | Direct `.xlsx` workbook manipulation & `Audit_Log` persistence |
| **Text Normalization** | Unidecode + Regex (`re`) | Accent-insensitive search & strict ISO `WW/YY` validation |
| **Localization** | `idm.i18n` | Instant live switching between Portuguese (`PT-BR`) and English (`EN`) |
| **Testing** | Pytest | Unit & integration test suite for validators and Excel repository |

---

## 📂 Project Architecture

```text
IdM/
├── idm/                          # Core modular package
│   ├── __init__.py
│   ├── i18n.py                   # Bilingual (PT-BR / EN) translation dictionary & state
│   ├── models.py                 # Dataclasses: Instrument, AuditEntry, DashboardStats, CalibrationStatus
│   ├── validators.py             # ISO calendar week (KW) math, validation & string normalization
│   ├── repository.py             # Excel (.xlsx) CRUD repository, sheet migration & Audit_Log writer
│   └── ui/                       # Modular CustomTkinter UI components
│       ├── __init__.py
│       ├── theme.py              # Bosch Digital Design System palette & status badge styling
│       ├── dialogs.py            # Modal dialogs for New/Edit Instrument & Audit Trail viewer
│       └── app.py                # Main window with KPI cards, multi-filter bar & paginated cards
├── tests/                        # Automated Pytest suite
│   ├── test_validators.py        # Unit tests for ISO week math, KW bounds & normalization
│   └── test_repository.py        # Integration tests for Excel CRUD, sheet transfers & Audit_Log
├── Instrumentos de medição.xlsx  # Standardized Excel database (Geral, Perdidos, Sucateados, Audit_Log)
├── main.py                       # Main GUI & CLI entry point
├── idmV2.py                      # Legacy entry point (preserved for backward compatibility)
└── requirements.txt              # Pinned runtime and test dependencies
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/cunhanina/IdM.git
cd IdM
```

### 2. Set Up Virtual Environment & Install Dependencies

```bash
# Standard setup (Windows / Linux / macOS with Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **macOS Note:** Avoid Apple's built-in `/usr/bin/python3` (which uses deprecated Tcl/Tk 8.5). If using Homebrew on macOS, install `python-tk` (`brew install python-tk`) and create your virtualenv with `/opt/homebrew/bin/python3 -m venv .venv`.

### 3. Launch the Application

```bash
# Launch GUI in Portuguese (default)
python3 main.py

# Launch GUI directly in English
python3 main.py --lang en
```

### 4. CLI Utilities & Automated Tests

```bash
# Print live KPI calibration statistics to the terminal (headless mode)
python3 main.py --stats

# Export full inventory report to CSV from the command line
python3 main.py --export relatorio_idm.csv

# Run the automated Pytest suite
pytest -v
```

---

<div align="center">

### Built with ❤️ by [Nina Cunha](https://github.com/cunhanina)

**Digital Transformation · Industrial Engineering**

[![LinkedIn](https://img.shields.io/badge/Connect-LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/nscunha/)
[![GitHub](https://img.shields.io/badge/Follow-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/cunhanina)

</div>
