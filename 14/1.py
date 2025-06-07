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

# ========================================
# ЗАВДАННЯ 1: Аналіз одного датасету
# ========================================
print("\n📊 ЗАВДАННЯ 1: Аналіз датасету House Prices")
print("-" * 50)

# Використовуємо датасет про ціни на житло
try:
    # Завантажуємо датасет про ціни на житло з kaggle
    house_url = "https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv"
    df1 = pd.read_csv(house_url)
    print("✅ Датасет успішно завантажено з:", house_url)
except:
    # Альтернативний датасет, якщо перший недоступний
    print("⚠️ Використовуємо альтернативний датасет")
    np.random.seed(42)
    df1 = pd.DataFrame({
        'price': np.random.normal(300000, 100000, 500),
        'area': np.random.normal(150, 50, 500),
        'bedrooms': np.random.choice([1, 2, 3, 4, 5], 500),
        'location': np.random.choice(['Downtown', 'Suburb', 'Rural'], 500),
        'age': np.random.randint(0, 50, 500)
    })

print("\n1. Методи для роботи з DataFrame:")
print("-" * 30)

# head – перші 5 рядків
print("🔹 head() - Перші 5 рядків:")
print(df1.head())

# tail – останні 5 рядків
print("\n🔹 tail() - Останні 5 рядків:")
print(df1.tail())

# shape – розмір DataFrame
print(f"\n🔹 shape - Розмір DataFrame: {df1.shape}")

# columns – назви стовпців
print(f"\n🔹 columns - Назви стовпців: {list(df1.columns)}")

# dtypes – типи даних
print("\n🔹 dtypes - Типи даних:")
print(df1.dtypes)

# describe – статистика
print("\n🔹 describe() - Статистичний опис:")
print(df1.describe())

# loc, iloc – доступ до даних
print("\n🔹 loc/iloc - Приклад доступу до даних:")
print("Перші 3 рядки і перші 2 стовпці:")
print(df1.iloc[:3, :2])

# value_counts для категоріальних даних
categorical_cols = df1.select_dtypes(include=['object']).columns
if len(categorical_cols) > 0:
    print(f"\n🔹 value_counts() для стовпця '{categorical_cols[0]}':")
    print(df1[categorical_cols[0]].value_counts())

# unique – унікальні значення
print(f"\n🔹 Кількість унікальних значень у кожному стовпці:")
for col in df1.columns:
    print(f"{col}: {df1[col].nunique()}")

# corr – кореляція між числовими стовпцями
numeric_df = df1.select_dtypes(include=[np.number])
if len(numeric_df.columns) > 1:
    print("\n🔹 corr() - Матриця кореляції:")
    print(numeric_df.corr().round(3))

# sample – випадкова вибірка
print("\n🔹 sample() - Випадкові 3 рядки:")
print(df1.sample(3))
