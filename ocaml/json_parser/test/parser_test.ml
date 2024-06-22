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
