import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from urllib.request import urlopen
import io

# Налаштування для відображення графіків
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

print("=== ЛАБОРАТОРНА РОБОТА №14 ===")
print("Аналіз статистичних даних засобами Python")
print("=" * 50)

print("\n\n📊 ЗАВДАННЯ 2: Робота з декількома датасетами")
print("-" * 50)

# Створюємо три пов'язані датасети
print("Створюємо три пов'язані датасети:")

# Датасет 1: Інформація про продукти
products = pd.DataFrame({
    'product_id': [1, 2, 3, 4, 5],
    'product_name': ['Laptop', 'Phone', 'Tablet', 'Watch', 'Headphones'],
    'category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
    'price': [1000, 800, 600, 300, 150]
})

# Датасет 2: Продажі
sales = pd.DataFrame({
    'sale_id': [101, 102, 103, 104, 105, 106, 107],
    'product_id': [1, 2, 1, 3, 4, 2, 5],
    'quantity': [2, 1, 1, 3, 2, 1, 4],
    'sale_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21']
})

# Датасет 3: Відгуки
reviews = pd.DataFrame({
    'review_id': [201, 202, 203, 204, 205],
    'product_id': [1, 2, 3, 1, 4],
    'rating': [4.5, 4.0, 3.5, 5.0, 4.2],
    'review_text': ['Great laptop', 'Good phone', 'Average tablet', 'Excellent!', 'Nice watch']
})

print("\n1. Датасет продуктів:")
print(products)

print("\n2. Датасет продажів:")
print(sales)

print("\n3. Датасет відгуків:")
print(reviews)

print("\n🔗 Використання методу merge():")
print("-" * 30)

# Об'єднання продуктів і продажів
merged_sales = pd.merge(products, sales, on='product_id', how='inner')
print("Об'єднання products і sales:")
print(merged_sales)

# Додавання відгуків
full_data = pd.merge(merged_sales, reviews, on='product_id', how='left')
print("\nПовне об'єднання з відгуками:")
print(full_data)

print("\n🔗 Використання методу join():")
print("-" * 30)

# Встановлення індексів для join
products_indexed = products.set_index('product_id')
reviews_indexed = reviews.set_index('product_id')

# Використання join
joined_data = products_indexed.join(reviews_indexed, rsuffix='_review')
print("Результат join операції:")
print(joined_data)
