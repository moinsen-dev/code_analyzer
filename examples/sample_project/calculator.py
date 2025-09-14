"""
Sample Python module for demonstration
"""

from typing import List


class Calculator:
    """A simple calculator class"""

    def __init__(self):
        self.history = []

    def add(self, a: int, b: int) -> int:
        """Add two numbers"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: int, b: int) -> int:
        """Subtract two numbers"""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers"""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a: int, b: int) -> float:
        """Divide two numbers"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def power(self, a: int, b: int) -> int:
        """Raise a to the power of b"""
        result = a**b
        self.history.append(f"{a} ** {b} = {result}")
        return result

    def get_history(self) -> List[str]:
        """Get calculation history"""
        return self.history


def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def factorial(n: int) -> int:
    """Calculate the factorial of n"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(1, 2))
    print(calc.multiply(3, 4))
    print(calc.power(2, 3))
    print(calc.get_history())
