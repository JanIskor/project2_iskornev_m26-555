"""Декораторы для обработки ошибок, подтверждений и замера времени."""

import time

import prompt


def handle_db_errors(func):
    """Перехватывает ожидаемые ошибки при работе с базой данных."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, FileNotFoundError) as error:
            print(f"Ошибка: {error}")
            return None

    return wrapper


def confirm_action(action_name):
    """Создаёт декоратор подтверждения потенциально опасной операции."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f"Вы уверены, что хотите выполнить {action_name}? (y/n): "
            )

            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Измеряет время выполнения функции."""

    def wrapper(*args, **kwargs):
        start_time = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed_time = time.monotonic() - start_time
            print(f"Время выполнения: {elapsed_time:.6f} сек.")

    return wrapper
