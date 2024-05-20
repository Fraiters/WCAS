from datetime import datetime


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
