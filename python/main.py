import re
import os
from pathlib import Path
import unittest

# load file --> f.read()
# handle incorrect trailing comma
# expect : to separate key/value pairs
# advance global ptr when processing string
# Use test runner pattern from command line like for OAM


class JsonParser(object):
    def __init__(self, s: str = ""):
        self.ptr = 0
        self.s = s
        self.json_dict = {}

    def skip_whitespace(self):
        self.ptr = 0
        for char in self.s:
            if char in [" ", "\n", "\t", "\r"]:
                self.ptr += 1
            else:
                break

        self.s = self.s[self.ptr :]

    def parse_comma(self):
        if self.s[0] != ",":
            return

        self.s = self.s[1:]
        self.skip_whitespace()

        if self.s[0] == "}":
            raise SyntaxError("Trailing commas are not allowed.")

    def parse_colon(self):
        if self.s[0] != ":":
            return

        self.s = self.s[1:]
        self.skip_whitespace()

    # add depth param to track nested objects
    def parse_object(self):
        self.skip_whitespace()

        if self.s[0] != "{":
            return

        self.s = self.s[1:]
        self.skip_whitespace()

        while self.s[0] != "}":
            key = self.parse_item()
            self.skip_whitespace()
            self.parse_colon()
            val = self.parse_item()
            self.skip_whitespace()
            self.parse_comma()
            self.json_dict[key] = val

    def parse_array(self):
        return

    def parse_string(self):
        res = ""

        if self.s[0] != '"':
            return

        # TODO - better management of global ptr
        self.ptr = 1

        while self.s[self.ptr] != '"':
            char = self.s[self.ptr]
            res += char
            self.ptr += 1

            # haven't encountered close quotes, return None
            if self.ptr >= len(self.s):
                return

        # advance ptr on input string json
        self.s = self.s[self.ptr + 1 :]

        return res

    def parse_reserved_word(self, reserved_word: str):
        match reserved_word:
            case "true":
                self.s = self.s[len(reserved_word) :]
                return True
            case "false":
                self.s = self.s[len(reserved_word) :]
                return False
            case "null":
                self.s = self.s[len(reserved_word) :]
                return "null"
            case _:
                return

    def parse_number(self):
        res = ""
        first_char = self.s[0]
        e_or_dot_counter = 0
        neg_counter = 0
        self.ptr = 0

        if not first_char.isdigit() and first_char != "-":
            return

        for char in self.s:
            if char.isdigit():
                res += char
                self.ptr += 1
            elif char in {"e", "."} and e_or_dot_counter == 0:
                res += char
                e_or_dot_counter += 1
                self.ptr += 1
            elif char == "-" and neg_counter == 0:
                res += char
                neg_counter += 1
                self.ptr += 1
            elif char in ["}", ",", "]"]:
                # advance ptr on input string json
                self.s = self.s[self.ptr :]
                return int(float(res)) if float(res) % 1 == 0 else float(res)
            else:
                return

        # advance ptr on input string json
        self.s = self.s[self.ptr :]
        return int(float(res)) if float(res) % 1 == 0 else float(res)

    def parse_item(self):
        item = self.parse_string()

        if item is None:
            item = self.parse_number()
        # if item is None:
        #     item = self.parse_reserved_word()
        if item is None:
            item = self.parse_object()
        if item is None:
            item = self.parse_array()

        return item

    def parse_json(self, s: str, kind: str) -> dict:
        if kind == "file_path":
            f = open(s, "r")
            self.s = f.read()
            f.close()
        if kind == "str":
            self.s = s

        self.skip_whitespace()
        self.parse_item()

        return self.json_dict


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
