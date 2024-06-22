open Core
open Lexing

(*This function takes a string s and uses the standard library’s
Lexing module to create a lexer buffer from it. Think of that buffer
as the token stream. The function then lexes and parses the string
into an AST, using Lexer.read and Parser.prog. The function Lexer.read
corresponds to the rule named read in our lexer definition (lexer.mll), and the
function Parser.prog to the rule named prog in our parser definition (parser.mly).
Note how this code runs the lexer on a string; there is a
corresponding function from_channel to read from a file.*)

let colnum pos =
  (pos.pos_cnum - pos.pos_bol) - 1

let pos_string pos =
  let l = string_of_int pos.pos_lnum
  and c = string_of_int ((colnum pos) + 1) in
  "line " ^ l ^ ", column " ^ c

let parse' mode f s =
  let lexbuf = mode s in
  try
    f Lexer.read lexbuf
  with Parser.Error ->
    raise (Failure ("Parse error at " ^ (pos_string lexbuf.lex_curr_p)))

let parse_program_from_string s =
  parse' Lexing.from_string Parser.prog s

let parse_program_from_channel s =
  parse' Lexing.from_channel Parser.prog s
