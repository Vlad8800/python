from database import get_db_connection
import mysql.connector

def get_user_id(author):
    if isinstance(author, int):
        return author
    elif isinstance(author, str):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM Users WHERE login = %s", (author,))
            row = cursor.fetchone()
            return row[0] if row else None
        except mysql.connector.Error as err:
            print("Помилка БД:", err)
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        return None

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