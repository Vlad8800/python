from typing import Iterator

def float_range(start: float, stop: float, step: float) -> Iterator[float]:
    if step == 0:
        raise ValueError("step must not be zero")

    current = start
    if step > 0:
        while current < stop:
            yield round(current, 10)
            current += step
    else:
        while current > stop:
            yield round(current, 10)
            current += step

# Приклади використання
print(list(float_range(1.0, 2.0, 0.3)))        
print(list(float_range(5.0, 3.0, -0.5)))       
print(list(float_range(0.0, 1.0, 0.1))[:3])    
print(list(float_range(0.0, 0.0, 1.0)))        
print(list(float_range(1.0, 2.0, -1.0)))       
