from aiogram.types import ReplyKeyboardMarkup
from utils.button import Button
from typing import List


class ExecutorKb:
    """Класс для управления клавиатурой "исполнителей" """
    kb = ...  # type: ReplyKeyboardMarkup

    def __init__(self):
        self.button = Button()

    def add(self, names_buttons: List[str]):
        """Добавление кнопок "исполнителей"

        :param names_buttons: список добавляемых кнопок
        :return: объект клавиатуры
        """
        self.button.add(names=names_buttons)
        self.kb = self.button.kb
        return self.kb
