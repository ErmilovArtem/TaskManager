import pytest
from task import Task

@pytest.mark.parametrize(
    "input_value, valid_values, expected_output",
    [
        ("учеб", ["учеба", "работа", "личное", "досуг", "другое"], "учеба"),
        ("   Работа  ", ["учеба", "работа", "личное", "досуг", "другое"], "работа"),
        ("личное", ["учеба", "работа", "личное", "досуг", "другое"], "личное"),
        ("друге", ["учеба", "работа", "личное", "досуг", "другое"], "другое"),
    ]
)
def test_normalize_value_positive(input_value, valid_values, expected_output):
    assert Task._normalize_value(input_value, valid_values) == expected_output


@pytest.mark.parametrize(
    "input_value, valid_values",
    [
        ("несуществующее", ["учеба", "работа", "личное", "досуг", "другое"]),
        ("", ["учеба", "работа", "личное", "досуг", "другое"]),
        ("ууууу", ["учеба", "работа", "личное", "досуг", "другое"]),
        ("уче", ["личное", "другое"]),
        ("другое", []),
    ]
)
def test_normalize_value_negative(input_value, valid_values):
    with pytest.raises(ValueError):
        Task._normalize_value(input_value, valid_values)

from datetime import datetime, timedelta
import pytest
from task import Task


@pytest.mark.parametrize(
    "due_date, expected_date",
    [
        ("2024-12-15", datetime(2024, 12, 15)),  # Абсолютная дата
        ("2024-12-15 14:30", datetime(2024, 12, 15, 14, 30)),  # Абсолютная дата и время
        ("14:30", datetime.combine(datetime.now().date(), datetime.strptime("14:30", "%H:%M").time())),  # Только время
        ("1d", datetime.now() + timedelta(days=1)),  # Относительная дата (день)
        ("2h 30m", datetime.now() + timedelta(hours=2, minutes=30)),  # Относительная дата (часы, минуты)
        ("1y 2mo", datetime.now() + timedelta(days=366) + timedelta(days=30 + 31)),  # Год и месяцы
        ("2y 4hours", datetime.now() + timedelta(days=365 * 2) + timedelta(hours=4)),  # Год и месяцы
    ]
)
def test_parse_due_date_positive(due_date, expected_date):
    parsed_date = Task._parse_due_date(due_date)
    # Проверяем, что даты совпадают с точностью до минут
    assert parsed_date.strftime("%Y-%m-%d %H:%M") == expected_date.strftime("%Y-%m-%d %H:%M")


@pytest.mark.parametrize(
    "due_date",
    [
        "2024-13-15",  # Некорректный месяц
        "2024-12-32",  # Некорректный день
        "-1years",  # Отрицательное значение
        "abc",  # Некорректный формат
        "",  # Пустая строка
    ]
)
def test_parse_due_date_negative(due_date):
    with pytest.raises(ValueError):
        Task._parse_due_date(due_date)


import pytest
from datetime import datetime
from task import Task


def test_constructor_minimal_params():
    task = Task(title="Test Task")
    assert task.title == "Test Task"
    assert task.description == ""
    assert task.category == "другое"
    assert task.priority == "отсутствует"
    assert task.status == "в процессе"
    assert isinstance(task.due_date, datetime)


def test_constructor_all_params():
    task = Task(
        title="Work Task",
        description="This is a task description.",
        category="работа",
        due_date="2024-12-31",
        priority="высокий",
        status="выполнена",
        id=5,
    )
    assert task.title == "Work Task"
    assert task.description == "This is a task description."
    assert task.category == "работа"
    assert task.priority == "высокий"
    assert task.status == "выполнена"
    assert task.due_date == datetime(2024, 12, 31)
    assert task.id == 5


def test_constructor_autoincrement_id():
    task1 = Task(title="Task 1")
    task2 = Task(title="Task 2")
    assert task1.id < task2.id


def test_constructor_custom_id():
    task = Task(title="Custom ID Task", id=10)
    assert task.id == 10


@pytest.mark.parametrize(
    "title",
    [
        "123 Task",  # Начинается с цифры
        "A valid task",  # Начинается с буквы
        "Задача 1",  # Кириллица
    ]
)
def test_constructor_valid_titles(title):
    task = Task(title=title)
    assert task.title == title


@pytest.mark.parametrize(
    "invalid_title",
    [
        "",  # Пустой заголовок
        "    ",  # Только пробелы
        "!Invalid",  # Начинается с недопустимого символа
        "@Task",  # Недопустимый символ
    ]
)
def test_constructor_invalid_titles(invalid_title):
    with pytest.raises(ValueError, match="Заголовок должен начинаться с буквы или цифры."):
        Task(title=invalid_title)


@pytest.mark.parametrize(
    "invalid_category",
    ["work", "unknown", "123", ""]
)
def test_constructor_invalid_category(invalid_category):
    with pytest.raises(ValueError):
        Task(title="Test Task", category=invalid_category)


@pytest.mark.parametrize(
    "invalid_priority",
    ["urgent", "low-priority", "123", ""]
)
def test_constructor_invalid_priority(invalid_priority):
    with pytest.raises(ValueError):
        Task(title="Test Task", priority=invalid_priority)


@pytest.mark.parametrize(
    "invalid_status",
    ["done", "not-started", "123", ""]
)
def test_constructor_invalid_status(invalid_status):
    with pytest.raises(ValueError):
        Task(title="Test Task", status=invalid_status)


@pytest.mark.parametrize(
    "invalid_due_date",
    [
        "2024-13-01",  # Некорректный месяц
        "invalid-date",  # Некорректный формат
        "-1d",  # Некорректный интервал
        "32:00",  # Некорректное время
    ]
)
def test_constructor_invalid_due_date(invalid_due_date):
    with pytest.raises(ValueError):
        Task(title="Test Task", due_date=invalid_due_date)
