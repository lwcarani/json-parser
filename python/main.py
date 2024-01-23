import re
import os
from pathlib import Path
import unittest

# load file --> f.read()
# handle incorrect trailing comma
# expect : to separate key/value pairs
# advance global ptr when processing string
# Use test runner pattern from command line like for OAM


def parse_string(s: str):
    res = ""
    first_char = s[0]
    last_char = s[-1]

    if first_char != '"' or last_char != '"':
        return

    for char in s[1:-1]:
        res += char

    return res


def parse_bool_or_null(s: str):
    match s:
        case "true":
            return True
        case "false":
            return False
        case "null":
            return "null"
        case _:
            return


def parse_number(s: str):
    res = ""
    first_char = s[0]
    e_or_dot_counter = 0
    neg_counter = 0

    if not first_char.isdigit() and first_char != "-":
        return

    for char in s:
        if char.isdigit():
            res += char
        elif char in {"e", "."} and e_or_dot_counter == 0:
            res += char
            e_or_dot_counter += 1
        elif char == "-" and neg_counter == 0:
            res += char
            neg_counter += 1
        else:
            return

    return res


def parse(s: str):
    res = parse_string(s)

    if res is None:
        res = parse_number(s)
    if res is None:
        res = parse_bool_or_null(s)

    return res


def load(s: str) -> dict:
    """
    Once JSON object has been lexed, parsed, and validated,
    deserialize the str instance 's' containing a JSON document
    to a Python object.
    """
    # ": Matches the double-quote character.
    # ([^"]+): Captures one or more characters that are not double-quotes.
    # "\s*:\s*": Matches the colon and space between the key and value with 0 or more whitespace characters (including spaces).
    # ([^"]+): Captures one or more characters that are not double-quotes.
    pattern = re.compile(r'"([^"]+)"\s*:\s*"([^"]+)"')
    # TODO value does not need to have double quotes

    matches = pattern.findall(s)

    result_dict = {key: value for key, value in matches}

    return result_dict


# f = open("test_files/step2/invalid.json", "r")
# json_tokens = f.readlines()
# f.close()
# # # json_tokens = [char.upper() for char in [token.strip().split(":") for token in json_tokens]]
# json_tokens
# json_tokens = [token.strip() for token in json_tokens]
# # json_tokens = [token.strip() for token in json_tokens]
# print(json_tokens)
# for token in json_tokens:
#     print(token)


def lexer(input_file: str) -> int:
    map_open_close_brackets = {")": "(", "}": "{", "]": "["}
    # Iterate over tokens, use a stack to keep
    # track of open/closed brackets
    stack = []

    f = open(input_file, "r")
    json_tokens: list = f.readlines()
    f.close()
    json_tokens: list = [
        t.replace("{", " { ").replace("}", " } ").strip().split(":")
        for t in json_tokens
    ]  # strip out newlines and whitespace

    if len(json_tokens) == 0:
        print("JSON object cannot be empty.")
        return 1

    if len(json_tokens) > 1 and (
        json_tokens[0][0] != "{" or json_tokens[-1][0] != "}"
    ):
        print("JSON object must start and end with open/closed curly braces.")
        return 1

    for sub_tokens in json_tokens:
        for token in sub_tokens:
            for char in token:
                if char in map_open_close_brackets.values():
                    stack.append(char)
                elif char in map_open_close_brackets.keys():
                    if (
                        len(stack) == 0
                        or stack.pop() != map_open_close_brackets[char]
                    ):
                        print(
                            "JSON object contains mismatched brackets ([], (), or {})"
                        )
                        return 1

    if len(stack) > 0:
        return 1

    # TODO - add a counter / check to see if last elements in JSON so we know that there shouldn't be trailing commas
    for i, sub_tokens in enumerate(json_tokens):
        if (
            len(sub_tokens) == 1
            and sub_tokens[0] == "{"
            or sub_tokens[0] == "}"
        ):
            continue

        if i == len(json_tokens) - 1:
            # TODO - don't just replace commas, need to account for trailing commas
            key = sub_tokens[0].strip()
            val = sub_tokens[1].strip()
        else:
            # TODO - don't just replace commas, need to account for trailing commas
            key = sub_tokens[0].strip().replace(",", "")
            val = sub_tokens[1].strip().replace(",", "")

        if (
            not key.startswith('"')
            or not key.endswith('"')
            or not val.startswith('"')
            or not val.endswith('"')
        ):
            return 1

    return 0
