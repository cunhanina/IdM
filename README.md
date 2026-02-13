<div align="center">

  # IdM - Instrument Management System
   
  ![Python](https://img.shields.io/badge/Python-3.13-007BC0?style=flat&logo=python&logoColor=white)
  ![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blue?style=flat)
  ![Excel](https://img.shields.io/badge/Database-Excel-green?logo=microsoftexcel)
  ![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=flat)

  **A professional, industrial-grade interface for tracking, validating, and managing measurement instrument lifecycles within the ETS department.**
</div>

---

## 📖 Executive Summary

The **IdM (Instrumentos de Medição) System** is a mission-critical tool designed to replace manual spreadsheet editing with a robust, error-resistant digital interface. In high-precision manufacturing, ensuring that instruments are within their calibration window (**KW**) is vital for quality compliance. 

**The Problem:** Direct Excel editing often leads to broken formulas, inconsistent date formatting (KW), and accidental data loss during row migration between "Active" and "Lost" sheets.

**The Solution:** A centralized dashboard that acts as a "Validation Layer." It allows apprentices to search, relocate, and update instrument status via a modern UI that enforces strict formatting rules and automates row transfers.

---

## ✨ Capabilities

* **🔍 Flexible "Fuzzy" Search:** Find instruments by **Name**, **Norm**, or **KW**. The intelligent search engine strips special characters, allowing you to find `03/25` just by typing `0325`.
* **🏷️ Dynamic Sheet Migration:** Each instrument card features a built-in **Location Dropdown**. Changing the location (e.g., from *Geral* to *Perdidos*) automatically moves the row in the Excel database and cleans up the source sheet.
* **📅 Automated Auditing:** Every KW update triggers an automatic timestamping process, recording the exact second the change was made for audit trail purposes.
* **🛡️ Format Protection:** Includes a **Regex Validation Engine** that checks entries before they hit the database. If a user enters an impossible date or wrong format, the system blocks the command and issues a visual warning.
* **🎨 Bosch Design System:** Built with a clean "Light Mode" aesthetic using **CustomTkinter** to ensure brand compliance and professional scannability.

## 🛠 Tech Stack
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Core** | Python 3.13 | Application logic and string normalization |
| **UI Framework** | CustomTkinter | Modernized, Bosch-blue themed interface |
| **Data Engine** | Openpyxl | Direct XML-based Excel manipulation |
| **Validation** | Regex (re) | WW/YY format enforcement |
| **Normalization** | Unidecode | Accented character handling for search |

---

## 📂 Project Structure
```text
IdM/
├── Instrumentos de medição.xlsx # The central database file
└── idmV2.py                 # Main Application Source
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone [https://github.com/cunhanina/IdM.git](https://github.com/cunhanina/IdM.git)
cd IdM

# 3. Launch the Manager
python idmV2.py
```

---

## 🧠 System Logic
1.  **Normalization Pass:** When a user searches, the query is passed through `unidecode` and `re.sub`. This ensures that "Padrão" matches "padrao" and "03/25" matches "0325".
2.  **Migration Pipeline:**
    * **Step 1:** The system reads the entire row from the source sheet.
    * **Step 2:** It appends the data to the target sheet's first empty row.
    * **Step 3:** It executes a `delete_rows` command on the source to prevent duplicates.
3.  **Validation Loop:** The KW input is filtered through a pattern `^[0-9]{2}/[0-9]{2}$`. Only valid strings are passed to the database setter.

---

<div align="center">

### Built with ❤️ by [Nina Cunha](https://github.com/cunhanina)

**Digital Transformation · Industrial Engineering**

[![LinkedIn](https://img.shields.io/badge/Connect-LinkedIn-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/nscunha/)
[![GitHub](https://img.shields.io/badge/Follow-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/cunhanina)


</div>
