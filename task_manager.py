import json
import os
import re
from typing import List, Optional

from task import Task


class TaskManager:
    def __init__(self, filename: str):
        """
        Инициализация менеджера задач.

        :param filename: Путь к файлу для хранения задач в формате JSON.
        """
        self.filename = filename
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> List[Task]:
        """
        Загрузка задач из файла JSON.

        :return: Список объектов Task.
        """
        if not os.path.exists(self.filename):
            return []

        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()  # Убираем лишние пробелы
                if not content:  # Если файл пустой
                    return []
                data = json.loads(content)  # Загружаем JSON из строки
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка при чтении JSON из файла '{self.filename}': {e}") from e

        tasks = []
        for task_data in data:
            task = Task(
                title=task_data["title"],
                description=task_data.get("description", ""),
                category=task_data["category"],
                due_date=task_data["due_date"],
                priority=task_data["priority"],
                status=task_data["status"],
                id=task_data["id"],
            )
            tasks.append(task)
        return tasks

    def _save_tasks(self):
        """
        Сохранение списка задач в файл JSON.
        """
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([task.to_dict() for task in self.tasks], f, ensure_ascii=False, indent=4)

    def add_task(self, title: str, description: Optional[str] = "", category: str = "другое",
                 due_date: Optional[str] = None, priority: str = "отсутствует", status: str = "в процессе"):
        """
        Добавление новой задачи в список и сохранение в файл.
        """
        task = Task(title, description, category, due_date, priority, status)
        self.tasks.append(task)
        self._save_tasks()

    def remove_task(self, task_id: int = None):
        """
        Удаление задачи по ID или категории.
        """
        if task_id:
            self.tasks = [task for task in self.tasks if task.id != task_id]
        self._save_tasks()

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None,
                    category: Optional[str] = None, due_date: Optional[str] = None,
                    priority: Optional[str] = None, status: Optional[str] = None):
        """
        Изменение информации о задаче по ID.
        """
        for task in self.tasks:
            if task.id == task_id:
                if title:
                    task.title = title
                if description:
                    task.description = description
                if category:
                    task.category = Task._normalize_value(category, ["учеба", "работа", "личное", "досуг", "другое"])
                if due_date:
                    task.due_date = Task._parse_due_date(due_date)
                if priority:
                    task.priority = Task._normalize_value(priority, ["высокий", "средний", "низкий", "отсутствует"])
                if status:
                    task.status = Task._normalize_value(status, ["выполнена", "не выполнена", "в процессе"])
                self._save_tasks()
                break

    def mark_as_done(self, task_id: int):
        """
        Отметить задачу как выполненную.
        """
        self.update_task(task_id, status="выполнена")

    def search_by_regex(self, pattern: str) -> List[Task]:
        """
        Поиск задач по регулярному выражению.

        :param pattern: Регулярное выражение для поиска.
        :return: Список найденных задач.
        """
        return [task for task in self.tasks if re.search(pattern, task.title) or
                re.search(pattern, task.description) or
                re.search(pattern, task.category) or
                re.search(pattern, task.status)]

    def search_by_prefix(self, prefix: str, field: Optional[str] = None) -> List[Task]:
        """
        Поиск задач по точному совпадению в начале строки.

        :param prefix: Префикс для поиска.
        :param field: Поле, в котором производится поиск.
        :return: Список найденных задач.
        """
        if field:
            return [task for task in self.tasks if str(getattr(task, field, "")).startswith(prefix)]

        return [task for task in self.tasks if task.title.startswith(prefix) or
                task.description.startswith(prefix) or
                task.category.startswith(prefix) or
                task.status.startswith(prefix) or
                str(task.id).startswith(prefix) or
                str(task.due_date).startswith(prefix)
        ]

    def search_by_term(self, search_term: str, field: Optional[str] = None) -> List[Task]:
        """
        Полный поиск по ключевому слову.

        :param search_term: Ключевое слово для поиска.
        :param field: Поле, в котором производится поиск.
        :return: Список найденных задач.
        """
        if field:
            # Получение значения поля
            return [
                task for task in self.tasks
                if str(search_term) in str(getattr(task, field, ""))
            ]
        return [
            task for task in self.tasks
            if search_term in task.title or
               search_term in task.description or
               search_term in task.category or
               search_term in task.status or
               str(search_term) in str(task.due_date)
        ]

    def search_by_id(self, task_id: int) -> Optional[Task]:
        """
        Поиск задачи по ID.

        :param task_id: ID задачи.
        :return: Найденная задача или None.
        """
        # Используем поиск по полю id
        result = self.search_by_prefix(str(task_id), "id")
        return result[0]

    def search_tasks(self, search_term: str, field: Optional[str] = None) -> List[Task]:
        """
        Универсальный менеджер поиска задач.

        :param search_term: Ключевое слово или регулярное выражение.
        :param field: Поле для поиска (опционально).
        :return: Список найденных задач.
        """
        if search_term.startswith("/"):  # Поиск по регулярному выражению
            pattern = search_term[1:-1]
            return self.search_by_regex(pattern)
        elif search_term.startswith("^"):  # Поиск по префиксу
            prefix = search_term[1:]
            return self.search_by_prefix(prefix, field)
        else:  # Полный поиск
            return self.search_by_term(search_term, field)

