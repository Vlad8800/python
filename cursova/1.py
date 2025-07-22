import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vlad8800',
    'database': 'LibrarySystem'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Вікно для читача
def show_reader_window(user_login):
    reader_window = Tk()
    reader_window.title("Вікно читача")
    reader_window.geometry("400x300")
    Label(reader_window, text=f"Вітаємо, {user_login} (Читач)!", font=("Arial", 16)).pack(pady=20)
    Button(reader_window, text="Вийти", command=lambda: [reader_window.destroy(), show_login_window()]).pack(pady=30)
    reader_window.mainloop()

# Вікно для бібліотекаря
def show_librarian_window(user_login):
    librarian_window = Tk()
    librarian_window.title("Вікно бібліотекаря")
    librarian_window.geometry("400x300")
    Label(librarian_window, text=f"Вітаємо, {user_login} (Бібліотекар)!", font=("Arial", 16)).pack(pady=20)
    Button(librarian_window, text="Вийти", command=lambda: [librarian_window.destroy(), show_login_window()]).pack(pady=30)
    librarian_window.mainloop()

# Перегляд книг автора
def show_books_by_author(author_login):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT author_id, name, surname FROM Authors WHERE user_id = (SELECT user_id FROM Users WHERE login = %s)", (author_login,))
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

# Додати книгу
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
            cursor.execute("""
                SELECT author_id FROM Authors WHERE user_id = (
                    SELECT user_id FROM Users WHERE login = %s
                )
            """, (author_login,))
            author_row = cursor.fetchone()

            if not author_row:
                messagebox.showerror("Помилка", "Автор не знайдений")
                return
            author_id = author_row[0]

            # Отримати category_id
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
            if cursor: cursor.close()
            if conn: conn.close()

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
    except:
        messagebox.showerror("Помилка", "Не вдалося завантажити категорії")

    Button(add_window, text="Зберегти книгу", command=save_book).pack(pady=20)

# Вікно автора
def show_writer_window(user_login):
    writer_window = Tk()
    writer_window.title("Вікно автора")
    writer_window.geometry("400x300")

    Label(writer_window, text=f"Вітаємо, {user_login} (Автор)!").pack(pady=20)
    Button(writer_window, text="Переглянути мої книги", command=lambda: show_books_by_author(user_login)).pack(pady=10)
    Button(writer_window, text="Додати нову книгу", command=lambda: show_add_book_window(user_login)).pack(pady=10)
    Button(writer_window, text="Вийти", command=lambda: [writer_window.destroy(), show_login_window()]).pack(pady=30)

    writer_window.mainloop()

# Вікно адміністратора
def show_admin_window(user_login):
    admin_window = Tk()
    admin_window.title("Вікно адміністратора")
    admin_window.geometry("400x300")
    Label(admin_window, text=f"Вітаємо, {user_login} (Адміністратор)!", font=("Arial", 16)).pack(pady=20)
    Button(admin_window, text="Вийти", command=lambda: [admin_window.destroy(), show_login_window()]).pack(pady=30)
    admin_window.mainloop()

# Вікно логіну
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

# Вікно реєстрації
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

    # Frames for role-specific fields
    reader_frame = Frame(register_window)
    librarian_frame = Frame(register_window)
    author_frame = Frame(register_window)
    student_fields_frame = Frame(reader_frame)

    # --- Reader Frame ---
    Label(reader_frame, text="Ім'я читача:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_reader_name = Entry(reader_frame)
    entry_reader_name.grid(row=0, column=1, padx=10, pady=5)

    Label(reader_frame, text="Адреса:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    entry_reader_address = Entry(reader_frame)
    entry_reader_address.grid(row=1, column=1, padx=10, pady=5)

    Label(reader_frame, text="Тип читача:").grid(row=2, column=0, sticky=E, padx=10, pady=5)
    reader_type_var = StringVar(value="")
    reader_type_combo = ttk.Combobox(reader_frame, textvariable=reader_type_var, state="readonly",
                                     values=["Студент", "Викладач", "Працівник", "Інше"])
    reader_type_combo.grid(row=2, column=1, padx=10, pady=5)

    # Student additional fields
    Label(student_fields_frame, text="Університет:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_university = Entry(student_fields_frame)
    entry_university.grid(row=0, column=1, padx=10, pady=5)

    Label(student_fields_frame, text="Факультет:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    entry_faculty = Entry(student_fields_frame)
    entry_faculty.grid(row=1, column=1, padx=10, pady=5)

    student_fields_frame.grid_remove()

    # --- Librarian Frame ---
    Label(librarian_frame, text="Ім'я бібліотекаря:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_librarian_name = Entry(librarian_frame)
    entry_librarian_name.grid(row=0, column=1, padx=10, pady=5)

    Label(librarian_frame, text="Читацький зал:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    reading_rooms_var = StringVar()
    reading_rooms_combo = ttk.Combobox(librarian_frame, textvariable=reading_rooms_var, state="readonly")
    reading_rooms_combo.grid(row=1, column=1, padx=10, pady=5)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT room_id, name FROM ReadingRooms")
        rooms = cursor.fetchall()
        reading_rooms_combo['values'] = [f"{r[0]}: {r[1]}" for r in rooms]
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося завантажити читацькі зали: {e}")

    def on_room_selected(event):
        selected = reading_rooms_var.get()
        if selected:
            room_id = selected.split(":")[0]
            reading_rooms_var.set(room_id)
        check_required_fields_filled()

    reading_rooms_combo.bind("<<ComboboxSelected>>", on_room_selected)

    # --- Author Frame (Writer) ---
    Label(author_frame, text="Імʼя:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_author_name = Entry(author_frame)
    entry_author_name.grid(row=0, column=1, padx=10, pady=5)

    Label(author_frame, text="Прізвище:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    entry_author_surname = Entry(author_frame)
    entry_author_surname.grid(row=1, column=1, padx=10, pady=5)

    Label(author_frame, text="Країна:").grid(row=2, column=0, sticky=E, padx=10, pady=5)
    entry_author_country = Entry(author_frame)
    entry_author_country.grid(row=2, column=1, padx=10, pady=5)

    Label(author_frame, text="Дата народження:").grid(row=3, column=0, sticky=E, padx=10, pady=5)
    author_birth_date = DateEntry(author_frame, width=27, background='darkblue',
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    author_birth_date.grid(row=3, column=1, padx=10, pady=5)

    # Приховати всі фрейми ролей на початку
    reader_frame.grid_remove()
    librarian_frame.grid_remove()
    author_frame.grid_remove()

    def toggle_student_fields(event=None):
        if role_var.get() == 'Reader' and reader_type_var.get() == 'Студент':
            student_fields_frame.grid(row=4, column=0, columnspan=2, pady=5)
        else:
            student_fields_frame.grid_remove()
        check_required_fields_filled()

    def toggle_role_fields(event=None):
        reader_frame.grid_remove()
        student_fields_frame.grid_remove()
        librarian_frame.grid_remove()
        author_frame.grid_remove()
        role = role_var.get()
        if role == 'Reader':
            reader_frame.grid(row=3, column=0, columnspan=2, pady=10)
            toggle_student_fields()
        elif role == 'Librarian':
            librarian_frame.grid(row=3, column=0, columnspan=2, pady=10)
        elif role == 'Writer':
            author_frame.grid(row=3, column=0, columnspan=2, pady=10)
        check_required_fields_filled()

    def check_required_fields_filled(*args):
        login = entry_login.get().strip()
        password = entry_password.get().strip()
        role = role_var.get()

        if not login or not password or not role:
            register_button.config(state=DISABLED)
            return

        if role == 'Reader':
            if not entry_reader_name.get().strip():
                register_button.config(state=DISABLED)
                return
            if reader_type_var.get() == 'Студент':
                if not entry_university.get().strip() or not entry_faculty.get().strip():
                    register_button.config(state=DISABLED)
                    return
        elif role == 'Librarian':
            if not entry_librarian_name.get().strip() or not reading_rooms_var.get():
                register_button.config(state=DISABLED)
                return
        elif role == 'Writer':
            if not entry_author_name.get().strip() or \
               not entry_author_surname.get().strip() or \
               not entry_author_country.get().strip() or \
               not author_birth_date.get_date():
                register_button.config(state=DISABLED)
                return
        register_button.config(state=NORMAL)
    # Прив’язка подій (продовження)
    role_combo.bind("<<ComboboxSelected>>", toggle_role_fields)
    reader_type_combo.bind("<<ComboboxSelected>>", toggle_student_fields)

    for widget in [entry_login, entry_password, entry_reader_name, entry_reader_address,
                   entry_university, entry_faculty, entry_librarian_name,
                   entry_author_name, entry_author_surname, entry_author_country]:
        widget.bind("<KeyRelease>", check_required_fields_filled)

    author_birth_date.bind("<<DateEntrySelected>>", lambda e: check_required_fields_filled())

    def register_user():
        login = entry_login.get().strip()
        password = entry_password.get().strip()
        role = role_var.get()

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

            if role == 'Reader':
                name = entry_reader_name.get().strip()
                address = entry_reader_address.get().strip()
                reader_type = reader_type_var.get()
                university = entry_university.get().strip() if reader_type == 'Студент' else None
                faculty = entry_faculty.get().strip() if reader_type == 'Студент' else None
                cursor.execute(
                    "INSERT INTO Readers (user_id, user_name, address, reader_type, university, faculty) VALUES (%s, %s, %s, %s, %s, %s)",
                    (user_id, name, address, reader_type, university, faculty)
                )
            elif role == 'Librarian':
                name = entry_librarian_name.get().strip()
                room_id = reading_rooms_var.get()
                cursor.execute(
                    "INSERT INTO Librarians (librarian_id, name, reading_room_id) VALUES (%s, %s, %s)",
                    (user_id, name, room_id)
                )
            elif role == 'Writer':
                name = entry_author_name.get().strip()
                surname = entry_author_surname.get().strip()
                country = entry_author_country.get().strip()
                birth_year = author_birth_date.get_date().strftime('%Y-%m-%d')
                cursor.execute(
                    "INSERT INTO Authors (user_id, name, surname, country, birth_year) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, name, surname, country, birth_year)
                )
            # Для ролі Admin поки без додаткових полів

            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Успіх", "Реєстрація успішна!")
            register_window.destroy()
            show_login_window()

        except mysql.connector.Error as err:
            messagebox.showerror("Помилка БД", str(err))
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    register_button = Button(register_window, text="Зареєструвати", command=register_user, bg="green", fg="white", state=DISABLED)
    register_button.grid(row=20, column=0, columnspan=2, pady=20)

    Label(register_window, text="Вже маєте акаунт?").grid(row=21, column=0, sticky=E)
    Button(register_window, text="Увійти", command=lambda: [register_window.destroy(), show_login_window()]).grid(row=21, column=1, sticky=W)

    register_window.mainloop()

if __name__ == "__main__":
    show_login_window()
