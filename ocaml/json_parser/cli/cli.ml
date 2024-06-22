open Json_parser.Main
open Json_parser.Json
open Core

let read_file filename =
  In_channel.create filename

(* Take in a JSON file from CLI,
 open channel to read file, parse,
 then print the result *)
let () =
  let argv = Sys.get_argv () in
  let filename = argv.(1) in
  let file_content = read_file filename in
  let value = parse_program_from_channel file_content in
  match value with 
  | Some res -> print_value res; print_endline "";
  | None -> ()
  