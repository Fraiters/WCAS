class Analytic:
    """ Класс Аналитика """

    def __init__(self):

        self.analytic_id = ...  # type: str

    def to_dict(self):
        """Перевод из данных 'аналитика' в словарь"""
        data = {
            "executor_id": self.analytic_id,
        }
        return data
