from prettytable import PrettyTable

from .decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .utils import load_table_data, save_table_data

ALLOW_TYPES = {'int','str','bool'}

query_cacher = create_cacher()

@handle_db_errors
def create_table(metadata:dict, table_name:str, columns) -> dict:
    """
    Ф-ция создания таблицы
    """
    if table_name in metadata:
        print(f'Данная таблица "{table_name}" уже существует.')
        return None

    prep_columns = []
    for col in columns:
        if ':' not in col:
            print(f'Неверное значение: {col}. Формат ввода: имя:тип')
            return None
        name, dtype = col.split(':', 1)
        if not name or dtype not in ALLOW_TYPES:
            print(f'Неверное значение: {col}. Допустимые типы: {ALLOW_TYPES}')
            return None
        prep_columns.append(f'{name}:{dtype}')

    col_final = ['ID:int'] + prep_columns

    metadata[table_name] = col_final
    print(f'Успешное создание таблицы {table_name}')
    return metadata


@confirm_action("Удаление таблицы")
@handle_db_errors
def drop_table(metadata:dict, table_name:str) -> dict:
    """
    Ф-ция удаляет таблицу
    """
    if table_name not in metadata:
        print(f"Таблицы '{table_name}' не существует")
        return metadata

    del metadata[table_name]

    return metadata

@handle_db_errors
def list_tables(metadata:dict) -> list:
    """
    Ф-ция выводит список всех таблиц
    """
    if not metadata:
        print('Нет таблиц')
        return

    for table in sorted(metadata.keys()):
        print(f'-> {table}')

def preparation_value(raw_str: str, attr_type: str):
    """
    Ф-ция преобразует строку в нужный тип данных
    """
    if attr_type == "bool":
        low = raw_str.strip().lower()
        if low in ("true", "1", "yes", "y"):
            return True
        if low in ("false", "0", "no", "n"):
            return False
        else:
            raise ValueError(f'Некорректное bool значение: {raw_str}')

    if attr_type == "str":
        s = raw_str.strip()
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")): # noqa: E501
            return s[1:-1]
        return s

    if attr_type == "int":
        try:
            return int(raw_str)
        except ValueError:
            raise ValueError(f'Некорректное int значение: {raw_str}')

    return False

def convert2string(value):
    """
    Ф-ция конвертирует в строку
    """
    if isinstance(value, bool):
        return str(value)
    return str(value)


@log_time
@handle_db_errors
def insert(metadata:dict, table_name:str, values:list) -> dict:
    """
    Ф-ция вставляет данные в таблицу
    """
    if table_name not in metadata:
        print(f"Таблицы '{table_name}' не существует")
        return metadata

    data = load_table_data(table_name)
    columns_schema = metadata[table_name]
    data_col = columns_schema[1:]

    if len(values) != len(data_col):
        print(f'Различается количество полученных значений {len(values)} и количество полей: {len(data_col)}') # noqa: E501
        return None

    preparated_values = []
    for i, value in enumerate(values):
        col_name, col_type = data_col[i].split(':',1)
        try:
            prep_value = preparation_value(value, col_type)
            preparated_values.append(prep_value)
        except ValueError as e:
            print(f'Ошибка в "{value}". Столбец "{col_name}": {e}')
            return None

    new_id = 1
    if data:
        ids = [record['ID'] for record in data]
        new_id = max(ids) + 1

    record = {'ID': new_id}
    for i, col in enumerate(data_col):
        col_name = col.split(':')[0]
        record[col_name] = preparated_values[i]

    data.append(record)
    save_table_data(table_name, data)

    print(f'Запись добавлена в таблицу "{table_name}"')
    return data

def parse_where(condition_str):
    """
    Ф-ция для парсинга условий WHERE
    """
    if '=' in condition_str:
        parts = condition_str.split('=', 1)
        column = parts[0].strip()
        value = parts[1].strip()
        return column, value
    return None

@log_time
@handle_db_errors
def select(metadata, table_name, where_clause=None):
    """
    Ф-ция для выбора данных
    """
    if table_name not in metadata:
        print(f'Таблицы "{table_name}" не существует.')
        return

    def execution_select():
        table_data = load_table_data(table_name)

        if not table_data:
            print(f'Таблица "{table_name}" пустая')
            return

        # фильтрация
        filtered_data = table_data
        if where_clause:
            column, value = parse_where(where_clause)
            if not column:
                print('Некорректное условие WHERE')
                return

            col_type = 'str'
            for col_schema in metadata[table_name]:
                col_name, col_type_str = col_schema.split(':')
                if col_name == column:
                    col_type = col_type_str
                    break

            try:
                parsed_value = preparation_value(value, col_type)
            except ValueError as e:
                print(f'Ошибка в условии WHERE: {e}')
                return

            filtered_data = [record for record in table_data
                             if str(record.get(column, '')) == str(parsed_value)]

        if not filtered_data:
            print('Записи не найдены')
            return

        table = PrettyTable()
        table.field_names = [col.split(':')[0] for col in metadata[table_name]]

        for record in filtered_data:
            row = []
            for col in metadata[table_name]:
                col_name = col.split(':')[0]
                row.append(convert2string(record.get(col_name, '')))
            table.add_row(row)

        print(table)
        return filtered_data

    cache_key = f"select_{table_name}_{where_clause}"

    return query_cacher(cache_key, execution_select)


@handle_db_errors
def update(metadata, table_name, set_clause, where_clause):
    """
    Ф-ция обновляет записи в таблице
    """
    if table_name not in metadata:
        print(f'Таблицы "{table_name}" не существует')
        return None

    table_data = load_table_data(table_name)

    if not table_data:
        print(f'Таблица "{table_name}" пустая')
        return None

    set_column, set_value = parse_where(set_clause)
    where_column, where_value = parse_where(where_clause)

    if not set_column or not where_column:
        print('Некорректный формат условия')
        return None

    set_col_type = 'str'
    for col_schema in metadata[table_name]:
        col_name, col_type_str = col_schema.split(':')
        if col_name == set_column:
            set_col_type = col_type_str
            break

    where_col_type = 'str'
    for col_schema in metadata[table_name]:
        col_name, col_type_str = col_schema.split(':')
        if col_name == where_column:
            where_col_type = col_type_str
            break

    try:
        parsed_set_value = preparation_value(set_value, set_col_type)
        parsed_where_value = preparation_value(where_value, where_col_type)
    except ValueError as e:
        print(f'Ошибка в значении: {e}')
        return None

    updated_count = 0
    updated_ids = []

    for record in table_data:
        if str(record.get(where_column, '')) == str(parsed_where_value):
            record[set_column] = parsed_set_value
            updated_count += 1
            updated_ids.append(record['ID'])

    if updated_count == 0:
        print('Записи для обновления не найдены')
        return None

    save_table_data(table_name, table_data)

    print(f'Запись с ID={updated_ids[0]} в таблице "{table_name}" успешно обновлена')
    return table_data

@handle_db_errors
def delete(metadata, table_name, where_clause):
    """
    Ф-ция удаляет строки из таблицы
    """
    if table_name not in metadata:
        print(f'Таблицы "{table_name}" не существует')
        return None

    table_data = load_table_data(table_name)

    if not table_data:
        print(f'Таблица "{table_name}" пустая')
        return None

    where_column, where_value = parse_where(where_clause)
    if not where_column:
        print('Некорректное условие WHERE')
        return None

    where_col_type = 'str'
    for col_schema in metadata[table_name]:
        col_name, col_type_str = col_schema.split(':')
        if col_name == where_column:
            where_col_type = col_type_str
            break

    try:
        parsed_where_value = preparation_value(where_value, where_col_type)
    except ValueError as e:
        print(f'Ошибка в условии WHERE: {e}')
        return None

    records2keep = []
    deleted_ids = []

    for record in table_data:
        if str(record.get(where_column, '')) == str(parsed_where_value):
            deleted_ids.append(record['ID'])
        else:
            records2keep.append(record)

    if not deleted_ids:
        print('Записи для удаления не найдены.')
        return None

    save_table_data(table_name, records2keep)

    print(f'Запись успешно удалена из таблицы "{table_name}"')
    return records2keep


@handle_db_errors
def info(metadata, table_name):
    """
    Ф-ция выводит информацию о таблице
    """
    if table_name not in metadata:
        print(f'Таблицы "{table_name}" не существует')
        return

    table_data = load_table_data(table_name)

    print(f'Таблица: {table_name}')
    print(f'Столбцы: {", ".join(metadata[table_name])}')
    print(f'Количество записей: {len(table_data)}')