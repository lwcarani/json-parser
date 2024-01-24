import unittest
from unittest import TestCase
from parameterized.parameterized import parameterized
import os

from main import (
    parse,
    parse_string,
    parse_number,
    parse_bool_or_null,
    skip_whitespace,
)


class TestPyLispInterpreter(TestCase):
    """Test json-parser functionality."""

    @parameterized.expand(
        [
            ['"hello world"', "hello world"],
            ['"hello world', None],
            ["hello world", None],
            ['hello world"', None],
            ["5", None],
            ["5.55", None],
            ["1e9", None],
            ["-5", None],
        ]
    )
    def test_parse_string(self, s: str, expected_result: str | None) -> None:
        res: str | None = parse_string(s)
        self.assertEqual(res, expected_result)

    @parameterized.expand(
        [
            ["       hello", "hello"],
            ["       hello   ", "hello   "],
            ["    \n   \n\t\t\t   hello ", "hello "],
            ["       hello ", "hello "],
            ["    \r\t    \n     \t    \n\n\n\n\n\n\n\n\n\n   hello", "hello"],
            ["       hello\n\n\n", "hello\n\n\n"],
            ["\nhello\n\n\n", "hello\n\n\n"],
        ]
    )
    def test_skip_whitespace(self, s: str, expected_result: str) -> None:
        res: str = skip_whitespace(s)
        self.assertEqual(res, expected_result)

    @parameterized.expand(
        [
            ['"hello world"', None],
            ['"hello world', None],
            ["hello world", None],
            ['hello world"', None],
            ["5", 5],
            ["5.55", 5.55],
            ["5.5.55", None],
            ["5.5.5..5", None],
            [".5.5.55..", None],
            ["+6", None],
            ["1e9", 1e9],
            ["-213431e9", -213431e9],
            ["1445e93232", 1445e93232],
            ["-121e9", -121e9],
            ["-121e9.87", None],
            ["1eee9", None],
            ["1e9e", None],
            ["-5", -5],
        ]
    )
    def test_parse_number(self, s: str, expected_result: str | None) -> None:
        res: str | None = parse_number(s)
        self.assertEqual(res, expected_result)

    @parameterized.expand(
        [
            ['"hello world"', None],
            ['"hello world', None],
            ["hello world", None],
            ['hello world"', None],
            ["5.5.55", None],
            ["5.5.5..5", None],
            [".5.5.55..", None],
            ["+6", None],
            ["1eee9", None],
            ["true", True],
            ["false", False],
            ["True", None],
            ["False", None],
            ["null", "null"],
            ["Null", None],
            ["None", None],
            ["NONE", None],
            ["nan", None],
            ["NaN", None],
        ]
    )
    def test_parse_bool_or_null(
        self, s: str, expected_result: str | None
    ) -> None:
        res: str | None = parse_bool_or_null(s)
        self.assertEqual(res, expected_result)

    @parameterized.expand(
        [
            ['"hello world"', "hello world"],
            ['"hello world', None],
            ["hello world", None],
            ['hello world"', None],
            ["5", 5],
            ["5.55", 5.55],
            ["5.5.55..", None],
            ["..5.5.55", None],
            ["+6", None],
            ["1e9", 1e9],
            ["1eee9", None],
            ["1e9e", None],
            ["-213431e9", -213431e9],
            ["1445e93232", 1445e93232],
            ["-121e9", -121e9],
            ["-121e9.87", None],
            ["-5", -5],
            ["true", True],
            ["false", False],
            ['"true"', "true"],
            ['"false"', "false"],
            ["True", None],
            ["False", None],
            ["null", "null"],
            ["Null", None],
            ["None", None],
            ["NONE", None],
            ["nan", None],
            ["NaN", None],
        ]
    )
    def test_parse(self, s: str, expected_result: str | None) -> None:
        res: str | None = parse(s)
        self.assertEqual(res, expected_result)


if __name__ == "__main__":
    unittest.main()
