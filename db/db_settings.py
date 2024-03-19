DB_NAME = "wcas.db"

# Команды БД для задачи
DB_TASKS_COMMANDS = {
    "create_task_table": 'CREATE TABLE IF NOT EXISTS tasks(uuid INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, '
                         'description TEXT, status TEXT, priority TEXT, deadline TEXT, executor_type TEXT, '
                         'executor_id TEXT)',
    "insert_task": 'INSERT INTO  tasks (title, description, status, priority, deadline, executor_type, executor_id) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?)',
    "select_uuid_by_title": 'SELECT uuid FROM tasks WHERE title = ?',
    "select_title_by_uuid": 'SELECT title FROM tasks WHERE uuid = ?',
    "select_all_tasks": 'SELECT uuid, title FROM tasks',
    "select_task_by_executor_id": 'SELECT * FROM tasks WHERE executor_id = ?',
    "select_task_by_uuid": 'SELECT * FROM tasks WHERE uuid = ?'
}

# Команды БД для отчета
DB_REPORTS_COMMANDS = {
    "create_report_table": 'CREATE TABLE IF NOT EXISTS reports(uuid INTEGER PRIMARY KEY AUTOINCREMENT, '
                           'title TEXT UNIQUE, title_related_task TEXT, id_related_task TEXT, description TEXT, '
                           'author TEXT, date TEXT, time TEXT)',
    "insert_report": 'INSERT INTO  reports (title, title_related_task, id_related_task, description, author, '
                     'date, time) '
                     'VALUES (?, ?, ?, ?, ?, ?, ?)',
    "select_uuid_by_title": 'SELECT uuid FROM reports WHERE title = ?',
    "select_all_reports": 'SELECT uuid, title FROM reports',
    "select_report_by_user_id": 'SELECT * FROM reports WHERE author = ?',
    "select_report_by_uuid": 'SELECT * FROM reports WHERE uuid = ?'
}
