from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import tkinter as tk
from datetime import date, timedelta
from database import get_db_connection
from utils import get_user_id
import mysql.connector  
def fetch_reading_rooms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, name FROM ReadingRooms")
    rooms = cursor.fetchall()
    conn.close()
    return rooms

def fetch_librarians_by_room(room_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if room_id:
        cursor.execute("""
            SELECT librarian_id, name 
            FROM Librarians 
            WHERE reading_room_id = %s
        """, (room_id,))
    else:
        cursor.execute("SELECT librarian_id, name FROM Librarians")
    
    librarians = cursor.fetchall()
    conn.close()
    return librarians

def fetch_all_librarians():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT librarian_id, name FROM Librarians")
    librarians = cursor.fetchall()
    conn.close()
    return librarians

def fetch_book_reading_place(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()   
    cursor.execute("""
        SELECT reading_place FROM BookReadingTypes WHERE book_id = %s
    """, (book_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def fetch_user_issued_books(reader_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ib.issue_id, ib.book_id, b.title, c.name as category, 
               ib.return_date, ib.reading_place, ib.room_id, ib.librarian_id
        FROM IssuedBooks ib
        JOIN Books b ON b.book_id = ib.book_id
        LEFT JOIN Categories c ON b.category_id = c.category_id
        WHERE ib.reader_id = %s AND ib.return_date >= CURDATE()
        ORDER BY ib.issue_date DESC
    """, (reader_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def return_book(issue_id, book_id, reader_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Отримуємо інформацію про книгу перед поверненням
        cursor.execute("SELECT reading_place FROM IssuedBooks WHERE issue_id = %s", (issue_id,))
        reading_place = cursor.fetchone()[0]
        
        # Видаляємо запис про видачу
        cursor.execute("DELETE FROM IssuedBooks WHERE issue_id = %s", (issue_id,))
        
        # ВИПРАВЛЕНО: Прибрано збільшення quantity, оскільки видалення запису з IssuedBooks
        # автоматично робить книгу доступною в підрахунку available_quantity
        
        conn.commit()
        messagebox.showinfo("Успіх", "Книгу повернено успішно.")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Помилка", f"Не вдалося повернути книгу: {e}")
    finally:
        conn.close()
    
    show_books(reader_id)
    show_returned_books_inline(reader_id, return_books_frame)

def show_returned_books_inline(reader_id, parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()
    tk.Label(parent_frame, text="\nВаші активні книги:", font=("Arial", 13, "bold"), anchor="w", bg="#f0f0f0").pack(anchor="w", padx=10, pady=(20, 5))
    header = tk.Frame(parent_frame, bg="#dddddd")
    header.pack(fill=tk.X, padx=10, pady=2)
    tk.Label(header, text="Назва книги", font=("Arial", 11, "bold"), width=30).pack(side=tk.LEFT)
    tk.Label(header, text="Категорія", font=("Arial", 11, "bold"), width=15).pack(side=tk.LEFT)
    tk.Label(header, text="Дата повернення", font=("Arial", 11, "bold"), width=20).pack(side=tk.LEFT)
    tk.Label(header, text="Місце", font=("Arial", 11, "bold"), width=20).pack(side=tk.LEFT)
    tk.Label(header, text="", width=15).pack(side=tk.LEFT)

    books = fetch_user_issued_books(reader_id)
    for issue_id, book_id, title, category, return_date, place, room_id, librarian_id in books:
        row = tk.Frame(parent_frame, bg="#ffffff")
        row.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(row, text=title, width=30, anchor="w", bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(row, text=category, width=15, anchor="w", bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(row, text=str(return_date), width=20, anchor="w", bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(row, text=place, width=20, anchor="w", bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Button(row, text="Повернути", command=lambda i=issue_id, b=book_id: return_book(i, b, reader_id), bg="red", fg="white").pack(side=tk.LEFT, padx=5)

def show_books(reader_id, category=None, title_search=None, room_filter=None, get_ids=None):
    global available_books_frame
    for widget in available_books_frame.winfo_children():
        widget.destroy()

    # Шапка таблиці
    header = tk.Frame(available_books_frame, bg="#f5f5f5")
    header.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(header, text="Назва книги", font=("Arial", 12, "bold"), width=30, anchor="w", bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Label(header, text="Категорія", font=("Arial", 12, "bold"), width=15, anchor="w", bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Label(header, text="У читальному залі", font=("Arial", 12, "bold"), width=20, anchor="w", bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Label(header, text="Доступна кількість", font=("Arial", 12, "bold"), width=18, anchor="w", bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Label(header, text="", width=20, bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Frame(available_books_frame, height=2, bg="gray").pack(fill=tk.X, padx=10, pady=2)

    # SQL
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT 
        b.book_id, 
        b.title, 
        COALESCE(c.name, 'Без категорії') AS category_name,
        b.access_type,
        IF(EXISTS (
            SELECT 1 FROM Placements p WHERE p.book_id = b.book_id
        ), 'Так', 'Ні') AS is_in_room,
        EXISTS (
            SELECT 1 FROM IssuedBooks ib
            WHERE ib.book_id = b.book_id
              AND ib.reader_id = %s
              AND ib.return_date >= CURDATE()
        ) AS is_issued_by_user,
        b.quantity - (
            SELECT COUNT(*) FROM IssuedBooks ib2
            WHERE ib2.book_id = b.book_id
              AND ib2.return_date >= CURDATE()
        ) AS available_quantity
    FROM Books b
    LEFT JOIN Categories c ON b.category_id = c.category_id
    """
    conditions = []
    params = [reader_id]

    if room_filter:
        conditions.append("EXISTS (SELECT 1 FROM Placements p WHERE p.book_id = b.book_id AND p.room_id = %s)")
        params.append(room_filter)
    if category:
        conditions.append("c.name = %s")
        params.append(category)
    if title_search:
        conditions.append("b.title LIKE %s")
        params.append(f"%{title_search}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY is_issued_by_user ASC, b.title"

    cursor.execute(query, params)
    books = cursor.fetchall()
    conn.close()

    # Кнопки
    def make_read_in_room_command(bid):
        def command():
            if get_ids is None:
                messagebox.showwarning("Увага", "Немає джерела вибору залу/бібліотекаря.")
                return
            room_id, librarian_id = get_ids()
            if not room_id:
                messagebox.showwarning("Увага", "Оберіть читальний зал.")
                return
            if not librarian_id:
                messagebox.showwarning("Увага", "Оберіть бібліотекаря.")
                return
            read_in_room(bid, reader_id, room_id, librarian_id)
        return command

    def make_read_at_home_command(bid):
        def command():
            if get_ids is None:
                messagebox.showwarning("Увага", "Немає джерела вибору залу/бібліотекаря.")
                return
            room_id, librarian_id = get_ids()
            if not room_id:
                messagebox.showwarning("Увага", "Оберіть читальний зал.")
                return
            if not librarian_id:
                messagebox.showwarning("Увага", "Оберіть бібліотекаря.")
                return
            read_at_home(bid, reader_id, room_id, librarian_id)
        return command

    # Рендер рядків
    for book_id, title, category_name, access_type, is_in_room, is_issued_by_user, available_quantity in books:
        row = tk.Frame(available_books_frame, bg="#e6e6e6" if is_issued_by_user else "#ffffff")
        row.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(row, text=title, font=("Arial", 11), width=30, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)
        tk.Label(row, text=category_name, font=("Arial", 11), width=15, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)
        tk.Label(row, text=is_in_room, font=("Arial", 11), width=20, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)
        tk.Label(row, text=str(available_quantity), font=("Arial", 11), width=18, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)

        btns = tk.Frame(row, bg=row.cget("bg"))
        btns.pack(side=tk.LEFT)

        in_room_btn = tk.Button(btns, text="В залі",  command=make_read_in_room_command(book_id), bg="orange", fg="white", padx=6, pady=2)
        home_btn   = tk.Button(btns, text="Вдома",   command=make_read_at_home_command(book_id), bg="lime green", fg="white", padx=6, pady=2)

        # Логіка для кнопок
        can_read_in_room = is_in_room == 'Так' and access_type in ['Тільки в читальній залі', 'У читальній залі і вдома'] and available_quantity > 0
        can_read_at_home = access_type == 'У читальній залі і вдома' and available_quantity > 0

        in_room_btn.config(state=tk.NORMAL if can_read_in_room else tk.DISABLED)
        home_btn.config(state=tk.NORMAL if can_read_at_home else tk.DISABLED)

        in_room_btn.pack(side=tk.LEFT, padx=5)
        home_btn.pack(side=tk.LEFT)

def read_in_room(book_id, reader_id, room_id, librarian_id):
    today = date.today()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ВАЖЛИВО: Перевіряємо, чи reader_id існує в таблиці Readers
        cursor.execute("SELECT reader_id FROM Readers WHERE reader_id = %s", (reader_id,))
        if not cursor.fetchone():
            conn.close()
            messagebox.showerror("Помилка", "Читач не знайдений в системі. Спробуйте вийти і увійти знову.")
            return

        # Перевірка, чи користувач вже має цю книгу сьогодні
        cursor.execute("""
            SELECT 1 FROM IssuedBooks 
            WHERE reader_id = %s AND book_id = %s 
            AND reading_place = 'Тільки в читальній залі' 
            AND issue_date = %s
        """, (reader_id, book_id, today))
        
        if cursor.fetchone():
            conn.close()
            messagebox.showinfo("Увага", "Ви вже взяли цю книгу для читання в залі сьогодні.")
            return

        # Перевірка доступності книги
        cursor.execute("""
            SELECT quantity - (
                SELECT COUNT(*) FROM IssuedBooks ib
                WHERE ib.book_id = %s
                AND ib.return_date >= CURDATE()
            ) AS available_quantity
            FROM Books WHERE book_id = %s
        """, (book_id, book_id))
        
        result = cursor.fetchone()
        if not result or result[0] <= 0:
            conn.close()
            messagebox.showinfo("Увага", "Немає доступних примірників цієї книги.")
            return

        # Додаємо запис про видачу - ВАЖЛИВО: використовуємо reader_id, а не user_id
        cursor.execute("""
            INSERT INTO IssuedBooks (reader_id, book_id, issue_date, return_date, reading_place, room_id, librarian_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (reader_id, book_id, today, today, 'Тільки в читальній залі', room_id, librarian_id))
        
        conn.commit()
        conn.close()
        messagebox.showinfo("Успіх", "Книга зареєстрована для читання в залі.")
        
        # Оновлюємо відображення
        show_books(reader_id)
        show_returned_books_inline(reader_id, return_books_frame)
        
    except mysql.connector.Error as err:
        if conn:
            conn.close()
        if err.errno == 1452:  # Foreign key constraint fail
            messagebox.showerror("Помилка", f"Помилка бази даних: Неправильний reader_id. Спробуйте вийти і увійти знову.\n{err}")
        else:
            messagebox.showerror("Помилка", f"Не вдалося зареєструвати книгу: {err}")
    except Exception as e:
        if conn:
            conn.close()
        messagebox.showerror("Помилка", f"Несподівана помилка: {e}")

def read_at_home(book_id, reader_id, room_id, librarian_id):
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

            # ВАЖЛИВО: Перевіряємо, чи reader_id існує в таблиці Readers
            cursor.execute("SELECT reader_id FROM Readers WHERE reader_id = %s", (reader_id,))
            if not cursor.fetchone():
                conn.close()
                messagebox.showerror("Помилка", "Читач не знайдений в системі. Спробуйте вийти і увійти знову.")
                return

            # Перевірка, чи користувач вже має цю книгу
            cursor.execute("""
                SELECT 1 FROM IssuedBooks 
                WHERE reader_id = %s AND book_id = %s 
                AND reading_place = 'У читальній залі і в дома' 
                AND return_date >= CURDATE()
            """, (reader_id, book_id))
            
            if cursor.fetchone():
                conn.close()
                messagebox.showinfo("Увага", "Ви вже маєте цю книгу вдома.")
                return

            # Перевірка доступності книги
            cursor.execute("""
                SELECT quantity - (
                    SELECT COUNT(*) FROM IssuedBooks ib
                    WHERE ib.book_id = %s
                    AND ib.return_date >= CURDATE()
                ) AS available_quantity
                FROM Books WHERE book_id = %s
            """, (book_id, book_id))
            
            result = cursor.fetchone()
            if not result or result[0] <= 0:
                conn.close()
                messagebox.showinfo("Увага", "Немає доступних примірників цієї книги.")
                return

            # Додаємо запис про видачу - ВАЖЛИВО: використовуємо reader_id, а не user_id
            cursor.execute("""
                INSERT INTO IssuedBooks (reader_id, book_id, issue_date, return_date, reading_place, room_id, librarian_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (reader_id, book_id, today, selected_date, 'У читальній залі і в дома', room_id, librarian_id))
            
            conn.commit()
            conn.close()
            
            top.destroy()
            messagebox.showinfo("Успіх", "Книга зареєстрована для читання вдома.")
            
            # Оновлюємо відображення
            show_books(reader_id)
            show_returned_books_inline(reader_id, return_books_frame)
            
        except mysql.connector.Error as err:
            if conn:
                conn.close()
            if err.errno == 1452:  # Foreign key constraint fail
                messagebox.showerror("Помилка", f"Помилка бази даних: Неправильний reader_id. Спробуйте вийти і увійти знову.\n{err}")
            else:
                messagebox.showerror("Помилка", f"Не вдалося зареєструвати книгу: {err}")
        except Exception as e:
            if conn:
                conn.close()
            messagebox.showerror("Помилка", f"Несподівана помилка: {e}")

    # Створення вікна вибору дати
    top = tk.Toplevel()
    top.title("Оберіть дату повернення")
    top.geometry("300x180")
    top.grab_set()
    
    tk.Label(top, text="Оберіть дату повернення:", font=("Arial", 11)).pack(pady=10)
    
    return_calendar = DateEntry(top, mindate=date.today(), 
                               maxdate=date.today() + timedelta(days=7), 
                               date_pattern='yyyy-mm-dd')
    return_calendar.pack(pady=5)
    
    tk.Button(top, text="Підтвердити", command=confirm_return_date, 
             bg="green", fg="white", font=("Arial", 10)).pack(pady=10)
def show_reader_window(reader_id):
    global available_books_frame, return_books_frame
    root = tk.Tk()
    root.title("Бібліотечна система")
    root.geometry("1050x750")
    root.configure(bg="#f0f0f0")

    # Дані для комбобоксів
    rooms = fetch_reading_rooms()
    room_ids = {name: rid for rid, name in rooms}

    all_librarians = fetch_all_librarians()
    librarian_ids = {name: lid for lid, name in all_librarians}

    # Змінні фільтрів
    room_var = tk.StringVar()
    librarian_var = tk.StringVar()
    category_var = tk.StringVar()
    search_var = tk.StringVar()

    # Топ-бар фільтрів
    top = tk.Frame(root, bg="#f0f0f0")
    top.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(top, text="Читальний зал:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    room_menu = ttk.Combobox(top, textvariable=room_var, state="readonly", width=22)
    room_menu['values'] = [''] + [name for _, name in rooms]
    room_menu.current(0)
    room_menu.pack(side=tk.LEFT, padx=5)

    tk.Label(top, text="Бібліотекар:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    librarian_menu = ttk.Combobox(top, textvariable=librarian_var, state="readonly", width=22)
    librarian_menu['values'] = [''] + [name for _, name in all_librarians]
    librarian_menu.current(0)
    librarian_menu.pack(side=tk.LEFT, padx=5)

    tk.Label(top, text="Категорія:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    category_menu = ttk.Combobox(top, textvariable=category_var, state="readonly", width=20)
    category_menu['values'] = ('', 'книги', 'журнали', 'газети', 'збірники статей',
                               'збірники віршів', 'дисертації', 'реферати', 'збірники доповідей і тез доповідей')
    category_menu.current(0)
    category_menu.pack(side=tk.LEFT, padx=5)

    tk.Label(top, text="Назва:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    search_entry = tk.Entry(top, textvariable=search_var, width=25)
    search_entry.pack(side=tk.LEFT, padx=5)

    # Функція для оновлення списку бібліотекарів при зміні читального залу
    def update_librarians(*args):
        selected_room_name = room_var.get()
        if selected_room_name:
            room_id = room_ids[selected_room_name]
            librarians_in_room = fetch_librarians_by_room(room_id)
            librarian_menu['values'] = [''] + [name for _, name in librarians_in_room]
        else:
            librarian_menu['values'] = [''] + [name for _, name in all_librarians]
        librarian_menu.current(0)
        librarian_var.set('')

    # Прив'язка події зміни читального залу
    room_var.trace_add('write', update_librarians)

    # Фрейми під таблиці
    books_frame = tk.Frame(root, bg="#f0f0f0")
    books_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    available_books_frame = books_frame

    return_books_frame = tk.Frame(root, bg="#f0f0f0")
    return_books_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def get_selected_ids():
        """Повертає (room_id, librarian_id) або (None, None) якщо не вибрано."""
        r = room_ids.get(room_var.get()) if room_var.get() else None
        l = librarian_ids.get(librarian_var.get()) if librarian_var.get() else None
        return r, l

    def refresh_books(*_):
        room_id = room_ids.get(room_var.get()) if room_var.get() else None
        cat = category_var.get() if category_var.get() else None
        title = search_var.get().strip() if search_var.get().strip() else None
        show_books(reader_id, room_filter=room_id, category=cat, title_search=title, get_ids=get_selected_ids)

    # Автооновлення при зміні залу/категорії, кнопка пошуку — для назви
    room_var.trace_add('write', refresh_books)
    category_var.trace_add('write', refresh_books)
    tk.Button(top, text="Пошук", command=refresh_books).pack(side=tk.LEFT, padx=5)

    # Початковий рендер
    refresh_books()
    show_returned_books_inline(reader_id, return_books_frame)

    root.mainloop()