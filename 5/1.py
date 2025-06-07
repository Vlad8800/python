import tkinter as tk
from tkinter import ttk, messagebox

class Person:
    def __init__(self, name, age, gender, weight, height):
        self.name = name
        self.age = int(age)
        self.gender = gender
        self.weight = float(weight)
        self.height = float(height)

    def body_mass_index(self):
        return self.weight / (self.height ** 2)

    def majority(self):
        return "Adult" if self.age >= 18 else "Minor"

    def information(self):
        return (f"Name: {self.name}, Age: {self.age}, Body Mass Index: {self.body_mass_index():.2f}, "
                f"Majority: {self.majority()}")

    def get_additional_fields(self):
        return []

    def set_additional_fields(self, additional_data):
        pass

class Child(Person):
    def __init__(self, name, age, gender, weight, height, parents_name=""):
        super().__init__(name, age, gender, weight, height)
        self.parents_name = parents_name

    def body_mass_index(self):
        return (self.weight / (self.height ** 2)) * 0.2

    def educational_institution(self):
        if self.age < 6:
            return "Preschool"
        else:
            return "School"

    def information(self):
        return (f"Child - {super().information()}, Parents' Name: {self.parents_name}, "
                f"Educational Institution: {self.educational_institution()}")

    def get_additional_fields(self):
        return [("Parents' Name", self.parents_name)]

    def set_additional_fields(self, additional_data):
        self.parents_name = additional_data[0]

class Pensioner(Person):
    def __init__(self, name, age, gender, weight, height, address=""):
        super().__init__(name, age, gender, weight, height)
        self.address = address

    def majority(self):
        return "Adult"

    def pension(self):
        eik = self.age
        if 70 <= eik <= 80:
            return eik * 55
        elif 80 < eik <= 90:
            return eik * 65
        elif 90 < eik:
            return eik * 75
        else:
            return 0

    def information(self):
        return (f"Pensioner - {super().information()}, Address: {self.address}, "
                f"Pension: {self.pension()}")

    def get_additional_fields(self):
        return [("Address", self.address)]

    def set_additional_fields(self, additional_data):
        self.address = additional_data[0]

class PersonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Person Information Management")
        self.root.geometry("600x500")

        # Dictionary to store objects
        self.objects = {
            "Person": Person("Alexander", 30, "Male", 75, 1.80),
            "Child": Child("Maria", 10, "Female", 30, 1.40, "Ivanenko Ivan Ivanovich"),
            "Pensioner": Pensioner("Anna", 70, "Female", 65, 1.60, "Central St, 5")
        }

        # Object type selection
        ttk.Label(self.root, text="Select Object Type:").grid(row=0, column=0, padx=5, pady=5)
        self.object_type = ttk.Combobox(self.root, values=["Person", "Child", "Pensioner"], state="readonly")
        self.object_type.grid(row=0, column=1, padx=5, pady=5)
        self.object_type.current(0)
        self.object_type.bind("<<ComboboxSelected>>", self.update_form)

        # Input fields frame
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Common fields
        self.entries = {}
        self.common_fields = ["Name", "Age", "Gender", "Weight (kg)", "Height (m)"]
        self.additional_entries = []

        # Initialize form with default object (Person)
        self.setup_form()

        # Buttons
        ttk.Button(self.root, text="Update", command=self.update_object).grid(row=2, column=0, columnspan=2, pady=10)

        # Info display
        ttk.Label(self.root, text="Object Information:").grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.info_display = tk.Text(self.root, height=5, width=50)
        self.info_display.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Display initial information
        self.update_info_display()

    def setup_form(self):
        # Clear previous entries
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        self.additional_entries.clear()

        # Common fields
        obj = self.objects[self.object_type.get()]
        values = [obj.name, obj.age, obj.gender, obj.weight, obj.height]

        for i, (field, value) in enumerate(zip(self.common_fields, values)):
            ttk.Label(self.input_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(self.input_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, value)
            self.entries[field] = entry

        # Additional fields (if any)
        additional_fields = obj.get_additional_fields()
        start_row = len(self.common_fields)
        for i, (field, value) in enumerate(additional_fields):
            ttk.Label(self.input_frame, text=f"{field}:").grid(row=start_row + i, column=0, padx=5, pady=5)
            entry = ttk.Entry(self.input_frame)
            entry.grid(row=start_row + i, column=1, padx=5, pady=5)
            entry.insert(0, value)
            self.additional_entries.append((field, entry))

    def update_form(self, event=None):
        self.setup_form()
        self.update_info_display()

    def update_object(self):
        try:
            obj_type = self.object_type.get()
            name = self.entries["Name"].get()
            age = int(self.entries["Age"].get())
            gender = self.entries["Gender"].get()
            weight = float(self.entries["Weight (kg)"].get())
            height = float(self.entries["Height (m)"].get())

            if obj_type == "Person":
                self.objects[obj_type] = Person(name, age, gender, weight, height)
            elif obj_type == "Child":
                parents_name = self.additional_entries[0][1].get()
                self.objects[obj_type] = Child(name, age, gender, weight, height, parents_name)
            elif obj_type == "Pensioner":
                address = self.additional_entries[0][1].get()
                self.objects[obj_type] = Pensioner(name, age, gender, weight, height, address)

            self.update_info_display()
        except ValueError:
            messagebox.showerror("Error", "Please check the input data (age must be an integer, weight and height must be numbers)")

    def update_info_display(self):
        self.info_display.delete(1.0, tk.END)
        obj = self.objects[self.object_type.get()]
        self.info_display.insert(tk.END, obj.information())

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonGUI(root)
    root.mainloop()