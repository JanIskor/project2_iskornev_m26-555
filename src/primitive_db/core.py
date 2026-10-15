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
