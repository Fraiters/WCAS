from aiogram.types import ReplyKeyboardMarkup
from utils.button import Button
from typing import List


class GeneralKb:
    """Класс для управления главной клавиатурой """
    kb = ...  # type: ReplyKeyboardMarkup

    def __init__(self):
        self.button = Button()

    def add(self, names_buttons: List[str]):
        """Добавление кнопок на главном меню при запуске

        :param names_buttons: список добавляемых кнопок
        :return: объект клавиатуры
        """
        self.button.add(names=names_buttons)
        self.kb = self.button.kb
        return self.kb
