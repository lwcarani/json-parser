# json-parser

## About
`json-parser` is a command line JSON parser written in Python. Running `jp` from the command line will allow the user to parse a JSON file from a provided file path, or manually type a JSON object in the command line to be parsed. Successful parsing returns `0`, unsuccessful parsing returns `1` along with an error message. 

## Instructions
For Windows, create a folder named `Aliases` in your C drive: `C:/Aliases`. Add this folder to PATH. Next, create a batch file that will execute when you call the specified alias. For example, on my machine, I have a batch file named `jp.bat` located at `C:/Aliases`, that contains the following script:

```bat
@echo off
echo.
python C:\...\json-parser\python\main.py %*
```

So now, when I type `jp` in the command prompt, this batch file will execute, which in turn runs the `json-parser` Python script.

## Examples

Running `jp` from the command line with no input file specified prompts the user to manually input a JSON object to parse:

```cmd
C:\> jp
No input file detected.
Manually type the JSON object you would like to parse:
>
```
So now, the user can type in a JSON object, and the program will return `1` if the JSON object was unable to be parsed (and print an error message), or the program will return `0` if the JSON object was able to be parsed, and print the resulting JSON object:

```cmd
C:\> jp
No input file detected.
Manually type the JSON object you would like to parse:
> { "key1": "value1", "key2": {"inner key": 42} }
{
    "key1": "value1"
    "key2": {
        "inner key": 42
    }
}
0
```
```cmd
C:\> jp
No input file detected.
Manually type the JSON object you would like to parse:
> { "key1": "value1", "key2": "value2", }
Trailing commas are not allowed.
1
```
```cmd
C:\> jp
No input file detected.
Manually type the JSON object you would like to parse:
> { "key1": "value1", key2: "value2" }
Keys must be valid strings.
1
```
```cmd
C:\> jp
No input file detected.
Manually type the JSON object you would like to parse:
> { "key1": true, "key2": false, "key3": 1e10 }
{
    "key1": True
    "key2": False
    "key3": 10000000000
}
0
```
You can also pass in a `-t` or `--tests` flag to run the test suite:
```cmd
C:\> jp -t
....................................................................................................................................................................................
----------------------------------------------------------------------
Ran 180 tests in 0.118s

OK
No input file detected.
Manually type the JSON object you would like to parse:
> 
```
```cmd
C:\> jp --tests
....................................................................................................................................................................................
----------------------------------------------------------------------
Ran 180 tests in 0.118s

OK
No input file detected.
Manually type the JSON object you would like to parse:
> 
```
You can run tests, and pass a path to the JSON file you want to parse:
```cmd
C:\> jp --tests step3/valid.json
....................................................................................................................................................................................
----------------------------------------------------------------------
Ran 180 tests in 0.119s

OK
{
    "key1": True
    "key2": False
    "key3": "null"
    "key4": "value"
    "key5": 101
}
0
```
And finally, you can pass in multiple JSON files to parse:
```cmd
C:\> jp step3/valid.json step4/valid2.json step4/valid.json
{
    "key1": True
    "key2": False
    "key3": "null"
    "key4": "value"
    "key5": 101
}
0
{
    "key": "value"
    "key-n": 101
    "key-o": {
        "inner key": "inner value"
    }
    "key-l":     [
        "list value"
    ]
}
0
{
    "key": "value"
    "key-n": 101
    "key-o": {
    }
    "key-l":     [
    ]
}
0
```

## Acknowledgements
Thanks to [John Crickett](https://github.com/JohnCrickett) for the idea from his site, [Coding Challenges](https://codingchallenges.fyi/challenges/challenge-json-parser)!

Feedback, bug reports, issues, and pull requests welcome!
