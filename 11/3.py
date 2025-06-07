from typing import Iterable

def capitalize_words(words: Iterable[str]) -> Iterable[str]:
    # Використовуємо map() і str.capitalize
    return map(str.capitalize, words)

# Приклади використання:
print(list(capitalize_words(["python", "java", "c++"])))           # ['Python', 'Java', 'C++']
print(tuple(capitalize_words(("hello", "world"))))                 # ('Hello', 'World')
print(list(capitalize_words([""])))                                # ['']
print(list(capitalize_words([])))                                  # []
