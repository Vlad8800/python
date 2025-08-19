from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import mysql.connector
from database import get_db_connection
from login_window import show_login_window
from database import get_db_connection

def show_register_window():
    from login_window import show_login_window  # імпорт всередині функції
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