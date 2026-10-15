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
    COMMAND_CREATE_TABLE,
    COMMAND_LIST_TABLES,
    COMMAND_DROP_TABLE,
    COMMAND_INSERT,
    COMMAND_SELECT,
    COMMAND_UPDATE,
    COMMAND_DELETE,
    COMMAND_INFO,
}


def show_help():
    """Выводит справку по доступным командам."""
    print(HELP_TEXT)


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

        if command == COMMAND_EXIT:
            if command_line != COMMAND_EXIT:
                print(f'Неизвестная команда: "{command_line}".')
                continue

            print("Выход из программы.")
            break

        if command == COMMAND_HELP:
            if command_line != COMMAND_HELP:
                print(f'Неизвестная команда: "{command_line}".')
                continue

            show_help()
            continue

        if command in NOT_IMPLEMENTED_COMMANDS:
            print("Команда пока не реализована.")
            continue

        print(f'Неизвестная команда: "{command_line}".')
