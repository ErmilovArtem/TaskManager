import re
from datetime import datetime, timedelta
from typing import Optional
from rapidfuzz import fuzz, process


class Task:
    """
    Класс для представления задачи с различными атрибутами, включая идентификатор,
    заголовок, описание, категорию, срок выполнения, приоритет и статус.
    """

    _id_counter = 0  # Классовая переменная для автоинкремента идентификатора задач

    def __init__(self, title: str, description: Optional[str] = "", category: str = "другое",
                 due_date: Optional[str] = None, priority: str = "отсутствует",
                 status: str = "в процессе", id: Optional[int] = None):
        """
        Инициализация объекта задачи.

        :param title: Заголовок задачи, должен начинаться с буквы или цифры.
        :param description: Описание задачи (может быть пустым).
        :param category: Категория задачи (учеба, работа, личное, досуг, другое).
        :param due_date: Срок выполнения задачи (строка с датой или временем, например, "1h 2m" или "2024-12-31").
        :param priority: Приоритет задачи (высокий, средний, низкий, отсутствует).
        :param status: Статус задачи (выполнена, не выполнена, в процессе).
        """
        if not re.match(r"^[A-Za-zА-Яа-я0-9]", title):
            raise ValueError("Заголовок должен начинаться с буквы или цифры.")
        self.title = title

        self.description = description if description else ""

        self.category = self._normalize_value(category, ["учеба", "работа", "личное", "досуг", "другое"])
        self.priority = self._normalize_value(priority, ["высокий", "средний", "низкий", "отсутствует"])
        self.status = self._normalize_value(status, ["выполнена", "не выполнена", "в процессе"])

        self.due_date = self._parse_due_date(due_date)

        if id is None:
            self.id = Task._id_counter
            Task._id_counter += 1
        else:
            self.id = id
            Task._id_counter = max(id, Task._id_counter) + 1

    @staticmethod
    def _normalize_value(input_value: str, valid_values: list[str]) -> str:
        input_value = input_value.strip().lower()

        # Получение лучшего совпадения
        result = process.extractOne(input_value, valid_values, scorer=fuzz.ratio)

        if result is None:  # Если совпадений нет
            raise ValueError(f"Некорректное значение '{input_value}'. Допустимые варианты: {valid_values}")

        best_match, score, _ = result
        # Устанавливаем порог для принятия результата
        if score < 70:  # Порог можно настроить
            raise ValueError(f"Некорректное значение '{input_value}'. Допустимые варианты: {valid_values}")

        return best_match

    @staticmethod
    def _normalize_value(input_value: str, valid_values: list[str]) -> str:
        """
        Нормализация значения путем сопоставления с допустимыми вариантами.

        :param input_value: Входное значение для нормализации.
        :param valid_values: Список допустимых значений.
        :return: Наиболее подходящее значение из valid_values.
        :raises ValueError: Если входное значение не соответствует ни одному допустимому варианту.
        """
        input_value = input_value.strip().lower()

        # Поиск наилучшего совпадения
        result = process.extractOne(input_value, valid_values, scorer=fuzz.ratio)
        if result is None:
            raise ValueError(f"Некорректное значение '{input_value}'. Допустимые варианты: {valid_values}")

        best_match, score, _ = result
        if score < 70:
            raise ValueError(f"Некорректное значение '{input_value}'. Допустимые варианты: {valid_values}")
        return best_match

    @staticmethod
    def _parse_due_date(due_date: Optional[str]) -> datetime:
        """
        Разбор строки с датой выполнения задачи.

        :param due_date: Строка с датой выполнения или None.
        :return: Объект datetime, представляющий дату выполнения.
        """
        if due_date is None:
            return datetime.now()

        date_formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M", "%H:%M", "%Y-%m-%dT%H:%M:%S"]
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(due_date, date_format)
                if date_format == "%H:%M":  # Если указано только время, добавляем сегодняшнюю дату
                    today = datetime.now()
                    return datetime.combine(today.date(), parsed_date.time())
                return parsed_date
            except ValueError:
                pass

        # Если явный формат не подошел, парсим относительные даты (например, "1h 2d")
        units = {
            "year": ["year", "years", "y", "год", "годы"],
            "month": ["month", "months", "mo", "месяц", "месяцы"],
            "day": ["day", "days", "d", "день", "дни"],
            "hour": ["hour", "hours", "h", "час", "часы"],
            "minute": ["minute", "minutes", "m", "минута", "минуты"],
        }

        # Инициализация временного дельта
        delta = timedelta()
        extra_months = 0
        extra_years = 0

        # Разделение строки на части и анализ каждой части
        match_bool = False
        for part in due_date.split():
            match = re.match(r"(\d+)\s*(\w+)", part)  # Шаблон: число и единица измерения
            if match:
                match_bool = True
                value, unit = int(match.group(1)), match.group(2).lower()
                # Нормализация единицы измерения
                normalized_unit = Task._normalize_value(unit, [key for sublist in units.values() for key in sublist])
                if normalized_unit in units["year"]:
                    extra_years += value
                elif normalized_unit in units["month"]:
                    extra_months += value
                elif normalized_unit in units["day"]:
                    delta += timedelta(days=value)
                elif normalized_unit in units["hour"]:
                    delta += timedelta(hours=value)
                elif normalized_unit in units["minute"]:
                    delta += timedelta(minutes=value)
        if not match_bool:
            raise ValueError(f"Некорректное значение '{due_date}'.")
        current_date = datetime.now()
        future_date = current_date + delta

        # Обработка добавления месяцев и лет
        if extra_months or extra_years:
            year = future_date.year + extra_years
            month = future_date.month + extra_months
            while month > 12:
                month -= 12
                year += 1
            return future_date.replace(year=year, month=month)

        return future_date

    def to_dict(self) -> dict:
        """Преобразование задачи в словарь."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "due_date": self.due_date.strftime('%Y-%m-%d %H:%M') if self.due_date else None,
            "priority": self.priority,
            "status": self.status
        }

    def __str__(self) -> str:
        """
        Возвращает строковое представление задачи.
        """
        due_date_str = self.due_date.strftime('%Y-%m-%d %H:%M') if self.due_date else "Не установлен"
        return (f"Задача #{self.id}: {self.title}\n"
                f"Описание: {self.description}\n"
                f"Категория: {self.category}\n"
                f"Срок выполнения: {due_date_str}\n"
                f"Приоритет: {self.priority}\n"
                f"Статус: {self.status}")
