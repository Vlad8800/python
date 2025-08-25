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

# ========== НОВА ФУНКЦІЯ: НАЙПОПУЛЯРНІШІ КНИГИ ==========
def show_popular_books_window():
    """Показує вікно з найпопулярнішими книгами"""
    popular_window = tk.Toplevel()
    popular_window.title("Найпопулярніші книги бібліотеки")
    popular_window.geometry("900x700")
    
    # Заголовок
    title_label = tk.Label(popular_window, text="Найпопулярніші книги бібліотеки", 
                          font=("Arial", 18, "bold"), fg="darkblue")
    title_label.pack(pady=20)
    
    # Фрейм для топ-3 книг
    top_frame = ttk.LabelFrame(popular_window, text="ТОП-3 Найпопулярніші твори", padding=20)
    top_frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    # Створення фрейму для карток
    top_books_frame = tk.Frame(top_frame)
    top_books_frame.pack(fill="both", expand=True)
    
    # Фрейм для всіх книг з статистикою
    all_books_frame = ttk.LabelFrame(popular_window, text="Всі книги з статистикою видач", padding=10)
    all_books_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Створення таблиці для всіх книг
    columns = ("Позиція", "Назва", "Автор", "Категорія", "Кількість видач", "В наявності")
    all_books_tree = ttk.Treeview(all_books_frame, columns=columns, show="headings", height=10)
    
    for col in columns:
        all_books_tree.heading(col, text=col)
        all_books_tree.column(col, width=130)
    
    scrollbar = ttk.Scrollbar(all_books_frame, orient="vertical", command=all_books_tree.yview)
    all_books_tree.configure(yscrollcommand=scrollbar.set)
    
    all_books_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def load_popular_books():
        """Завантаження найпопулярніших книг"""
        # Очищення попередніх даних в топ-3
        for widget in top_books_frame.winfo_children():
            widget.destroy()
        
        # Очищення таблиці всіх книг
        for item in all_books_tree.get_children():
            all_books_tree.delete(item)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Перевіряємо чи існує стовпець borrowed_count
            cursor.execute("SHOW COLUMNS FROM Books LIKE 'borrowed_count'")
            column_exists = cursor.fetchone()
            
            if not column_exists:
                # Додаємо стовпець, якщо його немає
                cursor.execute("ALTER TABLE Books ADD COLUMN borrowed_count INT DEFAULT 0")
                conn.commit()
            
            # SQL запит для отримання топ-3 найпопулярніших книг
            cursor.execute("""
                SELECT b.title, CONCAT(a.name, ' ', a.surname) as author, c.name as category, 
                       b.year, COALESCE(b.borrowed_count, 0) as borrowed_count, b.quantity
                FROM Books b
                JOIN Authors a ON b.author_id = a.author_id
                LEFT JOIN Categories c ON b.category_id = c.category_id
                ORDER BY COALESCE(b.borrowed_count, 0) DESC
                LIMIT 3
            """)
            
            top_books = cursor.fetchall()
            
            # Створення карток для топ-3
            for i, book in enumerate(top_books):
                create_book_card(top_books_frame, book, i + 1)
            
            # SQL запит для отримання всіх книг з статистикою
            cursor.execute("""
                SELECT b.title, CONCAT(a.name, ' ', a.surname) as author, c.name as category, 
                       COALESCE(b.borrowed_count, 0) as borrowed_count, b.quantity
                FROM Books b
                JOIN Authors a ON b.author_id = a.author_id
                LEFT JOIN Categories c ON b.category_id = c.category_id
                ORDER BY COALESCE(b.borrowed_count, 0) DESC
            """)
            
            all_books = cursor.fetchall()
            
            # Заповнення таблиці всіх книг
            for i, book in enumerate(all_books, 1):
                title, author, category, borrowed_count, quantity = book
                all_books_tree.insert("", "end", values=(i, title, author, category or "Не вказана", borrowed_count, quantity))
        
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при завантаженні даних:\n{e}")
        finally:
            conn.close()
    
    def create_book_card(parent_frame, book, position):
        """Створення картки книги"""
        title, author, category, year, borrowed_count, quantity = book
        
        # Визначення кольору залежно від позиції
        colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}  # Золото, Срібло, Бронза
        bg_color = colors.get(position, "#f0f0f0")
        
        # Фрейм для картки
        card_frame = tk.Frame(parent_frame, bg=bg_color, relief="raised", bd=2)
        card_frame.pack(fill="x", pady=10, padx=20)
        
        # Позиція та медаль
        position_label = tk.Label(card_frame, text=f"#{position}", 
                                 font=("Arial", 24, "bold"), bg=bg_color)
        position_label.pack(side="left", padx=20, pady=10)
        
        # Інформація про книгу
        info_frame = tk.Frame(card_frame, bg=bg_color)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Назва книги
        title_label = tk.Label(info_frame, text=title, 
                              font=("Arial", 16, "bold"), bg=bg_color)
        title_label.pack(anchor="w")
        
        # Автор
        author_label = tk.Label(info_frame, text=f"Автор: {author}", 
                               font=("Arial", 12), bg=bg_color)
        author_label.pack(anchor="w")
        
        # Категорія та рік
        if category:
            category_label = tk.Label(info_frame, text=f"Категорія: {category}", 
                                     font=("Arial", 10), bg=bg_color, fg="gray")
            category_label.pack(anchor="w")
        
        if year:
            year_label = tk.Label(info_frame, text=f"Рік: {year}", 
                                 font=("Arial", 10), bg=bg_color, fg="gray")
            year_label.pack(anchor="w")
        
        # Статистика видач
        stats_frame = tk.Frame(card_frame, bg=bg_color)
        stats_frame.pack(side="right", padx=20, pady=10)
        
        borrowed_label = tk.Label(stats_frame, text=f"Видач: {borrowed_count}", 
                                 font=("Arial", 14, "bold"), bg=bg_color, fg="darkred")
        borrowed_label.pack()
        
        quantity_label = tk.Label(stats_frame, text=f"В наявності: {quantity}", 
                                 font=("Arial", 10), bg=bg_color, fg="darkgreen")
        quantity_label.pack()
    
    def show_add_borrow_window():
        """Показ вікна додавання видачі"""
        add_window = tk.Toplevel(popular_window)
        add_window.title("Додати видачу книги")
        add_window.geometry("500x250")
        
        # Список книг
        tk.Label(add_window, text="Виберіть книгу:", font=("Arial", 12)).pack(pady=10)
        
        # Отримання списку книг
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.book_id, b.title, CONCAT(a.name, ' ', a.surname) as author
            FROM Books b 
            JOIN Authors a ON b.author_id = a.author_id
            ORDER BY b.title
        ''')
        books = cursor.fetchall()
        conn.close()
        
        book_var = tk.StringVar()
        book_combo = ttk.Combobox(add_window, textvariable=book_var, width=60)
        book_combo['values'] = [f"{book[1]} - {book[2]}" for book in books]
        book_combo.pack(pady=10)
        
        def add_borrow():
            if not book_var.get():
                messagebox.showwarning("Попередження", "Виберіть книгу!")
                return
            
            selected_index = book_combo.current()
            if selected_index >= 0:
                book_id = books[selected_index][0]
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                try:
                    # Перевіряємо чи існує стовпець
                    cursor.execute("SHOW COLUMNS FROM Books LIKE 'borrowed_count'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE Books ADD COLUMN borrowed_count INT DEFAULT 0")
                    
                    # Збільшуємо лічильник видач
                    cursor.execute("UPDATE Books SET borrowed_count = COALESCE(borrowed_count, 0) + 1 WHERE book_id = %s", 
                                   (book_id,))
                    conn.commit()
                    
                    messagebox.showinfo("Успішно", "Видачу додано!")
                    add_window.destroy()
                    load_popular_books()
                except Exception as e:
                    messagebox.showerror("Помилка", f"Помилка при додаванні видачі:\n{e}")
                finally:
                    conn.close()
        
        tk.Button(add_window, text="Додати видачу", command=add_borrow,
                 bg="lightgreen", font=("Arial", 12)).pack(pady=20)
    
    # Фрейм для кнопок управління
    control_frame = tk.Frame(popular_window)
    control_frame.pack(pady=10)
    
    # Кнопки
    tk.Button(control_frame, text="Оновити дані", command=load_popular_books,
              bg="lightblue", font=("Arial", 12)).pack(side="left", padx=10)
    
    tk.Button(control_frame, text="Додати видачу", command=show_add_borrow_window,
              bg="lightgreen", font=("Arial", 12)).pack(side="left", padx=10)
    
    # Завантаження даних при відкритті вікна
    load_popular_books()

# ========== ІСНУЮЧІ ФУНКЦІ Ї (БЕЗ ЗМІН) ==========

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

def get_readers_by_criteria(university=None, faculty=None, reader_type=None, organization=None):
    """Отримує список читачів за вказаними критеріями"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT reader_id, user_name, address, reader_type, university, faculty, organization
        FROM Readers
        WHERE 1=1
    """
    params = []
    
    if university:
        query += " AND university = %s"
        params.append(university)
    
    if faculty:
        query += " AND faculty = %s"
        params.append(faculty)
    
    if reader_type:
        query += " AND reader_type = %s"
        params.append(reader_type)
    
    if organization:
        query += " AND organization = %s"
        params.append(organization)
    
    cursor.execute(query, params)
    readers = cursor.fetchall()
    conn.close()
    
    return readers
def fetch_all_overdue_books():
    """
    АДМІН: Отримує список всіх просрочених книг у системі
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ib.issue_id, r.reader_id, r.user_name as reader_name,
               b.book_id, b.title, c.name as category, 
               ib.issue_date, ib.return_date, ib.reading_place,
               DATEDIFF(CURDATE(), ib.return_date) as days_overdue,
               rr.name as room_name, l.name as librarian_name
        FROM IssuedBooks ib
        JOIN Readers r ON ib.reader_id = r.reader_id
        JOIN Books b ON b.book_id = ib.book_id
        LEFT JOIN Categories c ON b.category_id = c.category_id
        LEFT JOIN ReadingRooms rr ON ib.room_id = rr.room_id
        LEFT JOIN Librarians l ON ib.librarian_id = l.librarian_id
        WHERE ib.return_date < CURDATE()
        ORDER BY DATEDIFF(CURDATE(), ib.return_date) DESC, ib.return_date ASC
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def fetch_reader_books_by_period_admin(reader_id, start_date, end_date):
    """
    АДМІН: Отримує список видань читача за період з додатковою інформацією
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ib.issue_id, ib.book_id, b.title, c.name as category, 
               ib.issue_date, ib.return_date, ib.reading_place,
               rr.name as room_name, l.name as librarian_name,
               r.user_name as reader_name,
               CASE 
                   WHEN ib.return_date < CURDATE() THEN 'Просрочена'
                   WHEN ib.return_date >= CURDATE() THEN 'Активна'
                   ELSE 'Повернена'
               END as status,
               CASE 
                   WHEN ib.return_date < CURDATE() THEN DATEDIFF(CURDATE(), ib.return_date)
                   ELSE 0
               END as days_overdue
        FROM IssuedBooks ib
        JOIN Books b ON b.book_id = ib.book_id
        JOIN Readers r ON ib.reader_id = r.reader_id
        LEFT JOIN Categories c ON b.category_id = c.category_id
        LEFT JOIN ReadingRooms rr ON ib.room_id = rr.room_id
        LEFT JOIN Librarians l ON ib.librarian_id = l.librarian_id
        WHERE ib.reader_id = %s 
        AND ib.issue_date BETWEEN %s AND %s
        ORDER BY ib.issue_date DESC
    """, (reader_id, start_date, end_date))
    result = cursor.fetchall()
    conn.close()
    return result

def fetch_all_readers_with_books():
    """
    АДМІН: Отримує список всіх читачів з інформацією про їх активні книги
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.reader_id, r.name, r.phone, r.email,
               COUNT(ib.issue_id) as total_books,
               COUNT(CASE WHEN ib.return_date < CURDATE() THEN 1 END) as overdue_books,
               COUNT(CASE WHEN ib.return_date >= CURDATE() THEN 1 END) as active_books,
               MIN(ib.return_date) as earliest_return_date,
               MAX(CASE WHEN ib.return_date < CURDATE() THEN DATEDIFF(CURDATE(), ib.return_date) END) as max_overdue_days
        FROM Readers r
        LEFT JOIN IssuedBooks ib ON r.reader_id = ib.reader_id
        GROUP BY r.reader_id, r.name, r.phone, r.email
        HAVING COUNT(ib.issue_id) > 0
        ORDER BY overdue_books DESC, total_books DESC
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def fetch_library_statistics():
    """
    АДМІН: Отримує загальну статистику бібліотеки
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Загальна статистика
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM Books) as total_books,
            (SELECT COUNT(*) FROM Readers) as total_readers,
            (SELECT COUNT(*) FROM IssuedBooks) as total_issued,
            (SELECT COUNT(*) FROM IssuedBooks WHERE return_date >= CURDATE()) as active_issued,
            (SELECT COUNT(*) FROM IssuedBooks WHERE return_date < CURDATE()) as overdue_issued,
            (SELECT COUNT(DISTINCT reader_id) FROM IssuedBooks WHERE return_date < CURDATE()) as readers_with_overdue
    """)
    stats = cursor.fetchone()
    
    # Топ популярних книг
    cursor.execute("""
        SELECT b.title, c.name as category, b.borrowed_count, 
               COUNT(ib.issue_id) as current_issued
        FROM Books b
        LEFT JOIN Categories c ON b.category_id = c.category_id
        LEFT JOIN IssuedBooks ib ON b.book_id = ib.book_id AND ib.return_date >= CURDATE()
        WHERE b.borrowed_count > 0
        GROUP BY b.book_id, b.title, c.name, b.borrowed_count
        ORDER BY b.borrowed_count DESC
        LIMIT 10
    """)
    popular_books = cursor.fetchall()
    
    conn.close()
    return stats, popular_books
def fetch_user_issued_books(reader_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ib.issue_id, ib.book_id, b.title, c.name as category, 
               ib.issue_date, ib.return_date, ib.reading_place, ib.room_id, ib.librarian_id,
               CASE WHEN ib.return_date < CURDATE() THEN DATEDIFF(CURDATE(), ib.return_date) ELSE 0 END as days_overdue
        FROM IssuedBooks ib
        JOIN Books b ON b.book_id = ib.book_id
        LEFT JOIN Categories c ON b.category_id = c.category_id
        WHERE ib.reader_id = %s AND (ib.return_date >= CURDATE() OR ib.return_date < CURDATE())
        ORDER BY ib.issue_date DESC
    """, (reader_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def show_admin_overdue_books():
    """
    АДМІН: Вікно для перегляду всіх просрочених книг в системі
    """
    overdue_window = tk.Toplevel()
    overdue_window.title("АДМІН: Просрочені книги в системі")
    overdue_window.geometry("1400x700")
    overdue_window.grab_set()
    
    # Заголовок з статистикой
    header_frame = tk.Frame(overdue_window)
    header_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(header_frame, text="📚 СПИСОК ВСІХ ПРОСРОЧЕНИХ КНИГ", 
            font=("Arial", 16, "bold"), fg="darkred").pack()
    
    # Кнопка оновлення
    tk.Button(header_frame, text="🔄 Оновити дані", 
             command=lambda: refresh_overdue_data(),
             bg="blue", fg="white", font=("Arial", 10)).pack(pady=5)
    
    # Створюємо фрейм з прокруткою
    canvas = tk.Canvas(overdue_window, bg="white")
    scrollbar = tk.Scrollbar(overdue_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    def refresh_overdue_data():
        # Очищаємо попередні дані
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        # Отримуємо нові дані
        overdue_books = fetch_all_overdue_books()
        
        if not overdue_books:
            tk.Label(scrollable_frame, text="🎉 Немає просрочених книг!", 
                    font=("Arial", 16, "bold"), fg="green", bg="white").pack(pady=50)
            return
        
        # Статистика
        stats_frame = tk.Frame(scrollable_frame, bg="#f0f8ff", relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        total_overdue = len(overdue_books)
        critical_overdue = len([book for book in overdue_books if book[9] > 30])  # days_overdue > 30
        
        tk.Label(stats_frame, text=f"📊 Загалом просрочених: {total_overdue} | Критично просрочених (>30 днів): {critical_overdue}", 
                font=("Arial", 12, "bold"), bg="#f0f8ff").pack(pady=5)
        
        # Шапка таблиці
        header = tk.Frame(scrollable_frame, bg="#2c3e50")
        header.pack(fill=tk.X, padx=10, pady=(10, 2))
        
        tk.Label(header, text="👤 Читач", font=("Arial", 10, "bold"), width=18, fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        tk.Label(header, text="📖 Книга", font=("Arial", 10, "bold"), width=35, fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        tk.Label(header, text="📅 Взято", font=("Arial", 10, "bold"), width=12, fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        tk.Label(header, text="⏰ Повернути до", font=("Arial", 10, "bold"), width=15, fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        tk.Label(header, text="⚠️ Просрочено", font=("Arial", 10, "bold"), width=12, fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        tk.Label(header, text="🏢 Місце", font=("Arial", 10, "bold"), width=20, fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        tk.Label(header, text="👨‍💼 Дії", font=("Arial", 10, "bold"), width=15, fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        
        # Дані
        for issue_id, reader_id, reader_name, book_id, title, category, issue_date, return_date, place, days_overdue, room_name, librarian_name in overdue_books:
            # Колір залежно від критичності
            if days_overdue > 30:
                row_color = "#ffcccc"  # Критично просрочені - яскраво-червоний
                text_color = "darkred"
                status_emoji = "🔴"
            elif days_overdue > 14:
                row_color = "#ffe6cc"  # Дуже просрочені - помаранчевий
                text_color = "darkorange"
                status_emoji = "🟠"
            elif days_overdue > 7:
                row_color = "#fff2cc"  # Просрочені - жовтий
                text_color = "orange"
                status_emoji = "🟡"
            else:
                row_color = "#ffe6e6"  # Легко просрочені - світло-червоний
                text_color = "red"
                status_emoji = "🟢"
                
            row = tk.Frame(scrollable_frame, bg=row_color, relief=tk.RIDGE, bd=1)
            row.pack(fill=tk.X, padx=10, pady=1)
            
            tk.Label(row, text=reader_name[:20], width=18, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
            tk.Label(row, text=title[:40], width=35, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
            tk.Label(row, text=str(issue_date), width=12, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
            tk.Label(row, text=str(return_date), width=15, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
            tk.Label(row, text=f"{status_emoji} {days_overdue} дн.", width=12, anchor="w", bg=row_color, 
                    font=("Arial", 9, "bold"), fg=text_color).pack(side=tk.LEFT)
            tk.Label(row, text=place[:18], width=20, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
            
            # Кнопки дій
            actions_frame = tk.Frame(row, bg=row_color)
            actions_frame.pack(side=tk.LEFT)
            
            tk.Button(actions_frame, text="👁️ Детально", 
                     command=lambda rid=reader_id, rname=reader_name: show_reader_details(rid, rname),
                     bg="blue", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
            
            tk.Button(actions_frame, text="📧 Повідомити", 
                     command=lambda rid=reader_id, rname=reader_name, days=days_overdue: notify_reader(rid, rname, days),
                     bg="orange", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
    
    def show_reader_details(reader_id, reader_name):
        """Показує детальну інформацію про читача"""
        details_window = tk.Toplevel()
        details_window.title(f"Детали читача: {reader_name}")
        details_window.geometry("800x500")
        
        tk.Label(details_window, text=f"📋 Детальна інформація про читача: {reader_name}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Тут можна додати детальну інформацію про всі книги читача
        books = fetch_user_issued_books(reader_id)  # Всі активні книги
        
        tk.Label(details_window, text=f"Всього активних книг: {len(books)}", 
                font=("Arial", 12)).pack(pady=5)
        
        # Створюємо таблицю з книгами
        books_frame = tk.Frame(details_window)
        books_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for issue_id, book_id, title, category, issue_date, return_date, place, room_id, librarian_id, days_overdue in books:
            status = "Просрочена" if days_overdue > 0 else "Активна"
            color = "#ffcccc" if days_overdue > 0 else "#ccffcc"
            
            book_row = tk.Frame(books_frame, bg=color, relief=tk.RIDGE, bd=1)
            book_row.pack(fill=tk.X, pady=2)
            
            tk.Label(book_row, text=f"📖 {title} | ⏰ {return_date} | Status: {status}", 
                    bg=color, font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
    
    def notify_reader(reader_id, reader_name, days_overdue):
        """Імітація відправки повідомлення читачу"""
        messagebox.showinfo("Повідомлення відправлено", 
                           f"📧 Повідомлення про просрочення ({days_overdue} днів) відправлено читачу {reader_name}")
    
    # Запускаємо початкове завантаження даних
    refresh_overdue_data()
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Кнопка закриття
    tk.Button(overdue_window, text="❌ Закрити", command=overdue_window.destroy,
             bg="gray", fg="white", font=("Arial", 12)).pack(pady=10)

def show_admin_reader_search():
    """
    АДМІН: Вікно пошуку книг конкретного читача за період
    """
    search_window = tk.Toplevel()
    search_window.title("АДМІН: Пошук книг читача")
    search_window.geometry("500x400")
    search_window.grab_set()
    
    tk.Label(search_window, text="🔍 ПОШУК КНИГ ЧИТАЧА ЗА ПЕРІОД", 
            font=("Arial", 16, "bold"), fg="darkblue").pack(pady=15)
    
    # Поле введення ID читача
    tk.Label(search_window, text="🆔 ID читача:", font=("Arial", 12)).pack(pady=5)
    reader_id_entry = tk.Entry(search_window, width=20, font=("Arial", 12))
    reader_id_entry.pack(pady=5)
    
    # Або пошук за ім'ям
    tk.Label(search_window, text="АБО 👤 Ім'я читача:", font=("Arial", 12)).pack(pady=(20, 5))
    reader_name_entry = tk.Entry(search_window, width=30, font=("Arial", 12))
    reader_name_entry.pack(pady=5)
    
    tk.Button(search_window, text="🔍 Знайти читача", 
             command=lambda: search_reader_by_name(),
             bg="green", fg="white", font=("Arial", 10)).pack(pady=5)
    
    # Період пошуку
    period_frame = tk.Frame(search_window)
    period_frame.pack(pady=20)
    
    tk.Label(period_frame, text="📅 Від:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    start_date_entry = DateEntry(period_frame, date_pattern='yyyy-mm-dd', font=("Arial", 11))
    start_date_entry.pack(side=tk.LEFT, padx=5)
    
    tk.Label(period_frame, text="📅 До:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    end_date_entry = DateEntry(period_frame, date_pattern='yyyy-mm-dd', font=("Arial", 11))
    end_date_entry.pack(side=tk.LEFT, padx=5)
    
    def search_reader_by_name():
        """Пошук читача за іменем"""
        name = reader_name_entry.get().strip()
        if not name:
            messagebox.showerror("Помилка", "Введіть ім'я читача")
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT reader_id, user_name FROM Readers WHERE user_name LIKE %s", (f"%{name}%",))
        readers = cursor.fetchall()
        conn.close()
        
        if not readers:
            messagebox.showinfo("Не знайдено", f"Читач з ім'ям '{name}' не знайдений")
            return
        elif len(readers) == 1:
            reader_id_entry.delete(0, tk.END)
            reader_id_entry.insert(0, str(readers[0][0]))
            messagebox.showinfo("Знайдено", f"Знайдено читача: {readers[0][1]} (ID: {readers[0][0]})")
        else:
            # Показуємо список для вибору
            show_readers_selection(readers)
    
    def show_readers_selection(readers):
        """Показує список читачів для вибору"""
        selection_window = tk.Toplevel()
        selection_window.title("Оберіть читача")
        selection_window.geometry("400x300")
        selection_window.grab_set()
        
        tk.Label(selection_window, text="Знайдено кілька читачів:", font=("Arial", 12, "bold")).pack(pady=10)
        
        for reader_id, name in readers:
            reader_frame = tk.Frame(selection_window, relief=tk.RIDGE, bd=1)
            reader_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(reader_frame, text=f"ID: {reader_id} | {name}", 
                    font=("Arial", 10)).pack(side=tk.LEFT, padx=10, pady=5)
            
            tk.Button(reader_frame, text="Вибрати", 
                     command=lambda rid=reader_id: select_reader(rid, selection_window),
                     bg="blue", fg="white").pack(side=tk.RIGHT, padx=10, pady=5)
    
    def select_reader(reader_id, window):
        reader_id_entry.delete(0, tk.END)
        reader_id_entry.insert(0, str(reader_id))
        window.destroy()
        messagebox.showinfo("Вибрано", f"Вибрано читача ID: {reader_id}")
    
    def search_books():
        reader_id = reader_id_entry.get().strip()
        if not reader_id:
            messagebox.showerror("Помилка", "Введіть ID читача")
            return
            
        try:
            reader_id = int(reader_id)
        except ValueError:
            messagebox.showerror("Помилка", "ID читача має бути числом")
            return
        
        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()
        
        if start_date > end_date:
            messagebox.showerror("Помилка", "Початкова дата не може бути пізніше кінцевої")
            return
        
        # Отримуємо дані
        books = fetch_reader_books_by_period_admin(reader_id, start_date, end_date)
        
        # Показуємо результати
        show_admin_search_results(reader_id, start_date, end_date, books)
    
    tk.Button(search_window, text="📊 ЗНАЙТИ КНИГИ", command=search_books,
             bg="darkblue", fg="white", font=("Arial", 14, "bold")).pack(pady=30)

def show_admin_search_results(reader_id, start_date, end_date, books):
    """
    АДМІН: Показує результати пошуку книг читача
    """
    results_window = tk.Toplevel()
    results_window.title(f"АДМІН: Книги читача {reader_id}")
    results_window.geometry("1200x700")
    
    # Заголовок з інформацією про читача
    if books:
        reader_info = f"👤 {books[0][9]}"
    else:
        reader_info = f"👤 Читач ID: {reader_id}"
    
    header_frame = tk.Frame(results_window, bg="#f0f8ff")
    header_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(header_frame, text=f"📚 КНИГИ ЧИТАЧА за період {start_date} - {end_date}", 
            font=("Arial", 16, "bold"), bg="#f0f8ff", fg="darkblue").pack()
    tk.Label(header_frame, text=reader_info, 
            font=("Arial", 12), bg="#f0f8ff").pack()
    
    if not books:
        tk.Label(results_window, text="📭 За вказаний період книги не видавались", 
                font=("Arial", 16), fg="gray").pack(pady=100)
        return
    
    # Статистика
    total_books = len(books)
    active_books = len([b for b in books if b[10] == "Активна"])
    overdue_books = len([b for b in books if b[10] == "Просрочена"])
    
    stats_frame = tk.Frame(results_window, bg="#e8f4fd", relief=tk.RAISED, bd=2)
    stats_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(stats_frame, text=f"📊 Загалом: {total_books} | 🟢 Активних: {active_books} | 🔴 Просрочених: {overdue_books}", 
            font=("Arial", 12, "bold"), bg="#e8f4fd").pack(pady=5)
    
    # Створюємо таблицю з прокруткою
    canvas = tk.Canvas(results_window)
    scrollbar = tk.Scrollbar(results_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Шапка таблиці
    header = tk.Frame(scrollable_frame, bg="#34495e")
    header.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(header, text="📖 Книга", font=("Arial", 11, "bold"), width=35, fg="white", bg="#34495e").pack(side=tk.LEFT)
    tk.Label(header, text="📂 Категорія", font=("Arial", 11, "bold"), width=15, fg="white", bg="#34495e").pack(side=tk.LEFT)
    tk.Label(header, text="📅 Взято", font=("Arial", 11, "bold"), width=12, fg="white", bg="#34495e").pack(side=tk.LEFT)
    tk.Label(header, text="⏰ Повернути", font=("Arial", 11, "bold"), width=12, fg="white", bg="#34495e").pack(side=tk.LEFT)
    tk.Label(header, text="🏢 Місце", font=("Arial", 11, "bold"), width=18, fg="white", bg="#34495e").pack(side=tk.LEFT)
    tk.Label(header, text="📍 Зал", font=("Arial", 11, "bold"), width=15, fg="white", bg="#34495e").pack(side=tk.LEFT)
    tk.Label(header, text="👨‍💼 Бібліотекар", font=("Arial", 11, "bold"), width=15, fg="white", bg="#34495e").pack(side=tk.LEFT)
    tk.Label(header, text="📊 Статус", font=("Arial", 11, "bold"), width=15, fg="white", bg="#34495e").pack(side=tk.LEFT)
    
    # Дані
    for issue_id, book_id, title, category, issue_date, return_date, place, room_name, librarian_name, reader_name, status, days_overdue in books:
        # Колір строки залежно від статусу
        if status == "Просрочена":
            row_color = "#ffebee" if days_overdue <= 7 else "#ffcccb"
            status_color = "red"
            status_emoji = "🔴"
        elif status == "Активна":
            row_color = "#e8f5e8"
            status_color = "green"
            status_emoji = "🟢"
        else:
            row_color = "#f5f5f5"
            status_color = "gray"
            status_emoji = "⚪"
        
        row = tk.Frame(scrollable_frame, bg=row_color, relief=tk.RIDGE, bd=1)
        row.pack(fill=tk.X, padx=10, pady=1)
        
        tk.Label(row, text=title[:40], width=35, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Label(row, text=category or "—", width=15, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Label(row, text=str(issue_date), width=12, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Label(row, text=str(return_date), width=12, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Label(row, text=place[:16], width=18, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Label(row, text=room_name or "—", width=15, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Label(row, text=librarian_name or "—", width=15, anchor="w", bg=row_color, font=("Arial", 9)).pack(side=tk.LEFT)
def show_readers_list_window():
    """Показує вікно для пошуку читачів за критеріями"""
    readers_window = tk.Toplevel()
    readers_window.title("Пошук читачів за характеристиками")
    readers_window.geometry("650x750")
    
    # Заголовок
    tk.Label(readers_window, text="Пошук читачів за характеристиками", 
             font=("Arial", 16, "bold")).pack(pady=10)
    
    # Фрейм для критеріїв пошуку
    criteria_frame = tk.LabelFrame(readers_window, text="Критерії пошуку", padx=10, pady=10)
    criteria_frame.pack(fill="x", padx=10, pady=5)
    
    # Університет
    tk.Label(criteria_frame, text="Навчальний заклад:").pack(anchor="w")
    university_entry = tk.Entry(criteria_frame, width=50)
    university_entry.pack(pady=5, fill="x")
    
    # Факультет
    tk.Label(criteria_frame, text="Факультет:").pack(anchor="w")
    faculty_entry = tk.Entry(criteria_frame, width=50)
    faculty_entry.pack(pady=5, fill="x")
    
    # Організація
    tk.Label(criteria_frame, text="Організація:").pack(anchor="w")
    organization_entry = tk.Entry(criteria_frame, width=50)
    organization_entry.pack(pady=5, fill="x")
    
    # Тип читача
    tk.Label(criteria_frame, text="Тип читача:").pack(anchor="w")
    reader_type_var = tk.StringVar()
    reader_type_combo = ttk.Combobox(criteria_frame, textvariable=reader_type_var, 
                                    values=["","Студент", "Викладач","Науковець", "Працівник", "Інше"],
                                    state="readonly", width=47)
    reader_type_combo.pack(pady=5)
    
    # Кнопки пошуку
    button_frame = tk.Frame(criteria_frame)
    button_frame.pack(pady=10)
    
    def search_readers():
        """Пошук читачів за вказаними критеріями"""
        university = university_entry.get().strip() or None
        faculty = faculty_entry.get().strip() or None
        organization = organization_entry.get().strip() or None
        reader_type = reader_type_var.get() or None
        
        # Якщо не вказано жодного критерію, шукаємо всіх
        if not any([university, faculty, organization, reader_type]):
            if not messagebox.askyesno("Попередження", 
                                     "Не вказано жодного критерію пошуку. Показати всіх читачів?"):
                return
        
        readers = get_readers_by_criteria(university, faculty, reader_type, organization)
        
        # Очищаємо попередні результати
        for item in results_tree.get_children():
            results_tree.delete(item)
        
        # Додаємо нові результати
        for reader in readers:
            reader_id, user_name, address, r_type, uni, fac, org = reader
            results_tree.insert("", "end", values=(
                reader_id, user_name, address, r_type, uni or "-", fac or "-", org or "-"
            ))
        
        total_label.config(text=f"Знайдено читачів: {len(readers)}")
    
    def clear_criteria():
        """Очищення критеріїв пошуку"""
        university_entry.delete(0, tk.END)
        faculty_entry.delete(0, tk.END)
        organization_entry.delete(0, tk.END)
        reader_type_var.set("")
        
        # Очищаємо результати
        for item in results_tree.get_children():
            results_tree.delete(item)
        total_label.config(text="Знайдено читачів: 0")
    
    def get_unique_organizations():
        """Отримує унікальні організації з бази даних"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT organization FROM Readers WHERE organization IS NOT NULL AND organization != '' ORDER BY organization")
        organizations = [org[0] for org in cursor.fetchall()]
        conn.close()
        return organizations
    
    def show_organization_suggestions():
        """Показує вікно з доступними організаціями"""
        org_window = tk.Toplevel(readers_window)
        org_window.title("Доступні організації")
        org_window.geometry("400x300")
        
        tk.Label(org_window, text="Список організацій:", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Отримуємо організації
        organizations = get_unique_organizations()
        
        if not organizations:
            tk.Label(org_window, text="Організації не знайдено", fg="gray").pack(pady=20)
            return
        
        # Створюємо список з організаціями
        listbox = tk.Listbox(org_window, width=50, height=15)
        scrollbar = tk.Scrollbar(org_window, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        for org in organizations:
            listbox.insert(tk.END, org)
        
        def select_organization():
            """Вибір організації зі списку"""
            selected_index = listbox.curselection()
            if selected_index:
                selected_org = listbox.get(selected_index[0])
                organization_entry.delete(0, tk.END)
                organization_entry.insert(0, selected_org)
                org_window.destroy()
        
        listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        tk.Button(org_window, text="Вибрати", command=select_organization, 
                 bg="blue", fg="white").pack(pady=10)
    
    tk.Button(button_frame, text="Пошук", command=search_readers, 
              bg="blue", fg="white", width=15).pack(side="left", padx=5)
    
    tk.Button(button_frame, text="Очистити", command=clear_criteria,
              bg="gray", fg="white", width=15).pack(side="left", padx=5)
    
    tk.Button(button_frame, text="Список організацій", command=show_organization_suggestions,
              bg="purple", fg="white", width=15).pack(side="left", padx=5)
    
    # Результати пошуку
    results_frame = tk.LabelFrame(readers_window, text="Результати пошуку", padx=10, pady=10)
    results_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Створюємо Treeview для відображення результатів
    columns = ("ID", "ПІБ", "Адреса", "Тип", "Університет", "Факультет", "Організація")
    results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
    
    # Налаштовуємо заголовки колонок
    column_widths = {"ID": 50, "ПІБ": 120, "Адреса": 100, "Тип": 80, "Університет": 100, "Факультет": 100, "Організація": 100}
    for col in columns:
        results_tree.heading(col, text=col)
        results_tree.column(col, width=column_widths.get(col, 100))
    
    # Додаємо скролбар
    scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview)
    results_tree.configure(yscrollcommand=scrollbar.set)
    
    results_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Підказки для фільтрації
    tip_frame = tk.Frame(readers_window)
    tip_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(tip_frame, text="💡 Для пошуку студентів конкретного університету: заповніть поле 'Навчальний заклад'",
             font=("Arial", 8), fg="gray").pack(anchor="w")
    tk.Label(tip_frame, text="💡 Для пошуку науковців: виберіть 'Викладач' у типі читача",
             font=("Arial", 8), fg="gray").pack(anchor="w")
    tk.Label(tip_frame, text="💡 Для пошуку працівників організацій: заповніть поле 'Організація'",
             font=("Arial", 8), fg="gray").pack(anchor="w")
    tk.Label(tip_frame, text="💡 Натисніть 'Список організацій' для перегляду доступних організацій",
             font=("Arial", 8), fg="gray").pack(anchor="w")
    
    # Лічильник результатів
    total_label = tk.Label(readers_window, text="Знайдено читачів: 0", 
                          font=("Arial", 10, "bold"))
    total_label.pack(pady=5)
    
    # Кнопка експорту
    def export_results():
        """Експорт результатів у файл"""
        if not results_tree.get_children():
            messagebox.showwarning("Попередження", "Немає даних для експорту!")
            return
        
        from tkinter import filedialog
        import csv
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Зберегти результати як"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Записуємо заголовки
                writer.writerow(columns)
                # Записуємо дані
                for item in results_tree.get_children():
                    values = results_tree.item(item)['values']
                    writer.writerow(values)
            
            messagebox.showinfo("Успіх", f"Результати успішно експортовано у файл: {file_path}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при експорті: {str(e)}")
    
    export_button = tk.Button(readers_window, text="Експортувати в CSV", 
                             command=export_results, bg="green", fg="white")
    export_button.pack(pady=5)
    
    # Додаткові функції для зручності
    def on_organization_focus_in(event):
        """Показує підказку при фокусі на полі організації"""
        organization_entry.config(bg="#FFFFE0")  # світло-жовтий фон
    
    def on_organization_focus_out(event):
        """Повертає звичайний фон при втраті фокусу"""
        organization_entry.config(bg="white")
    
    # Додаємо обробники подій для поля організації
    organization_entry.bind("<FocusIn>", on_organization_focus_in)
    organization_entry.bind("<FocusOut>", on_organization_focus_out)

# Додамо цю функцію до головного вікна адміністратора
def show_admin_window(user_login):
    admin_window = tk.Tk()
    admin_window.title("Вікно адміністратора")
    admin_window.geometry("450x950")  # Збільшено висоту для нової кнопки

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
    tk.Button(admin_window, text="Управління книгами та звіти", command=show_books_management_window).pack(pady=5)
    tk.Button(admin_window, text="Найпопулярніші книги", command=show_popular_books_window, 
              bg="purple", fg="white", width=25, height=2).pack(pady=5)
    tk.Button(admin_window, text="Пошук читачів за характеристиками", 
              command=show_readers_list_window, bg="orange", fg="white", width=30, height=2).pack(pady=5)
    tk.Button(admin_window, text="Переглягнути заборговані книги", command=show_admin_overdue_books).pack(pady=5)
    tk.Button(admin_window, text="Вийти", command=admin_window.destroy).pack(pady=10)

    admin_window.mainloop()