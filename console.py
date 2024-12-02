import os
import re
from task_manager import TaskManager

def clear_console():
    """Очищает консоль."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Отображает главное меню."""
    print("Выберите действие:")
    print("1. Просмотр / поиск задач")
    print("2. Добавление задачи")
    print("3. Изменение задачи")
    print("4. Удаление задачи")
    print("0. Выход")

def show_search_info():
    """Отображает информацию о возможностях поиска."""
    print("Возможности поиска:")
    print("- Поиск по частичному вхождению (например, 'работа').")
    print("- Поиск по регулярным выражениям (например, '/\\d{4}-\\d{2}-\\d{2}/').")
    print("- Поиск по полю (например, '^личное' для точного совпадения).")

def main():
    task_manager = TaskManager("tasks.json")
    while True:
        try:
            if not task_manager.tasks:
                print("Нет задач для отображения.")
                input("\nНажмите Enter, чтобы добавить задачу...")
                clear_console()
                print("Добавление задачи")
                title = input("Введите заголовок: ")
                description = input("Введите описание: ")
                category = input("Введите категорию (учеба, работа, личное, досуг, другое): ")
                due_date = input("Введите срок выполнения (например, '2024-12-31' или '1h 2m'): ")
                priority = input("Введите приоритет (высокий, средний, низкий, отсутствует): ")
                status = input("Введите статус (выполнена, не выполнена, в процессе): ")
                task_manager.add_task(title, description, category, due_date, priority, status)
                print("\nЗадача добавлена!")
                input("\nНажмите Enter, чтобы вернуться...")
                continue

            clear_console()
            show_menu()
            choice = input("Введите номер действия: ")

            # Просмотр задач
            if choice == "1":
                clear_console()
                print("Просмотр задач")
                print("1. Все задачи")
                print("2. Поиск по вхождению / регулярному выражению")
                print("0. Назад")
                sub_choice = input("\nВыберите действие: ")

                # Вывод всех задач
                if sub_choice == "1":
                    tasks = task_manager.tasks
                    if tasks:
                        for task in tasks:
                            print(task)
                    else:
                        print("Нет задач для отображения.")
                    input("\nНажмите Enter, чтобы вернуться...")

                # Поиск полю / по всем полям с помощью регулярного выражения / полного вхождения / частичного вхождения
                elif sub_choice == "2":
                    print("Поля для поиска: title, description, category, due_date, priority, status")
                    field = input("Введите поле (нажмите Enter, чтобы искать по всем полям): ")
                    clear_console()
                    show_search_info()
                    search_term = input("\nВыражение для поиска: ")

                    if not search_term.strip():
                        print("Выражение для поиска не может быть пустым.")
                    else:
                        try:
                            if field in ['title', 'description', 'category', 'due_date', 'priority', 'status']:
                                tasks = task_manager.search_tasks(search_term, field) if search_term else task_manager.tasks
                            else:
                                if field:
                                    print("Введенное поле не 'title', 'description', 'category', 'due_date', 'priority' или 'status'")
                                    print("поиск будет произведен по всем полям")
                                tasks = task_manager.search_tasks(search_term)

                            if tasks:
                                for task in tasks:
                                    print(task)
                            else:
                                print("По вашему запросу задачи не найдены.")
                        except re.error:
                            print("Некорректное регулярное выражение. Попробуйте снова.")
                    input("\nНажмите Enter, чтобы вернуться...")

            # Добавление задачи
            elif choice == "2":
                clear_console()
                print("Добавление задачи")
                title = input("Введите заголовок: ")
                description = input("Введите описание: ")
                category = input("Введите категорию (учеба, работа, личное, досуг, другое): ")
                due_date = input("Введите срок выполнения (например, '2024-12-31' или '1h 2m'): ")
                priority = input("Введите приоритет (высокий, средний, низкий, отсутствует): ")
                status = input("Введите статус (выполнена, не выполнена, в процессе): ")
                task_manager.add_task(title, description, category, due_date, priority, status)
                print("\nЗадача добавлена!")
                input("\nНажмите Enter, чтобы вернуться...")

            # Изменение задачи
            elif choice == "3":
                clear_console()
                print("Изменение задачи")
                task_id = int(input("Введите ID задачи для изменения: "))
                task = task_manager.search_by_id(task_id)
                if not task:
                    print("Задача не найдена.")
                    input("\nНажмите Enter, чтобы вернуться...")
                    continue

                print(f"Выбрана задача для изменения:\n{task}")
                print(f"\nЧто именно вы хотите изменить?:\n{task}")
                print("0. Назад")
                print("1. Заголовок")
                print("2. Описание")
                print("3. Категория")
                print("4. Срок выполнения")
                print("5. Приоритет")
                print("6. Статус")
                print("7. Отметить задачу как выполненную")
                sub_choice = input("Выберите поле для изменения: ")
                if sub_choice != "0":
                    if sub_choice == "7":
                        task_manager.update_task(task_id, status="выполнена")
                        print("\nЗадача отмечена как выполненная!")
                    else:
                        new_value = input("Введите новое значение: ")
                        fields = ["", "title", "description", "category", "due_date", "priority", "status"]
                        field = fields[int(sub_choice)]
                        task_manager.update_task(task_id, **{field: new_value})
                        print("\nЗадача обновлена!")
                input("\nНажмите Enter, чтобы вернуться...")

            # Удаление задачи
            elif choice == "4":
                clear_console()
                print("Удаление задач")
                print("1. По ID")
                print("2. Поиск по вхождению / регулярному выражению")
                print("0. Назад")

                sub_choice = input("\nВыберите действие: ")
                tasks = []
                if sub_choice == "1":
                    task_id = int(input("Введите ID задачи для удаления: "))
                    tasks = [task_manager.search_by_id(task_id)]
                if sub_choice == "2":
                    show_search_info()
                    search_term = input("\nВведите ключевое слово для поиска задач: ")
                    field = input("Укажите поле для поиска (title, description, category, status) или оставьте пустым: ")
                    tasks = task_manager.search_tasks(search_term, field) if search_term else task_manager.tasks

                if not tasks:
                    print("Задачи не найдены.")
                    input("\nНажмите Enter, чтобы вернуться...")
                    continue

                print("\nНайдены задачи:")
                for task in tasks:
                    print(task)
                confirm = input("\nВы уверены, что хотите удалить эти задачи? (да/нет): ")
                if confirm.lower() == "да":
                    for task in tasks:
                        task_manager.remove_task(task_id=task.id)
                    print("\nЗадачи удалены.")
                else:
                    print("\nУдаление отменено.")
                input("\nНажмите Enter, чтобы вернуться...")

            # Выход
            elif choice == "0":
                print("Выход из программы...")
                break

            else:
                print("Некорректный выбор. Попробуйте снова.")
        except Exception as err:
            print('Ошибка:\n' + str(err))


if __name__ == "__main__":
    task_manager = TaskManager("tasks.json")
    task_manager.add_task("Заголовок 1",
                          "Описание 1",
                          "Учеба",
                          "2h",
                          "Высокий",
                          "в процессе")
    task_manager.add_task("Заголовок 2",
                          "Описание 2",
                          "Работа",
                          "6h",
                          "Низкий",
                          "не выполнена")
    task_manager.add_task("Пример заголовка",
                          "Описание задачи",
                          "Личное",
                          "2024-12-12",
                          "Низкий",
                          "выполнена")
    main()
