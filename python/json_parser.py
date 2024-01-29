# load file --> f.read()
# handle incorrect trailing comma
# expect : to separate key/value pairs
# advance global ptr when processing string
# Use test runner pattern from command line like for OAM
# TODO - have main just be loading json from input path, or running tests, return 0 or 1


class JsonParser(object):
    def __init__(self, s: str = ""):
        self.ptr = 0
        self.s = s

    def reset_ptr(self):
        self.ptr = 0

    def skip_whitespace(self):
        for char in self.s:
            if char in [" ", "\n", "\t", "\r"]:
                self.ptr += 1
            else:
                break

        self.s = self.s[self.ptr :]

        self.reset_ptr()

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

    def parse_object(self):
        res = {}
        # TODO - add code to check for comma after the final closing bracket fo the JSON
        # add code to check for nested objects
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
            res[key] = val

        # drop final closing bracket
        self.s = self.s[1:]

        return res

    def parse_array(self):
        res = []
        # TODO - add code to check for comma after the final closing bracket fo the JSON
        # add code to check for nested objects
        self.skip_whitespace()

        if self.s[0] != "[":
            return

        self.s = self.s[1:]
        self.skip_whitespace()

        while self.s[0] != "]":
            elem = self.parse_item()
            self.skip_whitespace()
            self.parse_comma()
            res.append(elem)

        # drop final closing square bracket
        self.s = self.s[1:]

        return res

    def parse_string(self):
        res = ""

        if self.s[0] != '"':
            return

        self.ptr += 1

        while self.s[self.ptr] != '"':
            char = self.s[self.ptr]
            res += char
            self.ptr += 1

            # haven't encountered close quotes, return None
            if self.ptr >= len(self.s):
                raise SyntaxError("String is missing close quote")

        # advance ptr on input string json
        self.s = self.s[self.ptr + 1 :]

        self.reset_ptr()

        return res

    def parse_reserved_word(self):
        if self.s[:4] == "true":
            self.s = self.s[len("true") :]
            return True
        elif self.s[:5] == "false":
            self.s = self.s[len("false") :]
            return False
        elif self.s[:4] == "null":
            self.s = self.s[len("null") :]
            return "null"
        else:
            return

    def parse_number(self):
        res = ""
        first_char = self.s[0]
        e_or_dot_counter = 0
        neg_counter = 0

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
                self.reset_ptr()
                return int(float(res)) if float(res) % 1 == 0 else float(res)
            else:
                self.reset_ptr()
                return

        # advance ptr on input string json
        self.s = self.s[self.ptr :]
        self.reset_ptr()
        return int(float(res)) if float(res) % 1 == 0 else float(res)

    def parse_item(self):
        item = self.parse_string()

        if item is None:
            item = self.parse_number()
        if item is None:
            item = self.parse_reserved_word()
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
        res = self.parse_item()

        return res
