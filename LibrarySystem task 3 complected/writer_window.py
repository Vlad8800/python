from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from database import get_db_connection
from utils import get_user_id

def get_user_id(author):
    if isinstance(author, int):
        # author — це вже user_id
        return author
    elif isinstance(author, str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM Users WHERE login = %s", (author,))
            row = cursor.fetchone()
            return row[0] if row else None
        except mysql.connector.Error as err:
            print("Помилка БД:", err)
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        return None

def show_books_by_author(author):
    try:
        user_id = get_user_id(author)
        if user_id is None:
            messagebox.showerror("Помилка", f"Користувача '{author}' не знайдено")
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT author_id, name, surname FROM Authors WHERE user_id = %s", (user_id,))
        author_row = cursor.fetchone()
        if not author_row:
            messagebox.showerror("Помилка", f"Автор для користувача '{author}' не знайдений")
            cursor.close()
            conn.close()
            return

        author_id, author_name, author_surname = author_row

        cursor.execute("SELECT title, year, languages, inventory_number FROM Books WHERE author_id = %s", (author_id,))
        books = cursor.fetchall()

        books_window = Toplevel()
        books_window.title("Книги автора")
        books_window.geometry("600x400")

        Label(books_window, text=f"Книги автора: {author_name} {author_surname}", font=("Arial", 14)).pack(pady=10)

        tree = ttk.Treeview(books_window, columns=("Назва", "Рік", "Мова", "Інвентарний номер"), show="headings")
        tree.heading("Назва", text="Назва")
        tree.heading("Рік", text="Рік")
        tree.heading("Мова", text="Мова")
        tree.heading("Інвентарний номер", text="Інвентарний номер")

        for book in books:
            tree.insert("", END, values=book)

        tree.pack(fill=BOTH, expand=True)

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Помилка БД", str(err))


def show_add_book_window(author):
    def generate_inventory_number():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Books")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return f"INV-{count + 1:05d}"
        except:
            return "INV-00001"

    def save_book():
        title = entry_title.get().strip()
        year = entry_year.get().strip()
        language = entry_language.get().strip()
        inventory_number = inventory_number_var.get()
        category_name = category_var.get().strip()

        if not (title and year and language and category_name):
            messagebox.showerror("Помилка", "Заповніть усі поля")
            return

        user_id = get_user_id(author)
        if user_id is None:
            messagebox.showerror("Помилка", "Автор не знайдений")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT author_id FROM Authors WHERE user_id = %s", (user_id,))
            author_row = cursor.fetchone()
            if not author_row:
                messagebox.showerror("Помилка", "Автор не знайдений")
                return
            author_id = author_row[0]

            cursor.execute("SELECT category_id FROM Categories WHERE name = %s", (category_name,))
            category_row = cursor.fetchone()
            if not category_row:
                messagebox.showerror("Помилка", f"Категорія '{category_name}' не знайдена")
                return
            category_id = category_row[0]

            cursor.execute("""
                INSERT INTO Books (title, author_id, category_id, year, languages, inventory_number)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, author_id, category_id, year, language, inventory_number))

            conn.commit()
            messagebox.showinfo("Успіх", "Книгу додано")
            add_window.destroy()

        except mysql.connector.Error as err:
            messagebox.showerror("Помилка БД", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    add_window = Toplevel()
    add_window.title("Додати книгу")
    add_window.geometry("400x400")

    Label(add_window, text="Назва:").pack(pady=5)
    entry_title = Entry(add_window, width=40)
    entry_title.pack(pady=5)

    Label(add_window, text="Рік:").pack(pady=5)
    entry_year = Entry(add_window, width=40)
    entry_year.pack(pady=5)

    Label(add_window, text="Мова:").pack(pady=5)
    entry_language = Entry(add_window, width=40)
    entry_language.pack(pady=5)

    Label(add_window, text="Інвентарний номер (генерується автоматично):").pack(pady=5)
    inventory_number_var = StringVar(value=generate_inventory_number())
    entry_inventory = Entry(add_window, textvariable=inventory_number_var, width=40, state='readonly')
    entry_inventory.pack(pady=5)

    Label(add_window, text="Категорія:").pack(pady=5)
    category_var = StringVar()
    category_combo = ttk.Combobox(add_window, textvariable=category_var)
    category_combo.pack(pady=5)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Categories")
        categories = [row[0] for row in cursor.fetchall()]
        category_combo['values'] = categories
        cursor.close()
        conn.close()
    except:
        messagebox.showerror("Помилка", "Не вдалося завантажити категорії")

    Button(add_window, text="Зберегти книгу", command=save_book).pack(pady=20)


# Для тестування: просте головне вікно з кнопками для автора
def show_writer_window(user_login):
    writer_window = Tk()
    writer_window.title("Вікно автора")
    writer_window.geometry("400x300")

    Label(writer_window, text=f"Вітаємо, {user_login} (Автор)!").pack(pady=20)
    Button(writer_window, text="Переглянути мої книги", command=lambda: show_books_by_author(user_login)).pack(pady=10)
    Button(writer_window, text="Додати нову книгу", command=lambda: show_add_book_window(user_login)).pack(pady=10)
    Button(writer_window, text="Вийти", command=writer_window.destroy).pack(pady=30)

    writer_window.mainloop()