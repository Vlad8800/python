def filter_long_words(words: list[str]) -> list[str]:
    return list(filter(lambda word: len(word) > 3, words))

# Приклад використання:
print(filter_long_words(["So","Python", "is", "the", "women", "language"]))
