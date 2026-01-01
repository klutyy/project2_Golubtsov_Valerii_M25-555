import shlex

from .core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .utils import load_metadata, save_metadata


def print_help():
    """справочная информация"""
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ... - создать таблицу") # noqa: E501
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.") # noqa: E501
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.") # noqa: E501
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.") # noqa: E501
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.") # noqa: E501
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """основной рабочий цикл"""
    print("\n***БАЗА ДАННЫХ***")
    print_help()

    while True:
        metadata = load_metadata()

        try:
            user_input = input('>>> Введите команду: ').strip()
            if not user_input:
                continue

            args = shlex.split(user_input)
            command = args[0].lower()

            if command == 'create_table':
                if len(args) < 3:
                    print('Недостаточно аргументов. Формат: create_table <имя> <столбец:тип> ...') # noqa: E501
                    continue
                table_name = args[1]
                columns = args[2:]
                result = create_table(metadata, table_name, columns)
                if result is not None:
                    save_metadata(result)

            elif command == 'drop_table':
                if len(args) != 2:
                    print('Неверный формат. Используйте: drop_table <имя_таблицы>')
                    continue
                table_name = args[1]
                result = drop_table(metadata, table_name)
                if result is not None:
                    save_metadata(result)

            elif command == 'list_tables':
                list_tables(metadata)

            elif command == 'insert':
                if len(args) < 4 or args[1].lower() != 'into' or args[3].lower() != 'values': # noqa: E501
                    print('Неверный формат. Используйте: insert into <таблица> values (<значение1>, <значение2>, ...)') # noqa: E501
                    continue

                table_name = args[2]

                values_str = ' '.join(args[4:])
                if not values_str.startswith('(') or not values_str.endswith(')'):
                    print('Значения должны быть в скобках.')
                    continue

                values_str = values_str[1:-1]
                values = [v.strip() for v in values_str.split(',')]

                result = insert(metadata, table_name, values)

            elif command == 'select':
                if len(args) < 3 or args[1].lower() != 'from':
                    print('Неверный формат. Используйте: select from <таблица> [where <условие>]') # noqa: E501
                    continue

                table_name = args[2]

                if len(args) > 4 and args[3].lower() == 'where':
                    where_clause = ' '.join(args[4:])
                    select(metadata, table_name, where_clause)
                else:
                    select(metadata, table_name)

            elif command == 'update':
                if len(args) < 4:
                    print('Неверный формат. Используйте: update <таблица> set <столбец>=<значение> where <столбец>=<значение>') # noqa: E501
                    continue

                set_index = -1
                where_index = -1

                for i, arg in enumerate(args):
                    if arg.lower() == 'set':
                        set_index = i
                    elif arg.lower() == 'where':
                        where_index = i

                if set_index == -1 or where_index == -1 or where_index <= set_index + 1:
                    print('Неверный формат. Используйте: update <таблица> set <столбец>=<значение> where <столбец>=<значение>') # noqa: E501
                    continue

                table_name = args[1]
                set_clause = ' '.join(args[set_index + 1:where_index])
                where_clause = ' '.join(args[where_index + 1:])

                result = update(metadata, table_name, set_clause, where_clause)

            elif command == 'delete':
                if len(args) < 4:
                    print('Неверный формат. Используйте: delete from <таблица> where <условие>') # noqa: E501
                    continue

                where_index = -1
                for i in range(2, len(args)):
                    if args[i].lower() == 'where':
                        where_index = i
                        break

                if where_index == -1 or where_index >= len(args) - 1:
                    print('Неверный формат. Используйте: delete from <таблица> where <условие>') # noqa: E501
                    continue

                table_name = args[2] if args[1].lower() == 'from' else args[1]
                where_clause = ' '.join(args[where_index + 1:])

                result = delete(metadata, table_name, where_clause)

            elif command == 'info':
                if len(args) != 2:
                    print('Неверный формат. Используйте: info <имя_таблицы>')
                    continue
                table_name = args[1]
                info(metadata, table_name)

            elif command == 'help':
                print_help()

            elif command == 'exit':
                print('Программа завершена. До свидания!')
                break

            else:
                print(f'Функции "{command}" нет. Попробуйте снова.')

        except KeyboardInterrupt:
            print('\nПрограмма прервана пользователем. До свидания!')
            break
        except Exception as e:
            print(f'Неожиданная ошибка: {e}. Попробуйте снова.')