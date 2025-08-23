from tkinter import *
from tkinter import messagebox
import mysql.connector
from database import get_db_connection
from reader_window import show_reader_window
from register_window import show_register_window

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

def show_login_window():
    login_window = Tk()
    login_window.title("Вхід в систему")
    login_window.geometry("300x250")
    
    # Frame для центрування
    frame = Frame(login_window)
    frame.pack(expand=True)
    
    Label(frame, text="Логін:", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky=E)
    global entry_login
    entry_login = Entry(frame, font=("Arial", 10))
    entry_login.grid(row=0, column=1, padx=10, pady=10)
    
    Label(frame, text="Пароль:", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky=E)
    global entry_password
    entry_password = Entry(frame, show="*", font=("Arial", 10))
    entry_password.grid(row=1, column=1, padx=10, pady=10)
    
    def login_user():
        login = entry_login.get()
        password = entry_password.get()
        
        if not login or not password:
            messagebox.showerror("Помилка", "Будь ласка, заповніть всі поля")
            return
            
        conn = None
        cursor = None
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Перевіряємо користувача
            cursor.execute("SELECT user_id, login, password, role FROM Users WHERE login = %s", (login,))
            result = cursor.fetchone()
            
            if result:
                user_id, db_login, db_password, role = result
                
                # Перевіряємо пароль
                if password == db_password:
                    if role == 'Reader':
                        # Отримуємо reader_id для читача
                        reader_id = get_reader_id_from_user_id(user_id)
                        if reader_id:
                            messagebox.showinfo("Успіх", "Вхід успішний!")
                            login_window.destroy()
                            show_reader_window(reader_id)
                        else:
                            messagebox.showerror("Помилка", "Читач не знайдений в системі")
                    
                    elif role == 'Librarian':
                        messagebox.showinfo("Успіх", "Вхід успішний! Бібліотекар")
                        login_window.destroy()
                        # Імпортуємо тут, щоб уникнути циклічного імпорту
                        from librarian_window import show_librarian_window
                        show_librarian_window(user_id)
                    
                    elif role == 'Writer':
                        messagebox.showinfo("Успіх", "Вхід успішний! Автор")
                        login_window.destroy()
                        # Імпортуємо тут, щоб уникнути циклічного імпорту
                        from writer_window import show_writer_window
                        show_writer_window(user_id)
                    
                    elif role == 'Admin':
                        messagebox.showinfo("Успіх", "Вхід успішний! Адміністратор")
                        login_window.destroy()
                        # Імпортуємо тут, щоб уникнути циклічного імпорту
                        from admin_window import show_admin_window
                        show_admin_window(user_id)
                    
                    else:
                        messagebox.showerror("Помилка", "Невідома роль користувача")
                else:
                    messagebox.showerror("Помилка", "Невірний пароль")
            else:
                messagebox.showerror("Помилка", "Невірний логін або пароль")
                
        except mysql.connector.Error as err:
            messagebox.showerror("Помилка БД", f"Помилка бази даних: {err}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Несподівана помилка: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    login_button = Button(frame, text="Увійти", command=login_user, bg="green", fg="white", font=("Arial", 12))
    login_button.grid(row=2, column=0, columnspan=2, pady=5)
    
    Label(frame, text="Ще не маєте акаунту?", font=("Arial", 10)).grid(row=3, column=0, columnspan=2, pady=5)
    
    register_button = Button(frame, text="Зареєструватися", command=lambda: [login_window.destroy(), show_register_window()], font=("Arial", 10))
    register_button.grid(row=4, column=0, columnspan=2, pady=5)
    
    # Додаємо обробник події для клавіші Enter
    def on_enter(event):
        login_user()
    
    entry_password.bind('<Return>', on_enter)
    
    login_window.mainloop()

# Якщо потрібно запускати вікно входу напряму
if __name__ == "__main__":
    show_login_window()