import tkinter as tk
from tkinter import messagebox
import os

# Базовий клас
class Document:
    def __init__(self, doc_number="0000", date="01.01.2025", amount=0.0):
        self.doc_number = doc_number
        self.date = date
        self.amount = amount

    # Конструктор за замовчуванням
    def __init_default__(self):
        self.doc_number = "0000"
        self.date = "01.01.2025"
        self.amount = 0.0

    # Деструктор
    def __del__(self):
        print("Лабораторна робота виконанна студентом 2 курсу Суслою Владиславом")

    # Метод базового класу для перевизначення
    def calculate_total(self):
        return self.amount

    # Метод для виведення даних
    def show(self):
        return f"Номер документа: {self.doc_number}\nДата: {self.date}\nСума: {self.amount:.2f}"

# Похідний клас - Квитанція
class Receipt(Document):
    def __init__(self, doc_number="0000", date="01.01.2025", amount=0.0, service=""):
        super().__init__(doc_number, date, amount)
        self.service = service

    def calculate_total(self):
        # Додаємо фіксовану плату за оформлення квитанції
        return self.amount + 10.0

    def show(self):
        return f"{super().show()}\nПослуга: {self.service}"

# Похідний клас - Рахунок
class Invoice(Document):
    def __init__(self, doc_number="0000", date="01.01.2025", amount=0.0, recipient=""):
        super().__init__(doc_number, date, amount)
        self.recipient = recipient

    def calculate_total(self):
        # Додаємо ПДВ 20%
        return self.amount * 1.20

    def show(self):
        return f"{super().show()}\nОтримувач: {self.recipient}"

# Похідний клас - Накладна
class Waybill(Document):
    def __init__(self, doc_number="0000", date="01.01.2025", amount=0.0, items_count=0):
        super().__init__(doc_number, date, amount)
        self.items_count = items_count

    def calculate_total(self):
        # Додаємо транспортний збір залежно від кількості позицій
        return self.amount + (self.items_count * 5.0)

    def show(self):
        return f"{super().show()}\nКількість позицій: {self.items_count}"

# GUI додаток
class DocumentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Документи")
        self.root.geometry("400x500")

        # Поля введення
        tk.Label(root, text="Номер документа:").pack()
        self.doc_number_entry = tk.Entry(root)
        self.doc_number_entry.pack()

        tk.Label(root, text="Дата (дд.мм.рррр):").pack()
        self.date_entry = tk.Entry(root)
        self.date_entry.pack()

        tk.Label(root, text="Сума:").pack()
        self.amount_entry = tk.Entry(root)
        self.amount_entry.pack()

        # Додаткові поля для похідних класів
        tk.Label(root, text="Послуга (для квитанції):").pack()
        self.service_entry = tk.Entry(root)
        self.service_entry.pack()

        tk.Label(root, text="Отримувач (для рахунку):").pack()
        self.recipient_entry = tk.Entry(root)
        self.recipient_entry.pack()

        tk.Label(root, text="Кількість позицій (для накладної):").pack()
        self.items_count_entry = tk.Entry(root)
        self.items_count_entry.pack()

        # Кнопки
        tk.Button(root, text="Створити квитанцію", command=self.create_receipt).pack(pady=5)
        tk.Button(root, text="Створити рахунок", command=self.create_invoice).pack(pady=5)
        tk.Button(root, text="Створити накладну", command=self.create_waybill).pack(pady=5)
        tk.Button(root, text="Зберегти у файл", command=self.save_to_file).pack(pady=5)

        self.current_doc = None

    def get_common_data(self):
        try:
            doc_number = self.doc_number_entry.get()
            date = self.date_entry.get()
            amount = float(self.amount_entry.get())
            return doc_number, date, amount
        except ValueError:
            messagebox.showerror("Помилка", "Перевірте правильність введених даних!")
            return None

    def create_receipt(self):
        data = self.get_common_data()
        if data:
            doc_number, date, amount = data
            service = self.service_entry.get()
            self.current_doc = Receipt(doc_number, date, amount, service)
            messagebox.showinfo("Квитанція", self.current_doc.show() + f"\nЗагальна сума: {self.current_doc.calculate_total():.2f}")

    def create_invoice(self):
        data = self.get_common_data()
        if data:
            doc_number, date, amount = data
            recipient = self.recipient_entry.get()
            self.current_doc = Invoice(doc_number, date, amount, recipient)
            messagebox.showinfo("Рахунок", self.current_doc.show() + f"\nЗагальна сума: {self.current_doc.calculate_total():.2f}")

    def create_waybill(self):
        data = self.get_common_data()
        if data:
            doc_number, date, amount = data
            try:
                items_count = int(self.items_count_entry.get())
                self.current_doc = Waybill(doc_number, date, amount, items_count)
                messagebox.showinfo("Накладна", self.current_doc.show() + f"\nЗагальна сума: {self.current_doc.calculate_total():.2f}")
            except ValueError:
                messagebox.showerror("Помилка", "Кількість позицій має бути цілим числом!")

    def save_to_file(self):
        if self.current_doc:
            with open("document.txt", "w", encoding="utf-8") as file:
                file.write(self.current_doc.show() + f"\nЗагальна сума: {self.current_doc.calculate_total():.2f}")
            messagebox.showinfo("Успіх", "Дані збережено у файл document.txt")
        else:
            messagebox.showwarning("Попередження", "Спочатку створіть документ!")

# Запуск програми
if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentApp(root)
    root.mainloop()