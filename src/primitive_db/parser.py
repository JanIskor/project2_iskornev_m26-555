"""Разбор SQL-подобных команд примитивной базы данных."""

import shlex


def parse_value(value):
    """Преобразует текстовое значение в int, str или bool."""
    value = value.strip()

    if not value:
        raise ValueError("Некорректное значение: пустой ввод.")

    if value.startswith('"'):
        if len(value) < 2 or not value.endswith('"'):
            raise ValueError(f"Некорректное значение: {value}.")

        content = value[1:-1]

        if '"' in content:
            raise ValueError(f"Некорректное значение: {value}.")

        return content

    if '"' in value:
        raise ValueError(f"Некорректное значение: {value}.")

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Некорректное значение: {value}.") from None


def parse_values(text):
    """Разбирает список значений в круглых скобках."""
    text = text.strip()

    if not text.startswith("(") or not text.endswith(")"):
        raise ValueError("Некорректный список значений: ожидаются круглые скобки.")

    content = text[1:-1]

    if not content.strip():
        raise ValueError("Некорректный список значений: список пуст.")

    try:
        lexer = shlex.shlex(content, posix=True)
        lexer.whitespace_split = True
        lexer.commenters = ""
        list(lexer)
    except ValueError:
        raise ValueError("Некорректный список значений: незакрытые кавычки.") from None

    values = []
    current = []
    inside_quotes = False

    for char in content:
        if char == '"':
            inside_quotes = not inside_quotes
            current.append(char)

        elif char == "," and not inside_quotes:
            value = "".join(current).strip()

            if not value:
                raise ValueError("Некорректный список значений: пропущено значение.")

            values.append(parse_value(value))
            current = []

        else:
            current.append(char)

    if inside_quotes:
        raise ValueError("Некорректный список значений: незакрытые кавычки.")

    value = "".join(current).strip()

    if not value:
        raise ValueError("Некорректный список значений: лишняя запятая.")

    values.append(parse_value(value))

    return values


def parse_insert(command):
    """Разбирает команду insert into <Название таблицы> values (...)."""
    command = command.strip()

    parts = command.split(maxsplit=3)

    if len(parts) != 4:
        raise ValueError("Некорректная команда insert.")

    operation, keyword, table_name, remainder = parts

    if operation != "insert" or keyword != "into":
        raise ValueError("Некорректная команда insert.")

    if not table_name.isascii() or not table_name.replace("_", "").isalnum():
        raise ValueError(f"Некорректное имя таблицы: {table_name}.")

    if table_name[0].isdigit():
        raise ValueError(f"Некорректное имя таблицы: {table_name}.")

    values_parts = remainder.split(maxsplit=1)

    if len(values_parts) != 2 or values_parts[0] != "values":
        raise ValueError("Некорректная команда insert: ожидается values.")

    values_text = values_parts[1]
    values = parse_values(values_text)

    return {
        "table": table_name,
        "values": values,
    }


def parse_condition(condition):
    """Разбирает условие <column> = <value>."""
    inside_quotes = False
    operator_positions = []

    for index, char in enumerate(condition):
        if char == '"':
            inside_quotes = not inside_quotes
        elif char == "=" and not inside_quotes:
            operator_positions.append(index)

    if inside_quotes:
        raise ValueError("Некорректное условие: незакрытые кавычки.")

    if len(operator_positions) != 1:
        raise ValueError("Некорректное условие: ожидается один оператор =.")

    position = operator_positions[0]

    column_name = condition[:position].strip()
    value_text = condition[position + 1 :].strip()

    if (
        not column_name
        or not column_name.isascii()
        or not column_name.replace("_", "").isalnum()
        or column_name[0].isdigit()
    ):
        raise ValueError(f"Некорректное имя столбца: {column_name}.")

    value = parse_value(value_text)

    return column_name, value


def parse_select(command):
    """Разбирает команду select from <Название таблицы> [where <column> = <value>]."""
    command = command.strip()
    parts = command.split(maxsplit=3)

    if len(parts) < 3:
        raise ValueError("Некорректная команда select.")

    if parts[0] != "select" or parts[1] != "from":
        raise ValueError("Некорректная команда select.")

    table_name = parts[2]

    if (
        not table_name.isascii()
        or not table_name.replace("_", "").isalnum()
        or table_name[0].isdigit()
    ):
        raise ValueError(f"Некорректное имя таблицы: {table_name}.")

    if len(parts) == 3:
        return {
            "table": table_name,
            "where": None,
        }

    remainder = parts[3]
    condition_parts = remainder.split(maxsplit=1)

    if len(condition_parts) != 2 or condition_parts[0] != "where":
        raise ValueError("Некорректная команда select: ожидается where.")

    column_name, value = parse_condition(condition_parts[1])

    return {
        "table": table_name,
        "where": (column_name, value),
    }


def parse_update(command):
    """Разбирает команду update с условиями set и where."""
    command = command.strip()
    parts = command.split(maxsplit=3)

    if len(parts) != 4 or parts[0] != "update":
        raise ValueError("Некорректная команда update.")

    table_name = parts[1]

    if (
        not table_name.isascii()
        or not table_name.replace("_", "").isalnum()
        or table_name[0].isdigit()
    ):
        raise ValueError(f"Некорректное имя таблицы: {table_name}.")

    if parts[2] != "set":
        raise ValueError("Некорректная команда update: ожидается set.")

    remainder = parts[3]

    # Ищем ключевое слово where вне строковых литералов.
    inside_quotes = False
    where_position = None

    for index, char in enumerate(remainder):
        if char == '"':
            inside_quotes = not inside_quotes

        if not inside_quotes and remainder[index : index + 5] == "where":
            before = index == 0 or remainder[index - 1].isspace()
            after = index + 5 == len(remainder) or remainder[index + 5].isspace()

            if before and after:
                where_position = index
                break

    if where_position is None:
        raise ValueError("Некорректная команда update: ожидается where.")

    set_text = remainder[:where_position].strip()
    where_text = remainder[where_position + 5 :].strip()

    if not set_text:
        raise ValueError("Некорректная команда update: отсутствует set-условие.")

    if not where_text:
        raise ValueError("Некорректная команда update: отсутствует where-условие.")

    set_column, set_value = parse_condition(set_text)
    where_column, where_value = parse_condition(where_text)

    return {
        "table": table_name,
        "set": (set_column, set_value),
        "where": (where_column, where_value),
    }


def parse_delete(command):
    """Разбирает команду delete from <table> where <condition>."""
    command = command.strip()
    parts = command.split(maxsplit=4)

    if len(parts) != 5:
        raise ValueError("Некорректная команда delete.")

    operation, keyword, table_name, where_keyword, condition = parts

    if operation != "delete" or keyword != "from":
        raise ValueError("Некорректная команда delete.")

    if (
        not table_name.isascii()
        or not table_name.replace("_", "").isalnum()
        or table_name[0].isdigit()
    ):
        raise ValueError(f"Некорректное имя таблицы: {table_name}.")

    if where_keyword != "where":
        raise ValueError("Некорректная команда delete: ожидается where.")

    column_name, value = parse_condition(condition)

    return {
        "table": table_name,
        "where": (column_name, value),
    }
