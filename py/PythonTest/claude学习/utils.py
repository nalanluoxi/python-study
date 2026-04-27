"""
Utility functions module
"""

def add_numbers(a, b):
    """Add two numbers and return the result."""
    return a + b

def multiply_numbers(a, b):
    """Multiply two numbers and return the result."""
    return a * b

def is_even(number):
    """Check if a number is even."""
    return number % 2 == 0

def factorial(n):
    """Calculate the factorial of a number."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result