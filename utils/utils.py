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
