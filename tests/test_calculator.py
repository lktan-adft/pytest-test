"""
Test cases for calculator module
"""
import pytest
from src.calculator import add, subtract, multiply, divide, is_even


class TestCalculator:
    """Test calculator functions"""
    
    def test_add_positive_numbers(self):
        """Test addition of positive numbers"""
        assert add(2, 3) == 5
        assert add(10, 5) == 15
    
    def test_add_negative_numbers(self):
        """Test addition with negative numbers"""
        assert add(-2, -3) == -5
        assert add(-10, 5) == -5
    
    def test_subtract(self):
        """Test subtraction"""
        assert subtract(10, 5) == 5
        assert subtract(5, 10) == -5
        assert subtract(0, 5) == -5
    
    def test_multiply(self):
        """Test multiplication"""
        assert multiply(3, 4) == 12
        assert multiply(-2, 5) == -10
        assert multiply(0, 100) == 0
    
    def test_divide(self):
        """Test division"""
        assert divide(10, 2) == 5
        assert divide(9, 3) == 3
        assert divide(7, 2) == 3.5
    
    def test_divide_by_zero(self):
        """Test division by zero raises ValueError"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)
    
    def test_is_even(self):
        """Test even number detection"""
        assert is_even(2) is True
        assert is_even(4) is True
        assert is_even(0) is True
        assert is_even(3) is False
        assert is_even(7) is False
        assert is_even(-2) is True


@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (5, 5, 10),
    (100, 200, 300),
    (-1, 1, 0),
])
def test_add_parametrized(a, b, expected):
    """Parametrized test for add function"""
    assert add(a, b) == expected


@pytest.mark.parametrize("n,expected", [
    (0, True),
    (2, True),
    (4, True),
    (1, False),
    (3, False),
    (99, False),
])
def test_is_even_parametrized(n, expected):
    """Parametrized test for is_even function"""
    assert is_even(n) == expected