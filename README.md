# PrimitiveDB

Простая консольная БД.  
Работает через терминал и поддерживает базовые CRUD-операции

---

## Установка

### Вариант 1 — через Poetry
```bash
poetry install
```

### Вариант 2 - через Makefile

```
make install
```

## Запуск игры

### Вариант 1 — через Poetry
```bash
poetry run project
```

### Вариант 2 - через Makefile
```
make project
```

## Поддерживаемые типы данных

- `int`
- `str`
- `bool`

---

## Управление таблицами

### Команды
**Для получения всех команд используйте help*

| Команда | Описание |
|-------|----------|
| `create_table <table> <column:type> ...` | Создать таблицу. Столбец `ID:int` добавляется автоматически |
| `drop_table <table>` | Удалить таблицу |
| `list_tables` | Показать список таблиц |
| `info <table>` | Показать информацию о таблице |
| `help` | Показать справку |
| `exit` | Выйти из программы 

### Пример

```
create_table users name:str age:int active:bool
list_tables
info users
```

Имеет механизм кэширования