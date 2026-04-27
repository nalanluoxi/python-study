"""
Test module for utils.py
"""

import unittest
import sys
import os

# Add the parent directory to the Python path to import the utils module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import add_numbers, multiply_numbers, is_even, factorial


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_add_numbers(self):
        """Test the add_numbers function."""
        self.assertEqual(add_numbers(2, 3), 5)
        self.assertEqual(add_numbers(-1, 5), 4)
        self.assertEqual(add_numbers(0, 0), 0)
        self.assertEqual(add_numbers(1.5, 2.5), 4.0)
    
    def test_multiply_numbers(self):
        """Test the multiply_numbers function."""
        self.assertEqual(multiply_numbers(2, 3), 6)
        self.assertEqual(multiply_numbers(-1, 5), -5)
        self.assertEqual(multiply_numbers(0, 10), 0)
        self.assertEqual(multiply_numbers(1.5, 2), 3.0)
    
    def test_is_even(self):
        """Test the is_even function."""
        self.assertTrue(is_even(2))
        self.assertTrue(is_even(0))
        self.assertTrue(is_even(-4))
        self.assertFalse(is_even(1))
        self.assertFalse(is_even(-3))
        self.assertFalse(is_even(7))
    
    def test_factorial(self):
        """Test the factorial function."""
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(1), 1)
        self.assertEqual(factorial(5), 120)
        self.assertEqual(factorial(7), 5040)
        
        # Test negative input
        with self.assertRaises(ValueError):
            factorial(-1)
        
        with self.assertRaises(ValueError):
            factorial(-5)
    
    def test_factorial_large_number(self):
        """Test factorial with a larger number."""
        self.assertEqual(factorial(10), 3628800)


if __name__ == '__main__':
    unittest.main()