import re

import pc_ast

from ply import lex
from ply import yacc

from llvmlite import ir

tokens = (
    'VAR',
    'DOUBLE','STRING',
    'INPUT','OUTPUT',
    'IF','THEN','ELSE','ENDIF',
    'WHILE','DO','ENDWHILE',
    'FOR','TO','NEXT',
    'DOUBLE_CONST','STRING_CONST',
    'PLUS','MINUS','TIMES','DIVIDE','EQUALS',
    'LPAREN','RPAREN', 'NEWLINE'
    )

reserved = r''.join(["(?!"+keyword+")" for keyword in tokens])

t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_EQUALS    = r'='

t_LPAREN    = r'\('
t_RPAREN    = r'\)'

t_DOUBLE    = 'DOUBLE'
t_STRING    = 'STRING'

t_INPUT     = 'INPUT'
t_OUTPUT    = 'OUTPUT'

t_IF        = 'IF'
t_THEN      = 'THEN'
t_ELSE      = 'ELSE'
t_ENDIF     = 'ENDIF'

t_WHILE     = 'WHILE'
t_DO        = 'DO'
t_ENDWHILE  = 'ENDWHILE'

t_FOR       = 'FOR'
t_TO        = 'TO'
t_NEXT      = 'NEXT'

t_VAR       = reserved + r'[a-zA-Z_][a-zA-Z0-9_]*'

t_ignore    = " \t"

def t_DOUBLE_CONST(t):
    r'\d+\.?\d*'
    t.value = float(t.value)
    return t

def t_STRING_CONST(t):
    r'".*?"'
    t.value = t.value[1:len(t.value)-1]
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    return t

def t_error(t):
    print(f"Illegal character {t.value[0]!r}")
    t.lexer.skip(1)

lex.lex()

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

def p_statement(p):
    '''statement : stmt_list'''
    
    ast.append(p[1])

def p_stmt_list(p):
    '''stmt_list : simple_stmt
                 | stmt_list NEWLINE simple_stmt'''
    
    if len(p) == 2:
        p[0] = [p[1]]
    
    elif len(p) > 3:
        p[0] = p[1] + [p[3]]
    
def p_if_stmt(p):
    '''if_stmt : IF expression THEN NEWLINE stmt_list NEWLINE ENDIF
               | IF expression THEN NEWLINE stmt_list NEWLINE ELSE NEWLINE stmt_list NEWLINE ENDIF'''
    
    if len(p) == 8:
        p[0] = pc_ast.If(p[2],p[5],None)
        
    elif len(p) == 12:
        p[0] = pc_ast.If(p[2],p[5],p[9])
        
def p_while_stmt(p):
    '''while_stmt : WHILE expression DO NEWLINE stmt_list NEWLINE ENDWHILE'''
    
    p[0] = pc_ast.While(p[2],p[5])
    
def p_for_stmt(p):
    '''for_stmt : FOR assignment_stmt TO expression NEWLINE stmt_list NEWLINE NEXT VAR'''
    
    p[0] = pc_ast.For(p[2],p[4],p[6])
    
def p_simple_stmt(p):
    '''simple_stmt : expression
                   | assignment_stmt
                   | if_stmt
                   | while_stmt
                   | for_stmt
                   | io_stmt'''
    
    p[0] = p[1]
    
def p_assignment_stmt(p):
    '''assignment_stmt : VAR EQUALS expression
                       | DOUBLE VAR EQUALS expression
                       | STRING VAR EQUALS expression'''
 
    if len(p) == 5:
        
        if p[1] == 'DOUBLE':
            p[0] = pc_ast.Assignment(p[3],float,p[2],p[4])
        
        elif p[1] == 'STRING':
            p[0] = pc_ast.Assignment(p[3],str,p[2],p[4])
        
    elif len(p) == 4:
        
        p[0] = pc_ast.Assignment(p[2],'dynamic',p[1],p[3])
        
def p_io_stmt(p):
    '''io_stmt : INPUT VAR
               | OUTPUT expression'''
    
    if p[1] == 'INPUT':
        p[0] = pc_ast.Input(p[2])
        
    elif p[1] == 'OUTPUT':
        p[0] = pc_ast.Output(p[2])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    
    p[0] = pc_ast.BinaryOp(p[2],p[1],p[3])

def p_expression_unop(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = pc_ast.UnaryOp(p[1],p[2])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]
      
def p_expression_constant(p):
    '''expression : DOUBLE_CONST
                  | STRING_CONST'''
    
    p[0] = pc_ast.Constant(type(p[1]),p[1])

def p_expression_var(p):
    'expression : VAR'
    
    p[0] = pc_ast.Variable(p[1])

def p_error(p):
    print(p)
    print(f"Syntax error at {p.value!r}")

yacc.yacc()

ast = []

input_file = open("code.pc")
lines = []

for i, line in enumerate(input_file):
    lines.append(line.lstrip())
    
yacc.parse(''.join(lines))

input_file.close()

print(ast[0][0].children().children()[0].dType)
    