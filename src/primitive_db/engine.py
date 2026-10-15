"""Интерактивный интерфейс примитивной базы данных."""

import prompt

from primitive_db.constants import (
    COMMAND_CREATE_TABLE,
    COMMAND_DELETE,
    COMMAND_DROP_TABLE,
    COMMAND_EXIT,
    COMMAND_HELP,
    COMMAND_INFO,
    COMMAND_INSERT,
    COMMAND_LIST_TABLES,
    COMMAND_SELECT,
    COMMAND_UPDATE,
)
from primitive_db.core import create_table, get_table_info, list_tables
from primitive_db.utils import load_metadata, load_table_data, save_metadata

HELP_TEXT = """Доступные команды:
  create_table <имя> <столбец:тип> ...  - Создать таблицу
  list_tables                         - Показать список таблиц
  drop_table <имя>                    - Удалить таблицу
  insert into <имя> values (...)      - Добавить запись
  select from <имя> [where ...]       - Выбрать записи
  update <имя> set ... where ...      - Обновить записи
  delete from <имя> where ...         - Удалить записи
  info <имя>                          - Информация о таблице
  help                                - Показать справку
  exit                                - Выйти из программы"""

NOT_IMPLEMENTED_COMMANDS = {
    COMMAND_DROP_TABLE,
    COMMAND_INSERT,
    COMMAND_SELECT,
    COMMAND_UPDATE,
    COMMAND_DELETE,
}


def show_help():
    """Выводит справку по доступным командам."""
    print(HELP_TEXT)


def handle_create_table(command_line):
    """Обрабатывает создание новой таблицы."""
    parts = command_line.split()

    if len(parts) < 3:
        raise ValueError(
            "Некорректный синтаксис. Используйте: create_table <имя> <столбец:тип> ..."
        )

    table_name = parts[1]
    columns = []

    for column_definition in parts[2:]:
        if column_definition.count(":") != 1:
            raise ValueError(f'Некорректное описание столбца: "{column_definition}".')

        column_name, column_type = column_definition.split(":")
        columns.append((column_name, column_type))

    metadata = load_metadata()
    updated_metadata = create_table(metadata, table_name, columns)

    save_metadata(updated_metadata)

    columns_description = ", ".join(
        f"{name}:{column_type}"
        for name, column_type in updated_metadata[table_name].items()
    )

    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_description}')


def handle_list_tables(command_line):
    """Выводит список существующих таблиц."""
    if command_line != COMMAND_LIST_TABLES:
        raise ValueError("Команда list_tables не принимает аргументы.")

    metadata = load_metadata()
    tables = list_tables(metadata)

    if not tables:
        print("В базе данных нет таблиц.")
        return

    print(f"Список таблиц: {', '.join(tables)}")


def handle_info(command_line):
    """Выводит структуру таблицы и количество записей."""
    parts = command_line.split()

    if len(parts) != 2:
        raise ValueError("Некорректный синтаксис. Используйте: info <имя>")

    table_name = parts[1]

    metadata = load_metadata()
    columns = get_table_info(metadata, table_name)
    records = load_table_data(table_name)

    print(f"Таблица: {table_name}")
    print("Столбцы:")

    for column_name, column_type in columns.items():
        print(f"  {column_name}: {column_type}")

    print(f"Количество записей: {len(records)}")


def run():
    """Запускает интерактивный цикл обработки команд."""
    print("***База данных***")
    print('Для просмотра доступных команд введите "help".')

    while True:
        try:
            command_line = prompt.string("Введите команду: ")
        except (EOFError, KeyboardInterrupt):
            print("\nВыход из программы.")
            break

        command_line = command_line.strip()

        if not command_line:
            continue

        command = command_line.split(maxsplit=1)[0]

        # Выход из программы
        if command == COMMAND_EXIT:
            if command_line != COMMAND_EXIT:
                print(f'Неизвестная команда: "{command_line}".')
                continue

            print("Выход из программы.")
            break

        # Отображение справки
        if command == COMMAND_HELP:
            if command_line != COMMAND_HELP:
                print(f'Неизвестная команда: "{command_line}".')
                continue

            show_help()
            continue

        # Создание таблицы
        if command == COMMAND_CREATE_TABLE:
            try:
                handle_create_table(command_line)
            except ValueError as error:
                print(f"Ошибка: {error}")
            continue

        # Список таблиц
        if command == COMMAND_LIST_TABLES:
            try:
                handle_list_tables(command_line)
            except ValueError as error:
                print(f"Ошибка: {error}")
            continue

        # Информация о таблице
        if command == COMMAND_INFO:
            try:
                handle_info(command_line)
            except ValueError as error:
                print(f"Ошибка: {error}")
            continue
        # Команды, которые пока не реализованы
        if command in NOT_IMPLEMENTED_COMMANDS:
            print("Команда пока не реализована.")
            continue

        # Неизвестная команда
        print(f'Неизвестная команда: "{command_line}".')
