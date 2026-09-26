"""Frappe framework constants mirrored from frappe/model/__init__.py,
frappe/core/doctype/doctype/doctype.py and frappe/model/document.py (v15-v17).

Kept here so specs can be validated without importing Frappe. When Frappe changes
one of these rules, update this file and the matching test in tests/test_spec.py.
"""

import re

DATA_FIELDTYPES = frozenset(
	{
		"Currency",
		"Int",
		"Long Int",
		"Float",
		"Percent",
		"Check",
		"Small Text",
		"Long Text",
		"Code",
		"Text Editor",
		"Markdown Editor",
		"HTML Editor",
		"Date",
		"Datetime",
		"Time",
		"Text",
		"Data",
		"Link",
		"Dynamic Link",
		"Password",
		"Select",
		"Rating",
		"Read Only",
		"Attach",
		"Attach Image",
		"Signature",
		"Color",
		"Barcode",
		"Geolocation",
		"Duration",
		"Icon",
		"Phone",
		"Autocomplete",
		"JSON",
	}
)

NO_VALUE_FIELDTYPES = frozenset(
	{
		"Section Break",
		"Column Break",
		"Tab Break",
		"HTML",
		"Table",
		"Table MultiSelect",
		"Button",
		"Image",
		"Fold",
		"Heading",
	}
)

TABLE_FIELDTYPES = frozenset({"Table", "Table MultiSelect"})
LAYOUT_FIELDTYPES = frozenset({"Section Break", "Column Break", "Tab Break"})
ALL_FIELDTYPES = DATA_FIELDTYPES | NO_VALUE_FIELDTYPES

# frappe.core.doctype.doctype.doctype.get_fields_not_allowed_in_list_view
NOT_ALLOWED_IN_LIST_VIEW = NO_VALUE_FIELDTYPES
NOT_ALLOWED_IN_GRID_VIEW = NO_VALUE_FIELDTYPES - {"Button", "HTML"}

UNIQUE_ALLOWED_FIELDTYPES = frozenset({"Data", "Link", "Read Only", "Int"})
NOT_INDEXABLE_FIELDTYPES = frozenset({"Text", "Long Text", "Small Text", "Code", "Text Editor"})
DATA_FIELD_OPTIONS = frozenset({"Email", "Name", "Phone", "URL", "Barcode", "IBAN"})
PRECISION_FIELDTYPES = frozenset({"Currency", "Float", "Percent"})

# Columns every DocType table already has.
DEFAULT_FIELDS = frozenset(
	{"doctype", "name", "owner", "creation", "modified", "modified_by", "docstatus", "idx"}
)
CHILD_TABLE_FIELDS = frozenset({"parent", "parentfield", "parenttype"})
OPTIONAL_FIELDS = frozenset({"_user_tags", "_comments", "_assign", "_liked_by", "_seen"})

# Attributes and methods of frappe.model.document.Document. A fieldname equal to one of
# these raises "Fieldname conflicting with meta object" when the DocType is saved.
DOCUMENT_ATTRIBUTES = frozenset(
	{
		"add_comment", "add_seen", "add_tag", "add_viewed", "append",
		"apply_fieldlevel_read_permissions", "as_dict", "as_json", "cancel", "cast",
		"check_docstatus_transition", "check_if_latest", "check_if_locked",
		"check_no_back_links_exist", "check_permission", "clear_cache",
		"copy_attachments_from_amended_from", "db_get", "db_insert", "db_set", "db_update",
		"db_update_all", "deferred_insert", "delete", "delete_key", "discard", "docstatus",
		"extend", "flags", "get", "get_all_children", "get_assigned_users", "get_db_value",
		"get_doc_before_save", "get_document_share_key", "get_formatted", "get_invalid_links",
		"get_latest", "get_liked_by", "get_onload", "get_parentfield_of_doctype",
		"get_password", "get_permissions", "get_permlevel_access", "get_signature",
		"get_table_field_doctype", "get_tags", "get_title", "get_url", "get_valid_columns",
		"get_valid_dict", "get_value", "get_value_before_save", "getone", "has_permission",
		"has_permlevel_access_to", "has_value_changed", "hook", "in_format_data",
		"init_child_tables", "init_valid_columns", "insert", "is_child_table_same",
		"is_dummy_password", "is_locked", "is_new", "is_print_hide", "is_whitelisted",
		"load_children_from_db", "load_doc_before_save", "load_from_db", "lock", "log_error",
		"meta", "notify_update", "parent_doc", "permitted_fieldnames", "precision",
		"queue_action", "raise_no_permission_to", "reload", "remove", "rename",
		"reset_seen", "round_floats_in", "run_before_save_methods", "run_method",
		"run_notifications", "run_post_save_methods", "run_trigger", "save", "save_version",
		"set", "set_docstatus", "set_fetch_from_value", "set_name_in_children",
		"set_new_name", "set_onload", "set_parent_in_children", "set_title_field",
		"set_user_and_timestamp", "submit", "unlock", "update", "update_child_table",
		"update_children", "update_if_missing", "update_modified", "update_single",
		"validate_amended_from", "validate_from_to_dates", "validate_higher_perm_levels",
		"validate_set_only_once", "validate_table_has_rows", "validate_update_after_submit",
		"validate_value", "validate_workflow", "dont_update_if_missing", "autoname",
		"validate", "on_update", "on_submit", "on_cancel", "on_trash", "before_save",
		"before_insert", "after_insert", "before_submit", "before_cancel",
		"get_field_name_by_key_name", "get_label_from_fieldname", "get_virtual_field_value",
		"mask_fields", "remove_tag", "remove_unpicklable_values", "reset_computed_child_tables",
		"reset_values_if_no_permlevel_access", "show_unique_validation_message",
		"throw_length_exceeded_error",
	}
)

RESERVED_FIELDNAMES = DEFAULT_FIELDS | CHILD_TABLE_FIELDS | OPTIONAL_FIELDS | DOCUMENT_ATTRIBUTES

PERMISSION_RIGHTS = (
	"read",
	"write",
	"create",
	"delete",
	"submit",
	"cancel",
	"amend",
	"report",
	"export",
	"import",
	"print",
	"email",
	"share",
	"select",
)
SUBMIT_RIGHTS = frozenset({"submit", "cancel", "amend"})

# MariaDB limits a table name to 64 characters; Frappe prefixes "tab".
MAX_DOCTYPE_NAME_LENGTH = 61
MAX_FIELDNAME_LENGTH = 64

# frappe.core.doctype.doctype.doctype.START_WITH_LETTERS_PATTERN
DOCTYPE_NAME_PATTERN = re.compile(r"^(?![\W])[^\d_\s][\w -]+$", flags=re.ASCII)
# Stricter than Frappe (which allows any \w), so generated code stays ASCII snake_case.
FIELDNAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
APP_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

NAMING_RULE_PREFIXES = ("field:", "naming_series:", "format:", "hash", "autoincrement", "prompt", "uuid")

# Roles Frappe creates on every site.
STANDARD_ROLES = frozenset({"Administrator", "System Manager", "All", "Guest", "Desk User"})


def scrub(txt: str) -> str:
	"""Same as frappe.scrub: 'Sales Order' -> 'sales_order'."""
	return str(txt).replace(" ", "_").replace("-", "_").lower()


def unscrub(txt: str) -> str:
	return txt.replace("_", " ").replace("-", " ").title()


def class_name(doctype: str) -> str:
	"""Controller class name Frappe expects: 'Sales Order' -> 'SalesOrder'."""
	return doctype.replace(" ", "").replace("-", "")
