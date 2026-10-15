"""Функции для чтения и записи JSON-файлов."""

import json
import os

from primitive_db.constants import DATA_DIR, METADATA_FILE


def load_metadata():
    """Загружает метаданные таблиц из JSON-файла."""
    if not os.path.exists(METADATA_FILE):
        return {}

    with open(METADATA_FILE, encoding="utf-8") as file:
        return json.load(file)


def save_metadata(metadata):
    """Сохраняет метаданные таблиц в JSON-файл."""
    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    """Загружает записи таблицы из JSON-файла."""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    if not os.path.exists(filepath):
        return []

    with open(filepath, encoding="utf-8") as file:
        return json.load(file)


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в JSON-файл."""
    os.makedirs(DATA_DIR, exist_ok=True)

    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Удаляет JSON-файл таблицы, если он существует."""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    if os.path.exists(filepath):
        os.remove(filepath)
