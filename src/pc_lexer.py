#!/usr/bin/env python

'''
A lexer that tokenizes Pseudocode
'''

from ply import lex

__author__ = "Mugilan Ganesan"
__email__ = "mugi.ganesan@gmail.com"
__status__ = "Developer"
__version__ = "1.0.0"


class PC_Lexer(object):
    
    def build(self):
        self.lexer = lex.lex(object=self)
        
    def input(self, text):
        self.lexer.input(text)
        
    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token
    
    def test(self, text):
        self.input(text)
        while True:
            tok = self.lexer.token()
            if not tok: 
                break
            print(tok)
    
    tokens = (
        'VAR',
        'INT','DOUBLE',
        'INPUT','OUTPUT',
        'IF','THEN','ELSE','ENDIF',
        'WHILE','DO','ENDWHILE',
        'FOR','TO','NEXT',
        'INT_CONST','DOUBLE_CONST','STRING_CONST',
        'PLUS','MINUS','TIMES','DIVIDE','EQUALS','PERCENT',
        'LPAREN','RPAREN', 'NEWLINE',
        'LBRACKET','RBRACKET',
        'LESS_THAN','LESS_EQUAL',
        'GREATER_THAN','GREATER_EQUAL',
        'EQUALITY','NOT_EQUALITY'
        )

    reserved = r''.join(["(?!"+keyword+")" for keyword in tokens])

    t_PLUS           = r'\+'
    t_MINUS          = r'-'
    t_TIMES          = r'\*'
    t_DIVIDE         = r'/'
    t_EQUALS         = r'='
    t_PERCENT        = r'%'

    t_LESS_THAN      = r'<'
    t_LESS_EQUAL     = r'<='
    t_GREATER_THAN   = r'>'
    t_GREATER_EQUAL  = r'>='
    t_EQUALITY       = r'=='
    t_NOT_EQUALITY   = r'<>'


    t_LPAREN         = r'\('
    t_RPAREN         = r'\)'
    t_LBRACKET       = r'\['
    t_RBRACKET       = r'\]'

    t_INT            = 'INT'
    t_DOUBLE         = 'DOUBLE'

    t_INPUT          = 'INPUT'
    t_OUTPUT         = 'OUTPUT'

    t_IF             = 'IF'
    t_THEN           = 'THEN'
    t_ELSE           = 'ELSE'
    t_ENDIF          = 'ENDIF'

    t_WHILE          = 'WHILE'
    t_DO             = 'DO'
    t_ENDWHILE       = 'ENDWHILE'

    t_FOR            = 'FOR'
    t_TO             = 'TO'
    t_NEXT           = 'NEXT'

    t_VAR            = reserved + r'[a-zA-Z_][a-zA-Z0-9_]*'

    t_ignore         = " \t"

    def t_DOUBLE_CONST(self, t):
        r'\d+\.\d*'
        t.value = float(t.value)
        return t

    def t_INT_CONST(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_STRING_CONST(self, t):
        r'".*?"'
        t.value = t.value[1:len(t.value)-1]
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        return t

    def t_error(self, t):
        print(f"Illegal character {t.value[0]!r}")
        t.lexer.skip(1)

if __name__ == "__main__":
    m = PC_Lexer()
    m.build()
    m.test("x = 2 + 2") 
