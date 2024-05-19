import os
from dotenv import load_dotenv

load_dotenv()

# Настройки для подключения к БД
DB_SETTINGS: dict[str, str] = {
    "database": os.getenv('DATABASE'),
    "user": os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "host": os.getenv('HOST'),
    "port": os.getenv('PORT')
}

# Команды БД для задачи
DB_TASKS_COMMANDS = {
    "create_task_table": 'CREATE TABLE IF NOT EXISTS tasks(uuid SERIAL PRIMARY KEY, title TEXT UNIQUE, '
                         'description TEXT, status TEXT, complexity TEXT, deadline TEXT, closing_date TEXT, '
                         'previous_task TEXT, next_task TEXT, executor_type TEXT, executor_id TEXT)',
    "insert_task": 'INSERT INTO  tasks (title, description, status, complexity, deadline, closing_date, previous_task, '
                   'next_task, executor_type, executor_id) '
                   'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
    "select_uuid_by_title": 'SELECT uuid FROM tasks WHERE title = %s',
    "select_title_by_uuid": 'SELECT title FROM tasks WHERE uuid = %s',
    "select_all_tasks": 'SELECT uuid, title FROM tasks',
    "select_task_by_executor_id": 'SELECT * FROM tasks WHERE executor_id = %s',
    "select_task_by_uuid": 'SELECT * FROM tasks WHERE uuid = %s',
    "delete_task": 'DELETE FROM tasks WHERE uuid = %s',
    "update_task": 'UPDATE tasks SET title = %s, description = %s, status = %s, complexity = %s, deadline = %s, '
                   'closing_date = %s, previous_task = %s, next_task = %s, '
                   'executor_type = %s, executor_id = %s WHERE uuid = %s',
}

# Команды БД для отчета
DB_REPORTS_COMMANDS = {
    "create_report_table": 'CREATE TABLE IF NOT EXISTS reports(uuid SERIAL PRIMARY KEY, '
                           'title TEXT UNIQUE, title_related_task TEXT, id_related_task TEXT, description TEXT, '
                           'author TEXT, date TEXT, time TEXT)',
    "insert_report": 'INSERT INTO  reports (title, title_related_task, id_related_task, description, author, '
                     'date, time) '
                     'VALUES (%s, %s, %s, %s, %s, %s, %s)',
    "select_uuid_by_title": 'SELECT uuid FROM reports WHERE title = %s',
    "select_all_reports": 'SELECT uuid, title FROM reports',
    "select_report_by_user_id": 'SELECT * FROM reports WHERE author = %s',
    "select_report_by_uuid": 'SELECT * FROM reports WHERE uuid = %s',
    "delete_report": 'DELETE FROM reports WHERE uuid = %s',
    "update_report": 'UPDATE reports SET title = %s, title_related_task = %s, id_related_task = %s, '
                     'description = %s, author = %s, date = %s, time = %s WHERE uuid = %s',
}

# Команды БД для пользователя
DB_USERS_COMMANDS = {
    "create_user_table": 'CREATE TABLE IF NOT EXISTS users(uuid SERIAL PRIMARY KEY, '
                         'username TEXT UNIQUE, user_id TEXT UNIQUE)',
    "insert_user": 'INSERT INTO  users (username, user_id) VALUES (%s, %s)',
    "select_uuid_by_username": 'SELECT uuid FROM users WHERE username = %s',
    "select_user_id_by_username": 'SELECT user_id FROM users WHERE username = %s',
}
