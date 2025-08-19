from tkinter import *
from tkinter import messagebox
import mysql.connector
from database import get_db_connection

def show_login_window():
    from register_window import show_register_window
    from reader_window import show_reader_window
    from writer_window import show_writer_window
    from librarian_window import show_librarian_window
    from admin_window import show_admin_window
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
