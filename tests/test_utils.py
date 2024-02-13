"""Utils Tests"""

from unittest import TestCase
from random import randrange
from utils import (
    str2bool,
    is_valid_url,
    is_dangerous_regex,
    get_percentage,
)


class TestUtils(TestCase):
    """Utils Test Cases"""

    def test_str2bool(self):
        """Test String To Boolean Convertor Function"""

        for value in ("yes", "y", "1", "on", "ok"):
            self.assertEqual(first=True, second=str2bool(string=value))
        for value in ("no", "n", "0", "toto", "false"):
            self.assertEqual(first=False, second=str2bool(string=value))

    def test_is_valid_url(self):
        """Test URL Validator Function"""

        self.assertEqual(first=True, second=is_valid_url(url="https://example.com"))
        self.assertEqual(first=False, second=is_valid_url(url="http://example.com"))
        self.assertEqual(first=False, second=is_valid_url(url=""))

    def test_is_dangerous_regex(self):
        """Test Dangerous Regex Pattern Detection Function"""

        self.assertEqual(first=True, second=is_dangerous_regex(pattern=".*"))
        self.assertEqual(
            first=False, second=is_dangerous_regex(pattern="^release/docker/my-poc")
        )

    def test_get_percentage(self):
        """Test Get Percentage Function"""

        numbers_1: list[int] = [randrange(1, 100) for _ in range(10)]
        numbers_2: list[int] = [randrange(1, 100) for _ in range(10)]

        for number_1 in numbers_1:
            for number_2 in numbers_2:
                self.assertEqual(
                    first=get_percentage(nbr_a=number_1, nbr_b=number_2),
                    second=number_1 / number_2,
                )
        self.assertEqual(first=get_percentage(nbr_a=1, nbr_b=0), second=0)
