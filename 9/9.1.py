import tkinter as tk
from tkinter import ttk

# Вершини та ребра графа (враховано петлі)
vertices = ['a', 'b', 'c', 'd', 'e', 'f']
edges = [
    ('a', 'e'),
    ('a', 'b'),
    ('a', 'a'),
    ('d', 'a'),
    ('c', 'b'),
    ('b', 'd'),
    ('b', 'f'),
    ('b', 'c'),
    ('c', 'f'),
    ('e', 'b'),
    ('e', 'c'),
    ('f', 'b'),
    ('c', 'c')
]

def adjacency_matrix(vertices, edges):
    size = len(vertices)
    matrix = [[0]*size for _ in range(size)]
    vertex_index = {v: i for i, v in enumerate(vertices)}
    for src, dst in edges:
        i = vertex_index[src]
        j = vertex_index[dst]
        matrix[i][j] = 1
    return matrix

def incidence_matrix(vertices, edges):
    rows = len(vertices)
    cols = len(edges)
    matrix = [[0]*cols for _ in range(rows)]
    vertex_index = {v: i for i, v in enumerate(vertices)}
    for idx, (src, dst) in enumerate(edges):
        i = vertex_index[src]
        j = vertex_index[dst]
        matrix[i][idx] = -1
        matrix[j][idx] = 1
    return matrix

# Функція для оновлення таблиці
def update_matrix_display(matrix_type):
    for widget in frame_table.winfo_children():
        widget.destroy()

    if matrix_type == "Adjacency":
        matrix = adjacency_matrix(vertices, edges)
        cols = vertices
    else:
        matrix = incidence_matrix(vertices, edges)
        cols = [f"e{i+1}" for i in range(len(edges))]

    # Заголовки
    for j, col in enumerate(cols):
        lbl = tk.Label(frame_table, text=col, relief="ridge", width=5, bg="#ccc")
        lbl.grid(row=0, column=j+1)

    for i, row in enumerate(matrix):
        tk.Label(frame_table, text=vertices[i], relief="ridge", width=5, bg="#ddd").grid(row=i+1, column=0)
        for j, val in enumerate(row):
            lbl = tk.Label(frame_table, text=str(val), relief="ridge", width=5)
            lbl.grid(row=i+1, column=j+1)

# Головне вікно
root = tk.Tk()
root.title("Graph Matrix Viewer")
root.geometry("600x400")

# Вибір типу матриці
frame_controls = tk.Frame(root)
frame_controls.pack(pady=10)

tk.Label(frame_controls, text="Тип матириці:").pack(side=tk.LEFT, padx=5)

combo = ttk.Combobox(frame_controls, values=["Adjacency", "Incidence"])
combo.set("Adjacency")
combo.pack(side=tk.LEFT, padx=5)

btn = tk.Button(frame_controls, text="Show Matrix", command=lambda: update_matrix_display(combo.get()))
btn.pack(side=tk.LEFT, padx=5)

# Таблиця для виводу матриці
frame_table = tk.Frame(root)
frame_table.pack(pady=10)

# Початковий виклик
update_matrix_display("Adjacency")

root.mainloop()
