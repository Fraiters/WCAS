from datetime import datetime
from typing import List

from user.db.user_db import UserDb


def is_datetime(date: str) -> bool:
    """ Проверка формата даты """
    try:
        datetime.strptime(date, '%d.%m.%Y')
        return True

    except Exception:
        return False


def get_current_date():
    """ Получение текущей даты в европейском формате """
    current_date = datetime.now().strftime('%d.%m.%Y')
    return current_date


def calculate_delta_date(date1: str, date2: str) -> int:
    """ Вычисление дельты дней между двумя датами

    :param date1: вычитаемая дата
    :param date2: уменьшаемая дата
    :return result: разность (в днях)
    """

    date1_times = datetime.strptime(date1, '%d.%m.%Y')
    date2_times = datetime.strptime(date2, '%d.%m.%Y')
    delta_time = date2_times - date1_times
    result = delta_time.days
    return result


def text_table_layout(data: List[List[str]], columns: List[str]) -> str:
    """ Компоновка текста-таблицы

    :param data: данные для таблицы
    :param columns: названия столбцов
    :return text_table: текст таблицы
    """
    # расчёт максимальной длины колонок
    max_columns = []  # список максимальной длины колонок
    for col in zip(*data):
        len_el = []
        [len_el.append(len(el)*2) for el in col]
        max_columns.append(max(len_el))

    text_table_list = []

    for column in columns:
        line = f'{column:{max(max_columns) + 3}}'
        text_table_list.append(line)
    text_table_list.append("\n")
    # разделитель шапки
    table_header = f'{"=" * max(max_columns) * 2}'
    text_table_list.append(table_header)
    text_table_list.append("\n")

    # тело таблицы
    for el in data:
        for col in el:
            table_body = f'{col:{max(max_columns) * 2}}'
            text_table_list.append(table_body)
        text_table_list.append("\n")

    text_table = "".join(text_table_list)
    return text_table


def date_time_join(date: str, time: str) -> datetime:
    """ Объединение двух строк даты и времени в формате "%d.%m.%Y %H:%M"

    :return formatted_date_time: объект даты и времени в формате "%d.%m.%Y %H:%M"
    """
    date_time_str = " ".join([date, time])

    date_time_object = datetime.strptime(date_time_str, "%d.%m.%Y %H:%M")

    return date_time_object
