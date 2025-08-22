from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from utils import get_user_id
from database import get_db_connection
import mysql.connector

def fetch_all_authors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT author_id, name, surname FROM Authors ORDER BY surname, name")
    authors = cursor.fetchall()
    conn.close()
    return authors

def fetch_all_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.book_id, b.title, a.name, a.surname 
        FROM Books b
        JOIN Authors a ON b.author_id = a.author_id
        ORDER BY a.surname, a.name, b.title
    """)
    books = cursor.fetchall()
    conn.close()
    return books

def show_books_by_author(author):
    user_id = get_user_id(author)
    if user_id is None:
        messagebox.showerror("Помилка", f"Користувача '{author}' не знайдено")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT author_id, name, surname FROM Authors WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Помилка", "Автор не знайдений")
            return
        author_id, name, surname = row

        cursor.execute("SELECT title, year, languages, inventory_number FROM Books WHERE author_id = %s", (author_id,))
        books = cursor.fetchall()

        books_window = Toplevel()
        books_window.title("Книги автора")
        books_window.geometry("600x400")

        Label(books_window, text=f"Книги автора: {name} {surname}", font=("Arial", 14)).pack(pady=10)

        tree = ttk.Treeview(books_window, columns=("Назва", "Рік", "Мова", "Інвентарний номер"), show="headings")
        tree.heading("Назва", text="Назва")
        tree.heading("Рік", text="Рік")
        tree.heading("Мова", text="Мова")
        tree.heading("Інвентарний номер", text="Інвентарний номер")
        for book in books:
            tree.insert("", END, values=book)
        tree.pack(fill=BOTH, expand=True)

    except mysql.connector.Error as err:
        messagebox.showerror("Помилка БД", str(err))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def show_add_book_window(author):
    def generate_inventory_number():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Books")
            count = cursor.fetchone()[0]
            return f"INV-{count + 1:05d}"
        except:
            return "INV-00001"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

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
            author_id = cursor.fetchone()[0]

            cursor.execute("SELECT category_id FROM Categories WHERE name = %s", (category_name,))
            category_id = cursor.fetchone()[0]

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
    except:
        messagebox.showerror("Помилка", "Не вдалося завантажити категорії")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    Button(add_window, text="Зберегти книгу", command=save_book).pack(pady=20)

def show_collection_window():
    """Вікно для створення збірки"""
    window = Toplevel()
    window.title("Створення збірки")
    window.geometry("900x700")
    window.grab_set()  # Робимо вікно модальним
    
    # Запобігаємо відкриттю кількох вікон
    window.focus_set()

    selected_authors = []
    selected_books = []

    # Основні поля збірки
    Label(window, text="Назва збірки:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    title_entry = Entry(window, width=40)
    title_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2)

    Label(window, text="Тип збірки:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    type_var = StringVar()
    type_combo = ttk.Combobox(window, textvariable=type_var, width=37, state="readonly")
    type_combo.grid(row=1, column=1, padx=10, pady=5, columnspan=2)

    # Завантаження типів збірок
    default_types = ('книги', 'журнали', 'газети', 'збірники статей', 
                     'збірники віршів', 'дисертації', 'реферати', 'збірники доповідей')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name FROM BookTypes ORDER BY name")
            book_types = [row[0] for row in cursor.fetchall()]
            if book_types:
                type_combo['values'] = book_types
            else:
                type_combo['values'] = default_types
        except mysql.connector.Error:
            type_combo['values'] = default_types
                
    except Exception as e:
        print(f"Помилка завантаження типів: {e}")
        type_combo['values'] = default_types
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

    # Рамка для вибору авторів
    authors_label_frame = LabelFrame(window, text="Оберіть авторів", font=("Arial", 10, "bold"))
    authors_label_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=NSEW)

    author_columns = ("author_id", "name", "surname")
    author_tree = ttk.Treeview(authors_label_frame, columns=author_columns, show="headings", height=6)
    author_tree.heading("author_id", text="ID")
    author_tree.heading("name", text="Ім'я")
    author_tree.heading("surname", text="Прізвище")
    author_tree.column("author_id", width=50)
    author_tree.column("name", width=150)
    author_tree.column("surname", width=150)

    # Завантажуємо авторів
    try:
        all_authors = fetch_all_authors()
        for author in all_authors:
            author_tree.insert("", "end", values=author)
    except:
        all_authors = []
        messagebox.showerror("Помилка", "Не вдалося завантажити авторів")

    author_scrollbar = ttk.Scrollbar(authors_label_frame, orient=VERTICAL, command=author_tree.yview)
    author_tree.configure(yscrollcommand=author_scrollbar.set)
    author_tree.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
    author_scrollbar.pack(side=RIGHT, fill=Y, pady=5)

    # Рамка для вибору книг
    books_label_frame = LabelFrame(window, text="Оберіть книги", font=("Arial", 10, "bold"))
    books_label_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky=NSEW)

    book_columns = ("book_id", "title", "author_name", "author_surname")
    book_tree = ttk.Treeview(books_label_frame, columns=book_columns, show="headings", height=6)
    book_tree.heading("book_id", text="ID")
    book_tree.heading("title", text="Назва книги")
    book_tree.heading("author_name", text="Ім'я автора")
    book_tree.heading("author_surname", text="Прізвище автора")
    book_tree.column("book_id", width=50)
    book_tree.column("title", width=200)
    book_tree.column("author_name", width=100)
    book_tree.column("author_surname", width=100)

    # Завантажуємо книги
    try:
        all_books = fetch_all_books()
        for book in all_books:
            book_tree.insert("", "end", values=book)
    except:
        all_books = []
        messagebox.showerror("Помилка", "Не вдалося завантажити книги")

    book_scrollbar = ttk.Scrollbar(books_label_frame, orient=VERTICAL, command=book_tree.yview)
    book_tree.configure(yscrollcommand=book_scrollbar.set)
    book_tree.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
    book_scrollbar.pack(side=RIGHT, fill=Y, pady=5)

    # Рамка для обраних елементів
    selected_label_frame = LabelFrame(window, text="Обрані елементи", font=("Arial", 10, "bold"))
    selected_label_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky=NSEW)
    
    selected_listbox = Listbox(selected_label_frame, height=6)
    selected_scrollbar_list = ttk.Scrollbar(selected_label_frame, orient=VERTICAL, command=selected_listbox.yview)
    selected_listbox.configure(yscrollcommand=selected_scrollbar_list.set)
    selected_listbox.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
    selected_scrollbar_list.pack(side=RIGHT, fill=Y, pady=5)

    def update_selected_items_list():
        selected_listbox.delete(0, END)
        for author_id in selected_authors:
            for author in all_authors:
                if author[0] == author_id:
                    selected_listbox.insert(END, f"АВТОР: {author[2]} {author[1]}")
        for book_id in selected_books:
            for book in all_books:
                if book[0] == book_id:
                    selected_listbox.insert(END, f"КНИГА: {book[1]} ({book[3]} {book[2]})")

    def add_author():
        selected = author_tree.selection()
        if selected:
            author_id = author_tree.item(selected[0])['values'][0]
            if author_id not in selected_authors:
                selected_authors.append(author_id)
                update_selected_items_list()
            else:
                messagebox.showwarning("Увага", "Цей автор вже доданий")
        else:
            messagebox.showwarning("Увага", "Оберіть автора зі списку")

    def add_book():
        selected = book_tree.selection()
        if selected:
            book_id = book_tree.item(selected[0])['values'][0]
            if book_id not in selected_books:
                selected_books.append(book_id)
                update_selected_items_list()
            else:
                messagebox.showwarning("Увага", "Ця книга вже додана")
        else:
            messagebox.showwarning("Увага", "Оберіть книгу зі списку")

    def remove_selected():
        selected = selected_listbox.curselection()
        if selected:
            index = selected[0]
            item_text = selected_listbox.get(index)
            if item_text.startswith("АВТОР:"):
                # Знаходимо і видаляємо автора
                author_name = item_text.replace("АВТОР: ", "")
                for i, author_id in enumerate(selected_authors):
                    for author in all_authors:
                        if author[0] == author_id and f"{author[2]} {author[1]}" == author_name:
                            selected_authors.pop(i)
                            break
            elif item_text.startswith("КНИГА:"):
                # Знаходимо і видаляємо книгу
                book_info = item_text.replace("КНИГА: ", "")
                for i, book_id in enumerate(selected_books):
                    for book in all_books:
                        if book[0] == book_id and f"{book[1]} ({book[3]} {book[2]})" == book_info:
                            selected_books.pop(i)
                            break
            update_selected_items_list()
        else:
            messagebox.showwarning("Увага", "Оберіть елемент для видалення")

    # Кнопки для додавання/видалення
    buttons_frame = Frame(window)
    buttons_frame.grid(row=5, column=0, columnspan=3, pady=10)
    
    Button(buttons_frame, text="Додати автора", command=add_author, bg="lightblue").pack(side=LEFT, padx=5)
    Button(buttons_frame, text="Додати книгу", command=add_book, bg="lightgreen").pack(side=LEFT, padx=5)
    Button(buttons_frame, text="Видалити обране", command=remove_selected, bg="lightcoral").pack(side=LEFT, padx=5)

    # Додаткові поля збірки
    details_frame = Frame(window)
    details_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky=W)

    Label(details_frame, text="Рік:").grid(row=0, column=0, padx=5, pady=2, sticky=W)
    year_entry = Entry(details_frame, width=15)
    year_entry.grid(row=0, column=1, padx=5, pady=2)

    Label(details_frame, text="Мова:").grid(row=0, column=2, padx=5, pady=2, sticky=W)
    language_entry = Entry(details_frame, width=15)
    language_entry.grid(row=0, column=3, padx=5, pady=2)

    Label(details_frame, text="Кількість:").grid(row=1, column=0, padx=5, pady=2, sticky=W)
    quantity_entry = Entry(details_frame, width=15)
    quantity_entry.grid(row=1, column=1, padx=5, pady=2)

    Label(details_frame, text="Тип доступу:").grid(row=1, column=2, padx=5, pady=2, sticky=W)
    access_var = StringVar()
    access_combo = ttk.Combobox(details_frame, textvariable=access_var, width=20, state="readonly")
    # ВИПРАВЛЕНО: Використовуємо правильні значення для ENUM поля
    access_combo['values'] = ('Тільки в читальній залі', 'У читальній залі і вдома')
    access_combo.grid(row=1, column=3, padx=5, pady=2)
    access_combo.current(0)  # Встановлюємо значення за замовчуванням

    Label(details_frame, text="Інвентарний номер:").grid(row=2, column=0, padx=5, pady=2, sticky=W)
    inventory_entry = Entry(details_frame, width=20)
    inventory_entry.grid(row=2, column=1, padx=5, pady=2)

    def save_collection():
        if not title_entry.get().strip():
            messagebox.showerror("Помилка", "Введіть назву збірки")
            return
            
        if not selected_authors and not selected_books:
            messagebox.showerror("Помилка", "Оберіть хоча б одного автора або книгу")
            return
            
        if not type_var.get():
            messagebox.showerror("Помилка", "Оберіть тип збірки")
            return

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Початок транзакції
            conn.autocommit = False

            # Отримуємо type_id
            type_name = type_var.get()
            try:
                cursor.execute("SELECT type_id FROM BookTypes WHERE name = %s", (type_name,))
                type_result = cursor.fetchone()
                if not type_result:
                    cursor.execute("INSERT INTO BookTypes (name) VALUES (%s)", (type_name,))
                    type_id = cursor.lastrowid
                else:
                    type_id = type_result[0]
            except mysql.connector.Error:
                messagebox.showerror("Помилка", "Не вдалося обробити тип збірки")
                return

            # Конвертуємо значення для access_type
            access_type_value = access_var.get()
            if access_type_value == 'В читальній залі':
                access_type_value = 'Тільки в читальній залі'
            elif access_type_value == 'В читальній залі і вдома':
                access_type_value = 'У читальній залі і вдома'
            else:
                access_type_value = 'Тільки в читальній залі'

            # Збираємо всі унікальні книги
            unique_books = set()
            
            # Додаємо книги обраних авторів
            for author_id in selected_authors:
                cursor.execute("SELECT book_id FROM Books WHERE author_id = %s", (author_id,))
                for (book_id,) in cursor.fetchall():
                    unique_books.add(book_id)
            
            # Додаємо окремо вибрані книги
            for book_id in selected_books:
                unique_books.add(book_id)
            
            if not unique_books:
                messagebox.showerror("Помилка", "Не знайдено жодної книги для збірки")
                conn.rollback()
                return

            # Створюємо збірку (колекцію) в таблиці Collections
            cursor.execute("""
                INSERT INTO Collections (title, category_id, year, languages, quantity, access_type, inventory_number, type_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                title_entry.get().strip(),
                type_id,  # category_id
                year_entry.get().strip() if year_entry.get().strip() else None,
                language_entry.get().strip() if language_entry.get().strip() else None,
                int(quantity_entry.get()) if quantity_entry.get().strip().isdigit() else len(unique_books),
                access_type_value,
                inventory_entry.get().strip() if inventory_entry.get().strip() else f"COLL-{cursor.lastrowid:05d}",
                type_id
            ))
            
            collection_id = cursor.lastrowid

            # НОВИЙ ФУНКЦІОНАЛ: Записуємо збірку також як книгу в таблицю Books
            # Визначаємо основного автора (перший з обраних або автор першої книги)
            main_author_id = None
            if selected_authors:
                main_author_id = selected_authors[0]
            elif unique_books:
                # Беремо автора першої книги
                first_book_id = list(unique_books)[0]
                cursor.execute("SELECT author_id FROM Books WHERE book_id = %s", (first_book_id,))
                result = cursor.fetchone()
                if result:
                    main_author_id = result[0]

            if main_author_id:
                # Генеруємо інвентарний номер для книги-збірки
                collection_inventory = inventory_entry.get().strip() if inventory_entry.get().strip() else f"COLL-BOOK-{collection_id:05d}"
                
                cursor.execute("""
                    INSERT INTO Books (title, author_id, category_id, year, languages, quantity, access_type, inventory_number, collection_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"[ЗБІРКА] {title_entry.get().strip()}",  # Додаємо префікс для розрізнення
                    main_author_id,
                    type_id,
                    year_entry.get().strip() if year_entry.get().strip() else None,
                    language_entry.get().strip() if language_entry.get().strip() else None,
                    int(quantity_entry.get()) if quantity_entry.get().strip().isdigit() else 1,
                    access_type_value,
                    collection_inventory,
                    collection_id  # Зв'язок з колекцією
                ))

            # Додаємо книги до збірки в CollectionBooks
            for book_id in unique_books:
                cursor.execute("""
                    INSERT INTO CollectionBooks (collection_id, book_id)
                    VALUES (%s, %s)
                """, (collection_id, book_id))

            # НОВИЙ ФУНКЦІОНАЛ: Копіюємо всі дані книг до CollectionItems
            # Це дозволить зберегти повну інформацію про книги на момент створення збірки
            try:
                # Створюємо таблицю CollectionItems якщо не існує
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS CollectionItems (
                        collection_id INT,
                        book_id INT,
                        title VARCHAR(255),
                        author_id INT,
                        category_id INT,
                        year YEAR,
                        languages VARCHAR(50),
                        quantity INT,
                        access_type ENUM('Тільки в читальній залі','У читальній залі і вдома'),
                        inventory_number VARCHAR(45),
                        PRIMARY KEY (collection_id, book_id),
                        FOREIGN KEY (collection_id) REFERENCES Collections(collection_id),
                        FOREIGN KEY (book_id) REFERENCES Books(book_id)
                    )
                """)
                
                for book_id in unique_books:
                    # Отримуємо всі дані про книгу
                    cursor.execute("""
                        SELECT title, author_id, category_id, year, languages, quantity, access_type, inventory_number
                        FROM Books WHERE book_id = %s
                    """, (book_id,))
                    book_data = cursor.fetchone()
                    
                    if book_data:
                        cursor.execute("""
                            INSERT INTO CollectionItems (collection_id, book_id, title, author_id, category_id, 
                                                       year, languages, quantity, access_type, inventory_number)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (collection_id, book_id) + book_data)
            except mysql.connector.Error as e:
                print(f"Помилка при збереженні до CollectionItems: {e}")
                # Продовжуємо виконання, навіть якщо ця частина не вдалася

            # Підтверджуємо транзакцію
            conn.commit()
            messagebox.showinfo("Успіх", 
                              f"Збірку '{title_entry.get()}' успішно створено!\n"
                              f"Додано {len(unique_books)} книг.\n"
                              f"Збірка також записана як книга в каталог.")
            window.destroy()

        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            messagebox.showerror("Помилка БД", f"Помилка бази даних: {err}")
        except Exception as err:
            if conn:
                conn.rollback()
            messagebox.showerror("Помилка", f"Невідома помилка: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Кнопки збереження та скасування
    save_buttons_frame = Frame(window)
    save_buttons_frame.grid(row=7, column=0, columnspan=3, pady=20)
    
    Button(save_buttons_frame, text="Зберегти збірку", command=save_collection, 
           bg="green", fg="white", font=("Arial", 12, "bold"), padx=20).pack(side=LEFT, padx=10)
    Button(save_buttons_frame, text="Скасувати", command=window.destroy, 
           bg="red", fg="white", font=("Arial", 12, "bold"), padx=20).pack(side=LEFT, padx=10)

    # Налаштування розтягування
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)
    window.columnconfigure(2, weight=1)
    window.rowconfigure(2, weight=1)
    window.rowconfigure(3, weight=1)
    window.rowconfigure(4, weight=1)

def show_writer_window(user_login):
    writer_window = Tk()
    writer_window.title("Вікно автора")
    writer_window.geometry("400x300")

    menu_frame = Frame(writer_window)
    menu_frame.pack(pady=20)

    Label(menu_frame, text=f"Вітаємо, {user_login} (Автор)!", font=("Arial", 14)).pack(pady=10)

    Button(menu_frame, text="Переглянути мої книги", command=lambda: show_books_by_author(user_login)).pack(pady=5)
    Button(menu_frame, text="Додати нову книгу", command=lambda: show_add_book_window(user_login)).pack(pady=5)
    Button(menu_frame, text="Створити збірку", command=show_collection_window).pack(pady=5)
    Button(menu_frame, text="Вийти", command=writer_window.destroy).pack(pady=20)

    writer_window.mainloop()