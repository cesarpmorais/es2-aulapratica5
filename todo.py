import json
import os
import argparse
from datetime import datetime
from typing import List, Dict, Optional


class TodoItem:
    def __init__(self, id: int, description: str, completed: bool = False, created_at: str = None):
        self.id = id
        self.description = description
        self.completed = completed
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoItem':
        return cls(
            id=data['id'],
            description=data['description'],
            completed=data['completed'],
            created_at=data['created_at']
        )


class TodoManager:
    def __init__(self, filename: str = 'todos.json'):
        self.filename = filename
        self.todos: List[TodoItem] = []
        self.load_todos()

    def load_todos(self) -> None:
        """Carrega todos do arquivo JSON"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.todos = [TodoItem.from_dict(item) for item in data]
            except (json.JSONDecodeError, KeyError):
                self.todos = []

    def save_todos(self) -> None:
        """Salva todos no arquivo JSON"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([todo.to_dict() for todo in self.todos],
                      f, indent=2, ensure_ascii=False)

    def add_todo(self, description: str) -> TodoItem:
        """Adiciona um novo todo"""
        new_id = max([todo.id for todo in self.todos], default=0) + 1
        todo = TodoItem(new_id, description)
        self.todos.append(todo)
        self.save_todos()
        return todo

    def list_todos(self, show_completed: bool = True) -> List[TodoItem]:
        """Lista todos os todos"""
        if show_completed:
            return self.todos
        return [todo for todo in self.todos if not todo.completed]

    def complete_todo(self, todo_id: int) -> bool:
        """Marca um todo como concluído"""
        for todo in self.todos:
            if todo.id == todo_id:
                todo.completed = True
                self.save_todos()
                return True
        return False

    def remove_todo(self, todo_id: int) -> bool:
        """Remove um todo"""
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                del self.todos[i]
                self.save_todos()
                return True
        return False

    def get_todo(self, todo_id: int) -> Optional[TodoItem]:
        """Busca um todo pelo ID"""
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def clear_completed(self) -> int:
        """Remove todos os todos concluídos"""
        initial_count = len(self.todos)
        self.todos = [todo for todo in self.todos if not todo.completed]
        removed_count = initial_count - len(self.todos)
        if removed_count > 0:
            self.save_todos()
        return removed_count

    def edit_todo(self, todo_id: int, new_description: str) -> bool:
        """Edita a descrição de um todo"""
        for todo in self.todos:
            if todo.id == todo_id:
                todo.description = new_description
                self.save_todos()
                return True
        return False


def display_menu():
    """Exibe o menu principal"""
    print("\n" + "="*50)
    print("📋 SISTEMA DE TO-DO")
    print("="*50)
    print("1. ➕ Adicionar tarefa")
    print("2. 📋 Listar todas as tarefas")
    print("3. ⏳ Listar apenas tarefas pendentes")
    print("4. ✅ Marcar tarefa como concluída")
    print("5. ✏️  Editar tarefa")
    print("6. 🗑️  Remover tarefa")
    print("7. 🧹 Limpar tarefas concluídas")
    print("8. 🔍 Buscar tarefa por ID")
    print("9. ❌ Sair")
    print("="*50)


def display_todos(todos: List[TodoItem], title: str = "Lista de Todos"):
    """Exibe a lista de todos formatada"""
    if not todos:
        print(f"\n📝 Nenhuma tarefa encontrada!")
        return

    print(f"\n📋 {title}:")
    print("-" * 60)
    for todo in todos:
        status = "✅" if todo.completed else "⏳"
        created_date = datetime.fromisoformat(
            todo.created_at).strftime("%d/%m/%Y %H:%M")
        print(f"{status} [{todo.id:2d}] {todo.description}")
        print(f"    📅 Criado em: {created_date}")
        print()


def get_valid_input(prompt: str, input_type=str, validator=None):
    """Função auxiliar para obter entrada válida do usuário"""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                print("❌ Entrada não pode estar vazia!")
                continue

            if input_type == int:
                user_input = int(user_input)

            if validator and not validator(user_input):
                print("❌ Entrada inválida!")
                continue

            return user_input
        except ValueError:
            print("❌ Por favor, digite um número válido!")
        except KeyboardInterrupt:
            print("\n👋 Operação cancelada!")
            return None


def interactive_mode():
    """Modo interativo principal"""
    todo_manager = TodoManager()

    print("🎉 Bem-vindo ao Sistema de To-Do Interativo!")
    print("Digite Ctrl+C a qualquer momento para cancelar uma operação")

    while True:
        try:
            display_menu()
            choice = input("🎯 Escolha uma opção (1-9): ").strip()

            if choice == '1':
                print("\n➕ ADICIONAR NOVA TAREFA")
                description = get_valid_input(
                    "📝 Digite a descrição da tarefa: ")
                if description:
                    todo = todo_manager.add_todo(description)
                    print(
                        f"✅ Tarefa adicionada com sucesso: [{todo.id}] {todo.description}")

            elif choice == '2':
                todos = todo_manager.list_todos()
                display_todos(todos, "Todas as Tarefas")

            elif choice == '3':
                todos = todo_manager.list_todos(show_completed=False)
                display_todos(todos, "Tarefas Pendentes")

            elif choice == '4':
                print("\n✅ MARCAR TAREFA COMO CONCLUÍDA")
                pending_todos = todo_manager.list_todos(show_completed=False)
                if not pending_todos:
                    print("📝 Nenhuma tarefa pendente encontrada!")
                    continue

                display_todos(pending_todos, "Tarefas Pendentes")
                todo_id = get_valid_input(
                    "🎯 Digite o ID da tarefa para marcar como concluída: ", int)
                if todo_id is not None:
                    if todo_manager.complete_todo(todo_id):
                        print(f"✅ Tarefa {todo_id} marcada como concluída!")
                    else:
                        print(f"❌ Tarefa {todo_id} não encontrada!")

            elif choice == '5':
                print("\n✏️ EDITAR TAREFA")
                todos = todo_manager.list_todos()
                if not todos:
                    print("📝 Nenhuma tarefa encontrada!")
                    continue

                display_todos(todos)
                todo_id = get_valid_input(
                    "🎯 Digite o ID da tarefa para editar: ", int)
                if todo_id is not None:
                    todo = todo_manager.get_todo(todo_id)
                    if todo:
                        print(f"📝 Descrição atual: {todo.description}")
                        new_description = get_valid_input(
                            "✏️ Digite a nova descrição: ")
                        if new_description:
                            if todo_manager.edit_todo(todo_id, new_description):
                                print(
                                    f"✅ Tarefa {todo_id} editada com sucesso!")
                            else:
                                print(f"❌ Erro ao editar tarefa {todo_id}!")
                    else:
                        print(f"❌ Tarefa {todo_id} não encontrada!")

            elif choice == '6':
                print("\n🗑️ REMOVER TAREFA")
                todos = todo_manager.list_todos()
                if not todos:
                    print("📝 Nenhuma tarefa encontrada!")
                    continue

                display_todos(todos)
                todo_id = get_valid_input(
                    "🎯 Digite o ID da tarefa para remover: ", int)
                if todo_id is not None:
                    todo = todo_manager.get_todo(todo_id)
                    if todo:
                        confirm = input(
                            f"⚠️ Tem certeza que deseja remover a tarefa '{todo.description}'? (s/N): ").strip().lower()
                        if confirm == 's':
                            if todo_manager.remove_todo(todo_id):
                                print(
                                    f"🗑️ Tarefa {todo_id} removida com sucesso!")
                            else:
                                print(f"❌ Erro ao remover tarefa {todo_id}!")
                        else:
                            print("❌ Operação cancelada!")
                    else:
                        print(f"❌ Tarefa {todo_id} não encontrada!")

            elif choice == '7':
                print("\n🧹 LIMPAR TAREFAS CONCLUÍDAS")
                completed_todos = [
                    todo for todo in todo_manager.todos if todo.completed]
                if not completed_todos:
                    print("📝 Nenhuma tarefa concluída encontrada!")
                    continue

                display_todos(completed_todos, "Tarefas Concluídas")
                confirm = input(
                    f"⚠️ Tem certeza que deseja remover {len(completed_todos)} tarefa(s) concluída(s)? (s/N): ").strip().lower()
                if confirm == 's':
                    removed_count = todo_manager.clear_completed()
                    print(
                        f"🧹 {removed_count} tarefa(s) concluída(s) removida(s)!")
                else:
                    print("❌ Operação cancelada!")

            elif choice == '8':
                print("\n🔍 BUSCAR TAREFA POR ID")
                todo_id = get_valid_input("🎯 Digite o ID da tarefa: ", int)
                if todo_id is not None:
                    todo = todo_manager.get_todo(todo_id)
                    if todo:
                        display_todos([todo], f"Tarefa Encontrada")
                    else:
                        print(f"❌ Tarefa {todo_id} não encontrada!")

            elif choice == '9':
                print("\n👋 Obrigado por usar o Sistema de To-Do!")
                print("💾 Todas as suas tarefas foram salvas automaticamente.")
                break

            else:
                print("❌ Opção inválida! Por favor, escolha uma opção de 1 a 9.")

            input("\n⏸️ Pressione Enter para continuar...")

        except KeyboardInterrupt:
            print("\n\n👋 Sistema encerrado pelo usuário!")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            input("⏸️ Pressione Enter para continuar...")


def command_line_mode():
    """Modo de linha de comando (original)"""
    parser = argparse.ArgumentParser(
        description='Sistema de To-Do para linha de comando')
    subparsers = parser.add_subparsers(
        dest='command', help='Comandos disponíveis')

    add_parser = subparsers.add_parser('add', help='Adicionar novo todo')
    add_parser.add_argument('description', help='Descrição do todo')

    list_parser = subparsers.add_parser('list', help='Listar todos')
    list_parser.add_argument(
        '--pending', action='store_true', help='Mostrar apenas pendentes')

    complete_parser = subparsers.add_parser(
        'complete', help='Marcar todo como concluído')
    complete_parser.add_argument('id', type=int, help='ID do todo')

    remove_parser = subparsers.add_parser('remove', help='Remover todo')
    remove_parser.add_argument('id', type=int, help='ID do todo')

    clear_parser = subparsers.add_parser(
        'clear', help='Remover todos concluídos')

    interactive_parser = subparsers.add_parser(
        'interactive', help='Iniciar modo interativo')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print(
            "\n💡 Dica: Use 'python todo_interactive.py interactive' para o modo interativo!")
        return

    if args.command == 'interactive':
        interactive_mode()
        return

    todo_manager = TodoManager()

    if args.command == 'add':
        todo = todo_manager.add_todo(args.description)
        print(f"✅ Todo adicionado: [{todo.id}] {todo.description}")

    elif args.command == 'list':
        todos = todo_manager.list_todos(show_completed=not args.pending)
        display_todos(todos)

    elif args.command == 'complete':
        if todo_manager.complete_todo(args.id):
            print(f"✅ Todo {args.id} marcado como concluído!")
        else:
            print(f"❌ Todo {args.id} não encontrado!")

    elif args.command == 'remove':
        if todo_manager.remove_todo(args.id):
            print(f"🗑️ Todo {args.id} removido!")
        else:
            print(f"❌ Todo {args.id} não encontrado!")

    elif args.command == 'clear':
        removed_count = todo_manager.clear_completed()
        print(f"🧹 {removed_count} todo(s) concluído(s) removido(s)!")


def main():
    """Função principal que detecta o modo de uso"""
    import sys

    if len(sys.argv) == 1:
        interactive_mode()
    else:
        command_line_mode()


if __name__ == '__main__':
    main()
