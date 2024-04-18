DB_NAME = "wcas.db"

# Команды БД для задачи
DB_TASKS_COMMANDS = {
    "create_task_table": 'CREATE TABLE IF NOT EXISTS tasks(uuid SERIAL PRIMARY KEY, title TEXT UNIQUE, '
                         'description TEXT, status TEXT, priority TEXT, deadline TEXT, executor_type TEXT, '
                         'executor_id TEXT)',
    "insert_task": 'INSERT INTO  tasks (title, description, status, priority, deadline, executor_type, executor_id) '
                   'VALUES (%s, %s, %s, %s, %s, %s, %s)',
    "select_uuid_by_title": 'SELECT uuid FROM tasks WHERE title = %s',
    "select_title_by_uuid": 'SELECT title FROM tasks WHERE uuid = %s',
    "select_all_tasks": 'SELECT uuid, title FROM tasks',
    "select_task_by_executor_id": 'SELECT * FROM tasks WHERE executor_id = %s',
    "select_task_by_uuid": 'SELECT * FROM tasks WHERE uuid = %s',
    "delete_task": 'DELETE FROM tasks WHERE uuid = %s',
    "update_task": 'UPDATE tasks SET title = %s, description = %s, status = %s, priority = %s, deadline = %s, '
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
