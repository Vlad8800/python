from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import mysql.connector
from database import get_db_connection
from utils import get_user_id, get_reading_rooms  

def get_reader_id_from_user_id(user_id):
    """Отримує reader_id з user_id"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT reader_id FROM Readers WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"Помилка отримання reader_id: {err}")
        return None
    except Exception as e:
        print(f"Несподівана помилка: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
def show_register_window():
    from login_window import show_login_window  # локальний імпорт для уникнення циклічності
    from reader_window import show_reader_window
    register_window = Tk()
    register_window.title("Реєстрація")
    register_window.geometry("500x600")

    # --- Основні поля ---
    Label(register_window, text="Логін:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_login = Entry(register_window)
    entry_login.grid(row=0, column=1, padx=10, pady=5)

    Label(register_window, text="Пароль:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    entry_password = Entry(register_window, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=5)

    Label(register_window, text="Роль:").grid(row=2, column=0, sticky=E, padx=10, pady=5)
    role_var = StringVar()
    role_combo = ttk.Combobox(register_window, textvariable=role_var, state="readonly",
                              values=["Reader", "Librarian", "Writer"])
    role_combo.grid(row=2, column=1, padx=10, pady=5)

    # --- Frames для ролей ---
    reader_frame = Frame(register_window)
    librarian_frame = Frame(register_window)
    author_frame = Frame(register_window)
    student_fields_frame = Frame(reader_frame)

    # --- Reader fields ---
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

    # --- Студентські поля ---
    Label(student_fields_frame, text="Університет:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_university = Entry(student_fields_frame)
    entry_university.grid(row=0, column=1, padx=10, pady=5)

    Label(student_fields_frame, text="Факультет:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    entry_faculty = Entry(student_fields_frame)
    entry_faculty.grid(row=1, column=1, padx=10, pady=5)
    student_fields_frame.grid_remove()

    # --- Науковець поля ---
    organization_label = Label(reader_frame, text="Організація:")
    entry_organization = Entry(reader_frame)
    organization_label.grid(row=5, column=0, sticky=E, padx=10, pady=5)
    entry_organization.grid(row=5, column=1, padx=10, pady=5)
    organization_label.grid_remove()
    entry_organization.grid_remove()

    # --- Librarian fields ---
    Label(librarian_frame, text="Ім'я бібліотекаря:").grid(row=0, column=0, sticky=E, padx=10, pady=5)
    entry_librarian_name = Entry(librarian_frame)
    entry_librarian_name.grid(row=0, column=1, padx=10, pady=5)

    Label(librarian_frame, text="Читацький зал:").grid(row=1, column=0, sticky=E, padx=10, pady=5)
    reading_rooms_var = StringVar()
    reading_rooms_combo = ttk.Combobox(librarian_frame, textvariable=reading_rooms_var, state="readonly")
    reading_rooms_combo.grid(row=1, column=1, padx=10, pady=5)

    try:
        rooms = get_reading_rooms()
        reading_rooms_combo['values'] = [f"{r[0]}: {r[1]}" for r in rooms]
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося завантажити читацькі зали: {e}")

    def on_room_selected(event):
        selected = reading_rooms_var.get()
        if selected:
            reading_rooms_var.set(selected.split(":")[0])
        check_required_fields_filled()

    reading_rooms_combo.bind("<<ComboboxSelected>>", on_room_selected)

    # --- Writer fields ---
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

    # --- Hide all frames initially ---
    reader_frame.grid_remove()
    librarian_frame.grid_remove()
    author_frame.grid_remove()

    # --- Функції для toggle ---
    def toggle_reader_type_fields(event=None):
        reader_type = reader_type_var.get()
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
            if not entry_author_name.get().strip() or not entry_author_surname.get().strip() or not entry_author_country.get().strip():
                register_button.config(state=DISABLED)
                return
        register_button.config(state=NORMAL)

    # --- Реєстрація функція ---
    def register_user():
        login = entry_login.get().strip()
        password = entry_password.get().strip()
        role = role_var.get()

        conn = None
        cursor = None
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Перевіряємо, чи вже існує транзакція
            try:
                # Спроба перевірити статус транзакції
                cursor.execute("SELECT 1")
                cursor.fetchall()  # Очищаємо результат
            except mysql.connector.errors.InternalError as e:
                if "Transaction already in progress" in str(e):
                    # Якщо транзакція вже активна, робимо rollback
                    conn.rollback()
            
            # Перевіряємо чи існує логін
            cursor.execute("SELECT user_id FROM Users WHERE login = %s", (login,))
            result = cursor.fetchone()  # Обов'язково зчитуємо результат
            if result:
                messagebox.showerror("Помилка", "Такий логін вже існує!")
                return

            # Явно починаємо транзакцію тільки якщо вона ще не активна
            if not conn.in_transaction:
                conn.start_transaction()

            # Створюємо користувача в таблиці Users
            cursor.execute("INSERT INTO Users (login, password, role) VALUES (%s, %s, %s)", 
                          (login, password, role))
            user_id = cursor.lastrowid
            
            print(f"Створено користувача з user_id: {user_id}")

            reader_id = None  # Ініціалізуємо змінну для reader_id

            if role == 'Reader':
                name = entry_reader_name.get().strip()
                address = entry_reader_address.get().strip()
                reader_type = reader_type_var.get()
                university = entry_university.get().strip() if reader_type == 'Студент' else None
                faculty = entry_faculty.get().strip() if reader_type == 'Студент' else None
                organization = entry_organization.get().strip() if reader_type == 'Науковець' else None
                
                cursor.execute("""
                    INSERT INTO Readers (user_id, user_name, address, reader_type, university, faculty, organization) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, name, address, reader_type, university, faculty, organization))
                
                reader_id = cursor.lastrowid
                print(f"Створено читача з reader_id: {reader_id}")
                
            elif role == 'Librarian':
                name = entry_librarian_name.get().strip()
                room_id_str = reading_rooms_var.get()
                
                try:
                    room_id = int(room_id_str) if room_id_str else None
                except ValueError:
                    messagebox.showerror("Помилка", "Неправильний ID читального залу")
                    if conn:
                        conn.rollback()
                    return
                
                cursor.execute("""
                    INSERT INTO Librarians (librarian_id, name, reading_room_id) 
                    VALUES (%s, %s, %s)
                """, (user_id, name, room_id))
                
            elif role == 'Writer':
                name = entry_author_name.get().strip()
                surname = entry_author_surname.get().strip()
                country = entry_author_country.get().strip()
                birth_date = author_birth_date.get_date().strftime('%Y-%m-%d')
                
                cursor.execute("""
                    INSERT INTO Authors (user_id, name, surname, country, birth_year) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, name, surname, country, birth_date))

            # Підтверджуємо транзакцію
            conn.commit()
            
            # ВИПРАВЛЕННЯ: Автоматичний вхід після реєстрації
            if role == 'Reader' and reader_id:
                messagebox.showinfo("Успіх", "Реєстрація успішна! Автоматичний вхід...")
                register_window.destroy()
                show_reader_window(reader_id)  # Безпосередньо відкриваємо вікно читача
            else:
                messagebox.showinfo("Успіх", "Реєстрація успішна! Будь ласка, увійдіть знову.")
                register_window.destroy()
                show_login_window()

        except mysql.connector.Error as err:
            print(f"Помилка БД: {err}")
            print(f"Код помилки: {err.errno}")
            messagebox.showerror("Помилка БД", f"Помилка бази даних: {err}")
            if conn:
                conn.rollback()
        except Exception as e:
            print(f"Загальна помилка: {e}")
            messagebox.showerror("Помилка", f"Несподівана помилка: {e}")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn:
                # Переконуємося, що з'єднання закривається без активних транзакцій
                try:
                    if conn.in_transaction:
                        conn.rollback()
                except:
                    pass
                conn.close()
    # --- Bind events ---
    role_combo.bind("<<ComboboxSelected>>", toggle_role_fields)
    reader_type_combo.bind("<<ComboboxSelected>>", toggle_reader_type_fields)

    for widget in [entry_login, entry_password, entry_reader_name, entry_reader_address,
                   entry_university, entry_faculty, entry_librarian_name,
                   entry_author_name, entry_author_surname, entry_author_country,
                   entry_organization]:
        widget.bind("<KeyRelease>", check_required_fields_filled)

    author_birth_date.bind("<<DateEntrySelected>>", lambda e: check_required_fields_filled())

    # --- Кнопка реєстрації ---
    register_button = Button(register_window, text="Зареєструвати", command=register_user,
                             bg="green", fg="white", state=DISABLED)
    register_button.grid(row=20, column=0, columnspan=2, pady=20)

    # --- Кнопка входу ---
    Label(register_window, text="Вже маєте акаунт?").grid(row=21, column=0, sticky=E)
    Button(register_window, text="Увійти", command=lambda: [register_window.destroy(), show_login_window()]).grid(row=21, column=1, sticky=W)

    register_window.mainloop()