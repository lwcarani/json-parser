import unittest
from unittest import TestCase
from parameterized.parameterized import parameterized
import os

from main import (
    parse_string,
)


class TestPyLispInterpreter(TestCase):
    """Test json-parser functionality."""

    # @parameterized.expand(
    #     [
    #         [os.path.join("test_files", "step1", "invalid1.json"), 1],
    #         [os.path.join("test_files", "step1", "invalid2.json"), 1],
    #         [os.path.join("test_files", "step1", "invalid3.json"), 1],
    #         [os.path.join("test_files", "step1", "invalid4.json"), 1],
    #         [os.path.join("test_files", "step1", "invalid5.json"), 1],
    #         [os.path.join("test_files", "step1", "valid1.json"), 0],
    #     ]
    # )
    # def test_step1(self, input_file_path: str, expected_result: int) -> None:
    #     res: int = lexer(input_file_path)
    #     self.assertEqual(res, expected_result)

    # @parameterized.expand(
    #     [
    #         [os.path.join("test_files", "step2", "invalid.json"), 1],
    #         [os.path.join("test_files", "step2", "invalid2.json"), 1],
    #         [os.path.join("test_files", "step2", "invalid3.json"), 1],
    #         [os.path.join("test_files", "step2", "valid.json"), 0],
    #         [os.path.join("test_files", "step2", "valid2.json"), 0],
    #     ]
    # )
    # def test_step2(self, input_file_path: str, expected_result: int) -> None:
    #     res: int = lexer(input_file_path)
    #     self.assertEqual(res, expected_result)

    @parameterized.expand(
        [
            ['"hello world"', "hello world"],
            [5, None],
        ]
    )
    def test_parse_string(self, s: str, expected_result: str | None) -> None:
        res: str | None = parse_string(s)
        self.assertEqual(res, expected_result)


if __name__ == "__main__":
    unittest.main()
