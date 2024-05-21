from typing import Tuple


class ExecutorRating:
    """ Модель строки рейтинга исполнителей """

    def __init__(self, current_executor_id: str, new_performance_indicator: float):
        self.executor_id = current_executor_id
        self.performance_indicator = new_performance_indicator

    def from_tuple(self, data: Tuple):
        """ Перевод из кортежа в данные 'строки рейтинга исполнителей' """
        for executor_id, performance_indicator in [data]:
            self.executor_id = executor_id
            self.performance_indicator = performance_indicator

    def to_dict_for_insert(self):
        """Перевод из данных 'строки рейтинга исполнителей' в словарь для вставки"""
        data = {
            "executor_id": self.executor_id,
            "performance_indicator": self.performance_indicator
        }
        return data

    def to_dict_for_update(self):
        """Перевод из данных 'строки рейтинга исполнителей' в словарь для обновления"""
        data = {
            "performance_indicator": self.performance_indicator,
            "executor_id": self.executor_id
        }
        return data
