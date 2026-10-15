"""Разбор SQL-подобных команд примитивной базы данных."""


def parse_value(value):
    """Преобразует текстовое значение в int, str или bool."""
    value = value.strip()

    if not value:
        raise ValueError("Некорректное значение: пустой ввод.")

    if value.startswith('"'):
        if len(value) < 2 or not value.endswith('"'):
            raise ValueError(f"Некорректное значение: {value}.")

        return value[1:-1]

    if value.endswith('"'):
        raise ValueError(f"Некорректное значение: {value}.")

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Некорректное значение: {value}.") from None
