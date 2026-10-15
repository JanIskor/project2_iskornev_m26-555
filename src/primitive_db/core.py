"""Логика управления структурой таблиц."""

from primitive_db.constants import ID_COLUMN, ID_TYPE, SUPPORTED_TYPES


def is_valid_identifier(name):
    """Проверяет допустимость имени таблицы или столбца."""
    if not name:
        return False

    first_char = name[0]

    if not (
        ("a" <= first_char <= "z") or ("A" <= first_char <= "Z") or first_char == "_"
    ):
        return False

    return all(
        ("a" <= char <= "z")
        or ("A" <= char <= "Z")
        or ("0" <= char <= "9")
        or char == "_"
        for char in name
    )


def create_table(metadata, table_name, columns):
    """Создаёт описание таблицы и возвращает обновлённые метаданные."""
    if not is_valid_identifier(table_name):
        raise ValueError(f'Недопустимое имя таблицы: "{table_name}".')

    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError("Необходимо указать хотя бы один столбец.")

    table_columns = {ID_COLUMN: ID_TYPE}

    for column_name, column_type in columns:
        if not is_valid_identifier(column_name):
            raise ValueError(f'Недопустимое имя столбца: "{column_name}".')

        if column_name == ID_COLUMN:
            raise ValueError('Столбец "ID" создаётся автоматически.')

        if column_name in table_columns:
            raise ValueError(f'Столбец "{column_name}" указан повторно.')

        if column_type not in SUPPORTED_TYPES:
            raise ValueError(
                f'Неподдерживаемый тип "{column_type}" для столбца "{column_name}".'
            )

        table_columns[column_name] = column_type

    updated_metadata = metadata.copy()
    updated_metadata[table_name] = table_columns

    return updated_metadata


def list_tables(metadata):
    """Возвращает список названий существующих таблиц."""
    return sorted(metadata)


def get_table_info(metadata, table_name):
    """Возвращает описание столбцов указанной таблицы."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    return metadata[table_name].copy()


def drop_table(metadata, table_name):
    """Удаляет описание таблицы и возвращает обновлённые метаданные."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    updated_metadata = metadata.copy()
    del updated_metadata[table_name]

    return updated_metadata


def validate_value_type(value, column_type):
    """Проверяет соответствие значения объявленному типу столбца."""
    expected_types = {
        "int": int,
        "str": str,
        "bool": bool,
    }

    expected_type = expected_types.get(column_type)

    if expected_type is None:
        raise ValueError(f'Неподдерживаемый тип данных: "{column_type}".')

    return type(value) is expected_type


def insert_record(columns, records, values):
    """Добавляет запись и возвращает новый список записей."""
    user_columns = [column_name for column_name in columns if column_name != ID_COLUMN]

    if len(values) != len(user_columns):
        raise ValueError(
            f"Некорректное количество значений: "
            f"ожидалось {len(user_columns)}, получено {len(values)}."
        )

    new_record = {}

    for column_name, value in zip(user_columns, values):
        column_type = columns[column_name]

        if not validate_value_type(value, column_type):
            raise ValueError(
                f'Некорректный тип значения для столбца "{column_name}": '
                f"ожидается {column_type}."
            )

        new_record[column_name] = value

    new_id = (
        max(
            (record[ID_COLUMN] for record in records),
            default=0,
        )
        + 1
    )

    new_record = {
        ID_COLUMN: new_id,
        **new_record,
    }

    return [*records, new_record]


def select_records(columns, records, where=None):
    """Возвращает записи таблицы, удовлетворяющие условию."""
    if where is None:
        return [record.copy() for record in records]

    column_name, value = where

    if column_name not in columns:
        raise ValueError(f'Столбец "{column_name}" не существует.')

    column_type = columns[column_name]

    if not validate_value_type(value, column_type):
        raise ValueError(
            f'Некорректный тип значения для столбца "{column_name}": '
            f"ожидается {column_type}."
        )

    return [record.copy() for record in records if record[column_name] == value]


def update_records(columns, records, set_clause, where):
    """Обновляет записи по условию и возвращает новый список и число изменений."""
    set_column, set_value = set_clause
    where_column, where_value = where

    for column_name, value in (set_clause, where):
        if column_name not in columns:
            raise ValueError(f'Столбец "{column_name}" не существует.')

        if not validate_value_type(value, columns[column_name]):
            raise ValueError(
                f'Некорректный тип значения для столбца "{column_name}": '
                f"ожидается {columns[column_name]}."
            )

    if set_column == ID_COLUMN:
        raise ValueError('Изменение столбца "ID" запрещено.')

    updated_records = []
    updated_count = 0

    for record in records:
        new_record = record.copy()

        if record[where_column] == where_value:
            new_record[set_column] = set_value
            updated_count += 1

        updated_records.append(new_record)

    return updated_records, updated_count


def delete_records(columns, records, where):
    """Удаляет записи по условию и возвращает новый список и число удалений."""
    column_name, value = where

    if column_name not in columns:
        raise ValueError(f'Столбец "{column_name}" не существует.')

    if not validate_value_type(value, columns[column_name]):
        raise ValueError(
            f'Некорректный тип значения для столбца "{column_name}": '
            f"ожидается {columns[column_name]}."
        )

    remaining_records = [
        record.copy() for record in records if record[column_name] != value
    ]

    deleted_count = len(records) - len(remaining_records)

    return remaining_records, deleted_count
