import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Завантаження даних
url = "https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv"
df = pd.read_csv(url)

# 1. Загальна інформація про базу даних
print("Загальна інформація про датасет:")
print(df.info())

# 2. Перші 5 та останні 10 записів
print("\nПерші 5 записів:")
print(df.head())

print("\nОстанні 10 записів:")
print(df.tail(10))

# 3. Середня вартість житла (medv) для кожного району (chas)
# chas — це змінна, яка позначає наявність річки Чарльз (1 — є, 0 — немає)
average_medv = df.groupby("chas")["medv"].mean().reset_index()
average_medv.columns = ["chas", "average_medv"]

# 4. Вивід таблиці
print("\nСередня вартість житла за наявністю річки Чарльз (chas):")
print(average_medv)

# 5. Побудова стовпчикової діаграми
plt.figure(figsize=(6, 4))
sns.barplot(x="chas", y="average_medv", data=average_medv, palette="pastel")
plt.title("Середня вартість житла (medv) в залежності від розташування біля річки")
plt.xlabel("Наявність річки Чарльз (chas)")
plt.ylabel("Середня вартість житла (medv)")
plt.xticks(ticks=[0, 1], labels=["Ні (0)", "Так (1)"])
plt.tight_layout()
plt.show()
