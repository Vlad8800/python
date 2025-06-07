import tkinter as tk
from tkinter import messagebox
from collections import deque

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class UniversityTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        new_node = Node(value)
        if not self.root:
            self.root = new_node
            return

        queue = deque([self.root])
        while queue:
            current = queue.popleft()
            if not current.left:
                current.left = new_node
                return
            else:
                queue.append(current.left)

            if not current.right:
                current.right = new_node
                return
            else:
                queue.append(current.right)

    def in_order_traversal(self, node):
        if not node:
            return []
        return self.in_order_traversal(node.left) + [node.value] + self.in_order_traversal(node.right)

    def search(self, value):
        if not self.root:
            return False
        queue = deque([self.root])
        while queue:
            current = queue.popleft()
            if current.value == value:
                return True
            if current.left:
                queue.append(current.left)
            if current.right:
                queue.append(current.right)
        return False

    def delete(self, value):
        if not self.root:
            return False

        queue = deque([self.root])
        node_to_delete = None
        last_node = None

        while queue:
            last_node = queue.popleft()
            if last_node.value == value:
                node_to_delete = last_node
            if last_node.left:
                queue.append(last_node.left)
            if last_node.right:
                queue.append(last_node.right)

        if node_to_delete:
            node_to_delete.value = last_node.value
            self._delete_deepest(last_node)
            return True
        else:
            return False

    def _delete_deepest(self, del_node):
        queue = deque([self.root])
        while queue:
            current = queue.popleft()
            if current.left:
                if current.left == del_node:
                    current.left = None
                    return
                queue.append(current.left)
            if current.right:
                if current.right == del_node:
                    current.right = None
                    return
                queue.append(current.right)

class UniversityGUI:
    def __init__(self, root):
        self.tree = UniversityTree()
        self.initialize_university_structure()

        self.root = root
        self.root.title("Дерево університету (текстове представлення)")

        self.entry = tk.Entry(root, font=('Segoe UI', 12), width=30)
        self.entry.pack(pady=10)

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack()

        tk.Button(self.btn_frame, text="Додати вузол", command=self.add_node, width=15).grid(row=0, column=0, padx=5)
        tk.Button(self.btn_frame, text="Видалити вузол", command=self.delete_node, width=15).grid(row=0, column=1, padx=5)
        tk.Button(self.btn_frame, text="Пошук", command=self.search_node, width=15).grid(row=0, column=2, padx=5)
        tk.Button(self.btn_frame, text="Обхід дерева", command=self.traverse_tree, width=15).grid(row=0, column=3, padx=5)

        self.result = tk.Text(root, font=('Segoe UI', 11), height=20, width=80)
        self.result.pack(pady=10)

        self.display_message("Автоматично згенероване дерево університету:")
        self.display_tree_structure()

    def initialize_university_structure(self):
        default_nodes = ["Університет", "Факультет", "Адміністрація", "Кафедра", "Лабораторія"]
        for node in default_nodes:
            self.tree.insert(node)

    def clear_and_show(self, message):
        self.result.delete(1.0, tk.END)
        self.result.insert(tk.END, message + "\n")
        self.display_tree_structure()

    def display_message(self, message):
        self.result.insert(tk.END, message + "\n")

    def add_node(self):
        value = self.entry.get().strip()
        if value:
            self.tree.insert(value)
            self.clear_and_show(f"Додано: {value}")
        else:
            messagebox.showwarning("Помилка", "Введіть назву вузла!")

    def delete_node(self):
        value = self.entry.get().strip()
        if value:
            deleted = self.tree.delete(value)
            if deleted:
                self.clear_and_show(f"Видалено: {value}")
            else:
                messagebox.showinfo("Інформація", f"Вузол '{value}' не знайдено.")
        else:
            messagebox.showwarning("Помилка", "Введіть назву вузла!")

    def search_node(self):
        value = self.entry.get().strip()
        if value:
            found = self.tree.search(value)
            msg = f"Знайдено: {value}\n" if found else f"Не знайдено: {value}\n"
            self.display_message(msg)
        else:
            messagebox.showwarning("Помилка", "Введіть назву вузла!")

    def traverse_tree(self):
        nodes = self.tree.in_order_traversal(self.tree.root)
        self.clear_and_show(f"Обхід (in-order): {', '.join(nodes)}")

    def display_tree_structure(self):
        self.result.insert(tk.END, "\nСтруктура дерева:\n")
        tree_str = self.get_tree_structure(self.tree.root)
        self.result.insert(tk.END, tree_str + "\n")

    def get_tree_structure(self, node, level=0, prefix=""):
        if node is None:
            return ""
        result = "  " * level + prefix + node.value + "\n"
        if node.left:
            result += self.get_tree_structure(node.left, level + 1, "├─ ")
        if node.right:
            result += self.get_tree_structure(node.right, level + 1, "└─ ")
        return result

# Запуск
if __name__ == "__main__":
    root = tk.Tk()
    app = UniversityGUI(root)
    root.mainloop()
