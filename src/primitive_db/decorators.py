"""Декораторы для обработки ошибок, подтверждений и замера времени."""

import time

import prompt


def handle_db_errors(func):
    """Перехватывает ошибки БД и выводит понятные сообщения."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except (KeyError, ValueError, FileNotFoundError) as error:
            message = str(error)

            if isinstance(error, ValueError) and message.startswith(
                "Некорректное значение:"
            ):
                print(f"{message} Попробуйте снова.")
            else:
                print(f"Ошибка: {message}")

            return None

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед опасной операцией."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
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
            print(f"Функция {func.__name__} выполнилась за {elapsed_time:.3f} секунд.")

    return wrapper


def create_cacher():
    """Создаёт независимый кеш результатов запросов."""

    cache = {}

    def cache_result(key, value_func):
        """Возвращает сохранённый результат или вычисляет и сохраняет новый."""
        if key not in cache:
            cache[key] = value_func()

        return cache[key]

    return cache_result
