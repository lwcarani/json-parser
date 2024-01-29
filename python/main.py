import argparse
from json_parser import JsonParser
from pprint_objects import pprint_dict

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

    # Parse the command-line arguments
    args = parser.parse_args()

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
