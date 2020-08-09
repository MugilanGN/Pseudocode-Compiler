# Pseudocode-Compiler

A modular Pseudocode compiler that compiles IGCSE pseudocode to LLVM IR. The IR can then be executed via other tools apart of the LLVM project.

## Installlation

This project was built on Python 3

Run this to install the necessary dependencies:

```sh 
pip install llvmlite click
```

Next, you can clone this repository.

## Language Specification

The Pseudocode syntax is similar to the IGCSE specification outlined here: https://filestore.aqa.org.uk/resources/computing/AQA-8520-TG-PC.PDF. However, there are notable differences between the AQA Pseudocode and this standard. This is because my school uses a variation of the AQA standard, so I sought to replicate it.

### Data Types

There are three data types that the user can use: integer, double, and string. In general, the following is true for operations:

- an Int and an Int will result in an Int
- a Double and a Double results in a Double
- a Double and an Int will result in a Double

Strings cannot be mixed with the other data types. However, two strings can be concatenated through the plus sign operator.

### Literals

Literals are values like ```5, "hello", 6.6```. A number is considered a double if it has a decimal point; otherwise it is taken as an int. String literals are surrounded in quotation marks.

### Variables

Variables are statically typed, but there is type inference, so the data type is not specified. Its static typing means that data cannot be assigned to a variable of a different type.

```
x = 5 + 3.0 // 5 + 3.0 = 8.0 so x is a double
x = 3 // this is illegal since an int is assigned to a double
```

Variables should not be redeclared with a different type like the above example. However, assigning a new value of the same type is syntactically identical to declaration and initialization. They should not be declared inside if statements either.

```
var = 6.0
var = var + 1
```

### If Statements

If statements follow the following format:

```
IF condition THEN
  statement //indents are optional
ELSE
  statement
ENDIF
```

The else can be ommited, leaving just the block that executes if it is true.

The condition takes the form of a comparison, such as:

```
x > 3
x + 1 < 40/x
5 % 2 == 0
```
### While Loops


### Output

The Output statement prints whatever it is given to the screen.

```OUTPUT "Hello World"```

It can be given variables, expressions, and array indices.

```
OUTPUT 5 + (4.0 * 3)
OUTPUT x + y[1]
OUTPUT "Hello" + " " + "World"
```



## Usage

### Running the Compiler
  
  Compiler.py is the program that will compile the Pseudocode. It can be ran through the CLI.

  Arguments in the CLI are typed like so: ```--output="file.ll"```
 
  - ```--filename``` is the path of the file containing the Pseudocode to be compiled . Defaults to "code.pc"
  - ```--output``` is the path of the file that will contain the generated IR. Defaults to "output.ll"
  - ```--help``` provides CLI help
  
  For example:
  
  ```sh
  python src/compiler.py --filename="ex/code.pc" --output="code.ll"
  ```
 
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
 
## Support

If you are having issues, please let me know. You can contact me at mugi.ganesan@gmail.com
