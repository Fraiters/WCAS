class Executor:
    """ Класс Исполнителя """

    def __init__(self):

        self.executor_id = ...  # type: str

    def to_dict(self):
        """Перевод из данных 'исполнителя' в словарь"""
        data = {
            "executor_id": self.executor_id,
        }
        return data
