# Кнопки в главном меню
GENERAL_BUTTONS = ['/start', '/help', '/Задачи', '/Отчеты']

# Кнопки для задачи
TASK_BUTTONS = {
    "task": ["/Добавить_задачу", "/Показать_задачу", "/Редактировать_задачу", "/Удалить_задачу", "/Назначить_задачу",
             "/Отмена"],
    "status": ["/ToDo", "/Doing", "/Done"],
    "priority": ["/low", "/medium", "/high"],
    "executor_type": ["/developer", "/tester"],
    "prepare_executor_id": ["/Да", "/Нет"],
    "check_task": ["/Да", "/Нет, необходима правка"],
    "show_tasks": ["/Показать_все_задачи", "/Показать_задачи_по_id_исполнителя",
                   "/Показать_задачу_по_уникальному_id"],
}

# Кнопки для составления отчета
REPORT_BUTTONS = {
    "report": ["/Добавить_отчет", "/Показать_отчет", "/Редактировать_отчет", "/Удалить_отчет"],
    "check_report": ["/Да", "/Нет, необходима правка"],
    "show_reports": ["/Показать_все_отчеты", "/Показать_отчеты_по_id_исполнителя",
                     "/Показать_отчет_по_уникальному_id"],
}
