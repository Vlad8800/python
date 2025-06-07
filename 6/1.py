import tkinter as tk
from tkinter import ttk, scrolledtext
from abc import ABC, abstractmethod
import datetime

class Teacher(ABC):
    def __init__(self, name, department, experience, degree):
        self.name = name
        self.department = department
        self.experience = experience
        self.degree = degree
    
    def get_basic_info(self):
        return f"Name: {self.name}, Department: {self.department}, Experience: {self.experience} years, Degree: {self.degree}"
    
    def calculate_salary(self):
        base_salary = 30000
        experience_bonus = self.experience * 1000
        return base_salary + experience_bonus
    
    @abstractmethod
    def get_position(self):
        pass
    
    @abstractmethod
    def get_qualification_info(self):
        pass

class Professor(Teacher):
    def __init__(self, name, department, experience, degree, publications, research_projects):
        super().__init__(name, department, experience, degree)
        self.publications = publications
        self.research_projects = research_projects
    
    def get_position(self):
        return "Professor"
    
    def get_qualification_info(self):
        return f"Publications: {self.publications}, Research Projects: {self.research_projects}"
    
    def calculate_research_bonus(self):
        return self.publications * 500 + self.research_projects * 2000
    
    def get_full_info(self):
        return (f"{self.get_basic_info()}, Position: {self.get_position()}, "
                f"{self.get_qualification_info()}, Salary: {self.calculate_salary() + self.calculate_research_bonus()} UAH")

class AssociateProfessor(Teacher):
    def __init__(self, name, department, experience, degree, courses_taught, mentoring_students):
        super().__init__(name, department, experience, degree)
        self.courses_taught = courses_taught
        self.mentoring_students = mentoring_students
    
    def get_position(self):
        return "Associate Professor"
    
    def get_qualification_info(self):
        return f"Courses Taught: {self.courses_taught}, Mentoring Students: {self.mentoring_students}"
    
    def calculate_teaching_load(self):
        return f"Teaching Load: {self.courses_taught * 4} hours/week"
    
    def get_full_info(self):
        return (f"{self.get_basic_info()}, Position: {self.get_position()}, "
                f"{self.get_qualification_info()}, {self.calculate_teaching_load()}, "
                f"Salary: {self.calculate_salary()} UAH")

# Створення бази викладачів
teachers = [
    Professor("John Smith", "Computer Science", 20, "PhD", 150, 5),
    AssociateProfessor("Mary Johnson", "Mathematics", 10, "PhD", 5, 15),
    Professor("Robert Brown", "Computer Science", 25, "PhD", 200, 8),
    AssociateProfessor("Anna Davis", "Physics", 8, "PhD", 4, 10),
    Professor("James Wilson", "Mathematics", 18, "PhD", 120, 3),
]

class TeacherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teacher Database")
        self.root.geometry("700x500")

        # Frame для пошуку
        self.search_frame = ttk.Frame(root)
        self.search_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(self.search_frame, text="Department:").pack(side="left")
        self.department_entry = ttk.Entry(self.search_frame, width=30)
        self.department_entry.pack(side="left", padx=5)
        
        ttk.Button(self.search_frame, text="Search", command=self.search_teachers).pack(side="left")
        ttk.Button(self.search_frame, text="Show All", command=self.show_all_teachers).pack(side="left", padx=5)
        ttk.Button(self.search_frame, text="Clear", command=self.clear_search).pack(side="left", padx=5)

        # Текстове поле для результатів
        self.result_text = scrolledtext.ScrolledText(root, height=20, width=80, wrap=tk.WORD)
        self.result_text.pack(pady=10, padx=10, fill="both", expand=True)

        # Початкове відображення всіх викладачів
        self.show_all_teachers()

    def show_all_teachers(self):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "All Teachers:\n\n")
        for teacher in teachers:
            self.result_text.insert(tk.END, f"{teacher.get_full_info()}\n\n")

    def search_teachers(self):
        department = self.department_entry.get().strip()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Teachers in {department} department:\n\n")
        found = False
        for teacher in teachers:
            if teacher.department.lower() == department.lower():
                self.result_text.insert(tk.END, f"{teacher.get_full_info()}\n\n")
                found = True
        if not found:
            self.result_text.insert(tk.END, "No teachers found in this department.\n")

    def clear_search(self):
        self.department_entry.delete(0, tk.END)
        self.show_all_teachers()

if __name__ == "__main__":
    root = tk.Tk()
    app = TeacherApp(root)
    root.mainloop()