import unittest
from unittest import TestCase
from parameterized.parameterized import parameterized
import os

from main import JsonParser


class TestPyLispInterpreter(TestCase):
    """Test json-parser functionality."""

    @parameterized.expand(
        [
            ['    {"key1": "value1"}', {"key1": "value1"}],
            ['    {  "key1"   :    "value1"}', {"key1": "value1"}],
            [
                '    \n\n{\n\n    \n\t\t    "key1": "value1"}',
                {"key1": "value1"},
            ],
            ['{"key1": "value1"}', {"key1": "value1"}],
            ['{"key1": 5}', {"key1": 5}],
        ]
    )
    def test_parse_object(self, s: str, expected_result: dict) -> None:
        js = JsonParser(s)
        js.parse_object()
        self.assertEqual(js.json_dict, expected_result)

    @parameterized.expand(
        [
            ['"hello world"', "hello world", ""],
            ['"hello world', None, '"hello world'],
            ["hello world", None, "hello world"],
            ['hello world"', None, 'hello world"'],
            ["5", None, "5"],
            ["5.55", None, "5.55"],
            ["1e9", None, "1e9"],
            ["-5", None, "-5"],
            ['    {"key1": "value1"}', None, '    {"key1": "value1"}'],
            ['{"key1": "value1"}', None, '{"key1": "value1"}'],
        ]
    )
    def test_parse_string(
        self, s: str, expected_result: str | None, remaining_str: str
    ) -> None:
        js = JsonParser(s)
        res = js.parse_string()
        self.assertEqual(res, expected_result)
        self.assertEqual(remaining_str, js.s)

    @parameterized.expand(
        [
            ["       hello", "hello"],
            ["       hello   ", "hello   "],
            ["    \n   \n\t\t\t   hello ", "hello "],
            ["       hello ", "hello "],
            ["    \r\t    \n     \t    \n\n\n\n\n\n\n\n\n\n   hello", "hello"],
            ["       hello\n\n\n", "hello\n\n\n"],
            ["\nhello\n\n\n", "hello\n\n\n"],
            ['    {"key1": "value1"}', '{"key1": "value1"}'],
            ['   \n\n\n    \n\n {"key1": "value1"}', '{"key1": "value1"}'],
            ['   \n     \t \n\t   {"key1": "value1"}', '{"key1": "value1"}'],
            ['{"key1": "value1"}', '{"key1": "value1"}'],
            ['\n{"key1": "value1"}', '{"key1": "value1"}'],
            [' \t{"key1": "value1"}', '{"key1": "value1"}'],
        ]
    )
    def test_skip_whitespace(self, s: str, expected_result: str) -> None:
        js = JsonParser(s)
        js.skip_whitespace()
        self.assertEqual(js.s, expected_result)

    @parameterized.expand(
        [
            [",   hello", "hello"],
            [",       hello   ", "hello   "],
            [",    \n   \n\t\t\t   hello ", "hello "],
            [",       hello ", "hello "],
            [",    \r\t    \n     \t    \n\n\n\n\n\n\n\n\n\n   hello", "hello"],
            [",       hello\n\n\n", "hello\n\n\n"],
            [",\nhello\n\n\n", "hello\n\n\n"],
            [',    {"key1": "value1"}', '{"key1": "value1"}'],
            [',   \n\n\n    \n\n {"key1": "value1"}', '{"key1": "value1"}'],
            [',   \n     \t \n\t   {"key1": "value1"}', '{"key1": "value1"}'],
            [',{"key1": "value1"}', '{"key1": "value1"}'],
            [',\n{"key1": "value1"}', '{"key1": "value1"}'],
            [', \t{"key1": "value1"}', '{"key1": "value1"}'],
        ]
    )
    def test_parse_comma(self, s: str, expected_result: str) -> None:
        js = JsonParser(s)
        js.parse_comma()
        self.assertEqual(js.s, expected_result)

    @parameterized.expand(
        [
            [":   hello", "hello"],
            [":       hello   ", "hello   "],
            [":    \n   \n\t\t\t   hello ", "hello "],
            [":       hello ", "hello "],
            [":    \r\t    \n     \t    \n\n\n\n\n\n\n\n\n\n   hello", "hello"],
            [":       hello\n\n\n", "hello\n\n\n"],
            [":\nhello\n\n\n", "hello\n\n\n"],
            [':    {"key1": "value1"}', '{"key1": "value1"}'],
            [':   \n\n\n    \n\n {"key1": "value1"}', '{"key1": "value1"}'],
            [':   \n     \t \n\t   {"key1": "value1"}', '{"key1": "value1"}'],
            [':{"key1": "value1"}', '{"key1": "value1"}'],
            [':\n{"key1": "value1"}', '{"key1": "value1"}'],
            [': \t{"key1": "value1"}', '{"key1": "value1"}'],
        ]
    )
    def test_parse_colon(self, s: str, expected_result: str) -> None:
        js = JsonParser(s)
        js.parse_colon()
        self.assertEqual(js.s, expected_result)

    @parameterized.expand(
        [
            ['"hello world"', None, '"hello world"'],
            ['"hello world', None, '"hello world'],
            ["hello world", None, "hello world"],
            ['hello world"', None, 'hello world"'],
            ["5", 5, ""],
            ["5.55", 5.55, ""],
            ["5.5.55", None, "5.5.55"],
            ["5.5.5..5", None, "5.5.5..5"],
            [".5.5.55..", None, ".5.5.55.."],
            ["+6", None, "+6"],
            ["1e9", 1e9, ""],
            ["-213431e9", -213431e9, ""],
            ["1445e93232", 1445e93232, ""],
            ["-121e9", -121e9, ""],
            ["-121e9.87", None, "-121e9.87"],
            ["1eee9", None, "1eee9"],
            ["1e9e", None, "1e9e"],
            ["-5", -5, ""],
        ]
    )
    def test_parse_number(
        self, s: str, expected_result: str | None, remaining_str: str
    ) -> None:
        js = JsonParser(s)
        res = js.parse_number()
        self.assertEqual(res, expected_result)
        self.assertEqual(remaining_str, js.s)

    # @parameterized.expand(
    #     [
    #         ['"hello world"', None],
    #         ['"hello world', None],
    #         ["hello world", None],
    #         ['hello world"', None],
    #         ["5.5.55", None],
    #         ["5.5.5..5", None],
    #         [".5.5.55..", None],
    #         ["+6", None],
    #         ["1eee9", None],
    #         ["true", True],
    #         ["false", False],
    #         ["True", None],
    #         ["False", None],
    #         ["null", "null"],
    #         ["Null", None],
    #         ["None", None],
    #         ["NONE", None],
    #         ["nan", None],
    #         ["NaN", None],
    #     ]
    # )
    # def test_parse_reserved_word(
    #     self, s: str, expected_result: str | None
    # ) -> None:
    #     res: str | None = parse_reserved_word(s)
    #     self.assertEqual(res, expected_result)

    # @parameterized.expand(
    #     [
    #         ['"hello world"', "hello world"],
    #         ['"hello world', None],
    #         ["hello world", None],
    #         ['hello world"', None],
    #         ["5", 5],
    #         ["5.55", 5.55],
    #         ["5.5.55..", None],
    #         ["..5.5.55", None],
    #         ["+6", None],
    #         ["1e9", 1e9],
    #         ["1eee9", None],
    #         ["1e9e", None],
    #         ["-213431e9", -213431e9],
    #         ["1445e93232", 1445e93232],
    #         ["-121e9", -121e9],
    #         ["-121e9.87", None],
    #         ["-5", -5],
    #         ["true", True],
    #         ["false", False],
    #         ['"true"', "true"],
    #         ['"false"', "false"],
    #         ["True", None],
    #         ["False", None],
    #         ["null", "null"],
    #         ["Null", None],
    #         ["None", None],
    #         ["NONE", None],
    #         ["nan", None],
    #         ["NaN", None],
    #     ]
    # )
    # def test_parse_item(self, s: str, expected_result: str | None) -> None:
    #     js = JsonParser(s)
    #     res = js.parse_item()
    #     self.assertEqual(res, expected_result)


if __name__ == "__main__":
    unittest.main()
