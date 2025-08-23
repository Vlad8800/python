from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import tkinter as tk
from datetime import date, timedelta
from database import get_db_connection
from utils import get_user_id
import mysql.connector
import random

# =============================== Глобальні фрейми ===============================
available_books_frame = None
return_books_frame = None

# =============================== Довідкові вибірки ===============================
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
        cursor.execute(
            """
            SELECT librarian_id, name
            FROM Librarians
            WHERE reading_room_id = %s
            """,
            (room_id,),
        )
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

# =============================== Активні видачі (книги + збірки) ===============================
def fetch_user_issued_items(reader_id):
    """
    Повертає активні видачі користувача (і книги, і збірки).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT ib.issue_id,
               ib.book_id,
               ib.collection_id,
               CASE 
                   WHEN ib.book_id IS NOT NULL THEN b.title
                   ELSE col.title
               END AS title,
               CASE 
                   WHEN ib.book_id IS NOT NULL THEN COALESCE(cat_b.name, 'Без категорії')
                   ELSE COALESCE(cat_c.name, 'Без категорії')
               END AS category,
               ib.return_date,
               ib.reading_place,
               ib.room_id,
               ib.librarian_id
        FROM IssuedBooks ib
        LEFT JOIN Books b ON b.book_id = ib.book_id
        LEFT JOIN collections col ON col.collection_id = ib.collection_id
        LEFT JOIN Categories cat_b ON b.category_id = cat_b.category_id
        LEFT JOIN Categories cat_c ON col.category_id = cat_c.category_id
        WHERE ib.reader_id = %s
          AND ib.return_date >= CURDATE()
        ORDER BY ib.issue_date DESC, title
        """,
        (reader_id,),
    )
    result = cursor.fetchall()
    conn.close()
    return result

# =============================== Повернення ===============================
def return_item(issue_id, reader_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM IssuedBooks WHERE issue_id = %s", (issue_id,))
        conn.commit()
        messagebox.showinfo("Успіх", "Повернення виконано успішно.")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Помилка", f"Не вдалося повернути: {e}")
    finally:
        conn.close()

    show_books_and_collections(reader_id)
    show_returned_items_inline(reader_id, return_books_frame)

# =============================== Відображення активних ===============================
def show_returned_items_inline(reader_id, parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    tk.Label(
        parent_frame,
        text="\nВаші активні книги/збірки:",
        font=("Arial", 13, "bold"),
        anchor="w",
        bg="#f0f0f0",
    ).pack(anchor="w", padx=10, pady=(20, 5))

    header = tk.Frame(parent_frame, bg="#dddddd")
    header.pack(fill=tk.X, padx=10, pady=2)
    tk.Label(header, text="Назва", font=("Arial", 11, "bold"), width=30).pack(side=tk.LEFT)
    tk.Label(header, text="Категорія", font=("Arial", 11, "bold"), width=15).pack(side=tk.LEFT)
    tk.Label(header, text="Дата повернення", font=("Arial", 11, "bold"), width=20).pack(side=tk.LEFT)
    tk.Label(header, text="Місце", font=("Arial", 11, "bold"), width=20).pack(side=tk.LEFT)
    tk.Label(header, text="", width=15).pack(side=tk.LEFT)

    items = fetch_user_issued_items(reader_id)
    for issue_id, book_id, collection_id, title, category, return_date, place, room_id, librarian_id in items:
        row = tk.Frame(parent_frame, bg="#ffffff")
        row.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(row, text=title, width=30, anchor="w", bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(row, text=category, width=15, anchor="w", bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(row, text=str(return_date), width=20, anchor="w", bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(row, text=place, width=20, anchor="w", bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Button(
            row,
            text="Повернути",
            command=lambda i=issue_id: return_item(i, reader_id),
            bg="red",
            fg="white",
        ).pack(side=tk.LEFT, padx=5)

# =============================== Універсальні функції для роботи з книгами та збірками ===============================
def _check_reader_exists(cursor, reader_id):
    cursor.execute("SELECT reader_id FROM Readers WHERE reader_id = %s", (reader_id,))
    return cursor.fetchone() is not None

def _available_items_count(cursor, item_type, item_id):
    if item_type == "book":
        query = """
            SELECT GREATEST(b.quantity - (
                SELECT COUNT(*) FROM IssuedBooks ib
                WHERE ib.book_id = %s AND ib.return_date >= CURDATE()
            ), 0) AS available_quantity
            FROM Books b
            WHERE b.book_id = %s
        """
    else:  # collection
        query = """
            SELECT GREATEST(col.quantity - (
                SELECT COUNT(*) FROM IssuedBooks ib
                WHERE ib.collection_id = %s AND ib.return_date >= CURDATE()
            ), 0) AS available_quantity
            FROM collections col
            WHERE col.collection_id = %s
        """
    
    cursor.execute(query, (item_id, item_id))
    res = cursor.fetchone()
    return (res[0] if res else 0)

def _check_already_issued(cursor, reader_id, item_type, item_id, reading_place, date_check=None):
    if item_type == "book":
        query = """
            SELECT 1 FROM IssuedBooks
            WHERE reader_id = %s AND book_id = %s
              AND reading_place = %s
        """
    else:  # collection
        query = """
            SELECT 1 FROM IssuedBooks
            WHERE reader_id = %s AND collection_id = %s
              AND reading_place = %s
        """
    
    params = [reader_id, item_id, reading_place]
    
    if date_check == "today":
        query += " AND issue_date = %s"
        params.append(date.today())
    elif date_check == "future":
        query += " AND return_date >= CURDATE()"
    
    cursor.execute(query, params)
    return cursor.fetchone() is not None

def _issue_item(reader_id, book_id, collection_id, return_date, reading_place, room_id, librarian_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if not _check_reader_exists(cursor, reader_id):
            conn.close()
            messagebox.showerror("Помилка", "Читач не знайдений в системі. Спробуйте вийти і увійти знову.")
            return False

        # Перевірка доступності
        item_type = "book" if book_id is not None else "collection"
        item_id = book_id if book_id is not None else collection_id
        
        if _available_items_count(cursor, item_type, item_id) <= 0:
            conn.close()
            messagebox.showinfo("Увага", "Немає доступних примірників.")
            return False

        # Перевірка чи вже видано
        date_check = "today" if reading_place == 'Тільки в читальній залі' else "future"
        if _check_already_issued(cursor, reader_id, item_type, item_id, reading_place, date_check):
            conn.close()
            messagebox.showinfo("Увага", "Ви вже маєте цей предмет.")
            return False

        # Видача
        cursor.execute(
            """
            INSERT INTO IssuedBooks
                (reader_id, book_id, collection_id, issue_date, return_date, reading_place, room_id, librarian_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                reader_id,
                book_id,
                collection_id,
                date.today(),
                return_date,
                reading_place,
                room_id,
                librarian_id,
            ),
        )

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        messagebox.showerror("Помилка", f"Не вдалося зареєструвати: {e}")
        return False

# =============================== Універсальні функції для читання ===============================
def read_in_room(item_type, item_id, reader_id, room_id, librarian_id):
    success = _issue_item(
        reader_id,
        item_id if item_type == "book" else None,
        item_id if item_type == "collection" else None,
        date.today(),
        'Тільки в читальній залі',
        room_id,
        librarian_id,
    )
    
    if success:
        item_name = "книгу" if item_type == "book" else "збірку"
        messagebox.showinfo("Успіх", f"{item_name.capitalize()} зареєстровано для читання в залі.")
        show_books_and_collections(reader_id)
        show_returned_items_inline(reader_id, return_books_frame)

def read_at_home(item_type, item_id, reader_id, room_id, librarian_id):
    def confirm_return_date():
        selected_date = return_calendar.get_date()
        today_ = date.today()
        max_return_date = today_ + timedelta(days=7)
        if selected_date < today_ or selected_date > max_return_date:
            messagebox.showerror("Помилка", "Дата повернення має бути в межах 7 днів від сьогодні.")
            return
        
        success = _issue_item(
            reader_id,
            item_id if item_type == "book" else None,
            item_id if item_type == "collection" else None,
            selected_date,
            'У читальній залі і вдома',
            room_id,
            librarian_id,
        )
        
        if success:
            item_name = "книгу" if item_type == "book" else "збірку"
            top.destroy()
            messagebox.showinfo("Успіх", f"{item_name.capitalize()} зареєстровано для читання вдома.")
            show_books_and_collections(reader_id)
            show_returned_items_inline(reader_id, return_books_frame)

    top = tk.Toplevel()
    top.title("Оберіть дату повернення")
    top.geometry("300x180")
    top.grab_set()

    tk.Label(top, text="Оберіть дату повернення:", font=("Arial", 11)).pack(pady=10)

    return_calendar = DateEntry(
        top,
        mindate=date.today(),
        maxdate=date.today() + timedelta(days=7),
        date_pattern='yyyy-mm-dd',
    )
    return_calendar.pack(pady=5)

    tk.Button(top, text="Підтвердити", command=confirm_return_date, bg="green", fg="white", font=("Arial", 10)).pack(pady=10)

# =============================== Список КНИГ + ЗБІРОК ===============================
def show_books_and_collections(reader_id, category=None, title_search=None, room_filter=None, get_ids=None):
    global available_books_frame
    for widget in available_books_frame.winfo_children():
        widget.destroy()

    # Шапка
    header = tk.Frame(available_books_frame, bg="#f5f5f5")
    header.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(header, text="Назва", font=("Arial", 12, "bold"), width=30, anchor="w", bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Label(header, text="Категорія", font=("Arial", 12, "bold"), width=15, anchor="w", bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Label(header, text="У читальному залі", font=("Arial", 12, "bold"), width=20, anchor="w", bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Label(header, text="Доступна кількість", font=("Arial", 12, "bold"), width=18, anchor="w", bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Label(header, text="", width=20, bg="#f5f5f5").pack(side=tk.LEFT)
    tk.Frame(available_books_frame, height=2, bg="gray").pack(fill=tk.X, padx=10, pady=2)

    conn = get_db_connection()
    cursor = conn.cursor()

    # -------------------- КНИГИ --------------------
    query_books = """
    SELECT 
        b.book_id,
        b.title,
        COALESCE(c.name, 'Без категорії') AS category_name,
        b.access_type,
        IF(EXISTS (SELECT 1 FROM Placements p WHERE p.book_id = b.book_id), 'Так', 'Ні') AS is_in_room,
        EXISTS (
            SELECT 1 FROM IssuedBooks ib
            WHERE ib.book_id = b.book_id
              AND ib.reader_id = %s
              AND ib.return_date >= CURDATE()
        ) AS is_issued_by_user,
        GREATEST(b.quantity - (
            SELECT COUNT(*) FROM IssuedBooks ib2
            WHERE ib2.book_id = b.book_id
              AND ib2.return_date >= CURDATE()
        ), 0) AS available_quantity
    FROM Books b
    LEFT JOIN Categories c ON b.category_id = c.category_id
    """
    conditions_b = []
    params_b = [reader_id]

    if room_filter:
        conditions_b.append("EXISTS (SELECT 1 FROM Placements p WHERE p.book_id = b.book_id AND p.room_id = %s)")
        params_b.append(room_filter)
    if category:
        conditions_b.append("c.name = %s")
        params_b.append(category)
    if title_search:
        conditions_b.append("b.title LIKE %s")
        params_b.append(f"%{title_search}%")

    if conditions_b:
        query_books += " WHERE " + " AND ".join(conditions_b)
    query_books += " ORDER BY is_issued_by_user ASC, b.title"

    cursor.execute(query_books, params_b)
    books = cursor.fetchall()

    # -------------------- ЗБІРКИ --------------------
    query_col = """
    SELECT
        col.collection_id,
        col.title,
        COALESCE(c2.name, 'Без категорії') AS category_name,
        col.access_type,
        IF(
            EXISTS (
                SELECT 1
                FROM collectionbooks cb
                JOIN Placements p ON p.book_id = cb.book_id
                WHERE cb.collection_id = col.collection_id
            ),
            'Так','Ні'
        ) AS is_in_room,
        EXISTS (
            SELECT 1 FROM IssuedBooks ib
            WHERE ib.collection_id = col.collection_id
              AND ib.reader_id = %s
              AND ib.return_date >= CURDATE()
        ) AS is_issued_by_user,
        GREATEST(col.quantity - (
            SELECT COUNT(*) FROM IssuedBooks ib2
            WHERE ib2.collection_id = col.collection_id
              AND ib2.return_date >= CURDATE()
        ), 0) AS available_quantity
    FROM collections col
    LEFT JOIN Categories c2 ON col.category_id = c2.category_id
    """
    conditions_c = []
    params_c = [reader_id]

    if room_filter:
        conditions_c.append(
            """
            EXISTS (
                SELECT 1
                FROM collectionbooks cb
                JOIN Placements p ON p.book_id = cb.book_id
                WHERE cb.collection_id = col.collection_id
                  AND p.room_id = %s
            )
            """
        )
        params_c.append(room_filter)
    if category:
        conditions_c.append("c2.name = %s")
        params_c.append(category)
    if title_search:
        conditions_c.append("col.title LIKE %s")
        params_c.append(f"%{title_search}%")

    if conditions_c:
        query_col += " WHERE " + " AND ".join(conditions_c)
    query_col += " ORDER BY is_issued_by_user ASC, col.title"

    cursor.execute(query_col, params_c)
    collections = cursor.fetchall()

    conn.close()

    # -------------------- Кнопки-команди --------------------
    def ensure_ids():
        if get_ids is None:
            messagebox.showwarning("Увага", "Немає джерела вибору залу/бібліотекаря.")
            return None, None, False
        room_id_, librarian_id_ = get_ids()
        if not room_id_:
            messagebox.showwarning("Увага", "Оберіть читальний зал.")
            return None, None, False
        if not librarian_id_:
            messagebox.showwarning("Увага", "Оберіть бібліотекаря.")
            return None, None, False
        return room_id_, librarian_id_, True

    def make_read_in_room_command(item_type, item_id):
        def command():
            room_id_, librarian_id_, ok = ensure_ids()
            if not ok:
                return
            read_in_room(item_type, item_id, reader_id, room_id_, librarian_id_)
        return command

    def make_read_at_home_command(item_type, item_id):
        def command():
            room_id_, librarian_id_, ok = ensure_ids()
            if not ok:
                return
            read_at_home(item_type, item_id, reader_id, room_id_, librarian_id_)
        return command

    # -------------------- Рендер КНИГ --------------------
    for book_id, title, category_name, access_type, is_in_room, is_issued_by_user, available_quantity in books:
        row = tk.Frame(available_books_frame, bg="#e6e6e6" if is_issued_by_user else "#ffffff")
        row.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(row, text=title, font=("Arial", 11), width=30, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)
        tk.Label(row, text=category_name, font=("Arial", 11), width=15, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)
        tk.Label(row, text=is_in_room, font=("Arial", 11), width=20, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)
        tk.Label(row, text=str(available_quantity), font=("Arial", 11), width=18, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)

        btns = tk.Frame(row, bg=row.cget("bg"))
        btns.pack(side=tk.LEFT)

        can_read_in_room = (is_in_room == 'Так') and (access_type in ['Тільки в читальній залі', 'У читальній залі і вдома']) and (available_quantity > 0)
        can_read_at_home = (access_type == 'У читальній залі і вдома') and (available_quantity > 0)

        in_room_btn = tk.Button(
            btns,
            text="В залі",
            command=make_read_in_room_command("book", book_id),
            bg="orange",
            fg="white",
            padx=6,
            pady=2,
            state=tk.NORMAL if can_read_in_room else tk.DISABLED,
        )
        in_room_btn.pack(side=tk.LEFT, padx=5)

        home_btn = tk.Button(
            btns,
            text="Вдома",
            command=make_read_at_home_command("book", book_id),
            bg="lime green",
            fg="white",
            padx=6,
            pady=2,
            state=tk.NORMAL if can_read_at_home else tk.DISABLED,
        )
        home_btn.pack(side=tk.LEFT)

    # Розділювач
    sep = tk.Frame(available_books_frame, height=2, bg="#c9c9c9")
    sep.pack(fill=tk.X, padx=10, pady=8)

    # -------------------- Рендер ЗБІРОК --------------------
    for collection_id, title, category_name, access_type, is_in_room, is_issued_by_user, available_quantity in collections:
        row = tk.Frame(available_books_frame, bg="#dfefff" if is_issued_by_user else "#f4f9ff")
        row.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(row, text=f"[Збірка] {title}", font=("Arial", 11), width=30, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)
        tk.Label(row, text=category_name, font=("Arial", 11), width=15, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)
        tk.Label(row, text=is_in_room, font=("Arial", 11), width=20, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)
        tk.Label(row, text=str(available_quantity), font=("Arial", 11), width=18, anchor="w", bg=row.cget("bg")).pack(side=tk.LEFT)

        btns = tk.Frame(row, bg=row.cget("bg"))
        btns.pack(side=tk.LEFT)

        can_read_in_room = (is_in_room == 'Так') and (access_type in ['Тільки в читальній залі', 'У читальній залі і вдома']) and (available_quantity > 0)
        can_read_at_home = (access_type == 'У читальній залі і вдома') and (available_quantity > 0)

        in_room_btn = tk.Button(
            btns,
            text="В залі",
            command=make_read_in_room_command("collection", collection_id),
            bg="orange",
            fg="white",
            padx=6,
            pady=2,
            state=tk.NORMAL if can_read_in_room else tk.DISABLED,
        )
        in_room_btn.pack(side=tk.LEFT, padx=5)

        home_btn = tk.Button(
            btns,
            text="Вдома",
            command=make_read_at_home_command("collection", collection_id),
            bg="lime green",
            fg="white",
            padx=6,
            pady=2,
            state=tk.NORMAL if can_read_at_home else tk.DISABLED,
        )
        home_btn.pack(side=tk.LEFT)

def show_reader_window(reader_id):
    global available_books_frame, return_books_frame
    root = tk.Tk()
    root.title("Бібліотечна система")
    root.geometry("1100x780")
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

    # Встановлення значень за замовчуванням
    if rooms:
        room_var.set(rooms[0][1])  # Встановлюємо перший зал за замовчуванням
    else:
        room_var.set('')  # Якщо залів немає
        messagebox.showwarning("Увага", "Немає доступних читальних залів.")

    if all_librarians:
        librarian_var.set(all_librarians[0][1])  # Встановлюємо першого бібліотекаря
    else:
        librarian_var.set('')
        messagebox.showwarning("Увага", "Немає доступних бібліотекарів.")

    # Топ-бар фільтрів
    top = tk.Frame(root, bg="#f0f0f0")
    top.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(top, text="Читальний зал:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    room_menu = ttk.Combobox(top, textvariable=room_var, state="readonly", width=22)
    room_menu['values'] = [''] + [name for _, name in rooms]
    room_menu.pack(side=tk.LEFT, padx=5)

    tk.Label(top, text="Бібліотекар:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    librarian_menu = ttk.Combobox(top, textvariable=librarian_var, state="readonly", width=22)
    librarian_menu['values'] = [''] + [name for _, name in all_librarians]
    librarian_menu.pack(side=tk.LEFT, padx=5)

    tk.Label(top, text="Категорія:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    category_menu = ttk.Combobox(top, textvariable=category_var, state="readonly", width=20)
    category_menu['values'] = (
        '',
        'книги', 'журнали', 'газети', 'збірники статей',
        'збірники віршів', 'дисертації', 'реферати', 'збірники доповідей і тез доповідей'
    )
    category_menu.current(0)
    category_menu.pack(side=tk.LEFT, padx=5)

    tk.Label(top, text="Назва:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    search_entry = tk.Entry(top, textvariable=search_var, width=25)
    search_entry.pack(side=tk.LEFT, padx=5)

    # Фрейми під таблиці
    books_frame = tk.Frame(root, bg="#f0f0f0")
    books_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    available_books_frame = books_frame

    return_books_frame = tk.Frame(root, bg="#f0f0f0")
    return_books_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    # Оновлення списку бібліотекарів при зміні залу
    def update_librarians(*args):
        selected_room_name = room_var.get()
        if selected_room_name:
            room_id = room_ids.get(selected_room_name)
            librarians_in_room = fetch_librarians_by_room(room_id)
            librarian_menu['values'] = [''] + [name for _, name in librarians_in_room]
            # Встановлюємо першого бібліотекаря для вибраного залу
            if librarians_in_room:
                librarian_var.set(librarians_in_room[0][1])
            else:
                librarian_var.set('')
                messagebox.showwarning("Увага", "Немає бібліотекарів для цього залу.")
        else:
            librarian_menu['values'] = [''] + [name for _, name in all_librarians]
            librarian_var.set(all_librarians[0][1] if all_librarians else '')

    room_var.trace_add('write', update_librarians)

    # Джерело вибраних ID (зал, бібліотекар)
    def get_selected_ids():
        r = room_ids.get(room_var.get()) if room_var.get() else (rooms[0][0] if rooms else None)
        l = None
        if librarian_var.get():
            l = librarian_ids.get(librarian_var.get())
            if l is None:
                selected_room_id = room_ids.get(room_var.get()) if room_var.get() else (rooms[0][0] if rooms else None)
                if selected_room_id:
                    for lid, name in fetch_librarians_by_room(selected_room_id):
                        if name == librarian_var.get():
                            l = lid
                            break
        else:
            # Якщо бібліотекар не вибраний, беремо першого доступного для залу
            selected_room_id = r or (rooms[0][0] if rooms else None)
            if selected_room_id:
                librarians_in_room = fetch_librarians_by_room(selected_room_id)
                l = librarians_in_room[0][0] if librarians_in_room else None
        return r, l

    # Функція оновлення списків
    def refresh_items(*_):
        room_id = room_ids.get(room_var.get()) if room_var.get() else (rooms[0][0] if rooms else None)
        cat = category_var.get() if category_var.get() else None
        title = search_var.get().strip() if search_var.get().strip() else None
        show_books_and_collections(
            reader_id,
            room_filter=room_id,
            category=cat,
            title_search=title,
            get_ids=get_selected_ids,
        )

    # Автооновлення при зміні залу/категорії, кнопка пошуку — для назви
    room_var.trace_add('write', refresh_items)
    category_var.trace_add('write', refresh_items)
    tk.Button(top, text="Пошук", command=refresh_items).pack(side=tk.LEFT, padx=5)

    # Початковий рендер
    refresh_items()
    show_returned_items_inline(reader_id, return_books_frame)

    root.mainloop()