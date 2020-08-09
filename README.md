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

  Arguments in the CLI are typed like so: ```--output="file.ll"```
 
  - ```--filename``` is the path of the file containing the Pseudocode to be compiled . Defaults to "code.pc"
  - ```--output``` is the path of the file that will contain the generated IR. Defaults to "output.ll"
  - ```--help``` provides CLI help
  
  For example:
  
  ```sh
  python src/compiler.py --filename="ex/code.pc" --output="code.ll"
  ```
  
 ### Using a specific component
 
 Alternatively, the different components of the compiler can be used independently within python programs.
 
 ```python
 from pc_lexer import PC_Lexer
 from pc_parser import PC_Parser
 from ir_generator import Generator
 ```
 
## Support

If you are having issues, please let me know. You can contact me at mugi.ganesan@gmail.com
