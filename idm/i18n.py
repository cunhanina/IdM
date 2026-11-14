"""Bilingual (PT-BR / EN) localization module for the IdM application."""

from typing import Dict

SUPPORTED_LANGUAGES = ("pt", "en")
_current_language = "pt"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "pt": {
        "app_title": "ETS - Gestão de Instrumentos de Medição v3.1",
        "header_title": "GESTÃO DE INSTRUMENTOS | ETS",
        "header_subtitle": "Controle de Calibração (KW), Rastreabilidade e Ciclo de Vida",
        "lang_toggle": "🌐 PT | EN",
        "btn_new_instrument": "+ Novo Instrumento",
        "btn_audit_log": "📋 Histórico (Audit)",
        "btn_export_csv": "⬇ Exportar CSV",
        "btn_refresh": "↻ Atualizar",
        # KPI Cards
        "kpi_all": "Total no Acervo",
        "kpi_valid": "Calibrados (Em Dia)",
        "kpi_due_soon": "Vencendo (≤ 4 sem.)",
        "kpi_expired": "Vencidos (KW Expirado)",
        "kpi_in_calibration": "Em Calibração / Sem KW",
        "kpi_inactive": "Perdidos / Sucateados",
        "current_kw_badge": "Semana Atual: KW {kw}",
        # Search & Filters
        "search_panel_title": "Painel de Busca & Filtros Inteligentes",
        "search_placeholder": "Pesquise por Nome, Norma/Série, Localização, Marca ou KW (ex: Paquímetro, 4738, Armário 35, 03/27)...",
        "btn_search": "Buscar",
        "btn_clear": "Limpar",
        "filter_mode_label": "Campo:",
        "mode_all": "Todos",
        "mode_nome": "Nome",
        "mode_norma": "Norma/Série",
        "mode_local": "Localização",
        "mode_kw": "KW",
        "filter_sheet_label": "Aba:",
        "sheet_all": "Todas as Abas",
        "filter_location_label": "Local:",
        "location_all": "Todos os Locais",
        "filter_status_label": "Status:",
        "status_all": "Todos os Status",
        "status_valid": "Em Dia",
        "status_due_soon": "Vencendo Breve",
        "status_expired": "Vencido",
        "status_in_calibration": "Em Calibração",
        "status_missing_kw": "Sem KW",
        "status_inactive": "Inativo (Perdido/Sucat.)",
        # Results & Pagination
        "results_Showing": "Exibindo {start}–{end} de {total} instrumentos",
        "results_empty": "Nenhum instrumento encontrado para os filtros selecionados.",
        "btn_prev_page": "← Anterior",
        "btn_next_page": "Próxima →",
        "page_indicator": "Página {page} de {total_pages}",
        # Instrument Card
        "card_norm": "Norma/Série",
        "card_location": "Local",
        "card_brand": "Marca",
        "card_letter": "Letra",
        "card_checkout": "Retirada",
        "card_return": "Retorno",
        "card_no_kw": "Sem KW",
        "btn_update_kw": "Atualizar KW",
        "btn_checkout": "Registrar Retirada",
        "btn_edit": "Editar",
        "weeks_remaining": "+{weeks} sem.",
        "weeks_overdue": "{weeks} sem. atrás",
        "weeks_current": "Esta semana",
        # Dialogs & Messages
        "confirm_move_title": "Confirmar Mudança de Aba",
        "confirm_move_msg": "Mover '{name}' ({norm}) da aba '{old_sheet}' para '{new_sheet}'?",
        "move_success_title": "Localização Atualizada",
        "move_success_msg": "Instrumento movido para '{sheet}' com sucesso.",
        "checkout_confirm_title": "Registrar Retirada para Calibração",
        "checkout_confirm_msg": "Registrar envio de '{name}' ({norm}) para calibração agora?",
        "checkout_success_msg": "Data de retirada registrada com sucesso.",
        "kw_dialog_title": "Atualizar Validade (KW) e Retorno",
        "kw_dialog_prompt": "Informe o novo KW (formato WW/YY, ex: 12/27):",
        "kw_invalid_title": "Formato de KW Inválido",
        "kw_invalid_msg": "O valor '{value}' é inválido.\nInforme uma semana ISO válida (01 a 53) e o ano com 2 dígitos (ex: 08/27 ou 0827).",
        "kw_updated_msg": "KW atualizado para {kw} e data de retorno registrada.",
        "modal_new_title": "Cadastrar Novo Instrumento",
        "modal_edit_title": "Editar Instrumento",
        "field_sheet": "Aba / Situação:",
        "field_location": "Localização Física *:",
        "field_letter": "Letra / Código:",
        "field_name": "Denominação (Nome) *:",
        "field_brand": "Marca:",
        "field_norm": "Norma / Nº de Série *:",
        "field_kw": "Validade KW (WW/YY):",
        "btn_save": "Salvar",
        "btn_cancel": "Cancelar",
        "validation_required": "Os campos Localização, Denominação e Norma/Série são obrigatórios.",
        "save_success_msg": "Instrumento salvo com sucesso.",
        "export_success_title": "Exportação Concluída",
        "export_success_msg": "{count} registros exportados para:\n{path}",
        "audit_modal_title": "Histórico de Auditoria (Audit Log)",
        "audit_empty": "Nenhum registro de auditoria encontrado.",
        "error_title": "Erro",
        "db_error_msg": "Erro ao acessar a base de dados Excel: {error}",
    },
    "en": {
        "app_title": "ETS - Measurement Instrument Management v3.1",
        "header_title": "INSTRUMENT MANAGEMENT | ETS",
        "header_subtitle": "Calibration Tracking (KW), Traceability & Lifecycle Control",
        "lang_toggle": "🌐 EN | PT",
        "btn_new_instrument": "+ New Instrument",
        "btn_audit_log": "📋 Audit Log",
        "btn_export_csv": "⬇ Export CSV",
        "btn_refresh": "↻ Refresh",
        # KPI Cards
        "kpi_all": "Total Inventory",
        "kpi_valid": "Calibrated (Valid)",
        "kpi_due_soon": "Due Soon (≤ 4 wks)",
        "kpi_expired": "Expired (Overdue KW)",
        "kpi_in_calibration": "In Calibration / No KW",
        "kpi_inactive": "Lost / Scrapped",
        "current_kw_badge": "Current Week: KW {kw}",
        # Search & Filters
        "search_panel_title": "Smart Search & Filter Panel",
        "search_placeholder": "Search by Name, Norm/Serial, Location, Brand, or KW (e.g., Micrômetro, 4738, Armário 35, 03/27)...",
        "btn_search": "Search",
        "btn_clear": "Clear",
        "filter_mode_label": "Field:",
        "mode_all": "All Fields",
        "mode_nome": "Name",
        "mode_norma": "Norm/Serial",
        "mode_local": "Location",
        "mode_kw": "KW",
        "filter_sheet_label": "Sheet:",
        "sheet_all": "All Sheets",
        "filter_location_label": "Location:",
        "location_all": "All Locations",
        "filter_status_label": "Status:",
        "status_all": "All Statuses",
        "status_valid": "Valid",
        "status_due_soon": "Due Soon",
        "status_expired": "Expired",
        "status_in_calibration": "In Calibration",
        "status_missing_kw": "Missing KW",
        "status_inactive": "Inactive (Lost/Scrap)",
        # Results & Pagination
        "results_Showing": "Showing {start}–{end} of {total} instruments",
        "results_empty": "No instruments match the selected filters.",
        "btn_prev_page": "← Previous",
        "btn_next_page": "Next →",
        "page_indicator": "Page {page} of {total_pages}",
        # Instrument Card
        "card_norm": "Norm/Serial",
        "card_location": "Location",
        "card_brand": "Brand",
        "card_letter": "Code",
        "card_checkout": "Checked Out",
        "card_return": "Returned",
        "card_no_kw": "No KW",
        "btn_update_kw": "Update KW",
        "btn_checkout": "Check Out",
        "btn_edit": "Edit",
        "weeks_remaining": "+{weeks} wks",
        "weeks_overdue": "{weeks} wks ago",
        "weeks_current": "Due this week",
        # Dialogs & Messages
        "confirm_move_title": "Confirm Sheet Transfer",
        "confirm_move_msg": "Move '{name}' ({norm}) from '{old_sheet}' to '{new_sheet}'?",
        "move_success_title": "Location Updated",
        "move_success_msg": "Instrument successfully moved to '{sheet}'.",
        "checkout_confirm_title": "Check Out for Calibration",
        "checkout_confirm_msg": "Record calibration checkout timestamp for '{name}' ({norm})?",
        "checkout_success_msg": "Checkout timestamp recorded successfully.",
        "kw_dialog_title": "Update Calibration KW & Return",
        "kw_dialog_prompt": "Enter new KW (WW/YY format, e.g., 12/27):",
        "kw_invalid_title": "Invalid KW Format",
        "kw_invalid_msg": "The value '{value}' is invalid.\nPlease enter a valid ISO week (01 to 53) and 2-digit year (e.g., 08/27 or 0827).",
        "kw_updated_msg": "KW updated to {kw} and return date recorded.",
        "modal_new_title": "Register New Instrument",
        "modal_edit_title": "Edit Instrument",
        "field_sheet": "Sheet / Lifecycle:",
        "field_location": "Physical Location *:",
        "field_letter": "Letter / Code:",
        "field_name": "Description (Name) *:",
        "field_brand": "Brand:",
        "field_norm": "Norm / Serial No. *:",
        "field_kw": "Calibration KW (WW/YY):",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "validation_required": "Location, Description, and Norm/Serial fields are required.",
        "save_success_msg": "Instrument saved successfully.",
        "export_success_title": "Export Complete",
        "export_success_msg": "{count} records exported to:\n{path}",
        "audit_modal_title": "Audit Trail History (Audit Log)",
        "audit_empty": "No audit log entries found.",
        "error_title": "Error",
        "db_error_msg": "Failed to access Excel database: {error}",
    },
}


def get_language() -> str:
    """Return the active language code ('pt' or 'en')."""
    return _current_language


def set_language(lang: str) -> None:
    """Set the active language code ('pt' or 'en')."""
    global _current_language
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {lang}")
    _current_language = lang


def toggle_language() -> str:
    """Switch between Portuguese ('pt') and English ('en')."""
    global _current_language
    _current_language = "en" if _current_language == "pt" else "pt"
    return _current_language


def t(key: str, **kwargs) -> str:
    """Translate a UI key using the active language and optional format kwargs."""
    lang_dict = TRANSLATIONS.get(_current_language, TRANSLATIONS["pt"])
    template = lang_dict.get(key, TRANSLATIONS["pt"].get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template
