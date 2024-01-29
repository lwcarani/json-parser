import unittest
from unittest import TestCase
from parameterized.parameterized import parameterized
from JsonParser.json_parser import JsonParser


class TestPyLispInterpreter(TestCase):
    """Test json-parser functionality."""

    @parameterized.expand(
        [
            ["test_files/step1/valid1.json", {}],
            [
                "test_files/step2/valid.json",
                {"key": "valuedfk/$#$#434546[]{}{f[d]fdaj,dfjwkejr"},
            ],
            ["test_files/step2/valid2.json", {"key": "value", "key2": "value"}],
            [
                "test_files/step3/valid.json",
                {
                    "key1": True,
                    "key2": False,
                    "key3": "null",
                    "key4": "value",
                    "key5": 101,
                },
            ],
            [
                "test_files/step4/valid.json",
                {"key": "value", "key-n": 101, "key-o": {}, "key-l": []},
            ],
            [
                "test_files/step4/valid2.json",
                {
                    "key": "value",
                    "key-n": 101,
                    "key-o": {"inner key": "inner value"},
                    "key-l": ["list value"],
                },
            ],
            [
                "test_files/step4/valid3.json",
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
    def test_valid_json_files(self, file_path: str, expected_result: dict) -> None:
        jp = JsonParser()
        res = jp.parse_json(file_path)
        self.assertEqual(res, expected_result)

    @parameterized.expand(
        [
            ["test_files/step1/invalid1.json"],
            ["test_files/step1/invalid2.json"],
            ["test_files/step1/invalid3.json"],
            ["test_files/step1/invalid4.json"],
            ["test_files/step1/invalid5.json"],
            ["test_files/step2/invalid.json"],
            ["test_files/step2/invalid2.json"],
            ["test_files/step2/invalid3.json"],
            ["test_files/step3/invalid.json"],
            ["test_files/step4/invalid.json"],
        ]
    )
    def test_invalid_json_files(self, file_path: str) -> None:
        jp = JsonParser()
        with self.assertRaises((SyntaxError, TypeError, IndexError)):
            jp.parse_json(file_path)


if __name__ == "__main__":
    unittest.main()
