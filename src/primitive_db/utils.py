import json
import os


def load_metadata(filepath='db_meta.json') -> dict:
    """
    Ф-ция загрузки данных из json
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(data, filepath='db_meta.json') -> None:
    """
    Ф-ция сохранения данных в json
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_table_data(table_name:str, data_dir:str = "data") -> list:
    """
    Ф-ция загружает данные таблицы из json
    """
    filepath = os.path.join(data_dir, f"{table_name}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: dict, data_dir: str = "data") -> None:
    """
    Ф-ция сохраняет данные таблицы в json
    """
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, f"{table_name}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)