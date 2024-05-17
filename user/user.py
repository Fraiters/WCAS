class User:
    """ Класс Пользователя """

    def __init__(self, username: str, user_id: str):

        self.username = username
        # id пользователя для отправки сообщений
        self.user_id = user_id

    def to_dict(self):
        """Перевод из данных 'пользователя' в словарь"""
        data = {
            "username": self.username,
            "user_id": self.user_id,
        }
        return data
