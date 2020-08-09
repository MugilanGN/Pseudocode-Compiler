# Pseudocode-Compiler

A modular Pseudocode compiler that compiles IGCSE pseudocode to LLVM IR. 

## Installlation

This project was built on Python 3.8.7

Run this to install the necessary dependencies:

```sh 
pip install llvmlite click
```

Next, you can clone this repository.

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
