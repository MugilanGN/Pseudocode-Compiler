# Pseudocode-Compiler

A modular Pseudocode compiler that compiles IGCSE pseudocode to LLVM IR. The IR can then be executed via other tools, like lli, that are a part of the LLVM project. Thus, an executable for any platform (Linux, Windows, Mac OS, etc.,) can be generated.

## Contents  
- [ Installation ](#Installation)
- [ Usage ](#Usage)
    - [ Compiling the Pseudocode ](#compiler)
    - [ Executing the Output](#ir)
- [ Language Specification ](#LanguageSpecification)
    - [ Data Types ](#types)
    - [ Literals ](#literals)
    - [ Variables ](#variables)
    - [ If Statements ](#if)
    - [ While Loops ](#while)
    - [ Arrays ](#arrays)
    - [ Output ](#output)
    - [ Input ](#input)
    - [ Functions ](#functions)
- [ Component Usage ](#components)
    - [ The Lexer ](#lexer)
    - [ The Parser ](#parser)
    - [ The IR Generator ](#generator)
- [ Support ](#Support)

<a name="Installation"></a>
## Installation

This project was built on Python 3

Run this to install the necessary dependencies:

```sh 
pip install llvmlite click
```

Next, you can clone this repository.

<a name="Usage"></a>
## Usage

<a name="compiler"></a>
### Compiling the Pseudocode
  
  Compiler.py is the program that will compile the Pseudocode. It can be ran through the CLI.

  Arguments in the CLI are typed like so: ```--output="file.ll"```
 
  - ```--filename``` is the path of the file containing the Pseudocode to be compiled . Defaults to "code.pc"
  - ```--output``` is the path of the file that will contain the generated IR. Defaults to "output.ll"
  - ```--help``` provides CLI help
  
  For example:
  
  ```sh
  python src/compiler.py --filename="ex/code.pc" --output="code.ll"
  ```
<a name="ir"></a>
### Executing the Compiled Output
 
Once the compiler has been executed, it will create a .ll file. However, it cannot be executed just yet. This is to provide flexibility with what you want to do with the generated LLVM IR. For example, you can compile the .ll file to machine code using LLC and GCC, or even compile it to JavaScript.

If you want to directly execute the .ll file, you can download the lli.exe file from the releases page (https://github.com/MugilanGN/Pseudocode-Compiler/releases). Then, you can add its file-path to Path. This will let you call it from the Command Line.

Now it's as simple as calling it on the .ll file from the Command Line:

```shell
lli output.ll
```

<a name="LanguageSpecification"></a>
## Language Specification

The Pseudocode syntax is similar to the IGCSE specification outlined here: https://filestore.aqa.org.uk/resources/computing/AQA-8520-TG-PC.PDF. However, there are notable differences between the AQA Pseudocode and this standard. This is because my school uses a variation of the AQA standard, so I sought to replicate it.

I will be using ```//``` for convenience to denote comments in the Pseudocode snippets, but keep in mind that they are not actually a part of the language, nor will they compile.

**WARNING: As of now there is no FOR loop. It might take some time to make one, but until then WHILE LOOPS are the only type of loop.**

<a name="types"></a>
### Data Types

There are three data types that the user can use: integer, double, and string. In general, the following is true for operations:

- an Int and an Int will result in an Int
- a Double and a Double results in a Double
- a Double and an Int will result in a Double

Strings cannot be mixed with the other data types. However, two strings can be concatenated through the plus sign operator.

<a name="literals"></a>
### Literals

Literals are values like ```5, "hello", 6.6```. A number is considered a double if it has a decimal point; otherwise it is taken as an int. String literals are surrounded in quotation marks.

<a name="variables"></a>
### Variables

Variables are statically typed (data types are set in stone). However, there is type inference, so the data type is not specified.

```
x = 5 + 3.0 // 5 + 3.0 = 8.0 so x is a double
y = "Hello" + " World" // y is now a string
```

The Static typing means that data cannot be assigned to a variable of a different type.

```
x = 5 // x is now an Int
x = 3.0 // Illegal since a Double is assigned to an Int
```

Variables should not be redeclared with a different type like the above example. However, assigning a new value of the same type is syntactically identical to declaration and initialization. They should not be declared inside if statements either.

```
var = 6.0
var = var + 1
```

<a name="if"></a>
### If Statements

If statements follow the following format:

```
IF condition THEN
  statements  //indents are optional
ELSE IF condition THEN
  statements
ELSE
  statements
ENDIF
```

The Else If clause is optional or can also be used as many times as necessary in a single If statement.

If statements can be nested. The Else statement is also optional and can be ommited entirely:

```
IF condition THEN
  statements
ENDIF
```

The condition takes the form of a comparison, such as:

```
x > 3
x + 1 < 40/x
5 % 2 == 0
```

<a name="while"></a>
### While Loops

A while loop can be represented like so:

```
WHILE condition DO
   statements
ENDWHILE
```

While statements can also be nested inside one another and combined with If statements flexibly.

<a name="arrays"></a>
### Arrays

#### Array Declaration

An array is declared with its data type, and then its name, followed by the number of elements it has. There are only Int and Double Arrays

```
INT x[5]
DOUBLE y[100 + (5 * 3)]
```

#### Array Elements

Array elements can be accessed through the square bracket notation:

```
y = x[0] + 3  // x[0] gives the 1st element of x
```

They can be assigned to just like variables, but the data assigned to that index must be of the same type as the array:

```
INT x[11]
x[10] = 345 + 3
```

<a name="output"></a>
### Output

The OUTPUT statement prints whatever it is given to the screen.

```OUTPUT "Hello World"```

It can be given variables, expressions, and array indices.

```
OUTPUT 5 + (4.0 * 3)
OUTPUT x + y[1]
OUTPUT "Hello" + " " + "World"
```

<a name="input"></a>
### Input

The INPUT statement takes user input and stores it to either a variable or an array index.

The variable to be input must be declared earlier in the code. This is to prevent ambiguity concerning the type of the variable.

```
x = 0
INPUT x // x is declared before, so it works

INPUT y // This is illegal, since y has not been declared or given a value before
```

Array indices can also be used instead of variables

```
INT x[5]
INPUT x[2] //stores input as the 3rd array value
```

It can only take Double and Int inputs.

<a name="functions"></a>
### Functions

Functions are defined like so:

```
TYPE SUBROUTINE name(TYPE arg, TYPE2 arg2, ...)
    statements
ENDSUBROUTINE
```

Type can be substituted with DOUBLE or INT. String and Array types are not supported yet as arguments or return values.

Each argument should be accompanied by its type. Alternatively, a function call also be defined with no arguments:

```
DOUBLE SUBROUTINE zero()
    OUTPUT 0.0
ENDSUBROUTINE

z = zero()
```

For example, this is a possible function:

```
INT SUBROUTINE add(INT x, INT y)
    RETURN x + y
ENDSUBROUTINE
```
If there is no return statement, the function will return either 0 or 0.0, depending on the type that the function should return.

This is the syntax to call a function:

```
z = function(arg, arg2, ...)
```

The function call can be used just like a normal variable. For example:

```
z = A[add(x,y) - 2]
OUTPUT add(3,z)
```

<a name="components"></a>
## Component Usage
 
<a name="lexer"></a>
### The Lexer

The lexer can be imported into your code like so:

```python
from pc_lexer import PC_Lexer
```

The PC_Lexer class can then be instantiated and built:

```python
lexer = PC_Lexer()
lexer.build()
```

To output the tokens of a string input, you can use the ```test``` method:

```python
lexer.test("INT") # will return the INT token
```

<a name="parser"></a>
### The Parser

The parser class resides in pc_parser:

```python
from pc_parser import PC_Parser
```

If no lexer is provided, it will default to using the PC_Lexer outlined above:

```python
parser = PC_Parser(lexer)
```

The ```parse``` method will output an AST of the string input:

```python
parser.parse("x = 5") #will return an AST with an assignment object
```

<a name="generator"></a>
### The IR Generator

The IR generator can be used standalone without the parser and lexer. It takes an AST and generates LLVM IR from it.

This is how you use it:

```python
from ir_generator import Generator

codegen = Generator() #creates a Generator object
```

The generator class has a ```generate``` method which takes in an AST and output file's name. If the name of the output file is not given, it defaults to "output.ll"

```python
module = codegen.generate(ast, output)
```

This will return an llvmlite module object, which can either be written into a file or used elsewhere

<a name="Support"></a>
## Support

If you are having issues, please let me know. You can contact me at mugi.ganesan@gmail.com
