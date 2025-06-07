import tkinter as tk
from tkinter import messagebox
from collections import namedtuple

# Іменований кортеж для цін інгредієнтів
IngredientsPrice = namedtuple('IngredientsPrice', ['ing1', 'ing2', 'ing3', 'ing4', 'ing5', 'ing6'])

# Функція для обчислення ринкової вартості
def get_price(product, ingredients_price, shipping_price):
    average_ip = sum(ingredients_price) / 6
    market_price = 0.75 * average_ip + 1.15 * shipping_price
    return f"Ринкова вартість продукту {product} становить {market_price:.2f}"

# Обробка натискання кнопки
def calculate_price():
    try:
        product = entry_product.get()
        prices = [float(entry.get()) for entry in ingredient_entries]
        shipping = float(entry_shipping.get())
        ingredients = IngredientsPrice(*prices)
        result = get_price(product, ingredients, shipping)
        messagebox.showinfo("Результат", result)
    except ValueError:
        messagebox.showerror("Помилка", "Будь ласка, введіть коректні числові значення!")

# Створення GUI
root = tk.Tk()
root.title("Обчислення ринкової вартості продукту")

tk.Label(root, text="Назва продукту:").grid(row=0, column=0, sticky="e")
entry_product = tk.Entry(root)
entry_product.grid(row=0, column=1)

ingredient_entries = []
for i in range(6):
    tk.Label(root, text=f"Ціна інгредієнта {i+1}:").grid(row=i+1, column=0, sticky="e")
    entry = tk.Entry(root)
    entry.grid(row=i+1, column=1)
    ingredient_entries.append(entry)

tk.Label(root, text="Ціна доставки:").grid(row=7, column=0, sticky="e")
entry_shipping = tk.Entry(root)
entry_shipping.grid(row=7, column=1)

btn = tk.Button(root, text="Обчислити", command=calculate_price)
btn.grid(row=8, column=0, columnspan=2, pady=10)

root.mainloop()
