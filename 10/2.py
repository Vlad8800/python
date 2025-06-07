class Countdown:
    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

if __name__ == "__main__":
    # Приклад використання
    for n in Countdown(5):
        print(n)

    # Додаткові приклади
    print(list(Countdown(3)))  
    print(list(Countdown(0)))  
    print(list(Countdown(-3)))  
