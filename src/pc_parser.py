#!/usr/bin/env python

'''
A modular parser which builds an AST using pc_ast's AST node
definitions from the Pseudocode tokens
'''

import sys

from ply import yacc

import pc_ast
from pc_lexer import PC_Lexer

__author__ = "Mugilan Ganesan"
__email__ = "mugi.ganesan@gmail.com"
__status__ = "Developer"
__version__ = "1.0.0"


class PC_Parser:
    
    precedence = (
        ('left','PLUS','MINUS'),
        ('left','TIMES','DIVIDE','PERCENT'),
        ('right','UMINUS'),
        )
    
    def __init__(self, lexer=PC_Lexer):
        
        self.ast             = []
        self.variable_types  = {}
        self.var_lengths     = {}
        self.functions       = {}
        self.scope           = ''
        
        self.Lexer = lexer()       
        self.Lexer.build()
        
        self.tokens = self.Lexer.tokens
        
        self.Parser = yacc.yacc(module=self)
        
    def parse(self, text):
        
        self.ast             = []
        self.variable_types  = {}
        self.var_lengths     = {}
        self.functions       = {}
        self.scope           = ''

        self.Parser.parse(input=text, lexer=self.Lexer)

        return self.ast

    def p_statement(self, p):
        '''statement : stmt_list'''

        self.ast.append(p[1])

    def p_stmt_list(self, p):
        '''stmt_list : simple_stmt
                     | stmt_list NEWLINE simple_stmt'''

        if len(p) == 2:
            p[0] = [p[1]]

        elif len(p) > 3:
            p[0] = p[1] + [p[3]]

    def p_if_stmt(self, p):
        '''if_stmt : IF expression THEN NEWLINE stmt_list NEWLINE ENDIF
                   | IF expression THEN NEWLINE stmt_list NEWLINE ELSE NEWLINE stmt_list NEWLINE ENDIF
                   | IF expression THEN NEWLINE stmt_list NEWLINE ELSE if_stmt'''

        if len(p) == 8:
            p[0] = pc_ast.If(p[2],p[5],None)
            
        elif len(p) == 9:
            p[0] = pc_ast.If(p[2],p[5],[p[8]])

        elif len(p) == 12:
            p[0] = pc_ast.If(p[2],p[5],p[9])

    def p_while_stmt(self, p):
        '''while_stmt : WHILE expression DO NEWLINE stmt_list NEWLINE ENDWHILE'''

        p[0] = pc_ast.While(p[2],p[5])

    def p_for_stmt(self, p):
        '''for_stmt : FOR assignment_stmt TO expression NEWLINE stmt_list NEWLINE NEXT VAR'''

        p[0] = pc_ast.For(p[2],p[4],p[6])

    def p_simple_stmt(self, p):
        '''simple_stmt : expression
                       | expr_list
                       | arg_list
                       | assignment_stmt
                       | array_decl_stmt
                       | if_stmt
                       | while_stmt
                       | for_stmt
                       | output_stmt
                       | input_stmt
                       | function_stmt
                       | return_stmt'''

        p[0] = p[1]

    def p_array_decl_stmt(self, p):
        '''array_decl_stmt : DOUBLE array_index
                           | INT array_index'''

        if p[1] == 'DOUBLE':
            dType = float
        elif p[1] == 'INT':
            dType = int

        name = p[2].name
        elements = p[2].index

        self.variable_types[(name, self.scope)] = dType

        p[0] = pc_ast.Array_Declaration(dType, name, elements)

    def p_assignment_stmt(self, p):
        '''assignment_stmt : VAR EQUALS expression'''

        dType = p[3].dType
        var = p[1]
        expr = p[3]
        length = p[3].length

        self.variable_types[(var, self.scope)] = dType
        self.var_lengths[(var, self.scope)] = length
        var = pc_ast.Variable(dType, var,length)
        p[0] = pc_ast.Assignment("=",dType,var,expr)

    def p_array_assign_stmt(self, p):
        '''assignment_stmt : array_index EQUALS expression'''

        if (p[1].name, self.scope) in self.variable_types:
            p[0] = pc_ast.Assignment("=", self.variable_types[(p[1].name, self.scope)], p[1], p[3])
        else:
            print("Undefined Variable")
            sys.exit()

    def p_input_stmt(self, p):
        '''input_stmt : INPUT VAR
                      | INPUT array_index'''

        if isinstance(p[2], pc_ast.Array_Element):
            name = p[2].name
        else:
            name = p[2]
        
        if (name, self.scope) not in self.variable_types:
            print("The variable " + name + " is undefined")
            sys.exit()
            
        if isinstance(p[2], pc_ast.Array_Element):
             var = p[2]
        else:
            var = pc_ast.Variable(self.variable_types[(name, self.scope)], p[2],0)
        
        p[0] = pc_ast.Input(var, self.variable_types[(name, self.scope)])
            
    def p_output_stmt(self, p):
        '''output_stmt : OUTPUT expression'''

        p[0] = pc_ast.Output(p[2])
        
    def p_return_stmt(self, p):
        '''return_stmt : RETURN expression'''
        
        p[0] = pc_ast.Return(p[2])
        
    def p_function_header(self, p):
        '''function_header : INT SUBROUTINE VAR LPAREN arg_list RPAREN
                           | DOUBLE SUBROUTINE VAR LPAREN arg_list RPAREN
                           | INT SUBROUTINE VAR LPAREN RPAREN
                           | DOUBLE SUBROUTINE VAR LPAREN RPAREN'''
             
        if p[1] == 'INT':
            dType = int
            
        elif p[1] == 'DOUBLE':
            dType = float
        
        name = p[3]
        
        self.functions[name] = dType
        self.var_lengths[(name, self.scope)] = 0
        
        self.scope = name
        
        if len(p) == 6:
            arg_list = []
            
        elif len(p) == 7:
            arg_list = p[5]
            
            for arg in arg_list:
                self.variable_types[(arg[0], self.scope)] = arg[1]
                self.var_lengths[(arg[0], self.scope)] = 0
        
        p[0] = [name, arg_list, dType]
        
    def p_function_stmt(self, p):
        '''function_stmt : function_header NEWLINE stmt_list NEWLINE ENDSUBROUTINE'''

        name, args, dType = p[1]
        
        self.scope = ''
        
        p[0] = pc_ast.Function_Decl(name, args, p[3], dType)
                   
    def p_arg_list(self, p):
        '''arg_list : INT VAR
                    | DOUBLE VAR
                    | arg_list COMMA INT VAR
                    | arg_list COMMA DOUBLE VAR'''
        
                    
        if p[len(p) - 2] == 'INT':
            dType = int
            
        elif p[len(p) - 2] == 'DOUBLE':
            dType = float
        
        if len(p) == 3:
            
            p[0] = [[p[2], dType]]
            
        elif len(p) == 5:

            p[0] = p[1] + [[p[4], dType]]
            
    def p_expr_list(self, p):
        '''expr_list : expression COMMA expression
                     | expr_list COMMA expression'''
        
        if type(p[1]) == list:
            p[0] = p[1] + [p[3]]
            
        else:
            p[0] = [p[1], p[3]]

    def p_expression_arithmetic_binop(self, p):
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression
                      | expression PERCENT expression'''
        
        if p[1].dType == None or p[3].dType == None:
            print("Variable is undefined")
            sys.exit()

        elif p[1].dType == str and p[3].dType == str:

            if p[2] == '+':

                if isinstance(p[1],pc_ast.Variable):
                    length1 = self.var_lengths[(p[1].name, self.scope)] - 1
                else:
                    length1 = p[1].length - 1

                if isinstance(p[3],pc_ast.Variable):
                    length2 = self.var_lengths[(p[3].name, self.scope)]
                else:
                    length2 = p[3].length


                total_length = length1 + length2
                p[0] = pc_ast.BinaryOp(p[2],p[1],p[3],str,total_length)

            else:
                print("Invalid operation")
                sys.exit()

        elif p[1].dType == str or p[3].dType == str:
            print("Invalid operation")
            sys.exit()

        elif p[1].dType == float or p[3].dType == float:
            p[0] = pc_ast.BinaryOp(p[2],p[1],p[3],float,0)

        elif p[1].dType == int and p[3].dType == int:
            p[0] = pc_ast.BinaryOp(p[2],p[1],p[3],int,0)

        else:
            print("Invalid operation")
            sys.exit()

    def p_expression_comp_binop(self, p):
        '''expression : expression LESS_THAN expression
                      | expression GREATER_THAN expression
                      | expression LESS_EQUAL expression
                      | expression GREATER_EQUAL expression
                      | expression EQUALITY expression
                      | expression NOT_EQUALITY expression'''

        if p[1].dType == None or p[3].dType == None:
            print("Variable is undefined")
            sys.exit()

        elif p[1].dType == str or p[3].dType == str:
            print("Strings cannot be compared")
            sys.exit()

        else:

            if p[2] == '<>':
                p[2] = '!='

            if p[1].dType == float or p[3].dType == float:
                p[0] = pc_ast.BinaryOp(p[2],p[1],p[3],float,0)

            elif p[1].dType == int and p[3].dType == int:
                p[0] = pc_ast.BinaryOp(p[2],p[1],p[3],int,0)


    def p_expression_unop(self, p):
        'expression : MINUS expression %prec UMINUS'

        p[0] = pc_ast.UnaryOp(p[2].dType, p[1], p[2], p[2].length)

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'

        p[0] = p[2]
        
    def p_expression_func_call(self, p):
        '''expression : VAR LPAREN expression RPAREN
                      | VAR LPAREN expr_list RPAREN
                      | VAR LPAREN RPAREN'''
        
        if p[1] not in self.functions:
            print("Function has not been defined")
            sys.exit()
        
        if len(p) == 5:
            
            if type(p[3]) == list:
                p[0] = pc_ast.Function_Call(p[1], p[3], self.functions[p[1]], 0)
                
            else:
                p[0] = pc_ast.Function_Call(p[1], [p[3]], self.functions[p[1]], 0)
        
        elif len(p) == 4:
            p[0] = pc_ast.Function_Call(p[1], [], self.functions[p[1]], 0)
        
    def p_expression_array_expr(self, p):
        '''expression : array_index'''

        p[0] = p[1]

    def p_expression_array_val(self, p):
        '''array_index : VAR LBRACKET expression RBRACKET'''

        if (p[1], self.scope) in self.variable_types:
            p[0] = pc_ast.Array_Element(self.variable_types[(p[1], self.scope)], p[1], p[3], 0)
        else:
            p[0] = pc_ast.Array_Element(None, p[1], p[3], None)
            
    def p_expression_literal(self, p):
        '''expression : literal'''
        
        p[0] = p[1]

    def p_literal_int_constant(self, p):
        '''literal : INT_CONST'''

        p[0] = pc_ast.Constant(int,p[1],0)

    def p_literal_double_constant(self, p):
        '''literal : DOUBLE_CONST'''

        p[0] = pc_ast.Constant(float,p[1],0)

    def p_literal_string_constant(self, p):
        '''literal : STRING_CONST'''

        p[0] = pc_ast.Constant(str,str(p[1]),len(p[1])+1)

    def p_expression_var(self, p):
        'expression : VAR'

        if (p[1], self.scope) in self.variable_types:
            length = self.var_lengths[(p[1], self.scope)]
            p[0] = pc_ast.Variable(self.variable_types[(p[1], self.scope)],p[1],length)
            
        else:
            p[0] = pc_ast.Variable(None,p[1],0)

    def p_error(self, p):
        print(f"Syntax error at {p.value!r}")

if __name__ == '__main__':
    m = PC_Parser()

    ast = m.parse("x = 2 + 2")
    
    print(ast)
