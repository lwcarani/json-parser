import unittest
from unittest import TestCase
from parameterized.parameterized import parameterized
import os
from pathlib import Path
from src.json_parser import JsonParser
from src.errors import JsonParseError

TEST_FILES_PATH = Path(__file__).parent / Path("test_files")


class TestPyLispInterpreter(TestCase):
    """Test json-parser functionality."""

    @parameterized.expand(
        [
            ['    {"key1": "value1"}', {"key1": "value1"}, ""],
            ["{}", {}, ""],
            ['    {  "key1"   :    "value1"}', {"key1": "value1"}, ""],
            [
                '    \n\n{\n\n    \n\t\t    "key1": "value1"}',
                {"key1": "value1"},
                "",
            ],
            ['{"key1": "value1"}', {"key1": "value1"}, ""],
            ['{"key1": 5}', {"key1": 5}, ""],
            ['{"key1": 5, "key2": 12e90}', {"key1": 5, "key2": 12e90}, ""],
            [
                '{"key1": 5, "key2": true, "key3": false, "key4": null}',
                {"key1": 5, "key2": True, "key3": False, "key4": "null"},
                "",
            ],
            ['{"key1": "5"}', {"key1": "5"}, ""],
            ['{"key1": null}', {"key1": "null"}, ""],
            ['{"key1": false}', {"key1": False}, ""],
            ['{"key1": true}', {"key1": True}, ""],
            ['{"key1": "true"}', {"key1": "true"}, ""],
            [
                '{"key1": "true", "key2": false}',
                {"key1": "true", "key2": False},
                "",
            ],
            [
                '{"key1": "true", "key2": false, "key3": 42, "key4": {}}',
                {"key1": "true", "key2": False, "key3": 42, "key4": {}},
                "",
            ],
            [
                '{"key1": "true", "key2": false, "key3": 42, "key4": {"k": "v", "k32": 56}}',
                {
                    "key1": "true",
                    "key2": False,
                    "key3": 42,
                    "key4": {"k": "v", "k32": 56},
                },
                "",
            ],
            [
                '{"key1": "true", "key2": {"k": 5}, "key3": 42, "key4": {}}',
                {
                    "key1": "true",
                    "key2": {"k": 5},
                    "key3": 42,
                    "key4": {},
                },
                "",
            ],
            [
                '{"key1": "true", "key2": {}, "key3": 42, "key4": {}}',
                {
                    "key1": "true",
                    "key2": {},
                    "key3": 42,
                    "key4": {},
                },
                "",
            ],
        ]
    )
    def test_parse_object(
        self, s: str, expected_result: dict, remaining_str: str
    ) -> None:
        jp = JsonParser(s)
        res = jp.parse_object()
        self.assertEqual(res, expected_result)
        self.assertEqual(remaining_str, jp.s)

    @parameterized.expand(
        [
            ['{"key1": value1"}'],
            ['{"key1": 5.5.5..5}'],
            ['{"key1": .5.5.55..}'],
            ['{"key1": +6}'],
            ['{"key1": +++6}'],
            ['{"key1": 63232323e43434.009-}'],
            ['{"key1": 34353434232332.2323232323434989.0}'],
            ['{"key1": value134"}'],
            ['{"key1": FALSE}'],
            ['{"key1": False}'],
            ['{"key1": True}'],
            ['{"key1": TRUE}'],
            ['{"key1": Null}'],
            ['{"key1": NULL}'],
            ['{"key1": NaN}'],
            ['{"key1": nan}'],
            ['{"key1": none}'],
            ['{"key1": NONE}'],
        ]
    )
    def test_raise_unable_parse_key_or_value(self, s: str):
        jp = JsonParser(s)
        with self.assertRaises(JsonParseError) as context:
            jp.parse_object()
        self.assertEqual(
            str(context.exception), "Value unable to be parsed: invalid entry."
        )

    @parameterized.expand(
        [
            ['"hello world'],
            ['"hello world la lala a<><>{}[]{}[]{}[]934839483$#$@$%@$%'],
        ]
    )
    def test_raise_missing_close_quote_error(self, s: str):
        jp = JsonParser(s)
        with self.assertRaises(JsonParseError) as context:
            jp.parse_string()
        self.assertEqual(str(context.exception), "String is missing close quote.")

    @parameterized.expand(
        [
            ['{"key1": false,}'],
            ['{"key1": true,}'],
            ['{"key1": 5,}'],
            ['{"key1": 5, "key2": "12e90",}'],
            ['{"key1": 5, "key2": true, "key3": false, "key4": null,}'],
        ]
    )
    def test_raise_trailing_comma_error(self, s: str):
        jp = JsonParser(s)
        with self.assertRaises(JsonParseError) as context:
            jp.parse_object()
        self.assertEqual(str(context.exception), "Trailing commas are not allowed.")

    @parameterized.expand(
        [
            ['"hello world"', "hello world", ""],
            ["hello world", None, "hello world"],
            ['hello world"', None, 'hello world"'],
            ["5", None, "5"],
            ["5.55", None, "5.55"],
            ["1e9", None, "1e9"],
            ["-5", None, "-5"],
            [
                '"valuedfk/$#$#434546[]{}{f[d]fdaj,dfjwkejr"',
                "valuedfk/$#$#434546[]{}{f[d]fdaj,dfjwkejr",
                "",
            ],
            ['    {"key1": "value1"}', None, '    {"key1": "value1"}'],
            ['{"key1": "value1"}', None, '{"key1": "value1"}'],
        ]
    )
    def test_parse_string(
        self, s: str, expected_result: str | None, remaining_str: str
    ) -> None:
        jp = JsonParser(s)
        res = jp.parse_string()
        self.assertEqual(res, expected_result)
        self.assertEqual(remaining_str, jp.s)

    @parameterized.expand(
        [
            ["[1, 2, 3]", [1, 2, 3], ""],
            [
                '["a", "b", "C", "D", "eeee"], foo bar foo',
                ["a", "b", "C", "D", "eeee"],
                ", foo bar foo",
            ],
            ["[]", [], ""],
            [
                "[[], [[], []], [], [{}, {}, {}]]",
                [[], [[], []], [], [{}, {}, {}]],
                "",
            ],
            [
                '[[1, 2, 3], {"k": 1}, 1e1909]',
                [[1, 2, 3], {"k": 1}, 1e1909],
                "",
            ],
            ["[1, 2, 3]", [1, 2, 3], ""],
            ["[1, 2, 3]   ", [1, 2, 3], "   "],
            [
                '[1, 2, 3, "a", "!", "2"], "key13": {}',
                [1, 2, 3, "a", "!", "2"],
                ', "key13": {}',
            ],
        ]
    )
    def test_parse_list(
        self, s: str, expected_result: str | None, remaining_str: str
    ) -> None:
        jp = JsonParser(s)
        res = jp.parse_list()
        self.assertEqual(res, expected_result)
        self.assertEqual(remaining_str, jp.s)

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
        jp = JsonParser(s)
        jp.skip_whitespace()
        self.assertEqual(jp.s, expected_result)

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
        jp = JsonParser(s)
        jp.parse_comma()
        self.assertEqual(jp.s, expected_result)

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
        jp = JsonParser(s)
        jp.parse_colon()
        self.assertEqual(jp.s, expected_result)

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
            ['-213431e9, "key2": ', -213431e9, ', "key2": '],
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
        jp = JsonParser(s)
        res = jp.parse_number()
        self.assertEqual(res, expected_result)
        self.assertEqual(remaining_str, jp.s)

    @parameterized.expand(
        [
            ['"hello world"', None, '"hello world"'],
            ['"hello world', None, '"hello world'],
            ["hello world", None, "hello world"],
            ['hello world"', None, 'hello world"'],
            ["5.5.55", None, "5.5.55"],
            ["5.5.5..5", None, "5.5.5..5"],
            [".5.5.55..", None, ".5.5.55.."],
            ["+6", None, "+6"],
            ["1eee9", None, "1eee9"],
            ["true", True, ""],
            ["false\t\n", False, "\t\n"],
            ['True, "key1": "value17"}', None, 'True, "key1": "value17"}'],
            ["False", None, "False"],
            ['null, "key17": 5e754}', "null", ', "key17": 5e754}'],
            ["Null", None, "Null"],
            ["None", None, "None"],
            ["NONE", None, "NONE"],
            ["nan", None, "nan"],
            ["NaN", None, "NaN"],
        ]
    )
    def test_parse_reserved_word(
        self, s: str, expected_result: str | None, remaining_str: str
    ) -> None:
        jp = JsonParser(s)
        res = jp.parse_reserved_word()
        self.assertEqual(res, expected_result)
        self.assertEqual(remaining_str, jp.s)

    @parameterized.expand(
        [
            ['null, "key17": 5e754}', "null", ', "key17": 5e754}'],
            ["true", True, ""],
            ["false\t\n", False, "\t\n"],
            ["5", 5, ""],
            ["5.55", 5.55, ""],
            ["1e9", 1e9, ""],
            ['-213431e9, "key2": ', -213431e9, ', "key2": '],
            ["1445e93232", 1445e93232, ""],
            ["-121e9", -121e9, ""],
            ['-121e9, "k": "value", ...}', -121e9, ', "k": "value", ...}'],
            [
                '"valuedfk/$#$#434546[]{}{f[d]fdaj,dfjwkejr"',
                "valuedfk/$#$#434546[]{}{f[d]fdaj,dfjwkejr",
                "",
            ],
        ]
    )
    def test_parse_value(
        self, s: str, expected_result: str | None, remaining_str: str
    ) -> None:
        jp = JsonParser(s)
        res = jp.parse_value()
        self.assertEqual(res, expected_result)
        self.assertEqual(remaining_str, jp.s)

    @parameterized.expand(
        [
            [os.path.join(TEST_FILES_PATH, "step1/valid1.json"), {}],
            [
                os.path.join(TEST_FILES_PATH, "step2/valid.json"),
                {"key": "valuedfk/$#$#434546[]{}{f[d]fdaj,dfjwkejr"},
            ],
            [
                os.path.join(TEST_FILES_PATH, "step2/valid2.json"),
                {"key": "value", "key2": "value"},
            ],
            [
                os.path.join(TEST_FILES_PATH, "step3/valid.json"),
                {
                    "key1": True,
                    "key2": False,
                    "key3": "null",
                    "key4": "value",
                    "key5": 101,
                },
            ],
            [
                os.path.join(TEST_FILES_PATH, "step4/valid.json"),
                {"key": "value", "key-n": 101, "key-o": {}, "key-l": []},
            ],
            [
                os.path.join(TEST_FILES_PATH, "step4/valid2.json"),
                {
                    "key": "value",
                    "key-n": 101,
                    "key-o": {"inner key": "inner value"},
                    "key-l": ["list value"],
                },
            ],
            [
                os.path.join(TEST_FILES_PATH, "step4/valid3.json"),
                {
                    "key": "value",
                    "key-n": 101,
                    "key-o": {
                        "inner key": "inner value",
                        "inner key 2": 42,
                        "inner key 3": {"inner inner key": 17},
                    },
                    "key-l": [
                        "list value",
                        1,
                        2,
                        3,
                        ["a", "b", "c"],
                        42,
                        14,
                        False,
                        True,
                        "null",
                    ],
                },
            ],
        ]
    )
    def test_valid_json_files(
        self, file_path_or_str: str, expected_result: dict
    ) -> None:
        jp = JsonParser()
        res = jp.parse_json(file_path_or_str)
        self.assertEqual(res, expected_result)

    @parameterized.expand(
        [
            [os.path.join(TEST_FILES_PATH, "step2/invalid.json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid2.json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid3json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid4json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid5json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid6json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid7json")],
            [os.path.join(TEST_FILES_PATH, "step3/invalid.json")],
            [os.path.join(TEST_FILES_PATH, "step4/invalid.json")],
        ]
    )
    def test_invalid_json_files(self, file_path: str) -> None:
        jp = JsonParser()
        with self.assertRaises(JsonParseError):
            jp.parse_json(file_path)

    @parameterized.expand(
        [
            [os.path.join(TEST_FILES_PATH, "step2/invalid2.json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid4.json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid5.json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid6.json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid7.json")],
        ]
    )
    def test_invalid_keys_json_files(self, file_path: str) -> None:
        jp = JsonParser()
        with self.assertRaises(JsonParseError) as context:
            jp.parse_json(file_path)
        self.assertEqual(str(context.exception), "Keys must be valid strings.")

    @parameterized.expand(
        [
            [os.path.join(TEST_FILES_PATH, "step2/invalid.json")],
            [os.path.join(TEST_FILES_PATH, "step2/invalid3.json")],
        ]
    )
    def test_trailing_commas_json_files(self, file_path: str) -> None:
        jp = JsonParser()
        with self.assertRaises(JsonParseError) as context:
            jp.parse_json(file_path)
        self.assertEqual(str(context.exception), "Trailing commas are not allowed.")

    @parameterized.expand(
        [
            [os.path.join(TEST_FILES_PATH, "step1/invalid.json")],
        ]
    )
    def test_missing_starting_open_bracket_json_files(self, file_path: str) -> None:
        jp = JsonParser()
        with self.assertRaises(JsonParseError) as context:
            jp.parse_json(file_path)
        self.assertEqual(
            str(context.exception),
            'JSON file is missing starting "{": invalid entry.',
        )

    @parameterized.expand(
        [
            [os.path.join(TEST_FILES_PATH, "step1/invalid2.json")],
        ]
    )
    def test_empty_json_file(self, file_path: str) -> None:
        jp = JsonParser()
        with self.assertRaises(JsonParseError) as context:
            jp.parse_json(file_path)
        self.assertEqual(
            str(context.exception),
            "Empty JSON file detected: invalid entry.",
        )

    @parameterized.expand(
        [
            [os.path.join(TEST_FILES_PATH, "step4/invalid5.json")],
        ]
    )
    def test_no_closing_bracket_json(self, file_path: str) -> None:
        jp = JsonParser()
        with self.assertRaises(JsonParseError) as context:
            jp.parse_json(file_path)
        self.assertEqual(
            str(context.exception),
            "Value unable to be parsed: invalid entry.",
        )

    @parameterized.expand(
        [
            [os.path.join(TEST_FILES_PATH, "step3/invalid.json")],
            [os.path.join(TEST_FILES_PATH, "step4/invalid.json")],
            [os.path.join(TEST_FILES_PATH, "step4/invalid1.json")],
            [os.path.join(TEST_FILES_PATH, "step4/invalid2.json")],
            [os.path.join(TEST_FILES_PATH, "step4/invalid3.json")],
            [os.path.join(TEST_FILES_PATH, "step4/invalid4.json")],
        ]
    )
    def test_invalid_values_json_files(self, file_path: str) -> None:
        jp = JsonParser()
        with self.assertRaises(JsonParseError) as context:
            jp.parse_json(file_path)
        self.assertEqual(
            str(context.exception), "Value unable to be parsed: invalid entry."
        )


if __name__ == "__main__":
    unittest.main()
