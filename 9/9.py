import tkinter as tk
from tkinter import filedialog, messagebox
import random

class ExamAssignmentApp:
    def __init__(self, master):
        self.master = master
        master.title("Exam Ticket Assignment")

        self.students = []
        self.tickets = []
        self.result = {}

        # UI
        self.load_button = tk.Button(master, text="Вивети списки", command=self.load_lists)
        self.load_button.pack(pady=5)

        self.assign_button = tk.Button(master, text="Тягнути білет", command=self.assign_tickets, state=tk.DISABLED)
        self.assign_button.pack(pady=5)

        self.save_button = tk.Button(master, text="Зберегти результат", command=self.save_result, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.text_display = tk.Text(master, height=20, width=60)
        self.text_display.pack(pady=10)

    def load_lists(self):
        try:
            with open("students.txt", "r", encoding="utf-8") as f:
                self.students = [line.strip() for line in f if line.strip()]
            with open("tickets.txt", "r", encoding="utf-8") as f:
                self.tickets = [line.strip() for line in f if line.strip()]

            if len(self.students) > len(self.tickets):
                messagebox.showerror("Error", "Not enough tickets for each student!")
                return

            self.display_text("Сутденти:\n" + "\n".join(self.students) + "\n\n" +
                              "Білети:\n" + "\n".join(self.tickets))

            self.assign_button.config(state=tk.NORMAL)
        except FileNotFoundError:
            messagebox.showerror("File Error", "Make sure 'students.txt' and 'tickets.txt' exist.")

    def assign_tickets(self):
        self.result.clear()
        students_cycle = self.students[:]
        tickets_cycle = self.tickets[:]
        random.shuffle(students_cycle)
        random.shuffle(tickets_cycle)

        for student, ticket in zip(students_cycle, tickets_cycle):
            self.result[student] = ticket

        display_result = "\n".join(f"{student} → Ticket {ticket}" for student, ticket in self.result.items())
        self.display_text("Результат:\n" + display_result)
        self.save_button.config(state=tk.NORMAL)

    def save_result(self):
        with open("result.txt", "w", encoding="utf-8") as f:
            for student, ticket in self.result.items():
                f.write(f"{student} -> Ticket {ticket}\n")
        messagebox.showinfo("Збережено", "Результат зберігся в файлі 'result.txt'.")

    def display_text(self, content):
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.END, content)

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = ExamAssignmentApp(root)
    root.mainloop()
