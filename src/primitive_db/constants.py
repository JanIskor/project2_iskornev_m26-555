"""Константы приложения «Примитивная база данных»."""

METADATA_FILE = "db_meta.json"
DATA_DIR = "data"

SUPPORTED_TYPES = ("int", "str", "bool")

ID_COLUMN = "ID"
ID_TYPE = "int"

COMMAND_CREATE_TABLE = "create_table"
COMMAND_LIST_TABLES = "list_tables"
COMMAND_DROP_TABLE = "drop_table"
COMMAND_INSERT = "insert"
COMMAND_SELECT = "select"
COMMAND_UPDATE = "update"
COMMAND_DELETE = "delete"
COMMAND_INFO = "info"
COMMAND_HELP = "help"
COMMAND_EXIT = "exit"
