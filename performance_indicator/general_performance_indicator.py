from typing import Tuple, Union


class GeneralPerformanceIndicator:
    """ Класс для расчета общего показателя эффективности исполнителя """
    general_performance_indicator = ...  # type: float

    @classmethod
    async def calculate_general_performance_indicator(cls, db_executor_rating: Union[Tuple, None],
                                                      current_performance_indicator: float) -> float:
        """ Расчет общего показателя эффективности исполнителя """

        if db_executor_rating is None:
            cls.general_performance_indicator = 0
        else:
            # приравниваем к значению показателя эффективности из таблицы в БД
            cls.general_performance_indicator = db_executor_rating[0]

        general_performance_indicator = cls.general_performance_indicator + current_performance_indicator
        cls.general_performance_indicator = round(general_performance_indicator, 2)
        return cls.general_performance_indicator
