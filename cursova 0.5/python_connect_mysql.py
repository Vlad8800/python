import mysql.connector

try:
    # Підключення до MySQL
    conn = mysql.connector.connect(
        host="localhost",
        username="root",
        password="Vlad8800",
        database="librarysystem"
    )

    my_cursor = conn.cursor()

    # Виконання SQL-запиту
    my_cursor.execute("SELECT * FROM Readers")  # або 'Readers' — залежно від назви

    # Отримання всіх результатів
    rows = my_cursor.fetchall()

    print("Дані з таблиці Reader:")
    for row in rows:
        print(row)

except mysql.connector.Error as e:
    print("Помилка підключення або виконання запиту:", e)

finally:
    if conn.is_connected():
        my_cursor.close()
        conn.close()
