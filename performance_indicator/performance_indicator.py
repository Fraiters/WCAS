from utils.utils import calculate_delta_date

CONTROL_DELTA_TIME = 3

# коэффициенты срока выполнения (раньше, вовремя, позже)
LATE_COEFFICIENT = 0.1
ON_TIME_COEFFICIENT = 0.2
EARLY_COEFFICIENT = 0.3
# коэффициенты сложности задачи
COMPLEXITY_COEFFICIENTS = {
    "low": 1,
    "medium": 2,
    "high": 3
}


class PerformanceIndicator:
    """ Класс для расчета показателя эффективности """

    def __init__(self):

        self.deadline_coefficient = ...  # type: float
        self.complexity_assessment = ...  # type: float
        self.performance_indicator = ...  # type: float

    async def set_deadline_coefficient(self, deadline: str, closing_date: str):
        delta_time = calculate_delta_date(date1=deadline, date2=closing_date)

        if delta_time >= CONTROL_DELTA_TIME:
            self.deadline_coefficient = LATE_COEFFICIENT
        elif delta_time < CONTROL_DELTA_TIME:
            self.deadline_coefficient = EARLY_COEFFICIENT
        else:
            self.deadline_coefficient = ON_TIME_COEFFICIENT

    async def set_complexity_assessment(self, complexity: str):
        self.complexity_assessment = COMPLEXITY_COEFFICIENTS.get(complexity)

    async def calculate_performance_indicator(self, deadline: str, closing_date: str, complexity: str) -> float:
        """ Расчет показателя эффективности за конкретную выполненную задачу """
        await self.set_deadline_coefficient(deadline=deadline, closing_date=closing_date)
        await self.set_complexity_assessment(complexity=complexity)

        performance_indicator = self.deadline_coefficient * self.complexity_assessment
        # округление до сотых
        self.performance_indicator = round(performance_indicator, 2)
        return self.performance_indicator
