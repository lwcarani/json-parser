# json_parser

## About
`json_parser` is a command line JSON parser written in OCaml. To build it, I used [Menhir](http://cristal.inria.fr/~fpottier/menhir/manual.pdf) - the standard parser generator for OCaml - and [ocamllex](https://ocaml.org/manual/5.2/lexyacc.html#s%3Aocamllex-overview) - the standard lexer generator for OCaml. Menhir and ocamllex were built to be used together, which makes them very easy to work with. After first building a JSON parser in Python, I chose to implement another JSON parser in OCaml because it's a great language for writing compilers - and learning Menhir and ocamllex is my first foray into the compiler world. 

I have `ocaml-base-compiler.5.0.0` installed on my windows machine, and specifically, I'm using Ubuntu on Windows Subsystem for Linux (WSL). I also have opam (OCaml's package manager) and dune (OCaml's build system) installed. 

## Project Structure
The project structure is:

```cmd
json_parser/
  cli/
    dune
    cli.ml
  src/
    dune
    json.ml
    lexer.mll
    parser.mly
    main.ml
  test/
    dune
    parser_test.ml
  dune-project
```

## Parsing

To write the JSON parser, we need to put all of the Menhir code we write into a file named `parser.mly`. The `.mly` file extension indicates that this file is input to Menhir (The 'y' actually alludes to yacc). This file contains the grammar definition for the "language" we want to parse. When we build our program with `dune build` later on, Menhir will generate the `parser.ml` file as output that actually contains the OCaml program that parses the language we specify here. 

Grammar definitions have four parts: header, declaration, rules, and trailer. 

### Header

The header appears between `%{` and `%}`. It is code that is literally copied into the generated `parser.ml` file. As an example, I've used it to open the `Json` module to show what it looks like, but since I don't need the `Json` module for this code, I've commented it out. 

```ocaml
(* Parser source code *)

(* Header - code that is copied into the generated .ml file, 
in this case, into parser.ml *)

%{
(* open Json *) 
%}
```

### Declarations

The declarations section begins by specifying what the lexical tokens of the language are. The tokens that have a `<type>` annotation appearing in them are declaring that they will carry some additional data along with them. In the case of `INT` that's an OCaml `int`. In the case of `STRING` that's an OCaml `string`. 

```ocaml
(* Declarations - define the lexical tokens of the language. 
The <type> specifications mean that a token carries a value. *)
%token <int> INT
%token <float> FLOAT
%token <string> STRING
%token TRUE
%token FALSE
%token NULL
%token LBRACKET
%token RBRACKET
%token LBRACE
%token RBRACE
%token COLON
%token COMMA
%token EOF
```

After declaring the tokens, we have to declare what the starting point is for parsing the language. The following declaration says to start with a rule (defined below) named `prog`. The declaration also says that parsing a `prog` will return an OCaml value of type `Json.value option`. Finally, `%%` ends the declarations section. 

```ocaml
(* The following declaration says to start with a rule
named `prog`. The declaration also says that parsing a
`prog` will return an OCaml value of type `Json.value option` *)
%start <Json.value option> prog
(* End the declaration section *)
%%
```

We define what a `Json.value` is in `src/json.ml`:

```ocaml
type value =
  (* use an association list to represent key value mappings of objects *)
  [ `Assoc of (string * value) list
  | `Bool of bool
  | `Float of float
  | `Int of int
  | `List of value list
  | `Null
  | `String of string ]
```

### Rules

The rules section contains production rules that resemble Backus–Naur form (BNF). The format of a rule is 

```
name: 
  | production1 { action1 }
  | production2 { action2 }
  | ...
  ;
```

The first rule, named `prog` has two productions. It says that `prog` is a valid `value`, or an `EOF` token. If `EOF`, we return `None` `option`. `v=value` says to match a `value` and bind the resulting value to `v`. The action simply says to return that value `v` wrapped in an `option`. 

The first rule, named `prog` (short for "program") has two production rules:

- `EOF { None }`

    - This rule matches when the input is empty (EOF stands for End Of File).
The semantic action `{ None }` means that when this rule matches, the parser will return `None`.
This handles the case where the input is empty, containing no JSON value.

- `v = value { Some v }`
    - This rule matches when the input consists of a single JSON value.
`v = value` means: match the value non-terminal (defined elsewhere in the grammar) and bind its result to the name `v`.
    - The semantic action `{ Some v }` wraps the parsed value in `Some`.
This handles the case where the input contains a valid JSON value.


The `prog` non-terminal is the starting symbol of the grammar. It essentially says:
    
- If the input is empty, return `None`.
- If the input contains a JSON value, parse it and return `Some` of that value.

This structure allows the parser to handle both empty inputs and inputs containing a single JSON value. The use of `Option` (`None` and `Some`) in the return type allows the caller to distinguish between these two cases.
The semicolon (`;`) at the end marks the end of the prog rule definition.

```ocaml
(* Rules - production rules (resembles BNF). 
The production is a sequence of symbols that the rule matches. 
A symbol is either a token or the name of another rule. The 
action is the OCaml value to return if a match occurs. Each 
production can bind the value carried by a symbol and use that
value in its action.*)

(* Curly braces contain a semantic action. We have two cases
for `prog`: either there's an EOF, which means the text is empty, 
and so there's no JSON value to read, so we return the OCaml value 
None; or we have an instance of the value nonterminal, which 
corresponds to a well-formed JSON value, and we wrap it with Some. *)
prog:
  | EOF       { None }
  | v = value { Some v }
  ;
```

The second rule named `value` has productions for all the possible value types we might encounter while parsing a JSON file. 
- The first production says to match a `LBRACE` (`{`), followed by `obj_values`, followed by a `RBRACE` (`}`), and bind the resulting association list to `obj`. 
- The second production says to match a `LBRACKET` (`[`), followed by `lst_values`, followed by a `RBRACKET` (`]`), and bind the resulting list to `lst`. 
- The third production, `i = INT`, says to match an INT token, bind the resulting OCaml `int` value to `i`, and return `Int i`. 
- The fourth production, `f = FLOAT`, says to match a FLOAT token, bind the resulting OCaml `float` value to `f`, and return `Float f`. 
- The fifth production, `s = STRING`, says to match a STRING token, bind the resulting OCaml `string` value to `s`, and return `String s`. 
- The sixth, seventh, and eighth productions match a `TRUE`, `FALSE`, or `NULL` token and return the corresponding type.

We also need to define what `obj_values` and `lst_values` are. `obj_values` are a list of `obj_value` separated by commas, where an `obj_value` is a key/value pair, separated by a colon, where the key is a `STRING` and the value is a `value`. `lst_values` are a list of `value` separated by commas.

```ocaml
value: 
  | LBRACE; obj = obj_values; RBRACE;     { `Assoc obj }
  | LBRACKET; lst = lst_values; RBRACKET; { `List lst }
  | i = INT                               { `Int i }
  | f = FLOAT                             { `Float f }
  | s = STRING                            { `String s }
  | TRUE                                  { `Bool true }
  | FALSE                                 { `Bool false }
  | NULL                                  { `Null }

(* [separated_list] is from the menhir standard library
https://gallium.inria.fr/~fpottier/menhir/manual.html#sec38
separated_list(sep, X): a possibly empty sequence of X’s separated with sep’s
*)
obj_values:
    obj = separated_list(COMMA, obj_value)    { obj } ;

obj_value:
    k = STRING; COLON; v = value              { (k, v) } ;

lst_values:
    lst = separated_list(COMMA, value)         { lst } ;
```

According to these rules, a JSON value is either:
- an object bracketed by curly braces (this allows for nested JSON objects)
- a list (array) bracketed by square braces
- a string, integer, float, bool, or null value

There can also be a trailer section after the rules, which like the header is OCaml code that is copied directly into the output `parser.ml` file. 

## Lexing

All of the `ocamllex` code we write goes into the `lexer.mll` file. The `.mll` file extension indicates that the file is intended as input to `ocamllex` (where the 'l' alludes to lexing). This file contains the lexer definition for the JSON parser, and Menhir processes this file and produces a file named `lexer.ml` as output. This file contains the OCaml program that lexes the language (in this case, a JSON parser). 

Similar to the parser, there are four parts to the lexer definition: header, identifiers, rules, and trailer. 

### Header

The header appears between `{` and `}`. It is code that will simply be copied directly into the `lexer.ml` file:

```ocaml
(* Lexer source code *)

(* Header *)
{
open Parser
}
```

Here, we've opened the `Parser` module, which is the code in `parser.ml` that was produced by Menhir from `parser.mly`. The reason we open it is so that we can use the token names we defined there, like `INT`, `TRUE`, `STRING`, `LBRACKET`, etc. This saves us from having to write `Parser.INT`, etc. 

### Identifiers

This next section contains identifiers, which are just regular expressions we have named. These will be used next in the rules section. 

Here are the identifiers we'll use for this JSON parser:

```ocaml
(* Identifiers *)
let digit = ['0'-'9']
let sign = ['-' '+']
let int = '-'? digit digit*
let exponent = ['e' 'E']
let float = '-'? digit+ '.'? digit+ (exponent sign? digit+)?
let whitespace = [' ' '\t']+
let newline = '\r' | '\n' | "\r\n"
```

This section isn't explicitly required, but naming the regular expressions improves readability when we get to the rules section. 

### Rules

The rules section of a lexer definition is written in a notation that resembles BNF. Specifically, a rule has the form

```
rule name = 
  parse
  | regexp1 { action1 }
  | regexp2 { action2 }
  | ...
```

Here, `rule` and `parse` are keywords. The lexer generated attempts to match against regular expressions *in the order they are listed*. When a regular expression matches, the lexer produces the token specified by its `action`. 

```ocaml
(* Rules *)
rule read =
  parse
  | whitespace { read lexbuf }
  | newline { Lexing.new_line lexbuf; read lexbuf }
  | int { INT (int_of_string (Lexing.lexeme lexbuf)) }
  | float { FLOAT (float_of_string (Lexing.lexeme lexbuf)) }
  | "true" { TRUE }
  | "false" { FALSE }
  | "null" { NULL }
  | '"' { STRING (read_string (Buffer.create 256) lexbuf) }
  | "[" { LBRACKET }
  | "]" { RBRACKET }
  | "{" { LBRACE }
  | "}" { RBRACE }
  | ":" { COLON }
  | "," { COMMA }
  | _ { raise (Failure ("Unexpected char: '" ^ Lexing.lexeme lexbuf ^ "'")) }
  | eof { EOF }

and read_string buf =
  parse
  | '"'       { (Buffer.contents buf) }
  | '\\' '/'  { Buffer.add_char buf '/'; read_string buf lexbuf }
  | '\\' '\\' { Buffer.add_char buf '\\'; read_string buf lexbuf }
  | [^ '"' '\\']+
    { Buffer.add_string buf (Lexing.lexeme lexbuf);
      read_string buf lexbuf
    }
  | _ { raise (Failure ("Illegal string character: " ^ Lexing.lexeme lexbuf)) }
  | eof { raise (Failure ("String is not terminated")) }
```

Most of the rules are self-explanatory, but let's go over the ones that are not:

- `whitespace { read lexbuf }` means that if whitespace (`let whitespace = [' ' '\t']+`) is matched, instead of returning a token the lexer should just call the `read` rule again and return whatever token results. In other words, whitespace will be skipped. 
- The two for ints and floats use the expression `Lexing.lexeme lexbuf`. This calls a function `lexeme` defined in the `Lexing` module, and returns the string that matched the regular expression. 
- The `eof` regular expression is a special one that matches the end of the file (or string) being lexed. 
- The rule `'"' { STRING (read_string (Buffer.create 256) lexbuf) }` handles string literals. When a double quote is encountered, it initiates string parsing by calling the `read_string` rule. This rule creates a new buffer (initial size 256) and passes it along with the lexing buffer to `read_string`.
The `read_string` rule is a separate lexer rule that handles the contents of string literals:

    - It accumulates characters into the buffer until it encounters a closing double quote.
    - It handles escape sequences like `\/` and `\\`.
    - It adds any non-special characters directly to the buffer.
    - If it encounters an illegal character or reaches the end of file without a closing quote, it raises an error.
    - When the closing quote is found, it returns the contents of the buffer as the string value.
    - This two-stage approach allows for efficient and correct handling of string literals, including proper processing of escape sequences and error detection.

Note that it's important that the string regular expression occur near the end. Otherwise, keywords like `true`, `false`, and `null`, would be lexed as strings rather than `TRUE`, `FALSE`, and `NULL` tokens. 

## Testing

I wrote a few tests for the program, which can be found in `test/parser_test.ml`:

```ocaml
(* Tests for parser *)

open OUnit2
open Json_parser.Main
open Json_parser.Json

let rec string_of_value_option = function
  | Some v -> string_of_value v
  | None -> "None"

and string_of_value = function
  | `Assoc lst -> "Assoc " ^ (String.concat ", " (List.map (fun (k, v) -> k ^ ": " ^ (string_of_value v)) lst))
  | `Bool b -> "Bool " ^ (string_of_bool b)
  | `Float f -> "Float " ^ (string_of_float f)
  | `Int i -> "Int " ^ (string_of_int i)
  | `List lst -> "List [" ^ (String.concat ", " (List.map string_of_value lst)) ^ "]"
  | `Null -> "Null"
  | `String s -> "String " ^ s

let parse_string_test name (s: string) (v: value option) =
  name >:: (fun _ -> assert_equal v (parse_program_from_string s) ~printer:string_of_value_option)
let tests = "test suite for parsing string" >::: [
  parse_string_test "Stanford" "\"Stanford\"" (Some (`String "Stanford"));
  parse_string_test "uscga2015" "\"uscga2015\"" (Some (`String "uscga2015"));
  parse_string_test "hello world" "\"hello world\"" (Some (`String "hello world"));
  parse_string_test "walruses eat seaweed?" "\"walruses eat seaweed?\"" (Some (`String "walruses eat seaweed?"));
  parse_string_test "x" "\"x\"" (Some (`String "x"));
  parse_string_test "foobar" "\"foobar\"" (Some (`String ("foobar")));
  parse_string_test "baz     baz!2312!@!#" "\"baz     baz!2312!@!#\"" (Some (`String ("baz     baz!2312!@!#")));
]
let _ = run_test_tt_main tests
  
let parse_int_test name (s: string) (v: value option) =
  name >:: (fun _ -> assert_equal v (parse_program_from_string s) ~printer:string_of_value_option)
let tests = "test suite for parsing int" >::: [
  parse_int_test "Zero" "0" (Some (`Int 0));
  parse_int_test "123" "123" (Some (`Int 123));
  parse_int_test "42" "42" (Some (`Int 42));
  parse_int_test "1000" "1000" (Some (`Int 1000));
  parse_int_test "-0" "-0" (Some (`Int 0));
  parse_int_test "-123" "-123" (Some (`Int (-123)));
]
let _ = run_test_tt_main tests

let parse_float_test name (s: string) (v: value option) =
  name >:: (fun _ -> assert_equal v (parse_program_from_string s) ~printer:string_of_value_option)
let tests = "test suite for parsing float" >::: [
  parse_float_test "0.0" "0.0" (Some (`Float 0.0));
  parse_float_test "123.0" "123.0" (Some (`Float 123.0));
  parse_float_test "42.0" "42.0" (Some (`Float 42.0));
  parse_float_test "1000.0" "1000.0" (Some (`Float 1000.0));
  parse_float_test "-123.0" "-123.0" (Some (`Float (-123.0)));
  parse_float_test "123.0e6" "123.0e6" (Some (`Float 123.0e6));
  parse_float_test "123.0e-6" "123.0e-6" (Some (`Float 123.0e-6));
  parse_float_test "-123.0e6" "-123.0e6" (Some (`Float (-123.0e6)));
  parse_float_test "-123.0e+6" "-123.0e+6" (Some (`Float (-123.0e6)));
  parse_float_test "-123.0e-6" "-123.0e-6" (Some (`Float (-123.0e-6)));
  parse_float_test "17e13" "17e13" (Some (`Float (17e13)));
]
let _ = run_test_tt_main tests

let parse_bool_test name (s: string) (v: value option) =
  name >:: (fun _ -> assert_equal v (parse_program_from_string s) ~printer:string_of_value_option)
let tests = "test suite for parsing boolean" >::: [
  parse_bool_test "true" "true" (Some (`Bool true));
  parse_bool_test "false" "false" (Some (`Bool false));
]
let _ = run_test_tt_main tests

let parse_null_test name (s: string) (v: value option) =
  name >:: (fun _ -> assert_equal v (parse_program_from_string s) ~printer:string_of_value_option)
let tests = "test suite for parsing null" >::: [
  parse_null_test "null" "null" (Some (`Null));
]
let _ = run_test_tt_main tests

let parse_list_test name (s: string) (v: value option) =
  name >:: (fun _ -> assert_equal v (parse_program_from_string s) ~printer:string_of_value_option)
let tests = "test suite for parsing array" >::: [
  parse_list_test "[1, 2, 3]" "[1, 2, 3]" (Some (`List [`Int 1; `Int 2; `Int 3;]));
  parse_list_test "[1.0, 2.0, 3.0]" "[1.0, 2.0, 3.0]" (Some (`List [`Float 1.0; `Float 2.0; `Float 3.0;]));
  parse_list_test "[1, 2.14, 3]" "[1, 2.14, 3]" (Some (`List [`Int 1; `Float 2.14; `Int 3;]));
  parse_list_test "[1, walrus stanford rowing 12345, 2.14, 3]" "[1, \"walrus stanford rowing 12345\", 2.14, 3]" (Some (`List [`Int 1; `String "walrus stanford rowing 12345"; `Float 2.14; `Int 3;]));
  parse_list_test "[1, 2.14, 3, go bears!!!]" "[1, 2.14, 3, \"go bears!!!\"]" (Some (`List [`Int 1; `Float 2.14; `Int 3; `String "go bears!!!"]));
]
let _ = run_test_tt_main tests

let parse_json_test name (s: string) (v: value option) =
  name >:: (fun _ -> assert_equal v (parse_program_from_string s) ~printer:string_of_value_option)
let tests = "test suite for parsing JSON object" >::: [
  parse_json_test "{\"key1\": 1, \"key2\": 2}" "{\"key1\": 1, \"key2\": 2}" (Some (`Assoc [("key1", `Int 1); ("key2", `Int 2)]));
  parse_json_test "{\"key1\": 1, \"key2\": 2, \"key3\": true}" "{\"key1\": 1, \"key2\": 2, \"key3\": true}" (Some (`Assoc [("key1", `Int 1); ("key2", `Int 2); ("key3", `Bool true)]));
  parse_json_test "{\"key1\": 1, \"key2\": 2, \"key3\": false}" "{\"key1\": 1, \"key2\": 2, \"key3\": false}" (Some (`Assoc [("key1", `Int 1); ("key2", `Int 2); ("key3", `Bool false)]));
  parse_json_test "{\"key1\": 1, \"key2\": 2, \"key3\": null}" "{\"key1\": 1, \"key2\": 2, \"key3\": null}" (Some (`Assoc [("key1", `Int 1); ("key2", `Int 2); ("key3", `Null)]));
  parse_json_test "{\"key1\": 1, \"key2\": 2.0}" "{\"key1\": 1, \"key2\": 2.0}" (Some (`Assoc [("key1", `Int 1); ("key2", `Float 2.0)]));
]
let _ = run_test_tt_main tests
```

To run all tests from the command line, simply run `dune exec test/parser_test.exe`:

```cmd
lwcarani@DESKTOP:~/json_parser$ dune exec test/parser_test.exe
.......                             
Ran: 7 tests in: 0.11 seconds.
OK
......
Ran: 6 tests in: 0.12 seconds.
OK
...........
Ran: 11 tests in: 0.13 seconds.
OK
..
Ran: 2 tests in: 0.11 seconds.
OK
.
Ran: 1 tests in: 0.11 seconds.
OK
.....
Ran: 5 tests in: 0.12 seconds.
OK
.....
Ran: 5 tests in: 0.11 seconds.
OK
```

## Running from CLI

The program also allows JSON parsing direct from the command line by calling `dune exec cli/cli.exe <filename>.json`:

```cmd
lwcarani@DESKTOP:~/json_parser$ dune exec cli/cli.exe test1.json
{ "a": 1, "b": 1.2e+44, "hello": "world", "true_key": true, "false_key": false, "null_key": null, "nested_json": { "foobar": "bar", "foobaz": "baz", "foo": 42, "foo_empty": {  },  }, "list": [ 1, 2, 3, 4, 5, 42,  ],  }
```

## Acknowledgements

Thanks to [Fernando Borretti](https://borretti.me/article/parsing-menhir-forth) and his blog post on using Menhir to build a parser for the Forth programming language. 

[This](https://dev.realworldocaml.org/parsing-with-ocamllex-and-menhir.html) guide was also helpful as I built my JSON parser. 

And of course, my favorite OCaml reference by [Michael Clarkson](https://cs3110.github.io/textbook/chapters/interp/parsing.html) was incredibly helpful, as always. 

And finally, thanks to [John Crickett](https://github.com/JohnCrickett) for the idea to build a JSON parser from his site, [Coding Challenges](https://codingchallenges.fyi/challenges/challenge-json-parser)!

Feedback, bug reports, issues, and pull requests welcome!
