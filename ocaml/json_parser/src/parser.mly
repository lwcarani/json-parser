(* Parser source code *)

(* Header - code that is copied into the generated .ml file, 
in this case, into parser.ml *)

%{
(* open Json *) 
%}

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

(* The following declaration says to start with a rule
named `prog`. The declaration also says that parsing a
`prog` will return an OCaml value of type `Json.value option` *)
%start <Json.value option> prog
(* End the declaration section *)
%%

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
