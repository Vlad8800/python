import mysql.connector
from tkinter import *
from tkinter import ttk
from datetime import date

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vlad8800',
    'database': 'LibrarySystem'
}

current_user_id = 1  # <-- встав сюди ID авторизованого користувача

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_books():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title FROM books")
    books = cursor.fetchall()
    conn.close()
    return books

def has_user_taken(book_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM issued_books
        WHERE book_id = %s AND user_id = %s AND returned = 0
    """, (book_id, user_id))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

def is_taken_by_other(book_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM issued_books
        WHERE book_id = %s AND user_id != %s AND returned = 0
    """, (book_id, user_id))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

def can_user_take(book_id, user_id):
    return not has_user_taken(book_id, user_id) and not is_taken_by_other(book_id, user_id)

def take_book(book_id):
    if not can_user_take(book_id, current_user_id):
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO issued_books (book_id, user_id, issue_date, returned)
        VALUES (%s, %s, %s, 0)
    """, (book_id, current_user_id, date.today()))
    conn.commit()
    conn.close()
    refresh_books()

def return_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE issued_books SET returned = 1, return_date = %s
        WHERE book_id = %s AND user_id = %s AND returned = 0
    """, (date.today(), book_id, current_user_id))
    conn.commit()
    conn.close()
    refresh_books()

def refresh_books():
    for widget in book_frame.winfo_children():
        widget.destroy()

    books = fetch_books()
    for book in books:
        frame = Frame(book_frame)
        frame.pack(fill=X, padx=5, pady=2)

        Label(frame, text=book['title'], width=30, anchor='w').pack(side=LEFT)

        if has_user_taken(book['id'], current_user_id):
            Button(frame, text="Повернути", command=lambda b=book['id']: return_book(b)).pack(side=RIGHT)
        elif can_user_take(book['id'], current_user_id):
            Button(frame, text="Взяти", command=lambda b=book['id']: take_book(b)).pack(side=RIGHT)
        else:
            Button(frame, text="Недоступна", state=DISABLED, bg="lightgray").pack(side=RIGHT)

# --------------------- GUI ---------------------
root = Tk()
root.title("Список книг")

book_frame = Frame(root)
book_frame.pack(padx=10, pady=10)

refresh_books()
root.mainloop()
