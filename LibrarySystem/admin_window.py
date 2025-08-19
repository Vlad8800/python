from tkinter import *
from tkinter import ttk, messagebox
import tkinter as tk
from tkinter import ttk
from database import get_db_connection
from utils import get_books, get_reading_rooms
import login_window

def get_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title FROM Books")
    books = cursor.fetchall()
    conn.close()
    return books

def get_reading_rooms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, name FROM ReadingRooms")
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
def find_who_has_book():
    search_window = tk.Toplevel()
    search_window.title("Хто взяв книгу")
    search_window.geometry("450x350")

    # Отримуємо всі книги
    books = get_books()  # Повертає [(id, title), ...]
    book_map = {f"{title} (ID: {book_id})": book_id for book_id, title in books}

    tk.Label(search_window, text="Оберіть книгу:").pack(pady=5)
    book_combo = ttk.Combobox(search_window, values=list(book_map.keys()), state="readonly", width=50)
    book_combo.pack(pady=5)

    result_box = tk.Text(search_window, width=55, height=12)
    result_box.pack(pady=10)

    def search_book():
        selected_book = book_combo.get()
        if not selected_book:
            messagebox.showerror("Помилка", "Оберіть книгу зі списку!")
            return

        book_id = book_map[selected_book]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.user_name, b.title, ib.issue_date, ib.return_date
            FROM IssuedBooks ib
            JOIN Readers r ON ib.reader_id = r.reader_id
            JOIN Books b ON ib.book_id = b.book_id
            WHERE b.book_id = %s
        """, (book_id,))
        results = cursor.fetchall()
        conn.close()

        result_box.delete(1.0, tk.END)
        if results:
            for user_name, title, issue_date, return_date in results:
                if return_date is None:
                    status = "книга зараз у користувача"
                else:
                    status = f"книга буде повернена {return_date}"
                result_box.insert(tk.END, f"{user_name} — '{title}' (взято {issue_date}) — {status}\n")
        else:
            result_box.insert(tk.END, "Цю книгу зараз ніхто не тримає.\n")

    tk.Button(search_window, text="Перевірити", command=search_book).pack(pady=5)

def show_edit_book_window():
    edit_window = tk.Toplevel()  # робимо Toplevel, щоб не запускати новий цикл головного вікна
    edit_window.title("Редагування розміщення та типу книги")
    edit_window.geometry("500x500")

    # Отримуємо книги та формуємо словник
    books = get_books()
    book_dict = {f"{title} (ID: {book_id})": book_id for book_id, title in books}

    # Отримуємо зали та формуємо словник
    rooms = get_reading_rooms()
    room_dict = {f"{name} (ID: {room_id})": room_id for room_id, name in rooms}

    # Книга
    tk.Label(edit_window, text="Оберіть книгу:").pack()
    book_combobox = ttk.Combobox(edit_window, width=40, values=list(book_dict.keys()))
    book_combobox.pack(pady=5)

    # Тип доступу
    tk.Label(edit_window, text="Тип доступу:").pack()
    access_type_var = StringVar()
    access_type_combobox = ttk.Combobox(edit_window, textvariable=access_type_var, state='readonly')
    access_type_combobox['values'] = [
        "У читальній залі і в дома",
        "Тільки в читальній залі"
    ]
    access_type_combobox.pack(pady=5)

    # Зал
    tk.Label(edit_window, text="Оберіть зал:").pack()
    room_combobox = ttk.Combobox(edit_window, width=40, values=list(room_dict.keys()))
    room_combobox.pack(pady=5)

    # Полиця
    tk.Label(edit_window, text="Полиця:").pack()
    shelf_entry = Entry(edit_window)
    shelf_entry.pack(pady=5)

    # Ряд
    tk.Label(edit_window, text="Ряд:").pack()
    row_entry = Entry(edit_window)
    row_entry.pack(pady=5)

    def load_book_info(event):
        selected_key = book_combobox.get()
        if not selected_key:
            return
        book_id = book_dict[selected_key]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT access_type FROM Books WHERE book_id = %s", (book_id,))
        result = cursor.fetchone()
        if result:
            access_type_combobox.set(result[0])
        else:
            access_type_combobox.set("")

        cursor.execute("SELECT room_id, shelf, `row` FROM Placements WHERE book_id = %s LIMIT 1", (book_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            room_id, shelf, row = result
            # Знайти ключ за room_id
            for name, rid in room_dict.items():
                if rid == room_id:
                    room_combobox.set(name)
                    break
            shelf_entry.delete(0, END)
            shelf_entry.insert(0, shelf)
            row_entry.delete(0, END)
            row_entry.insert(0, row)
        else:
            room_combobox.set("")
            shelf_entry.delete(0, END)
            row_entry.delete(0, END)

    book_combobox.bind("<<ComboboxSelected>>", load_book_info)

    def update_book():
        selected_book = book_combobox.get()
        if not selected_book:
            messagebox.showerror("Помилка", "Оберіть книгу.")
            return

        book_id = book_dict[selected_book]
        access_type = access_type_var.get()
        selected_room = room_combobox.get()
        shelf = shelf_entry.get()
        row = row_entry.get()

        if not selected_room or not access_type or not shelf or not row:
            messagebox.showerror("Помилка", "Усі поля мають бути заповнені.")
            return

        room_id = room_dict[selected_room]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Books SET access_type = %s WHERE book_id = %s", (access_type, book_id))
            cursor.execute("DELETE FROM Placements WHERE book_id = %s", (book_id,))
            cursor.execute(
                "INSERT INTO Placements (book_id, room_id, shelf, `row`) VALUES (%s, %s, %s, %s)",
                (book_id, room_id, shelf, row)
            )
            conn.commit()
            messagebox.showinfo("Успіх", "Інформацію оновлено успішно.")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))
        finally:
            conn.close()

    update_btn = ttk.Button(edit_window, text="Оновити", command=update_book)
    update_btn.pack(pady=10)

def show_librarian_window(user):
    librarian_window = Tk()
    librarian_window.title("Вікно бібліотекаря")
    librarian_window.geometry("400x250")

    # Визначимо текст привітання: якщо user - це user_id (int), виведемо так, якщо логін (str) - так
    if isinstance(user, int):
        greeting = f"Вітаємо, користувач з ID {user} (Бібліотекар)!"
    else:
        greeting = f"Вітаємо, {user} (Бібліотекар)!"

    Label(librarian_window, text=greeting, font=("Arial", 16), pady=30).pack()

    Button(librarian_window, text="Вийти", font=("Arial", 12),
           command=lambda: [librarian_window.destroy(), login_window()]).pack(pady=20)

    librarian_window.mainloop()

def show_admin_window(user_login):
    admin_window = tk.Tk()
    admin_window.title("Вікно адміністратора")
    admin_window.geometry("450x900")

    tk.Label(admin_window, text=f"Вітаємо, {user_login} (Адміністратор)!", font=("Arial", 16)).pack(pady=10)

    # Вибір книги
    tk.Label(admin_window, text="Оберіть книгу для розподілу:").pack(anchor="w", padx=10)
    tk.Label(admin_window, text="(Інвентарний номер співпадає з ID книги)").pack(anchor="w", padx=10)
    books = get_books()
    book_map = {f"{title} (ID: {book_id})": book_id for book_id, title in books}
    book_combo = ttk.Combobox(admin_window, values=list(book_map.keys()), state="readonly", width=50)
    book_combo.pack(padx=10, pady=5)

    # Тип доступу
    tk.Label(admin_window, text="Оберіть тип доступу до книги:").pack(anchor="w", padx=10, pady=(15, 0))
    access_combo = ttk.Combobox(admin_window, values=["Тільки в читальній залі", "У читальній залі і в дома"], state="readonly", width=35)
    access_combo.current(0)
    access_combo.pack(padx=10, pady=5)

    # Читальні зали
    tk.Label(admin_window, text="Оберіть читальні зали:").pack(anchor="w", padx=10, pady=(15, 0))
    rooms = get_reading_rooms()
    room_vars = []
    rooms_frame = tk.Frame(admin_window)
    rooms_frame.pack(padx=20, pady=5, fill='x')
    for room_id, room_name in rooms:
        var = tk.IntVar()
        tk.Checkbutton(rooms_frame, text=room_name, variable=var).pack(anchor='w')
        room_vars.append((var, room_id))

    # Полиця
    tk.Label(admin_window, text="Оберіть полицю (Shelf):").pack(anchor="w", padx=10, pady=(15, 0))
    shelf_combo = ttk.Combobox(admin_window, values=["A", "B", "C", "D", "E"], state="readonly", width=5)
    shelf_combo.current(0)
    shelf_combo.pack(padx=10, pady=5)

    # Ряд
    tk.Label(admin_window, text="Оберіть ряд (Row):").pack(anchor="w", padx=10, pady=(15, 0))
    row_combo = ttk.Combobox(admin_window, values=[str(i) for i in range(1, 11)], state="readonly", width=5)
    row_combo.current(0)
    row_combo.pack(padx=10, pady=5)

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

        save_distribution(book_id, selected_rooms, shelf, row)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Books SET access_type = %s WHERE book_id = %s", (access_type, book_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успішно", "Книгу розподілено та оновлено access_type.")

    # Кнопки дій
    tk.Button(admin_window, text="Розподілити книгу", command=on_save, width=25).pack(pady=10)
    tk.Button(admin_window, text="Редагувати книгу", command=show_edit_book_window).pack(pady=5)
    tk.Button(admin_window, text="Статистика бібліотекарів", command=show_librarian_stats).pack(pady=5)
    tk.Button(admin_window, text="Хто тримає книгу", command=find_who_has_book).pack(pady=5)
    tk.Button(admin_window, text="Вийти", command=admin_window.destroy).pack(pady=10)

    admin_window.mainloop()


def show_admin_window(user_login):
    admin_window = tk.Tk()
    admin_window.title("Вікно адміністратора")
    admin_window.geometry("450x900")

    tk.Label(admin_window, text=f"Вітаємо, {user_login} (Адміністратор)!", font=("Arial", 16)).pack(pady=10)

    # Вибір книги
    tk.Label(admin_window, text="Оберіть книгу для розподілу:").pack(anchor="w", padx=10)
    tk.Label(admin_window, text="(Інвентарний номер співпадає з ID книги)").pack(anchor="w", padx=10)
    books = get_books()
    book_map = {f"{title} (ID: {book_id})": book_id for book_id, title in books}
    book_combo = ttk.Combobox(admin_window, values=list(book_map.keys()), state="readonly", width=50)
    book_combo.pack(padx=10, pady=5)

    # Тип доступу
    tk.Label(admin_window, text="Оберіть тип доступу до книги:").pack(anchor="w", padx=10, pady=(15, 0))
    access_combo = ttk.Combobox(admin_window, values=["Тільки в читальній залі", "У читальній залі і вдома"], state="readonly", width=35)
    access_combo.current(0)
    access_combo.pack(padx=10, pady=5)

    # Читальні зали
    tk.Label(admin_window, text="Оберіть читальні зали:").pack(anchor="w", padx=10, pady=(15, 0))
    rooms = get_reading_rooms()
    room_vars = []
    rooms_frame = tk.Frame(admin_window)
    rooms_frame.pack(padx=20, pady=5, fill='x')
    for room_id, room_name in rooms:
        var = tk.IntVar()
        tk.Checkbutton(rooms_frame, text=room_name, variable=var).pack(anchor='w')
        room_vars.append((var, room_id))

    # Полиця
    tk.Label(admin_window, text="Оберіть полицю (Shelf):").pack(anchor="w", padx=10, pady=(15, 0))
    shelf_combo = ttk.Combobox(admin_window, values=["A", "B", "C", "D", "E"], state="readonly", width=5)
    shelf_combo.current(0)
    shelf_combo.pack(padx=10, pady=5)

    # Ряд
    tk.Label(admin_window, text="Оберіть ряд (Row):").pack(anchor="w", padx=10, pady=(15, 0))
    row_combo = ttk.Combobox(admin_window, values=[str(i) for i in range(1, 11)], state="readonly", width=5)
    row_combo.current(0)
    row_combo.pack(padx=10, pady=5)

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

        save_distribution(book_id, selected_rooms, shelf, row)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Books SET access_type = %s WHERE book_id = %s", (access_type, book_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успішно", "Книгу розподілено та оновлено access_type.")

    # Кнопки дій
    tk.Button(admin_window, text="Розподілити книгу", command=on_save, width=25).pack(pady=10)
    tk.Button(admin_window, text="Редагувати книгу", command=show_edit_book_window).pack(pady=5)
    tk.Button(admin_window, text="Статистика бібліотекарів", command=show_librarian_stats).pack(pady=5)
    tk.Button(admin_window, text="Хто тримає книгу", command=find_who_has_book).pack(pady=5)
    tk.Button(admin_window, text="Вийти", command=admin_window.destroy).pack(pady=10)

    admin_window.mainloop()
def show_librarian_stats():
    stats_window = tk.Toplevel()
    stats_window.title("Статистика бібліотекарів")
    stats_window.geometry("600x400")

    # Рамка для вибору бібліотекаря та кнопок
    selection_frame = tk.Frame(stats_window)
    selection_frame.pack(fill=tk.X, pady=10)

    tk.Label(selection_frame, text="Оберіть бібліотекаря:").pack(side=tk.LEFT, padx=5)

    # Підключення до БД
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_id, l.name
        FROM Users u
        JOIN Librarians l ON u.user_id = l.librarian_id
    """)
    librarians = cursor.fetchall()
    librarian_map = {f"{name} (ID: {user_id})": user_id for user_id, name in librarians}
    conn.close()

    librarian_combo = ttk.Combobox(selection_frame, values=list(librarian_map.keys()), state="readonly", width=30)
    librarian_combo.pack(side=tk.LEFT, padx=5)

    # Кнопки
    def get_specific_stats():
        result_text.delete(1.0, tk.END)
        selected = librarian_combo.get()
        if not selected:
            result_text.insert(tk.END, "Помилка: Оберіть бібліотекаря.\n")
            return

        librarian_id = librarian_map[selected]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT ib.reader_id)
            FROM IssuedBooks ib
            WHERE ib.librarian_id = %s
        """, (librarian_id,))
        count = cursor.fetchone()[0]
        conn.close()

        result_text.insert(tk.END, f"Бібліотекар {selected} обслуговував {count} унікальних читачів.\n")

    def get_general_stats():
        result_text.delete(1.0, tk.END)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.name, COUNT(DISTINCT ib.reader_id) as reader_count
            FROM Librarians l
            LEFT JOIN IssuedBooks ib ON l.librarian_id = ib.librarian_id
            GROUP BY l.librarian_id, l.name
        """)
        results = cursor.fetchall()
        conn.close()

        total = sum(row[1] for row in results)
        stats_text = "Статистика обслуговування читачів:\n\n"
        for name, count in results:
            stats_text += f"{name}: {count} читачів\n"
        stats_text += f"\nЗагалом всі бібліотекарі обслуговували {total} унікальних читачів"
        result_text.insert(tk.END, stats_text)

    tk.Button(selection_frame, text="Показати вибраного", command=get_specific_stats).pack(side=tk.LEFT, padx=5)
    tk.Button(selection_frame, text="Загальна статистика", command=get_general_stats).pack(side=tk.LEFT, padx=5)

    # Поле для результату (тепер внизу)
    result_text = tk.Text(stats_window, wrap=tk.WORD)
    result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
