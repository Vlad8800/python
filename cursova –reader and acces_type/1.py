from datetime import date
import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Combobox
import mysql.connector
from datetime import date, timedelta

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vlad8800',
    'database': 'LibrarySystem'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_reading_rooms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, name FROM ReadingRooms")
    rooms = cursor.fetchall()
    conn.close()
    return rooms

def fetch_book_reading_place(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT reading_place FROM BookReadingTypes WHERE book_id = %s
    """, (book_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def fetch_books(category=None, title_search=None, room_filter=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT b.book_id, b.title, b.category_id, b.access_type,
               IF(EXISTS (
                   SELECT 1 FROM Placements p WHERE p.book_id = b.book_id
               ), 'Так', 'Ні') AS is_in_room,
               EXISTS (
                   SELECT 1 FROM IssuedBooks ib
                   WHERE ib.book_id = b.book_id AND (
                       (ib.reading_place = 'У читальній залі і в дома' AND ib.return_date >= CURDATE())
                       OR 
                       (ib.reading_place = 'Тільки в читальній залі' AND ib.issue_date = CURDATE())
                   )
               ) AS is_issued
        FROM Books b
    """
    conditions = []
    params = []
    if room_filter:
        conditions.append("EXISTS (SELECT 1 FROM Placements p WHERE p.book_id = b.book_id AND p.room_id = %s)")
        params.append(room_filter)
    if category:
        conditions.append("b.category_id = %s")
        params.append(category)
    if title_search:
        conditions.append("b.title LIKE %s")
        params.append(f"%{title_search}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY is_issued ASC, b.title"
    cursor.execute(query, params)
    books = cursor.fetchall()
    conn.close()
    return books

def fetch_user_issued_books(reader_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ib.book_id, b.title, b.category_id, ib.return_date, ib.reading_place
        FROM IssuedBooks ib
        JOIN Books b ON b.book_id = ib.book_id
        WHERE ib.reader_id = %s AND (
            (ib.reading_place = 'У читальній залі і в дома' AND ib.return_date >= CURDATE())
            OR 
            (ib.reading_place = 'Тільки в читальній залі' AND ib.issue_date = CURDATE())
        )
    """, (reader_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def return_book(book_id, reader_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM IssuedBooks
        WHERE book_id = %s AND reader_id = %s
    """, (book_id, reader_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Успіх", "Книгу повернено успішно.")
    show_books(reader_id)
    show_returned_books_inline(reader_id, return_books_frame)

def show_returned_books_inline(reader_id, parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()
    Label(parent_frame, text="\nВаші активні книги (для дострокового повернення):", font=("Arial", 13, "bold"), anchor="w", bg="#f0f0f0").pack(anchor="w", padx=10, pady=(20, 5))
    header = Frame(parent_frame, bg="#dddddd")
    header.pack(fill=X, padx=10, pady=2)
    Label(header, text="Назва книги", font=("Arial", 11, "bold"), width=30).pack(side=LEFT)
    Label(header, text="Категорія", font=("Arial", 11, "bold"), width=15).pack(side=LEFT)
    Label(header, text="Дата повернення", font=("Arial", 11, "bold"), width=20).pack(side=LEFT)
    Label(header, text="Місце", font=("Arial", 11, "bold"), width=20).pack(side=LEFT)
    Label(header, text="", width=15).pack(side=LEFT)

    books = fetch_user_issued_books(reader_id)
    for book_id, title, category, return_date, place in books:
        row = Frame(parent_frame, bg="#ffffff")
        row.pack(fill=X, padx=10, pady=2)
        Label(row, text=title, width=30, anchor="w", bg="white", font=("Arial", 10)).pack(side=LEFT)
        Label(row, text=category, width=15, anchor="w", bg="white", font=("Arial", 10)).pack(side=LEFT)
        Label(row, text=str(return_date), width=20, anchor="w", bg="white", font=("Arial", 10)).pack(side=LEFT)
        Label(row, text=place, width=20, anchor="w", bg="white", font=("Arial", 10)).pack(side=LEFT)
        Button(row, text="Повернути", command=lambda b=book_id: [return_book(b, reader_id), parent_frame.after(100, lambda: show_returned_books_inline(reader_id, parent_frame))], bg="red", fg="white").pack(side=LEFT, padx=5)

def show_books(reader_id, category=None, title_search=None, room_filter=None):
    global available_books_frame
    for widget in available_books_frame.winfo_children():
        widget.destroy()

    def refresh_books():
        selected_category = category_var.get()
        title_search_val = search_var.get().strip()
        selected_room = room_var.get()
        room_id = room_ids.get(selected_room)
        show_books(reader_id, selected_category, title_search_val, room_id)

    top_bar = Frame(available_books_frame, bg="#e0e0e0")
    top_bar.pack(fill=X, padx=10, pady=5)
    Label(top_bar, text="Категорія:", bg="#e0e0e0").pack(side=LEFT, padx=5)
    category_var = StringVar()
    category_menu = ttk.Combobox(top_bar, textvariable=category_var, width=20, state="readonly")
    category_menu['values'] = ('', 'книги', 'журнали', 'газети', 'збірники статей', 'збірники віршів', 'дисертації', 'реферати', 'збірники доповідей і тез доповідей')
    category_menu.current(0)
    category_menu.pack(side=LEFT, padx=5)

    Label(top_bar, text="Назва:", bg="#e0e0e0").pack(side=LEFT, padx=5)
    search_var = StringVar()
    Entry(top_bar, textvariable=search_var, width=25).pack(side=LEFT, padx=5)

    Label(top_bar, text="Зал:", bg="#e0e0e0").pack(side=LEFT, padx=5)
    room_var = StringVar()
    room_menu = ttk.Combobox(top_bar, textvariable=room_var, width=22, state="readonly")
    rooms = fetch_reading_rooms()
    room_names = [room[1] for room in rooms]
    room_ids = {room[1]: room[0] for room in rooms}
    room_menu['values'] = [''] + room_names
    room_menu.current(0)
    room_menu.pack(side=LEFT, padx=5)

    Button(top_bar, text="Пошук", command=refresh_books).pack(side=LEFT, padx=5)

    header = Frame(available_books_frame, bg="#f5f5f5")
    header.pack(fill=X, padx=10, pady=5)
    Label(header, text="Назва книги", font=("Arial", 12, "bold"), width=30, anchor="w", bg="#f5f5f5").pack(side=LEFT)
    Label(header, text="Тип", font=("Arial", 12, "bold"), width=15, anchor="w", bg="#f5f5f5").pack(side=LEFT)
    Label(header, text="У читальному залі", font=("Arial", 12, "bold"), width=20, anchor="w", bg="#f5f5f5").pack(side=LEFT)
    Label(header, text="", width=25, bg="#f5f5f5").pack(side=LEFT)

    Frame(available_books_frame, height=2, bg="gray").pack(fill=X, padx=10, pady=2)

    books = fetch_books(category, title_search, room_filter)
    for book_id, title, book_type, access_type, is_in_room, is_issued in books:
        row = Frame(available_books_frame, bg="#e6e6e6" if is_issued else "#ffffff")
        row.pack(fill=X, padx=10, pady=3)
        Label(row, text=title, font=("Arial", 11), width=30, anchor="w", bg=row.cget("bg")).pack(side=LEFT)
        Label(row, text=book_type, font=("Arial", 11), width=15, anchor="w", bg=row.cget("bg")).pack(side=LEFT)
        Label(row, text=is_in_room, font=("Arial", 11), width=20, anchor="w", bg=row.cget("bg")).pack(side=LEFT)
        btn_frame = Frame(row, bg=row.cget("bg"))
        btn_frame.pack(side=LEFT)

        in_room_btn = Button(btn_frame, text="В залі", command=lambda b=book_id: read_in_room(b, reader_id),
                             bg="orange", fg="white", font=("Arial", 9), padx=5, pady=2)
        home_btn = Button(btn_frame, text="Вдома", command=lambda b=book_id: read_at_home(b, reader_id),
                          bg="lime green", fg="white", font=("Arial", 9), padx=5, pady=2)

        if is_issued:
            in_room_btn.config(state=DISABLED)
            home_btn.config(state=DISABLED)
        else:
            if access_type == 'Тільки в читальній залі':
                home_btn.config(state=DISABLED)
            elif access_type == 'У читальній залі і в дома':
                pass  # обидві активні
            else:  # інші випадки, заборонити обидві кнопки
                in_room_btn.config(state=DISABLED)
                home_btn.config(state=DISABLED)

        in_room_btn.pack(side=LEFT, padx=5)
        home_btn.pack(side=LEFT)
        
def read_in_room(book_id, reader_id):
    today = date.today()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO IssuedBooks (reader_id, book_id, issue_date, return_date, reading_place)
            VALUES (%s, %s, %s, %s, %s)
        """, (reader_id, book_id, today, today, 'Тільки в читальній залі'))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успіх", "Книга зареєстрована для читання в залі.")
        show_books(reader_id)
        show_returned_books_inline(reader_id, return_books_frame)
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося зареєструвати книгу: {e}")


def read_at_home(book_id, reader_id):
    def confirm_return_date():
        selected_date = return_calendar.get_date()
        today = date.today()
        max_return_date = today + timedelta(days=7)
        if selected_date < today or selected_date > max_return_date:
            messagebox.showerror("Помилка", "Дата повернення має бути в межах 7 днів від сьогодні.")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO IssuedBooks (reader_id, book_id, issue_date, return_date, reading_place)
                VALUES (%s, %s, %s, %s, %s)
            """, (reader_id, book_id, today, selected_date, 'У читальній залі і в дома'))
            conn.commit()
            conn.close()
            top.destroy()
            messagebox.showinfo("Успіх", "Книга зареєстрована для читання вдома.")
            show_books(reader_id)
            show_returned_books_inline(reader_id, return_books_frame)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зареєструвати книгу: {e}")

    top = Toplevel()
    top.title("Оберіть дату повернення")
    top.geometry("300x180")
    top.grab_set()
    Label(top, text="Оберіть дату повернення:", font=("Arial", 11)).pack(pady=10)
    return_calendar = DateEntry(top, mindate=date.today(), maxdate=date.today() + timedelta(days=7), date_pattern='yyyy-mm-dd')
    return_calendar.pack(pady=5)
    Button(top, text="Підтвердити", command=confirm_return_date, bg="green", fg="white", font=("Arial", 10)).pack(pady=10)


def show_reader_window(reader_id):
    global available_books_frame, return_books_frame
    root = Tk()
    root.title("Бібліотечна система")
    root.geometry("1000x700")
    root.configure(bg="#f0f0f0")

    books_frame = Frame(root, bg="#f0f0f0")
    books_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
    available_books_frame = books_frame

    return_books_frame = Frame(root, bg="#f0f0f0")
    return_books_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    Button(root, text="Оновити книги", command=lambda: [show_books(reader_id), show_returned_books_inline(reader_id, return_books_frame)], font=("Arial", 11)).pack(pady=10)

    show_books(reader_id)
    show_returned_books_inline(reader_id, return_books_frame)

    root.mainloop()


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
    def generate_inventory_number():
        # Простий приклад генерації інвентарного номера — INV- + кількість книг + 1
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Books")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return f"{count + 1:05d}"  # наприклад, INV-00001
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

    # Інвентарний номер (не редагується, автоматично генерується)
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
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title FROM books")
    books = cursor.fetchall()
    conn.close()
    return books


def get_reading_rooms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, name FROM readingrooms")
    rooms = cursor.fetchall()
    conn.close()
    return rooms

def save_distribution(book_id, selected_room_ids, shelf, row):
    conn = get_db_connection()
    cursor = conn.cursor()
    for room_id in selected_room_ids:
        cursor.execute("""
            INSERT INTO Placements (book_id, room_id, shelf, `row`) 
            VALUES (%s, %s, %s, %s)
        """, (book_id, room_id, shelf, row))
    conn.commit()
    conn.close()
    messagebox.showinfo("Успішно", "Книгу розподілено по читальних залах!")

def show_admin_window(user_login):
    admin_window = tk.Tk()
    admin_window.title("Вікно адміністратора")
    admin_window.geometry("450x600")

    tk.Label(admin_window, text=f"Вітаємо, {user_login} (Адміністратор)!", font=("Arial", 16)).pack(pady=10)

    # Вибір книги
    tk.Label(admin_window, text="Оберіть книгу для розподілу:").pack(anchor="w", padx=10)
    tk.Label(admin_window, text="(Інвентарний номер співпадає з ID книги)").pack(anchor="w", padx=10)
    books = get_books()
    book_map = {f"{title} (ID: {book_id})": book_id for book_id, title in books}
    book_combo = Combobox(admin_window, values=list(book_map.keys()), state="readonly", width=50)
    book_combo.pack(padx=10, pady=5)

    # Access type
    tk.Label(admin_window, text="Оберіть тип доступу до книги:").pack(anchor="w", padx=10, pady=(15, 0))
    access_combo = Combobox(admin_window, values=["Тільки в читальній залі", "У читальній залі і в дома"], state="readonly", width=35)
    access_combo.current(0)
    access_combo.pack(padx=10, pady=5)

    # Вибір читальних залів
    tk.Label(admin_window, text="Оберіть читальні зали:").pack(anchor="w", padx=10, pady=(15, 0))
    rooms = get_reading_rooms()
    room_vars = []
    rooms_frame = tk.Frame(admin_window)
    rooms_frame.pack(padx=20, pady=5, fill='x')
    for room_id, room_name in rooms:
        var = tk.IntVar()
        chk = tk.Checkbutton(rooms_frame, text=room_name, variable=var)
        chk.pack(anchor='w')
        room_vars.append((var, room_id))

    # Вибір shelf
    tk.Label(admin_window, text="Оберіть полицю (Shelf):").pack(anchor="w", padx=10, pady=(15, 0))
    shelf_combo = Combobox(admin_window, values=["A", "B", "C", "D", "E"], state="readonly", width=5)
    shelf_combo.current(0)
    shelf_combo.pack(padx=10, pady=5)

    # Вибір row
    tk.Label(admin_window, text="Оберіть ряд (Row):").pack(anchor="w", padx=10, pady=(15, 0))
    row_combo = Combobox(admin_window, values=[str(i) for i in range(1, 11)], state="readonly", width=5)
    row_combo.current(0)
    row_combo.pack(padx=10, pady=5)

    # Збереження розподілу
    def on_save():
        selected_book = book_combo.get()
        if not selected_book:
            messagebox.showerror("Помилка", "Будь ласка, оберіть книгу.")
            return
        book_id = book_map[selected_book]

        selected_rooms = [room_id for var, room_id in room_vars if var.get() == 1]
        if not selected_rooms:
            messagebox.showerror("Помилка", "Оберіть хоча б один читальний зал.")
            return

        shelf = shelf_combo.get()
        row = row_combo.get()
        access_type = access_combo.get()

        # Збереження розподілу
        save_distribution(book_id, selected_rooms, shelf, row)

        # Оновлення типу доступу до книги
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Books SET access_type = %s WHERE book_id = %s", (access_type, book_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успішно", "Книгу розподілено та оновлено access_type.")

    tk.Button(admin_window, text="Розподілити книгу", command=on_save, width=25).pack(pady=20)
    tk.Button(admin_window, text="Вийти", command=admin_window.destroy).pack(pady=10)

    admin_window.mainloop()


# Вікно логіну
def show_login_window():
    global login_window  # оголошуємо глобальну змінну відразу

    def login_user():
        login = entry_login.get().strip()
        password = entry_password.get().strip()
        if not login or not password:
            messagebox.showerror("Помилка", "Введіть логін і пароль")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, password, role FROM Users WHERE login = %s", (login,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row is None:
                messagebox.showerror("Помилка", "Невірний логін")
                return
            user_id, db_password, role = row
            if password == db_password:
                login_window.destroy()
                if role == 'Reader':
                    show_reader_window(user_id)
                elif role == 'Librarian':
                    show_librarian_window(user_id)
                elif role == 'Writer':
                    show_writer_window(user_id)
                elif role == 'Admin':
                    show_admin_window(user_id)
                else:
                    messagebox.showerror("Помилка", f"Невідома роль користувача: {role}")
            else:
                messagebox.showerror("Помилка", "Невірний пароль")
        except mysql.connector.Error as err:
            messagebox.showerror("Помилка БД", str(err))

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
    role_combo = ttk.Combobox(register_window, textvariable=role_var, state="readonly", values=["Reader", "Librarian", "Writer"])
    role_combo.grid(row=2, column=1, padx=10, pady=5)

    reader_frame = Frame(register_window)
    librarian_frame = Frame(register_window)
    author_frame = Frame(register_window)
    student_fields_frame = Frame(reader_frame)

    Label(reader_frame, text="Ім'я читача:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_reader_name = Entry(reader_frame)
    entry_reader_name.grid(row=0, column=1, padx=10, pady=5)

    Label(reader_frame, text="Адреса:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    entry_reader_address = Entry(reader_frame)
    entry_reader_address.grid(row=1, column=1, padx=10, pady=5)

    Label(reader_frame, text="Тип читача:").grid(row=2, column=0, sticky=E, padx=10, pady=5)
    reader_type_var = StringVar(value="")
    reader_type_combo = ttk.Combobox(reader_frame, textvariable=reader_type_var, state="readonly",
                                     values=["Студент", "Викладач", "Працівник", "Науковець"])
    reader_type_combo.grid(row=2, column=1, padx=10, pady=5)

    Label(student_fields_frame, text="Університет:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_university = Entry(student_fields_frame)
    entry_university.grid(row=0, column=1, padx=10, pady=5)

    Label(student_fields_frame, text="Факультет:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    entry_faculty = Entry(student_fields_frame)
    entry_faculty.grid(row=1, column=1, padx=10, pady=5)

    student_fields_frame.grid_remove()

    organization_label = Label(reader_frame, text="Організація:")
    entry_organization = Entry(reader_frame)
    organization_label.grid(row=5, column=0, sticky=E, padx=10, pady=5)
    entry_organization.grid(row=5, column=1, padx=10, pady=5)
    organization_label.grid_remove()
    entry_organization.grid_remove()

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

    reader_frame.grid_remove()
    librarian_frame.grid_remove()
    author_frame.grid_remove()

    def toggle_reader_type_fields(event=None):
        reader_type = reader_type_var.get()
        if role_var.get() == 'Reader':
            if reader_type == 'Студент':
                student_fields_frame.grid(row=4, column=0, columnspan=2, pady=5)
                organization_label.grid_remove()
                entry_organization.grid_remove()
            elif reader_type == 'Науковець':
                student_fields_frame.grid_remove()
                organization_label.grid(row=5, column=0, sticky=E, padx=10, pady=5)
                entry_organization.grid(row=5, column=1, padx=10, pady=5)
            else:
                student_fields_frame.grid_remove()
                organization_label.grid_remove()
                entry_organization.grid_remove()
        check_required_fields_filled()

    def toggle_role_fields(event=None):
        reader_frame.grid_remove()
        student_fields_frame.grid_remove()
        librarian_frame.grid_remove()
        author_frame.grid_remove()
        organization_label.grid_remove()
        entry_organization.grid_remove()
        role = role_var.get()
        if role == 'Reader':
            reader_frame.grid(row=3, column=0, columnspan=2, pady=10)
            toggle_reader_type_fields()
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
            elif reader_type_var.get() == 'Науковець':
                if not entry_organization.get().strip():
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

    role_combo.bind("<<ComboboxSelected>>", toggle_role_fields)
    reader_type_combo.bind("<<ComboboxSelected>>", toggle_reader_type_fields)

    for widget in [entry_login, entry_password, entry_reader_name, entry_reader_address,
                   entry_university, entry_faculty, entry_librarian_name,
                   entry_author_name, entry_author_surname, entry_author_country,
                   entry_organization]:
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
                organization = entry_organization.get().strip() if reader_type == 'Науковець' else None
                cursor.execute(
                    "INSERT INTO Readers (user_id, user_name, address, reader_type, university, faculty, organization) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (user_id, name, address, reader_type, university, faculty, organization)
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
