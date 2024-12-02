from datetime import datetime, timedelta

import pytest
import json
from unittest.mock import patch, mock_open
from task_manager import TaskManager
from task import Task


# Фикстуры
@pytest.fixture
def mock_task_file():
    """Мок задачи для тестов."""
    tasks = [
        {
            "id": 3,
            "title": "Задача 1",
            "description": "Описание задачи 1",
            "category": "работа",
            "due_date": "2024-12-31 00:00",
            "priority": "высокий",
            "status": "в процессе"
        },
        {
            "id": 5,
            "title": "Личная задача",
            "description": "Задача по личным делам",
            "category": "личное",
            "due_date": "2024-12-31 00:00",
            "priority": "средний",
            "status": "в процессе"
        }
    ]
    return json.dumps(tasks)


@pytest.fixture
def mock_file_system(mock_task_file):
    """Мок для файловой системы."""
    with patch("builtins.open", mock_open(read_data=mock_task_file)) as mocked_file, \
            patch("os.path.exists", return_value=True):
        yield mocked_file


@pytest.fixture
def empty_file_system():
    """Мок для пустого файла."""
    with patch("builtins.open", mock_open(read_data="")), \
            patch("os.path.exists", return_value=True):
        yield


@pytest.fixture
def task_manager(mock_file_system):
    """Создает TaskManager с замокированным файлом."""
    return TaskManager("mock_file.json")


# Тесты инициализации
def test_init_with_existing_file(mock_file_system):
    """Тест инициализации менеджера с существующим файлом."""
    manager = TaskManager("mock_file.json")
    assert len(manager.tasks) == 2


def test_init_with_empty_file(empty_file_system):
    """Тест инициализации менеджера с пустым файлом."""
    manager = TaskManager("empty_file.json")
    assert len(manager.tasks) == 0


def test_init_with_missing_file():
    """Тест инициализации менеджера при отсутствии файла."""
    with patch("os.path.exists", return_value=False):
        manager = TaskManager("missing_file.json")
        assert len(manager.tasks) == 0


def test_tomli_tasks_invalid_json():
    """Тест загрузки задач из файла с некорректным JSON."""
    with patch("builtins.open", mock_open(read_data="{invalid_json}")), \
            patch("os.path.exists", return_value=True):
        with pytest.raises(ValueError, match="Ошибка при чтении JSON из файла"):
            TaskManager("invalid_file.json")


# Тесты добавления задач
def test_add_task(task_manager):
    """Тест добавления новой задачи."""
    task_manager.add_task(title="New Task", description="Test", category="работа", priority="высокий")
    assert len(task_manager.tasks) == 3  # Включая задачи из mock_task_file
    assert task_manager.tasks[-1].title == "New Task"


# Тесты удаления задач
def test_remove_task_by_id(task_manager):
    """Тест удаления задачи по ID."""
    task_manager.tasks = [Task(id=1, title="Task 1"), Task(id=2, title="Task 2")]
    task_manager.remove_task(task_id=1)
    assert len(task_manager.tasks) == 1
    assert task_manager.tasks[0].id == 2


# Тесты удаления задач
def test_remove_task_by_invalid_id(task_manager):
    """Тест удаления задачи по ID."""
    task_manager.tasks = [Task(id=1, title="Task 1"), Task(id=2, title="Task 2")]
    task_manager.remove_task(task_id=10)
    assert len(task_manager.tasks) == 2


# Тесты обновления задач
import pytest
from task import Task


@pytest.mark.parametrize("field, value, expected", [
    ("title", "Updated Task", "Updated Task"),
    ("description", "Updated Description", "Updated Description"),
    ("category", "личное", "личное"),
    ("due_date", "2024-12-31", "2024-12-31 00:00"),
    ("due_date", "2h 2d", (datetime.now() + timedelta(days=2, hours=2)).strftime("%Y-%m-%d %H:%M")),
    ("priority", "средний", "средний"),
    ("status", "выполнена", "выполнена"),
])
def test_update_task_positive(task_manager, field, value, expected):
    """Позитивный тест обновления задачи по всем возможным полям."""
    task_manager.tasks = [Task(id=1, title="Task 1", status="в процессе")]
    update_kwargs = {field: value}
    task_manager.update_task(1, **update_kwargs)

    updated_task = task_manager.tasks[0]
    actual = getattr(updated_task, field)
    if field == "due_date":
        # Форматирование даты для проверки
        actual = updated_task.due_date.strftime("%Y-%m-%d %H:%M")

    assert actual == expected


@pytest.mark.parametrize("field, invalid_value", [
    ("category", "неизвестная категория"),  # Некорректная категория
    ("priority", "экстренный"),  # Некорректный приоритет
    ("status", "завершено"),  # Некорректный статус
    ("due_date", "invalid_date"),  # Некорректная дата
])
def test_update_task_negative(task_manager, field, invalid_value):
    """Негативный тест обновления задачи с некорректными значениями."""
    task_manager.tasks = [Task(id=1, title="Task 1", status="в процессе")]
    update_kwargs = {field: invalid_value}

    with pytest.raises(ValueError):
        task_manager.update_task(1, **update_kwargs)


# Тесты отметки выполнения задач
def test_mark_as_done(task_manager):
    """Тест отметки задачи как выполненной."""
    task_manager.tasks = [Task(id=1, title="Task 1", status="в процессе")]
    task_manager.mark_as_done(1)
    assert task_manager.tasks[0].status == "выполнена"


# Тесты поиска
@pytest.mark.parametrize("field, pattern, expected_count", [
    ("title", r"Задача", 2),
    ("description", r"Описание задачи", 1),
    ("category", r"личное", 1),
    ("status", r"в процессе", 2),
])
def test_search_by_regex_positive(task_manager, mock_task_file, field, pattern, expected_count):
    """Позитивный тест поиска задач по регулярному выражению."""
    with patch("builtins.open", mock_open(read_data=mock_task_file)):
        task_manager.tasks = [Task(**task) for task in json.loads(mock_task_file)]
        tasks = task_manager.search_by_regex(pattern)
        assert len(tasks) == expected_count


@pytest.mark.parametrize("field, pattern", [
    ("title", r"\("),  # Некорректное регулярное выражение
    ("description", r"Несуществующее описание"),
    ("category", r"несуществующая категория"),
])
def test_search_by_regex_negative(task_manager, mock_task_file, field, pattern):
    """Негативный тест поиска задач по регулярному выражению."""
    with patch("builtins.open", mock_open(read_data=mock_task_file)):
        task_manager.tasks = [Task(**task) for task in json.loads(mock_task_file)]
        tasks = task_manager.search_by_regex(pattern)
        assert len(tasks) == 0


@pytest.mark.parametrize("field, pattern, expected_count", [
    ("title", "Задача 1", 1),
    ("description", "Задача по личным делам", 1),
    ("category", "личное", 1),
    ("status", "в процессе", 2),
])
def test_search_by_prefix_positive(task_manager, mock_task_file, field, pattern, expected_count):
    """Позитивный тест поиска задач по регулярному выражению."""
    with patch("builtins.open", mock_open(read_data=mock_task_file)):
        task_manager.tasks = [Task(**task) for task in json.loads(mock_task_file)]
        tasks = task_manager.search_by_prefix(pattern)
        assert len(tasks) == expected_count


@pytest.mark.parametrize("field, pattern", [
    ("title", "\("),
    ("description", "Несуществующее описание"),
    ("category", "несуществующая категория"),
])
def test_search_by_prefix_negative(task_manager, mock_task_file, field, pattern):
    """Негативный тест поиска задач по префиксному выражению."""
    with patch("builtins.open", mock_open(read_data=mock_task_file)):
        task_manager.tasks = [Task(**task) for task in json.loads(mock_task_file)]

        if field == "title":
            tasks = task_manager.search_by_prefix(pattern)
            assert len(tasks) == 0
        elif field == "description":
            tasks = task_manager.search_by_prefix(pattern)
            assert len(tasks) == 0
        elif field == "category":
            tasks = task_manager.search_by_prefix(pattern)
            assert len(tasks) == 0


@pytest.mark.parametrize("field, pattern, expected_count", [
    ("title", "Зада", 2),
    ("description", " личным делам", 1),
    ("category", "лич", 1),
    ("status", "цессе", 2),
])
def test_search_by_term_positive(task_manager, mock_task_file, field, pattern, expected_count):
    """Позитивный тест поиска задач по терм выражению."""
    with patch("builtins.open", mock_open(read_data=mock_task_file)):
        task_manager.tasks = [Task(**task) for task in json.loads(mock_task_file)]
        tasks = task_manager.search_by_term(pattern)
        assert len(tasks) == expected_count


@pytest.mark.parametrize("field, pattern", [
    ("title", "\("),
    ("description", "Несуществующее описание"),
    ("category", "несуществующая категория"),
])
def test_search_by_term_negative(task_manager, mock_task_file, field, pattern):
    """Негативный тест поиска задач по терм выражению."""
    with patch("builtins.open", mock_open(read_data=mock_task_file)):
        task_manager.tasks = [Task(**task) for task in json.loads(mock_task_file)]
        tasks = task_manager.search_by_term(pattern)
        assert len(tasks) == 0


def test_search_by_id_positive(task_manager, mock_task_file):
    """Позитивный тест поиска задач по префиксному выражению."""
    with patch("builtins.open", mock_open(read_data=mock_task_file)):
        task_manager.tasks = [Task(**task) for task in json.loads(mock_task_file)]
        task = task_manager.search_by_id(3)
        assert task.id == 3
        task = task_manager.search_by_id(5)
        assert task.id == 5


def test_search_by_id_negative(task_manager, mock_task_file):
    """Негативный тест поиска задач по регулярному выражению."""
    with patch("builtins.open", mock_open(read_data=mock_task_file)):
        with pytest.raises(IndexError):
            task_manager.tasks = [Task(**task) for task in json.loads(mock_task_file)]
            task = task_manager.search_by_id(99)
            assert not task

import pytest
from unittest.mock import patch

@pytest.mark.parametrize("search_term, expected_pattern", [
    ("/regex_pattern/", "regex_pattern"),
    ("/another_pattern/", "another_pattern"),
])
def test_search_by_regex(task_manager, search_term, expected_pattern):
    """Тест поиска задач по регулярному выражению."""
    with patch.object(task_manager, "search_by_regex") as mock_search_by_regex:
        task_manager.search_tasks(search_term)
        mock_search_by_regex.assert_called_once_with(expected_pattern)

@pytest.mark.parametrize("search_term, field, expected_prefix", [
    ("^prefix", "title", "prefix"),
    ("^another_prefix", "description", "another_prefix"),
])
def test_search_by_prefix(task_manager, search_term, field, expected_prefix):
    """Тест поиска задач по префиксу."""
    with patch.object(task_manager, "search_by_prefix") as mock_search_by_prefix:
        task_manager.search_tasks(search_term, field)
        mock_search_by_prefix.assert_called_once_with(expected_prefix, field)

@pytest.mark.parametrize("search_term, field", [
    ("exact_term", "category"),
    ("another_term", "status"),
])
def test_search_by_term(task_manager, search_term, field):
    """Тест полного поиска задач."""
    with patch.object(task_manager, "search_by_term") as mock_search_by_term:
        task_manager.search_tasks(search_term, field)
        mock_search_by_term.assert_called_once_with(search_term, field)
