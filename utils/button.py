from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import List


class Button:
    """Класс для работы с кнопками"""
    kb = ...

    def add(self, names: List[str]):
        """Добавление кнопок

        :param names: список названий кнопок
        """
        # список кнопок
        buttons = [KeyboardButton(name) for name in names]
        self.kb = ReplyKeyboardMarkup(resize_keyboard=True)

        for button in buttons:
            self.kb.add(button)
