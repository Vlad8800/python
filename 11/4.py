from typing import Callable

# Перевірки окремими функціями
def has_uppercase(password: str) -> bool:
    return any(c.isupper() for c in password)

def has_digit(password: str) -> bool:
    return any(c.isdigit() for c in password)

def is_long_enough(password: str) -> bool:
    return len(password) >= 8

def has_special_char(password: str) -> bool:
    special_chars = "!@#$%^&*()"
    return any(c in special_chars for c in password)

def no_spaces(password: str) -> bool:
    return ' ' not in password

# Основна функція перевірки
def validate_password(password: str) -> bool:
    rules: list[Callable[[str], bool]] = [
        has_uppercase,
        has_digit,
        is_long_enough,
        has_special_char,
        no_spaces
    ]
    return all(rule(password) for rule in rules)

# Приклади
print(validate_password("StrongPass1!"))     # True
print(validate_password("weakpass"))         # False
print(validate_password("Short7!"))          # False
print(validate_password("With Space1!"))     # False
print(validate_password("NoSpecialChar1"))   # False
