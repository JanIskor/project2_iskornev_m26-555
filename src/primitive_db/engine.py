"""Интерактивный интерфейс примитивной базы данных."""

import prompt
from prettytable import PrettyTable

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
from primitive_db.core import (
    create_table,
    delete_records,
    drop_table,
    get_table_info,
    insert_record,
    list_tables,
    select_records,
    update_records,
)
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.parser import (
    parse_delete,
    parse_insert,
    parse_select,
    parse_update,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

HELP_TEXT = (
    "***База данных***\n"
    "\n"
    "Функции:\n"
    "<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу\n"
    "<command> list_tables - показать список всех таблиц\n"
    "<command> drop_table <имя_таблицы> - удалить таблицу\n"
    "<command> insert into <имя_таблицы> values (<значение1>, ...) - создать запись\n"
    "<command> select from <имя_таблицы> where <столбец> = <значение> "
    "- прочитать записи по условию\n"
    "<command> select from <имя_таблицы> - прочитать все записи\n"
    "<command> update <имя_таблицы> set <столбец> = <значение> "
    "where <столбец> = <значение> - обновить запись\n"
    "<command> delete from <имя_таблицы> where <столбец> = <значение> "
    "- удалить запись\n"
    "<command> info <имя_таблицы> - информация о таблице\n"
    "<command> exit - выход из программы\n"
    "<command> help - справочная информация"
)

cache_result = create_cacher()


def reset_cache():
    """Сбрасывает кеш результатов SELECT."""
    global cache_result
    cache_result = create_cacher()


def show_help():
    """Выводит справку по доступным командам."""
    print(HELP_TEXT)


def load_existing_table(table_name):
    """Загружает схему и записи существующей таблицы."""
    metadata = load_metadata()
    columns = get_table_info(metadata, table_name)
    records = load_table_data(table_name)
    return columns, records


@handle_db_errors
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


@handle_db_errors
def handle_list_tables(command_line):
    """Выводит список существующих таблиц."""
    if command_line != COMMAND_LIST_TABLES:
        raise ValueError("Команда list_tables не принимает аргументы.")

    metadata = load_metadata()
    tables = list_tables(metadata)

    if not tables:
        print("В базе данных нет таблиц.")
        return

    for table_name in tables:
        print(f"- {table_name}")


@handle_db_errors
def handle_info(command_line):
    """Выводит структуру таблицы и количество записей."""
    parts = command_line.split()

    if len(parts) != 2:
        raise ValueError("Некорректный синтаксис. Используйте: info <имя>")

    table_name = parts[1]
    columns, records = load_existing_table(table_name)

    columns_description = ", ".join(
        f"{column_name}:{column_type}" for column_name, column_type in columns.items()
    )

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_description}")
    print(f"Количество записей: {len(records)}")


@handle_db_errors
def handle_drop_table(command_line):
    """Проверяет команду и запускает удаление таблицы."""
    parts = command_line.split()

    if len(parts) != 2:
        raise ValueError("Некорректный синтаксис. Используйте: drop_table <имя>")

    table_name = parts[1]
    metadata = load_metadata()

    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    return execute_drop_table(metadata, table_name)


@confirm_action("удаление таблицы")
def execute_drop_table(metadata, table_name):
    """Удаляет таблицу после подтверждения и сбрасывает кеш."""
    updated_metadata = drop_table(metadata, table_name)

    save_metadata(updated_metadata)
    delete_table_data(table_name)
    reset_cache()

    print(f'Таблица "{table_name}" успешно удалена.')


@handle_db_errors
@log_time
def handle_insert(command_line):
    """Добавляет запись в таблицу и сбрасывает кеш SELECT."""
    parsed = parse_insert(command_line)
    table_name = parsed["table"]

    columns, records = load_existing_table(table_name)
    updated_records = insert_record(columns, records, parsed["values"])

    save_table_data(table_name, updated_records)
    reset_cache()

    new_id = updated_records[-1]["ID"]
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')


@handle_db_errors
@log_time
def handle_select(command_line):
    """Выводит записи таблицы, используя кеш повторных запросов."""
    parsed = parse_select(command_line)
    table_name = parsed["table"]
    where = parsed["where"]

    cache_key = (table_name, repr(where))

    def execute_select():
        columns, records = load_existing_table(table_name)
        selected_records = select_records(columns, records, where)
        return columns, selected_records

    columns, selected_records = cache_result(cache_key, execute_select)

    if not selected_records:
        print("Записи не найдены.")
        return

    table = PrettyTable()
    table.field_names = list(columns)

    for record in selected_records:
        table.add_row([record[column_name] for column_name in columns])

    print(table)
    print(f"Найдено записей: {len(selected_records)}")


@handle_db_errors
def handle_update(command_line):
    """Обновляет записи таблицы и сбрасывает кеш при изменениях."""
    parsed = parse_update(command_line)
    table_name = parsed["table"]

    columns, records = load_existing_table(table_name)

    matching_records = select_records(columns, records, parsed["where"])

    updated_records, updated_count = update_records(
        columns,
        records,
        parsed["set"],
        parsed["where"],
    )

    if updated_count:
        save_table_data(table_name, updated_records)
        reset_cache()

    if updated_count == 1:
        record_id = matching_records[0]["ID"]
        print(f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.')
    else:
        print(f"Обновлено записей: {updated_count}")


@handle_db_errors
def handle_delete(command_line):
    """Проверяет команду и запускает удаление записей."""
    parsed = parse_delete(command_line)
    table_name = parsed["table"]

    columns, records = load_existing_table(table_name)

    selected_records = select_records(columns, records, parsed["where"])

    if not selected_records:
        print("Записи для удаления не найдены.")
        return

    return execute_delete(
        table_name,
        columns,
        records,
        parsed["where"],
    )


@confirm_action("удаление записей")
def execute_delete(table_name, columns, records, where):
    """Удаляет записи после подтверждения и сбрасывает кеш."""
    selected_records = select_records(columns, records, where)

    updated_records, deleted_count = delete_records(
        columns,
        records,
        where,
    )

    save_table_data(table_name, updated_records)
    reset_cache()

    if deleted_count == 1:
        record_id = selected_records[0]["ID"]
        print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')
    else:
        print(f"Удалено записей: {deleted_count}")


def run():
    """Запускает интерактивный цикл обработки команд базы данных."""
    print("***База данных***")
    print('Для просмотра доступных команд введите "help".')

    handlers = {
        COMMAND_CREATE_TABLE: handle_create_table,
        COMMAND_LIST_TABLES: handle_list_tables,
        COMMAND_INFO: handle_info,
        COMMAND_DROP_TABLE: handle_drop_table,
        COMMAND_INSERT: handle_insert,
        COMMAND_SELECT: handle_select,
        COMMAND_UPDATE: handle_update,
        COMMAND_DELETE: handle_delete,
    }

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

        if command == COMMAND_EXIT:
            if command_line != COMMAND_EXIT:
                print(f"Функции {command_line} нет. Попробуйте снова.")
                continue

            print("Выход из программы.")
            break

        if command == COMMAND_HELP:
            if command_line != COMMAND_HELP:
                print(f"Функции {command_line} нет. Попробуйте снова.")
                continue

            show_help()
            continue

        handler = handlers.get(command)

        if handler is None:
            print(f"Функции {command} нет. Попробуйте снова.")
            continue

        handler(command_line)
