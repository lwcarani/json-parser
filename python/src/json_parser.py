import os
from enum import Enum
from src.errors import JsonParseError

WHITESPACE = [" ", "\n", "\t", "\r"]


class ReservedWords(Enum):
    TRUE = "true"
    FALSE = "false"
    NULL = "null"


class JsonParser(object):
    def __init__(self, s: str = "") -> None:
        self.ptr = 0
        self.s = s

    def reset_ptr(self) -> None:
        self.ptr = 0

    def skip_whitespace(self) -> None:
        for char in self.s:
            if char in WHITESPACE:
                self.ptr += 1
            else:
                break

        self.s = self.s[self.ptr :]

        self.reset_ptr()

    def parse_comma(self) -> None:
        if self.s[0] != ",":
            return

        self.s = self.s[1:]
        self.skip_whitespace()

        # if we encounter a closing bracket immediately
        # following a comma, the JSON is invalid
        if self.s[0] == "}":
            raise JsonParseError("Trailing commas are not allowed.")

    def parse_colon(self) -> None:
        if self.s[0] != ":":
            return

        self.s = self.s[1:]
        self.skip_whitespace()

    def parse_object(self) -> None | dict:
        res = {}
        self.skip_whitespace()

        if self.s[0] != "{":
            return

        self.s = self.s[1:]
        self.skip_whitespace()

        while self.s[0] != "}":
            key = self.parse_string()
            if key is None:
                raise JsonParseError("Keys must be valid strings.")
            self.skip_whitespace()
            self.parse_colon()
            # now that we've successfully parsed a key and colon,
            # parse the corresponding value for this key
            val = self.parse_value()
            self.skip_whitespace()
            self.parse_comma()
            res[key] = val

        # drop final closing bracket
        self.s = self.s[1:]

        return res

    def parse_array(self) -> None | list:
        res = []
        self.skip_whitespace()

        if self.s[0] != "[":
            return

        self.s = self.s[1:]
        self.skip_whitespace()

        while self.s[0] != "]":
            elem = self.parse_value()
            self.skip_whitespace()
            self.parse_comma()
            res.append(elem)

        # drop final closing square bracket
        self.s = self.s[1:]

        return res

    def parse_string(self) -> None | str:
        res = ""

        if self.s[0] != '"':
            return

        self.ptr += 1

        while self.s[self.ptr] != '"':
            char = self.s[self.ptr]
            res += char
            self.ptr += 1

            # no closing quotation encountered, invalid JSON format
            if self.ptr >= len(self.s):
                raise JsonParseError("String is missing close quote.")

        # advance ptr on input string json
        self.s = self.s[self.ptr + 1 :]

        self.reset_ptr()

        return res

    def parse_reserved_word(self) -> None | str | bool:
        if self.s[:4] == ReservedWords.TRUE.value:
            self.s = self.s[len(ReservedWords.TRUE.value) :]
            return True
        elif self.s[:5] == ReservedWords.FALSE.value:
            self.s = self.s[len(ReservedWords.FALSE.value) :]
            return False
        elif self.s[:4] == ReservedWords.NULL.value:
            self.s = self.s[len(ReservedWords.NULL.value) :]
            return ReservedWords.NULL.value
        else:
            return

    def parse_number(self) -> None | int | float:
        res = ""
        first_char = self.s[0]
        e_or_dot_counter = 0
        neg_counter = 0

        if not first_char.isdigit() and first_char != "-":
            return

        # parse one char at a time until the string 's' is empty,
        # or until we trigger a reason to break or return 'None'
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
            elif char in WHITESPACE + ["}", ",", "]"]:
                # end of number encountered, break and return the number
                break
            else:
                self.reset_ptr()
                return

        # advance ptr on input string
        self.s = self.s[self.ptr :]
        self.reset_ptr()
        return int(float(res)) if float(res) % 1 == 0 else float(res)

    def parse_value(self) -> None | int | float | str | bool | list | dict:
        item = self.parse_string()

        if item is None:
            item = self.parse_number()
        if item is None:
            item = self.parse_reserved_word()
        if item is None:
            item = self.parse_object()
        if item is None:
            item = self.parse_array()
        if item is None:
            raise JsonParseError("Value unable to be parsed: invalid entry.")

        return item

    def parse_json(self, s: str) -> dict:
        if os.path.exists(s):
            f = open(s, "r")
            self.s = f.read()
            f.close()
        else:
            self.s = s

        self.skip_whitespace()

        # do basic checks before parsing
        if len(self.s) == 0:
            raise JsonParseError("Empty JSON file detected: invalid entry.")
        if self.s[0] != "{":
            raise JsonParseError('JSON file is missing starting "{": invalid entry.')

        res: dict = self.parse_object()

        return res
