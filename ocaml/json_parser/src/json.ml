(* Types to represent JSON values *)

type value =
  (* use an association list to represent key value mappings of objects *)
  [ `Assoc of (string * value) list
  | `Bool of bool
  | `Float of float
  | `Int of int
  | `List of value list
  | `Null
  | `String of string ]


(* Helper function for printing JSON values *)
let rec print_value json_value =
  match json_value with
  | `Assoc assoc_list -> 
      print_string "{ ";
      List.iter (fun (key, value) -> 
        print_string ("\"" ^ key ^ "\": ");
        print_value value;
        print_string ", "
      ) assoc_list;
      print_string " }"
  | `Bool b -> print_string (string_of_bool b)
  | `Float f -> print_string (string_of_float f)
  | `Int i -> print_string (string_of_int i)
  | `List value_list -> 
      print_string "[ ";
      List.iter (fun value -> 
        print_value value;
        print_string ", "
      ) value_list;
      print_string " ]"
  | `Null -> print_string "null"
  | `String s -> print_string ("\"" ^ s ^ "\"")
  