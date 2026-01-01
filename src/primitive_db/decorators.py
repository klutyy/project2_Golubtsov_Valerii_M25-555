import time
from functools import wraps


def handle_db_errors(func):
    """
    Декоратор обработки ошибок
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f'Обращение к несуществующему объекту -> {e}')
            return None
        except ValueError as e:
            print(f'Ошибка валидации: {e}')
            return None
        except FileNotFoundError as e:
            print(f'Ошибка файла: {e}')
            return None
        except Exception as e:
            print(f'Непредвиденная ошибка: {e}')
            return None

    return wrapper


def confirm_action(action_name: str):
    """
    Декоратор для подтверждения операций
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if kwargs.get("confirm") is False:
                return func(*args, **kwargs)

            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            answer = input(question).strip().lower()

            if answer == "y":
                return func(*args, **kwargs)

            print("Операция отменена.")
            return None

        return wrapper

    return decorator


def log_time(func):
    """
    Декоратор для подсчёта времени выполнения функции
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f'Функция {func.__name__} выполнилась за {execution_time:.3f} секунд')

        return result

    return wrapper


def create_cacher():
    """
    Ф-ция создаёт кэшер на замыкании
    """
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result
