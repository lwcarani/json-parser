import argparse
import unittest
from pathlib import Path
from json_parser import JsonParser

# TODO - update README with cli examples

PARENT_OUTPUT_PATH = Path(__file__).parent
TEST_PATH = PARENT_OUTPUT_PATH / Path("../tests")
print(TEST_PATH)


def pprint_dict(d: dict, depth: int = 0) -> None:
    print("{")
    for k, v in d.items():
        print(f'{" " * (depth + 1) * 4}"{k}": ', end="")
        if isinstance(v, dict):
            depth += 1
            pprint_dict(v, depth)
            depth -= 1
        elif isinstance(v, list):
            depth += 1
            pprint_list(v, depth)
            depth -= 1
        elif isinstance(v, str):
            print(f'"{v}"')
        else:
            print(v)
    print(" " * depth * 4, end="")
    print("}")


def pprint_list(L: list, depth: int = 0) -> None:
    print(" " * depth * 4, end="")
    print("[")
    for elem in L:
        if isinstance(elem, dict):
            depth += 1
            pprint_dict(elem, depth)
            depth -= 1
        elif isinstance(elem, list):
            depth += 1
            pprint_list(elem, depth)
            depth -= 1
        elif isinstance(elem, str):
            print(f'{" " * (depth + 1) * 4}"{elem}"')
        else:
            print(f'{" " * (depth + 1) * 4}{elem}')
    print(" " * depth * 4, end="")
    print("]")


if __name__ == "__main__":
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process text file(s).")

    # Add arguments for input file(s)
    parser.add_argument(
        "input_files",
        nargs="*",  # 0 or more input file(s)
        type=str,
        default=[],
        help="Path to the input file(s). Pass no file to read from user input.",
    )

    parser.add_argument(
        "-t", "--tests", action="store_true", help="run tests for json-parser"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # if args.tests:
    if True:
        loader = unittest.TestLoader()
        suite = loader.discover(str(TEST_PATH))
        runner = unittest.TextTestRunner()
        runner.run(suite)

    if len(args.input_files) == 0:
        user_input = []
        user_input.append(input())
    else:
        user_input: list = args.input_files

    jp = JsonParser()

    for ui in user_input:
        try:
            res = jp.parse_json(ui)
            pprint_dict(res)
            print(0)
        except Exception as e:
            print(e)
            print(1)
