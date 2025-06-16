import unittest
import os
import tempfile
import json
from todo import TodoItem, TodoManager


class TestTodoItem(unittest.TestCase):

    def test_todo_item_creation(self):
        todo = TodoItem(1, "Teste")
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.description, "Teste")
        self.assertFalse(todo.completed)
        self.assertIsNotNone(todo.created_at)

    def test_todo_item_to_dict(self):
        todo = TodoItem(1, "Teste", True, "2024-01-01T10:00:00")
        expected = {
            "id": 1,
            "description": "Teste",
            "completed": True,
            "created_at": "2024-01-01T10:00:00",
        }
        self.assertEqual(todo.to_dict(), expected)

    def test_todo_item_from_dict(self):
        data = {
            "id": 1,
            "description": "Teste",
            "completed": True,
            "created_at": "2024-01-01T10:00:00",
        }
        todo = TodoItem.from_dict(data)
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.description, "Teste")
        self.assertTrue(todo.completed)
        self.assertEqual(todo.created_at, "2024-01-01T10:00:00")


class TestTodoManager(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        )
        self.temp_file.close()
        self.todo_manager = TodoManager(self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_add_todo(self):
        todo = self.todo_manager.add_todo("Minha tarefa")
        self.assertEqual(todo.description, "Minha tarefa")
        self.assertEqual(todo.id, 1)
        self.assertFalse(todo.completed)
        self.assertEqual(len(self.todo_manager.todos), 1)

    def test_complete_todo(self):
        todo = self.todo_manager.add_todo("Tarefa para completar")

        result = self.todo_manager.complete_todo(todo.id)
        self.assertTrue(result)
        self.assertTrue(todo.completed)

        result = self.todo_manager.complete_todo(999)
        self.assertFalse(result)

    def test_list_todos(self):
        todo1 = self.todo_manager.add_todo("Tarefa 1")
        todo2 = self.todo_manager.add_todo("Tarefa 2")
        self.todo_manager.complete_todo(todo2.id)

        all_todos = self.todo_manager.list_todos()
        self.assertEqual(len(all_todos), 2)

        pending_todos = self.todo_manager.list_todos(show_completed=False)
        self.assertEqual(len(pending_todos), 1)
        self.assertEqual(pending_todos[0].description, "Tarefa 1")

    def test_remove_todo(self):
        todo = self.todo_manager.add_todo("Tarefa para remover")
        initial_count = len(self.todo_manager.todos)

        result = self.todo_manager.remove_todo(todo.id)
        self.assertTrue(result)
        self.assertEqual(len(self.todo_manager.todos), initial_count - 1)

        result = self.todo_manager.remove_todo(999)
        self.assertFalse(result)

    def test_clear_completed(self):
        todo1 = self.todo_manager.add_todo("Tarefa 1")
        todo2 = self.todo_manager.add_todo("Tarefa 2")
        todo3 = self.todo_manager.add_todo("Tarefa 3")

        self.todo_manager.complete_todo(todo1.id)
        self.todo_manager.complete_todo(todo3.id)

        removed_count = self.todo_manager.clear_completed()
        self.assertEqual(removed_count, 2)
        self.assertEqual(len(self.todo_manager.todos), 1)
        self.assertEqual(self.todo_manager.todos[0].description, "Tarefa 2")

    def test_save_and_load_todos(self):
        self.todo_manager.add_todo("Tarefa persistente")
        todo2 = self.todo_manager.add_todo("Tarefa concluída")
        self.todo_manager.complete_todo(todo2.id)

        new_manager = TodoManager(self.temp_file.name)

        self.assertEqual(len(new_manager.todos), 2)
        self.assertEqual(new_manager.todos[0].description, "Tarefa persistente")
        self.assertFalse(new_manager.todos[0].completed)
        self.assertEqual(new_manager.todos[1].description, "Tarefa concluída")
        self.assertTrue(new_manager.todos[1].completed)

    def test_get_todo(self):
        todo = self.todo_manager.add_todo("Tarefa para buscar")

        found_todo = self.todo_manager.get_todo(todo.id)
        self.assertIsNotNone(found_todo)
        self.assertEqual(found_todo.description, "Tarefa para buscar")

        not_found = self.todo_manager.get_todo(999)
        self.assertIsNone(not_found)


if __name__ == "__main__":
    unittest.main()
