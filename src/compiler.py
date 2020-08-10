#!/usr/bin/env python

'''
A simple program that chains together the various
programs into a functional Pseudocode to IR compiler 
'''

import click

from pc_parser import PC_Parser
from ir_generator import Generator


@click.command()

@click.option('--filename', 
              default="code.pc", 
              help="The file from which the pseudocode will be read"
             )

@click.option('--output',
              default="output.ll",
              help="The file which will contain the compiled code"
             )

def main(filename, output):
    
    input_file = open(filename)
    lines = [line.lstrip() for i, line in enumerate(input_file) if line.strip()]
    lines[-1] = lines[-1].rstrip()
    input_file.close()

    text = ''.join(lines)
    
    ast = PC_Parser().parse(text)
    ir = Generator().generate(ast, output)
    
    output_file = open(output,"w+")
    output_file.write(str(ir))
    output_file.close()
    
if __name__ == "__main__":
    main()
