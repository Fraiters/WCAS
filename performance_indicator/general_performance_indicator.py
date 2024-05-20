
class GeneralPerformanceIndicator:
    """ Класс для расчета общего показателя эффективности исполнителя """
    general_performance_indicator = 0  # type: float

    @classmethod
    async def calculate_general_performance_indicator(cls, current_performance_indicator: float) -> float:
        """ Расчет общего показателя эффективности исполнителя """
        general_performance_indicator = cls.general_performance_indicator + current_performance_indicator
        cls.general_performance_indicator = round(general_performance_indicator, 2)
        return cls.general_performance_indicator
