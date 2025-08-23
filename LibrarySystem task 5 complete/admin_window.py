from tkinter import *
from tkinter import ttk, messagebox
import tkinter as tk
from tkinter import ttk
from database import get_db_connection
from utils import get_books, get_reading_rooms
import login_window
from tkcalendar import DateEntry
import tkinter as tk
from datetime import date, timedelta
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

def get_libraries():
    """Отримуємо список всіх бібліотек"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT library_id, name FROM Libraries")
    libraries = cursor.fetchall()
    conn.close()
    return libraries

def get_reading_rooms_by_library(library_id):
    """Отримуємо читальні зали вказаної бібліотеки"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, name FROM ReadingRooms WHERE library_id = %s", (library_id,))
    rooms = cursor.fetchall()
    conn.close()
    return rooms
import tkinter as tk
from tkinter import messagebox
from database import get_db_connection

import tkinter as tk
from tkinter import messagebox
from database import get_db_connection

import tkinter as tk
from tkinter import messagebox
from database import get_db_connection


import tkinter as tk
from tkinter import messagebox
from database import get_db_connection

def find_books_by_work_or_author():
    search_window = tk.Toplevel()
    search_window.title("Пошук книг за назвою та автором")
    search_window.geometry("700x600")
    # Фрейм для пошуку книги за назвою
    book_frame = tk.LabelFrame(search_window, text="Пошук книги за назвою", padx=10, pady=10)
    book_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(book_frame, text="Введіть назву книги:").pack(anchor="w")
    title_entry = tk.Entry(book_frame, width=60)
    title_entry.pack(pady=5)

    # Фрейм для пошуку книг автора
    author_frame = tk.LabelFrame(search_window, text="Пошук всіх книг автора", padx=10, pady=10)
    author_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(author_frame, text="Введіть ім'я або прізвище автора:").pack(anchor="w")
    author_entry = tk.Entry(author_frame, width=60)
    author_entry.pack(pady=5)

    # Результати пошуку
    result_frame = tk.LabelFrame(search_window, text="Результати пошуку", padx=10, pady=10)
    result_frame.pack(fill="both", expand=True, padx=10, pady=5)

    result_box = tk.Text(result_frame, width=85, height=20, wrap=tk.WORD)
    result_box.pack(fill="both", expand=True, padx=5, pady=5)

    scrollbar = tk.Scrollbar(result_box)
    scrollbar.pack(side="right", fill="y")
    result_box.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=result_box.yview)

    def search_by_title():
        """Пошук книги за назвою"""
        title_query = title_entry.get().strip()
        if not title_query:
            messagebox.showerror("Помилка", "Введіть назву книги!")
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT b.book_id, b.title, CONCAT(a.name, ' ', a.surname) AS author, 
                       b.access_type, b.inventory_number
                FROM Books b
                JOIN Authors a ON b.author_id = a.author_id
                WHERE b.title LIKE %s
            """, (f"%{title_query}%",))

            books = cursor.fetchall()
            result_box.delete(1.0, tk.END)

            if not books:
                result_box.insert(tk.END, f"📭 Книг з назвою '{title_query}' не знайдено.\n")
                return

            result_box.insert(tk.END, f"📚 Знайдено книг за назвою '{title_query}': {len(books)}\n\n")
            
            for book_id, title, author, access_type, inventory_number in books:
                result_box.insert(tk.END, f"📘 '{title}' (Інвентарний номер: {inventory_number})\n")
                result_box.insert(tk.END, f"   Автор: {author}\n")
                result_box.insert(tk.END, f"   Доступ: {access_type}\n")

                # Перевірка на збірки
                cursor.execute("""
                    SELECT c.collection_id, c.title, c.year
                    FROM CollectionItems ci
                    JOIN Collections c ON ci.collection_id = c.collection_id
                    WHERE ci.book_id = %s
                """, (book_id,))
                collections = cursor.fetchall()

                if collections:
                    result_box.insert(tk.END, "   🔗 Належить до збірок:\n")
                    for coll_id, coll_title, year in collections:
                        result_box.insert(tk.END, f"      • {coll_title} (ID: {coll_id}, {year})\n")
                else:
                    result_box.insert(tk.END, "   ❌ Не входить до жодної збірки\n")
                result_box.insert(tk.END, "\n")

        except Exception as e:
            messagebox.showerror("Помилка", f"Сталася помилка при пошуку:\n{e}")
        finally:
            conn.close()

    def search_by_author():
        """Пошук всіх книг автора"""
        author_query = author_entry.get().strip()
        if not author_query:
            messagebox.showerror("Помилка", "Введіть ім'я або прізвище автора!")
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT b.book_id, b.title, CONCAT(a.name, ' ', a.surname) AS author, 
                       b.access_type, b.inventory_number
                FROM Books b
                JOIN Authors a ON b.author_id = a.author_id
                WHERE a.name LIKE %s OR a.surname LIKE %s
                ORDER BY b.title
            """, (f"%{author_query}%", f"%{author_query}%"))

            books = cursor.fetchall()
            result_box.delete(1.0, tk.END)

            if not books:
                result_box.insert(tk.END, f"📭 Книг автора '{author_query}' не знайдено.\n")
                return

            result_box.insert(tk.END, f"👤 Всі книги автора '{author_query}': {len(books)}\n\n")
            
            for book_id, title, author, access_type, inventory_number in books:
                result_box.insert(tk.END, f"📘 '{title}' (Інвентарний номер: {inventory_number})\n")
                result_box.insert(tk.END, f"   Автор: {author}\n")
                result_box.insert(tk.END, f"   Доступ: {access_type}\n")

                # Перевірка на збірки
                cursor.execute("""
                    SELECT c.collection_id, c.title, c.year
                    FROM CollectionItems ci
                    JOIN Collections c ON ci.collection_id = c.collection_id
                    WHERE ci.book_id = %s
                """, (book_id,))
                collections = cursor.fetchall()

                if collections:
                    result_box.insert(tk.END, "   🔗 Належить до збірок:\n")
                    for coll_id, coll_title, year in collections:
                        result_box.insert(tk.END, f"      • {coll_title} (ID: {coll_id}, {year})\n")
                else:
                    result_box.insert(tk.END, "   ❌ Не входить до жодної збірки\n")
                result_box.insert(tk.END, "\n")

        except Exception as e:
            messagebox.showerror("Помилка", f"Сталася помилка при пошуку:\n{e}")
        finally:
            conn.close()

    # Кнопки для пошуку
    button_frame = tk.Frame(search_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Пошук за назвою книги", command=search_by_title, 
              bg="blue", fg="white", width=20).pack(side="left", padx=5)
    
    tk.Button(button_frame, text="Пошук книг автора", command=search_by_author, 
              bg="green", fg="white", width=20).pack(side="left", padx=5)

    # Кнопка очищення результатів
    def clear_results():
        result_box.delete(1.0, tk.END)
        title_entry.delete(0, tk.END)
        author_entry.delete(0, tk.END)

    tk.Button(button_frame, text="Очистити", command=clear_results, 
              bg="gray", fg="white", width=10).pack(side="left", padx=5)
def get_librarians_worked_in_room():
    """Показує вікно для пошуку бібліотекарів, які працюють у вказаному залі"""
    search_window = tk.Toplevel()
    search_window.title("Бібліотекарі за читальним залом")
    search_window.geometry("600x500")
    
    # Вибір бібліотеки
    tk.Label(search_window, text="Оберіть бібліотеку:").pack(pady=5)
    libraries = get_libraries()
    library_map = {f"{name} (ID: {lib_id})": lib_id for lib_id, name in libraries}
    library_combo = ttk.Combobox(search_window, values=list(library_map.keys()), state="readonly", width=50)
    library_combo.pack(pady=5)
    
    # Вибір читального залу
    tk.Label(search_window, text="Оберіть читальний зал:").pack(pady=5)
    room_combo = ttk.Combobox(search_window, state="readonly", width=50)
    room_combo.pack(pady=5)
    
    def update_rooms(*args):
        """Оновлює список читальних залів при зміні бібліотеки"""
        selected_library = library_combo.get()
        if selected_library:
            library_id = library_map[selected_library]
            rooms = get_reading_rooms_by_library(library_id)
            room_map = {f"{name} (ID: {room_id})": room_id for room_id, name in rooms}
            room_combo['values'] = list(room_map.keys())
            room_combo.set('')  # Очищуємо вибір залу
        else:
            room_combo['values'] = []
            room_combo.set('')
    
    library_combo.bind('<<ComboboxSelected>>', update_rooms)
    
    # Результати
    result_frame = tk.Frame(search_window)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    tk.Label(result_frame, text="Результати пошуку:").pack(anchor='w')
    result_text = tk.Text(result_frame, wrap=tk.WORD, height=15)
    result_text.pack(fill=tk.BOTH, expand=True)
    
    def search_librarians():
        """Пошук всіх бібліотекарів, які працюють у вказаному залі"""
        selected_library = library_combo.get()
        selected_room = room_combo.get()
        
        if not selected_library:
            messagebox.showerror("Помилка", "Оберіть бібліотеку!")
            return
        if not selected_room:
            messagebox.showerror("Помилка", "Оберіть читальний зал!")
            return
        
        # Отримуємо ID з вибраних значень
        library_id = library_map[selected_library]
        # Парсимо room_id з рядка формату "Name (ID: room_id)"
        room_id = selected_room.split("ID: ")[1].rstrip(")")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQL запит для отримання всіх бібліотекарів, які працюють у вказаному залі
        cursor.execute("""
            SELECT l.librarian_id, l.name, u.login,
                   COALESCE(stats.books_issued, 0) as books_issued,
                   stats.first_work_date,
                   stats.last_work_date
            FROM Librarians l
            INNER JOIN Users u ON l.librarian_id = u.user_id
            INNER JOIN ReadingRooms rr ON l.reading_room_id = rr.room_id
            LEFT JOIN (
                SELECT ib.librarian_id,
                       COUNT(ib.issue_id) as books_issued,
                       MIN(ib.issue_date) as first_work_date,
                       MAX(ib.issue_date) as last_work_date
                FROM IssuedBooks ib
                WHERE ib.room_id = %s
                GROUP BY ib.librarian_id
            ) stats ON l.librarian_id = stats.librarian_id
            WHERE l.reading_room_id = %s 
              AND rr.library_id = %s
            ORDER BY l.name
        """, (room_id, room_id, library_id))
        
        results = cursor.fetchall()
        conn.close()
        
        # Очищуємо і заповнюємо результати
        result_text.delete(1.0, tk.END)
        
        if results:
            library_name = selected_library.split(" (ID:")[0]
            room_name = selected_room.split(" (ID:")[0]
            
            header = f"Бібліотекарі, які працюють у залі '{room_name}' бібліотеки '{library_name}':\n\n"
            result_text.insert(tk.END, header)
            
            for librarian_id, name, login, books_count, first_date, last_date in results:
                info = f"• {name} (ID: {librarian_id}, Логін: {login})\n"
                info += f"  Видано книг у цьому залі: {books_count}\n"
                
                if first_date and last_date:
                    info += f"  Перша видача в залі: {first_date}\n"
                    info += f"  Остання видача в залі: {last_date}\n"
                else:
                    info += f"  Ще не видавав книги в цьому залі\n"
                
                info += "\n"
                result_text.insert(tk.END, info)
                
            result_text.insert(tk.END, f"Загалом знайдено: {len(results)} бібліотекар(ів)")
        else:
            result_text.insert(tk.END, "У вказаному читальному залі цієї бібліотеки не знайдено жодного бібліотекаря.")
    
    # Кнопка пошуку
    tk.Button(search_window, text="Знайти бібліотекарів", command=search_librarians, 
              bg="blue", fg="white", font=("Arial", 10)).pack(pady=10)
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
    edit_window = tk.Toplevel()
    edit_window.title("Редагування книги")
    edit_window.geometry("500x550")

    # Отримуємо книги та формуємо словник
    books = get_books()
    book_dict = {f"{title} (ID: {book_id})": book_id for book_id, title in books}

    # Отримуємо зали
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
        "У читальній залі і вдома",
        "Тільки в читальній залі"
    ]
    access_type_combobox.pack(pady=5)

    # Зал
    tk.Label(edit_window, text="Оберіть зал:").pack()
    room_combobox = ttk.Combobox(edit_window, width=40, values=list(room_dict.keys()))
    room_combobox.pack(pady=5)

    # Полиця
    tk.Label(edit_window, text="Полиця:").pack()
    shelf_entry = tk.Entry(edit_window)
    shelf_entry.pack(pady=5)

    # Ряд
    tk.Label(edit_window, text="Ряд:").pack()
    row_entry = tk.Entry(edit_window)
    row_entry.pack(pady=5)

    # Кількість книг
    tk.Label(edit_window, text="Кількість примірників:").pack()
    quantity_entry = tk.Entry(edit_window)
    quantity_entry.pack(pady=5)

    # Завантаження інформації про книгу при виборі
    def load_book_info(event):
        selected_key = book_combobox.get()
        if not selected_key:
            return
        book_id = book_dict[selected_key]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Завантажуємо тип доступу і кількість
        cursor.execute("SELECT access_type, quantity FROM Books WHERE book_id = %s", (book_id,))
        result = cursor.fetchone()
        if result:
            access_type_combobox.set(result[0])
            quantity_entry.delete(0, tk.END)
            quantity_entry.insert(0, result[1])
        else:
            access_type_combobox.set("")
            quantity_entry.delete(0, tk.END)

        # Завантажуємо розміщення
        cursor.execute("SELECT room_id, shelf, `row` FROM Placements WHERE book_id = %s LIMIT 1", (book_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            room_id, shelf, row = result
            for name, rid in room_dict.items():
                if rid == room_id:
                    room_combobox.set(name)
                    break
            shelf_entry.delete(0, tk.END)
            shelf_entry.insert(0, shelf)
            row_entry.delete(0, tk.END)
            row_entry.insert(0, row)
        else:
            room_combobox.set("")
            shelf_entry.delete(0, tk.END)
            row_entry.delete(0, tk.END)

    book_combobox.bind("<<ComboboxSelected>>", load_book_info)

    # Оновлення книги
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
        quantity = quantity_entry.get()

        if not selected_room or not access_type or not shelf or not row or not quantity:
            messagebox.showerror("Помилка", "Усі поля мають бути заповнені.")
            return

        try:
            quantity = int(quantity)
            if quantity < 0:
                messagebox.showerror("Помилка", "Кількість не може бути менше нуля.")
                return
        except ValueError:
            messagebox.showerror("Помилка", "Кількість повинна бути числом.")
            return

        room_id = room_dict[selected_room]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Books SET access_type = %s, quantity = %s WHERE book_id = %s",
                           (access_type, quantity, book_id))
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
def show_books_management_window():
    """Головне вікно управління книгами"""
    management_window = tk.Toplevel()
    management_window.title("Управління книгами та звіти")
    management_window.geometry("600x500")

    tk.Label(management_window, text="Управління книгами", font=("Arial", 16, "bold")).pack(pady=10)

    # Фрейм для кнопок
    buttons_frame = tk.Frame(management_window)
    buttons_frame.pack(pady=20)

    tk.Button(buttons_frame, text="Списати книги", command=show_writeoff_window,
              bg="red", fg="white", width=25, height=2).pack(pady=5)
    
    tk.Button(buttons_frame, text="Звіт по надходженню", command=show_arrivals_report,
              bg="green", fg="white", width=25, height=2).pack(pady=5)
    
    tk.Button(buttons_frame, text="Звіт по списанню", command=show_writeoff_report,
              bg="orange", fg="white", width=25, height=2).pack(pady=5)
    
    tk.Button(buttons_frame, text="Переглянути списані книги", command=show_written_off_books,
              bg="gray", fg="white", width=25, height=2).pack(pady=5)

def show_writeoff_window():
    """Вікно для списання книг"""
    writeoff_window = tk.Toplevel()
    writeoff_window.title("Списання книг")
    writeoff_window.geometry("700x600")

    # Пошук книги
    search_frame = tk.LabelFrame(writeoff_window, text="Пошук книги для списання", padx=10, pady=10)
    search_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(search_frame, text="Пошук за назвою або інвентарним номером:").pack(anchor="w")
    search_entry = tk.Entry(search_frame, width=50)
    search_entry.pack(pady=5)

    # Список знайдених книг
    books_frame = tk.LabelFrame(writeoff_window, text="Знайдені книги", padx=10, pady=10)
    books_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Створюємо Treeview для відображення книг
    columns = ("ID", "Назва", "Автор", "Інвентарний номер", "Дата додавання")
    books_tree = ttk.Treeview(books_frame, columns=columns, show="headings", height=10)
    
    for col in columns:
        books_tree.heading(col, text=col)
        books_tree.column(col, width=120)

    scrollbar = ttk.Scrollbar(books_frame, orient="vertical", command=books_tree.yview)
    books_tree.configure(yscrollcommand=scrollbar.set)
    
    books_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Причина списання
    reason_frame = tk.Frame(writeoff_window)
    reason_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(reason_frame, text="Причина списання:").pack(anchor="w")
    reason_entry = tk.Entry(reason_frame, width=60)
    reason_entry.pack(pady=5)

    def search_books():
        """Пошук книг або показ усіх, якщо поле порожнє"""
        search_query = search_entry.get().strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        if search_query:
            cursor.execute("""
                SELECT b.book_id, b.title, CONCAT(a.name, ' ', a.surname) as author,
                       b.inventory_number, b.date_added
                FROM Books b
                JOIN Authors a ON b.author_id = a.author_id
                WHERE b.title LIKE %s OR b.inventory_number LIKE %s
                ORDER BY b.title
            """, (f"%{search_query}%", f"%{search_query}%"))
        else:
            # Якщо поле пусте — показати всі книги
            cursor.execute("""
                SELECT b.book_id, b.title, CONCAT(a.name, ' ', a.surname) as author,
                       b.inventory_number, b.date_added
                FROM Books b
                JOIN Authors a ON b.author_id = a.author_id
                ORDER BY b.title
            """)
        
        results = cursor.fetchall()
        conn.close()

        # Очищуємо попередні результати
        for item in books_tree.get_children():
            books_tree.delete(item)

        # Додаємо нові результати
        for book_id, title, author, inventory_number, date_added in results:
            books_tree.insert("", "end", values=(book_id, title, author, inventory_number, date_added))

    def writeoff_selected_book():
        """Списати вибрану книгу"""
        selected_item = books_tree.selection()
        if not selected_item:
            messagebox.showerror("Помилка", "Оберіть книгу для списання!")
            return

        reason = reason_entry.get().strip()
        if not reason:
            messagebox.showerror("Помилка", "Вкажіть причину списання!")
            return

        # Отримуємо ID книги
        book_data = books_tree.item(selected_item[0])["values"]
        book_id = book_data[0]
        book_title = book_data[1]

        # Підтвердження
        if not messagebox.askyesno("Підтвердження", 
                                 f"Ви дійсно хочете списати книгу:\n'{book_title}'?\n\nПричина: {reason}"):
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Виконуємо процедуру списання (або SQL запити)
            cursor.callproc('WriteOffBook', [book_id, reason])
            conn.commit()
            
            messagebox.showinfo("Успіх", f"Книгу '{book_title}' успішно списано!")
            
            # Оновлюємо список
            search_books()
            reason_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при списанні книги:\n{e}")
        finally:
            conn.close()

    # Кнопки
    buttons_frame = tk.Frame(writeoff_window)
    buttons_frame.pack(pady=10)

    tk.Button(buttons_frame, text="Пошук", command=search_books, 
              bg="blue", fg="white", width=15).pack(side="left", padx=5)
    
    tk.Button(buttons_frame, text="Списати книгу", command=writeoff_selected_book,
              bg="red", fg="white", width=15).pack(side="left", padx=5)

    # 🔹 Викликаємо одразу при відкритті, щоб показати всі книги
    search_books()

def show_arrivals_report():
    """Звіт по надходженню книг за період"""
    report_window = tk.Toplevel()
    report_window.title("Звіт по надходженню книг")
    report_window.geometry("800x600")

    # Вибір періоду
    period_frame = tk.LabelFrame(report_window, text="Оберіть період", padx=10, pady=10)
    period_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(period_frame, text="Від:").grid(row=0, column=0, sticky="w", padx=5)
    start_date = DateEntry(period_frame, width=12, background='darkblue',
                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    start_date.grid(row=0, column=1, padx=5)

    tk.Label(period_frame, text="До:").grid(row=0, column=2, sticky="w", padx=5)
    end_date = DateEntry(period_frame, width=12, background='darkblue',
                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    end_date.grid(row=0, column=3, padx=5)

    # Результати
    results_frame = tk.LabelFrame(report_window, text="Результати", padx=10, pady=10)
    results_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("ID", "Назва", "Автор", "Інвентарний номер", "Дата додавання", "Категорія")
    results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
    
    for col in columns:
        results_tree.heading(col, text=col)
        results_tree.column(col, width=120)

    scrollbar_results = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview)
    results_tree.configure(yscrollcommand=scrollbar_results.set)
    
    results_tree.pack(side="left", fill="both", expand=True)
    scrollbar_results.pack(side="right", fill="y")

    def generate_report():
        """Генерувати звіт"""
        start_date_str = start_date.get()
        end_date_str = end_date.get()

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT b.book_id, b.title, CONCAT(a.name, ' ', a.surname) as author,
                   b.inventory_number, b.date_added, c.name as category
            FROM Books b
            JOIN Authors a ON b.author_id = a.author_id
            LEFT JOIN Categories c ON b.category_id = c.category_id
            WHERE b.date_added BETWEEN %s AND %s
            ORDER BY b.date_added DESC
        """, (start_date_str, end_date_str))
        
        results = cursor.fetchall()
        conn.close()

        # Очищуємо попередні результати
        for item in results_tree.get_children():
            results_tree.delete(item)

        # Додаємо нові результати
        for result in results:
            results_tree.insert("", "end", values=result)
        
        total_label.config(text=f"Загалом знайдено: {len(results)} книг")

    # Кнопка генерації звіту
    tk.Button(period_frame, text="Генерувати звіт", command=generate_report,
              bg="green", fg="white").grid(row=0, column=4, padx=10)

    # Label для відображення загальної кількості
    total_label = tk.Label(report_window, text="", font=("Arial", 10, "bold"))
    total_label.pack(pady=5)

def show_writeoff_report():
    """Звіт по списанню книг за період"""
    report_window = tk.Toplevel()
    report_window.title("Звіт по списанню книг")
    report_window.geometry("800x600")

    # Вибір періоду
    period_frame = tk.LabelFrame(report_window, text="Оберіть період", padx=10, pady=10)
    period_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(period_frame, text="Від:").grid(row=0, column=0, sticky="w", padx=5)
    start_date = DateEntry(period_frame, width=12, background='darkblue',
                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    start_date.grid(row=0, column=1, padx=5)

    tk.Label(period_frame, text="До:").grid(row=0, column=2, sticky="w", padx=5)
    end_date = DateEntry(period_frame, width=12, background='darkblue',
                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    end_date.grid(row=0, column=3, padx=5)

    # Результати
    results_frame = tk.LabelFrame(report_window, text="Результати", padx=10, pady=10)
    results_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("ID списання", "Назва", "Автор", "Інвентарний номер", "Дата списання", "Причина")
    results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
    
    for col in columns:
        results_tree.heading(col, text=col)
        results_tree.column(col, width=130)

    scrollbar_results = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview)
    results_tree.configure(yscrollcommand=scrollbar_results.set)
    
    results_tree.pack(side="left", fill="both", expand=True)
    scrollbar_results.pack(side="right", fill="y")

    def generate_writeoff_report():
        """Генерувати звіт по списанню"""
        start_date_str = start_date.get()
        end_date_str = end_date.get()

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT wob.writeoff_id, wob.title, CONCAT(a.name, ' ', a.surname) as author,
                   wob.inventory_number, wob.date_written_off, wob.writeoff_reason
            FROM WrittenOffBooks wob
            JOIN Authors a ON wob.author_id = a.author_id
            WHERE wob.date_written_off BETWEEN %s AND %s
            ORDER BY wob.date_written_off DESC
        """, (start_date_str, end_date_str))
        
        results = cursor.fetchall()
        conn.close()

        # Очищуємо попередні результати
        for item in results_tree.get_children():
            results_tree.delete(item)

        # Додаємо нові результати
        for result in results:
            results_tree.insert("", "end", values=result)
        
        total_label.config(text=f"Загалом списано: {len(results)} книг")

    # Кнопка генерації звіту
    tk.Button(period_frame, text="Генерувати звіт", command=generate_writeoff_report,
              bg="orange", fg="white").grid(row=0, column=4, padx=10)

    # Label для відображення загальної кількості
    total_label = tk.Label(report_window, text="", font=("Arial", 10, "bold"))
    total_label.pack(pady=5)

def show_written_off_books():
    """Показати всі списані книги"""
    books_window = tk.Toplevel()
    books_window.title("Списані книги")
    books_window.geometry("900x600")

    # Результати
    results_frame = tk.LabelFrame(books_window, text="Список усіх списаних книг", padx=10, pady=10)
    results_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("ID", "Назва", "Автор", "Інвентарний номер", "Дата додавання", "Дата списання", "Причина")
    results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=20)
    
    for col in columns:
        results_tree.heading(col, text=col)
        results_tree.column(col, width=120)

    scrollbar_results = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview)
    results_tree.configure(yscrollcommand=scrollbar_results.set)
    
    results_tree.pack(side="left", fill="both", expand=True)
    scrollbar_results.pack(side="right", fill="y")

    # Завантажуємо дані
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT wob.writeoff_id, wob.title, CONCAT(a.name, ' ', a.surname) as author,
               wob.inventory_number, wob.date_added, wob.date_written_off, wob.writeoff_reason
        FROM WrittenOffBooks wob
        JOIN Authors a ON wob.author_id = a.author_id
        ORDER BY wob.date_written_off DESC
    """)
    
    results = cursor.fetchall()
    conn.close()

    # Додаємо результати
    for result in results:
        results_tree.insert("", "end", values=result)

    total_label = tk.Label(books_window, text=f"Загалом списано книг: {len(results)}", 
                          font=("Arial", 10, "bold"))
    total_label.pack(pady=5)
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
    tk.Button(admin_window, text="Бібліотекарі за залом", command=get_librarians_worked_in_room).pack(pady=5)
    tk.Button(admin_window, text="Пошук книг за назвою/автором/ID", command=find_books_by_work_or_author).pack(pady=5)
    tk.Button(admin_window, text="Курування наявнити та списаними книгами", command=show_books_management_window).pack(pady=5)
    tk.Button(admin_window, text="Вийти", command=admin_window.destroy).pack(pady=10)

    admin_window.mainloop()
    