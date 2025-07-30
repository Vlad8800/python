import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

# Конфігурація підключення до БД
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vlad8800',
    'database': 'LibrarySystem'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --- Вікно читача ---
def show_reader_window(user_login):
    window = Tk()
    window.title("Вікно читача")
    window.geometry("400x300")
    Label(window, text=f"Вітаємо, {user_login} (Читач)!", font=("Arial", 16)).pack(pady=20)
    Button(window, text="Вийти", command=lambda: [window.destroy(), show_login_window()]).pack(pady=30)
    window.mainloop()

# --- Вікно бібліотекаря ---
def show_librarian_window(user_login):
    window = Tk()
    window.title("Вікно бібліотекаря")
    window.geometry("400x300")
    Label(window, text=f"Вітаємо, {user_login} (Бібліотекар)!", font=("Arial", 16)).pack(pady=20)
    Button(window, text="Вийти", command=lambda: [window.destroy(), show_login_window()]).pack(pady=30)
    window.mainloop()

# --- Вікно адміністратора ---
def show_admin_window(user_login):
    window = Tk()
    window.title("Вікно адміністратора")
    window.geometry("400x300")
    Label(window, text=f"Вітаємо, {user_login} (Адміністратор)!", font=("Arial", 16)).pack(pady=20)
    Button(window, text="Вийти", command=lambda: [window.destroy(), show_login_window()]).pack(pady=30)
    window.mainloop()

# --- Перегляд книг автора ---
def show_books_by_author(author_login):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Отримуємо author_id по login
        cursor.execute("""
            SELECT a.author_id, a.name, a.surname FROM Authors a
            JOIN Users u ON a.name = u.login
            WHERE u.login = %s
        """, (author_login,))
        author = cursor.fetchone()

        if not author:
            messagebox.showerror("Помилка", "Автор не знайдений")
            cursor.close()
            conn.close()
            return

        author_id, author_name, author_surname = author

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


# --- Додати книгу ---
# --- Додати книгу ---
def show_add_book_window(author_login):
    def save_book():
        title = entry_title.get().strip()
        year = entry_year.get().strip()
        language = entry_language.get().strip()
        inventory_number = entry_inventory.get().strip()
        category_name = category_var.get().strip()

        if not (title and year and language and inventory_number and category_name):
            messagebox.showerror("Помилка", "Заповніть усі поля")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Отримуємо author_id
            cursor.execute("""
                SELECT a.author_id FROM Authors a
                JOIN Users u ON a.name = u.login
                WHERE u.login = %s
            """, (author_login,))
            author_row = cursor.fetchone()
            if not author_row:
                messagebox.showerror("Помилка", "Автор не знайдений")
                cursor.close()
                conn.close()
                return
            author_id = author_row[0]

            # Отримуємо category_id
            cursor.execute("SELECT category_id FROM Categories WHERE name = %s", (category_name,))
            category_row = cursor.fetchone()
            if not category_row:
                messagebox.showerror("Помилка", f"Категорія '{category_name}' не знайдена")
                cursor.close()
                conn.close()
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

    Label(add_window, text="Інвентарний номер:").pack(pady=5)
    entry_inventory = Entry(add_window, width=40)
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
    except Exception:
        messagebox.showerror("Помилка", "Не вдалося завантажити категорії")

    Button(add_window, text="Зберегти книгу", command=save_book).pack(pady=20)

# --- Вікно автора ---
def show_writer_window(user_login):
    window = Tk()
    window.title("Вікно автора")
    window.geometry("400x300")

    Label(window, text=f"Вітаємо, {user_login} (Автор)!").pack(pady=20)
    Button(window, text="Переглянути мої книги", command=lambda: show_books_by_author(user_login)).pack(pady=10)
    Button(window, text="Додати нову книгу", command=lambda: show_add_book_window(user_login)).pack(pady=10)
    Button(window, text="Вийти", command=lambda: [window.destroy(), show_login_window()]).pack(pady=30)

    window.mainloop()

# --- Вікно входу ---
def show_login_window():
    def login_user():
        login = entry_login.get().strip()
        password = entry_password.get().strip()
        if not login or not password:
            messagebox.showerror("Помилка", "Введіть логін і пароль")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password, role FROM Users WHERE login = %s", (login,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row is None:
                messagebox.showerror("Помилка", "Невірний логін")
                return
            db_password, role = row
            if password == db_password:
                login_window.destroy()
                if role == 'Reader':
                    show_reader_window(login)
                elif role == 'Librarian':
                    show_librarian_window(login)
                elif role == 'Writer':
                    show_writer_window(login)
                elif role == 'Admin':
                    show_admin_window(login)
                else:
                    messagebox.showerror("Помилка", f"Невідома роль користувача: {role}")
            else:
                messagebox.showerror("Помилка", "Невірний пароль")
        except mysql.connector.Error as err:
            messagebox.showerror("Помилка БД", str(err))

    global login_window
    login_window = Tk()
    login_window.title("Вхід")
    login_window.geometry("350x200")
    Label(login_window, text="Логін:").grid(row=0, column=0, padx=10, pady=10, sticky=E)
    entry_login = Entry(login_window)
    entry_login.grid(row=0, column=1, padx=10, pady=10)
    Label(login_window, text="Пароль:").grid(row=1, column=0, padx=10, pady=10, sticky=E)
    entry_password = Entry(login_window, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=10)
    Button(login_window, text="Увійти", command=login_user, bg="blue", fg="white").grid(row=2, column=0, columnspan=2, pady=20)
    Label(login_window, text="Немає акаунту?").grid(row=3, column=0, sticky=E)
    Button(login_window, text="Зареєструватися", command=lambda: [login_window.destroy(), show_register_window()]).grid(row=3, column=1, sticky=W)
    login_window.mainloop()

# --- Вікно реєстрації ---
def show_register_window():
    register_window = Tk()
    register_window.title("Реєстрація")
    register_window.geometry("500x600")

    Label(register_window, text="Логін:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_login = Entry(register_window)
    entry_login.grid(row=0, column=1, padx=10, pady=5)

    Label(register_window, text="Пароль:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    entry_password = Entry(register_window, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=5)

    Label(register_window, text="Роль:").grid(row=2, column=0, sticky=E, padx=10, pady=5)
    role_var = StringVar()
    role_combo = ttk.Combobox(register_window, textvariable=role_var, state="readonly", values=["Reader", "Librarian", "Writer", "Admin"])
    role_combo.grid(row=2, column=1, padx=10, pady=5)

    # Тут можна додати фрейми для специфічних полів кожної ролі (як у твоєму коді)
    # ...

    def register_user():
        login = entry_login.get().strip()
        password = entry_password.get().strip()
        role = role_var.get()

        if not login or not password or not role:
            messagebox.showerror("Помилка", "Заповніть всі основні поля")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM Users WHERE login = %s", (login,))
            if cursor.fetchone():
                messagebox.showerror("Помилка", "Такий логін вже існує!")
                cursor.close()
                conn.close()
                return

            cursor.execute("INSERT INTO Users (login, password, role) VALUES (%s, %s, %s)", (login, password, role))
            user_id = cursor.lastrowid

            # Вставити додаткові дані у відповідні таблиці (Readers, Librarians, Authors) залежно від ролі
            # Аналогічно твоєму коду — тут потрібно додати

            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Успіх", "Реєстрація успішна!")
            register_window.destroy()
            show_login_window()
        except mysql.connector.Error as err:
            messagebox.showerror("Помилка БД", str(err))
            if cursor: cursor.close()
            if conn: conn.close()

    register_button = Button(register_window, text="Зареєструвати", command=register_user, bg="green", fg="white")
    register_button.grid(row=20, column=0, columnspan=2, pady=20)

    Label(register_window, text="Вже маєте акаунт?").grid(row=21, column=0, sticky=E)
    Button(register_window, text="Увійти", command=lambda: [register_window.destroy(), show_login_window()]).grid(row=21, column=1, sticky=W)

    register_window.mainloop()

# --- Запуск ---
if __name__ == "__main__":
    show_login_window()
