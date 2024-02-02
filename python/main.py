import argparse
import unittest
from pathlib import Path
from src.json_parser import JsonParser
from src.pprint_objects import pprint_dict

TEST_PATH = Path(__file__).parent / Path("tests")


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

    parser.add_argument("-t", "--tests", action="store_true", help="Run all tests.")

    # Parse the command-line arguments
    args = parser.parse_args()

    if args.tests:
        loader = unittest.TestLoader()
        suite = loader.discover(str(TEST_PATH))
        runner = unittest.TextTestRunner()
        runner.run(suite)

    if len(args.input_files) == 0:
        user_input = []
        print("No input file detected.")
        print("Manually type the JSON object you would like to parse: ")
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
