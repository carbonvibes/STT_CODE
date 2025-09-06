#!/usr/bin/env python3
"""
A simple calculator application demonstrating basic Python programming.
This file is created for CS202 Lab 1 to demonstrate GitHub Actions with pylint.

Author: Lab Student
Date: September 1, 2025
Course: CS202 Software Tools and Techniques for CSE
"""

from typing import Union


class Calculator:
    """A simple calculator class with basic arithmetic operations."""

    def __init__(self):
        """Initialize the calculator."""
        self.history = []

    def add(self, num1: float, num2: float) -> float:
        """Add two numbers and return the result."""
        result = num1 + num2
        self.history.append(f"{num1} + {num2} = {result}")
        return result

    def subtract(self, num1: float, num2: float) -> float:
        """Subtract second number from first and return the result."""
        result = num1 - num2
        self.history.append(f"{num1} - {num2} = {result}")
        return result

    def multiply(self, num1: float, num2: float) -> float:
        """Multiply two numbers and return the result."""
        result = num1 * num2
        self.history.append(f"{num1} * {num2} = {result}")
        return result

    def divide(self, num1: float, num2: float) -> Union[float, str]:
        """Divide first number by second and return the result."""
        if num2 == 0:
            error_msg = "Error: Division by zero is not allowed"
            self.history.append(f"{num1} / {num2} = {error_msg}")
            return error_msg
        result = num1 / num2
        self.history.append(f"{num1} / {num2} = {result}")
        return result

    def get_history(self) -> list:
        """Return the calculation history."""
        return self.history

    def clear_history(self) -> None:
        """Clear the calculation history."""
        self.history.clear()


def main():
    """Main function to demonstrate calculator usage."""
    calc = Calculator()

    print("Welcome to the Simple Calculator!")
    print("This calculator supports basic arithmetic operations.")
    print("-" * 50)

    # Demonstrate calculator operations
    result1 = calc.add(10, 5)
    print(f"Addition: 10 + 5 = {result1}")

    result2 = calc.subtract(20, 8)
    print(f"Subtraction: 20 - 8 = {result2}")

    result3 = calc.multiply(7, 6)
    print(f"Multiplication: 7 * 6 = {result3}")

    result4 = calc.divide(15, 3)
    print(f"Division: 15 / 3 = {result4}")

    result5 = calc.divide(10, 0)
    print(f"Division by zero: 10 / 0 = {result5}")

    print("\nCalculation History:")
    for entry in calc.get_history():
        print(f"  {entry}")

    print("\nCalculator demonstration completed successfully!")


if __name__ == "__main__":
    main()
