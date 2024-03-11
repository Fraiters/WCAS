import datetime


def is_datetime(date: str) -> bool:
    """ Проверка формата даты """
    try:
        datetime.datetime.strptime(date, '%d.%m.%Y')
        return True

    except Exception:
        return False
