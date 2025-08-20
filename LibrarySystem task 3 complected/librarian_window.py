from tkinter import *
from tkinter import messagebox
from database import get_db_connection
from login_window import show_login_window

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
           command=lambda: [librarian_window.destroy(), show_login_window()]).pack(pady=20)

    librarian_window.mainloop()

    pass