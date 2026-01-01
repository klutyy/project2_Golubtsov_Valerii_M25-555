def _convert_value(value: str):
    """
    Преобразует строку в int, bool или строку без кавычек.
    """
    value = value.strip()

    # Удаляем кавычки, если есть
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    # Преобразуем в число, если это целое
    if value.isdigit():
        return int(value)

    # Преобразуем в bool, если это true/false
    lowered = value.lower()
    if lowered in ["true", "false"]:
        return lowered == "true"

    # Иначе возвращаем как есть (строка)
    return value

def parse_where_clause(where_str: str) -> dict:
    """
    Парсит строку условия WHERE в словарь.
    Пример: 'age = 30 and active = true' -> {'age': 30, 'active': True}
    """
    conditions: dict = {}
    parts = where_str.split(" and ")

    for part in parts:
        if "=" not in part:
            continue

        key, value = part.split("=", 1)
        key = key.strip()
        value = _convert_value(value)

        conditions[key] = value

    return conditions

def parse_set_clause(set_str: str) -> dict:
    """
    Парсит строку SET в словарь.
    Пример: 'age = 30, active = false' -> {'age': 30, 'active': False}
    """
    set_clause: dict = {}
    parts = set_str.split(",")

    for part in parts:
        if "=" not in part:
            continue

        key, value = part.split("=", 1)
        key = key.strip()
        value = _convert_value(value)

        set_clause[key] = value

    return set_clause

def parse_values(values_str: str) -> list:
    """
    Парсит строку VALUES в список значений.
    Пример: '(1, \"John\", true)' -> [1, 'John', True]
    """
    # Удаляем внешние скобки, если есть
    values_str = values_str.strip()
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]

    values: list = []
    parts = values_str.split(",")

    for part in parts:
        value = _convert_value(part)
        values.append(value)

    return values
