#!/usr/bin/env python

'''
An independent code generator that takes an AST and creates LLVM IR 
from it. The IR is returned as an llvmlite module instance.
'''

from llvmlite import ir
from llvmlite import binding

import pc_ast
from pc_lexer import PC_Lexer
from pc_parser import PC_Parser

__author__ = "Mugilan Ganesan"
__email__ = "mugi.ganesan@gmail.com"
__status__ = "Developer"
__version__ = "1.0.0"


class Generator:
    
    def __init__(self):
        
        self.variables = {}
        self.constants = {}
    
    def setup_std_funcs(self):

        fmt_type = ir.ArrayType(ir.IntType(8),4)
        fmt_double = "%lf\0"
        c_fmt = ir.Constant(fmt_type, bytearray(fmt_double.encode("utf8")))
        self.double_fmt = ir.GlobalVariable(self.module, c_fmt.type, "fmt_double")
        self.double_fmt.global_constant = True
        self.double_fmt.initializer = c_fmt

        fmt_type = ir.ArrayType(ir.IntType(8),3)
        fmt_string = "%s\0"
        c_fmt = ir.Constant(fmt_type, bytearray(fmt_string.encode("utf8")))
        self.string_fmt = ir.GlobalVariable(self.module, c_fmt.type, "fmt_string")
        self.string_fmt.global_constant = True
        self.string_fmt.initializer = c_fmt

        fmt_type = ir.ArrayType(ir.IntType(8),3)
        fmt_int= "%d\0"
        c_fmt = ir.Constant(fmt_type, bytearray(fmt_int.encode("utf8")))
        self.int_fmt = ir.GlobalVariable(self.module, c_fmt.type, "fmt_int")
        self.int_fmt.global_constant = True
        self.int_fmt.initializer = c_fmt
          
        fmt_type = ir.ArrayType(ir.IntType(8),2)
        fmt_newline = "\n\0"
        c_fmt = ir.Constant(fmt_type, bytearray(fmt_newline.encode("utf8")))
        self.newline_fmt = ir.GlobalVariable(self.module, c_fmt.type, "fmt_newline")
        self.newline_fmt.global_constant = True
        self.newline_fmt.initializer = c_fmt

        void_ptr_ty = ir.IntType(8).as_pointer()
        printf_ty = ir.FunctionType(ir.IntType(32), [void_ptr_ty], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")

        malloc_ty = ir.FunctionType(void_ptr_ty, [ir.IntType(32)])
        self.malloc = ir.Function(self.module, malloc_ty, name="malloc")

        memcpy_ty = ir.FunctionType(ir.VoidType(), [void_ptr_ty, void_ptr_ty, ir.IntType(32)])
        self.memcpy = ir.Function(self.module, memcpy_ty, name="memcpy")
            
        scanf_ty = ir.FunctionType(ir.IntType(32), [void_ptr_ty], var_arg=True)
        self.scanf = ir.Function(self.module, scanf_ty, name="scanf")

        realloc_ty = ir.FunctionType(ir.VoidType(), [void_ptr_ty, ir.IntType(32)])
        self.realloc = ir.Function(self.module, realloc_ty, name="realloc")
        
    def generate(self, ast=[[]], output="output.ll"):
        
        self.variables = {}
        self.constants = {}

        self.module = ir.Module(name=output)

        triple =  binding.get_default_triple()
        self.module.triple = triple

        self.setup_std_funcs()

        main_ty = ir.FunctionType(ir.IntType(32), ())
        self.main = ir.Function(self.module, main_ty, name="main")

        main_block = self.main.append_basic_block(name="entry")
        builder = ir.IRBuilder(main_block)

        for statement in ast[0]:
            builder = self.codegen(statement,builder)

        builder.ret(ir.IntType(32)(0))

        return self.module

    def codegen(self, node, builder):

        if isinstance(node, pc_ast.Constant):

            if node.dType == float:
                dType = ir.DoubleType()

                return dType(node.value)

            elif node.dType == int:
                dType = ir.IntType(32)

                return dType(node.value)

            elif node.dType == str:

                if node.value not in self.constants:
                    dType = ir.ArrayType(ir.IntType(8), node.length)
                    str_val = ir.Constant(dType, bytearray((node.value+"\0").encode("utf8")))
                    str_global = ir.GlobalVariable(self.module, str_val.type, "_str." + node.value)
                    str_global.global_constant = True
                    str_global.initializer = str_val
                    fmt_ptr = builder.gep(str_global, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=False, name=node.value+"_ptr")
                    self.constants[node.value] = fmt_ptr

                return self.constants[node.value]

        elif isinstance(node, pc_ast.Variable):

            if node.dType == float:   
                ptr_type = ir.PointerType(ir.DoubleType(), addrspace=0)

            elif node.dType == int:
                ptr_type = ir.PointerType(ir.IntType(32), addrspace=0)

            elif node.dType == str:
                ptr_type = ir.PointerType(ir.IntType(8), addrspace=0)

            return ptr_type('%"'+node.name+'"')

        elif isinstance(node, pc_ast.Array_Declaration):

            self.variables[node.name] = node.dType

            r = node.elements

            if isinstance(r, pc_ast.Variable) or isinstance(r, pc_ast.Array_Element):
                rvalue = self.codegen(r, builder)

                if r.dType == float or r.dType == int:
                    rvalue = builder.load(rvalue,name=r.name + "_val",align=None)

            else:
                rvalue = self.codegen(r, builder)

            if node.dType == int:
                raw = builder.call(self.malloc, [rvalue], name=node.name+"_raw")
                builder.bitcast(raw, ir.PointerType(ir.IntType(32), addrspace=0), name=node.name)

            elif node.dType == float:
                raw = builder.call(self.malloc, [rvalue], name=node.name+"_raw")
                builder.bitcast(raw, ir.PointerType(ir.DoubleType(), addrspace=0), name=node.name)

            return builder

        elif isinstance(node, pc_ast.Array_Element):

            if node.dType == int:
                ptr_type = ir.PointerType(ir.IntType(32), addrspace=0)
            elif node.dType == float:
                ptr_type = ir.PointerType(ir.DoubleType(), addrspace=0)

            index = self.codegen(node.index, builder)

            if isinstance(node.index, pc_ast.Variable) or isinstance(node.index, pc_ast.Array_Element):
                index = builder.load(index,name="_val",align=None)

            arr = ptr_type('%"'+node.name+'"')
            index_ptr = builder.gep(arr, [index], name="element")

            return index_ptr

        elif isinstance(node, pc_ast.Assignment):

            l, r = node.children()

            lvalue = self.codegen(l, builder)

            if isinstance(r, pc_ast.Variable) or isinstance(r, pc_ast.Array_Element):
                rvalue = self.codegen(r, builder)

                if r.dType == float or r.dType == int:
                    rvalue = builder.load(rvalue,name=r.name + "_val",align=None)

            else:
                rvalue = self.codegen(r, builder)

            if node.dType == float:
                if l.name not in self.variables:
                    self.variables[l.name] = 0
                    builder.alloca(ir.DoubleType(),size=None,name=l.name)

                builder.store(rvalue,lvalue,align=None)

            elif node.dType == int:
                if l.name not in self.variables:
                    self.variables[l.name] = 0
                    builder.alloca(ir.IntType(32),size=None,name=l.name)

                builder.store(rvalue,lvalue,align=None)

            elif node.dType == str:
                if l.name in self.variables:
                    if self.variables[l.name] != l.length:
                        builder.call(self.realloc, [lvalue, ir.IntType(32)(l.length)])
                        self.variables[l.name] = l.length

                else:
                    self.variables[l.name] = l.length
                    builder.call(self.malloc, [ir.IntType(32)(l.length)], name=l.name)

                if isinstance(r, pc_ast.Constant):
                    temp = builder.bitcast(rvalue, ir.PointerType(ir.IntType(8), addrspace=0), name="temp")
                else:
                    temp = rvalue

                builder.call(self.memcpy, [lvalue, temp, ir.IntType(32)(l.length)])

            return builder

        elif isinstance(node, pc_ast.BinaryOp):

            cmp_op = {">","<","!=",">=",'<=',"=="}

            l, r = node.children()

            if isinstance(l, pc_ast.Variable) or isinstance(l, pc_ast.Array_Element):
                lvalue = self.codegen(l, builder)

                if l.dType == float or l.dType == int:
                    lvalue = builder.load(lvalue,name=l.name + "_val",align=None)

            else:
                lvalue = self.codegen(l, builder)

            if isinstance(r, pc_ast.Variable) or isinstance(r, pc_ast.Array_Element):
                rvalue = self.codegen(r, builder)

                if r.dType == float or r.dType == int:
                    rvalue = builder.load(rvalue,name=r.name + "_val",align=None)

            else:
                rvalue = self.codegen(r, builder)

            if l.dType == float and r.dType == int:
                rvalue = builder.sitofp(rvalue, ir.DoubleType(), name="_casted")

            elif l.dType == int and r.dType == float:
                lvalue = builder.sitofp(lvalue, ir.DoubleType(), name="_casted")

            if node.op == '+':

                if node.dType == str:

                    res = builder.call(self.malloc, [ir.IntType(32)(node.length)], name="pt1")
                    builder.call(self.memcpy, [res, lvalue, ir.IntType(32)(l.length - 1)])
                    pt2 = builder.gep(res, [ir.IntType(32)(l.length - 1)], "pt2")
                    builder.call(self.memcpy, [pt2, rvalue, ir.IntType(32)(r.length)])

                elif node.dType == float:
                    res = builder.fadd(lvalue, rvalue, name="t")

                elif node.dType == int:
                    res = builder.add(lvalue, rvalue, name="t")

            elif node.op == '-':
                if node.dType == float:
                    res = builder.fsub(lvalue, rvalue, name="t")

                elif node.dType == int:
                    res = builder.sub(lvalue, rvalue, name="t")

            elif node.op == '*':
                if node.dType == float:
                    res = builder.fmul(lvalue, rvalue, name="t")

                elif node.dType == int:
                    res = builder.mul(lvalue, rvalue, name="t")

            elif node.op == '/':
                if node.dType == float:
                    res = builder.fdiv(lvalue, rvalue, name="t")

                elif node.dType == int:
                    res = builder.sdiv(lvalue, rvalue, name="t")

            elif node.op == '%':
                if node.dType == float:
                    res = builder.frem(lvalue, rvalue, name="t")

                elif node.dType == int:
                    res = builder.srem(lvalue, rvalue, name="t")

            elif node.op in cmp_op:

                if node.dType == float:
                    res = builder.fcmp_unordered(node.op, lvalue, rvalue, name="t")

                elif node.dType == int:
                    res = builder.icmp_signed(node.op, lvalue, rvalue, name="t")

            return res

        elif isinstance(node, pc_ast.UnaryOp):

            r = node.right

            if isinstance(r, pc_ast.Variable) or isinstance(r, pc_ast.Array_Element):
                rvalue = self.codegen(r, builder)

                if r.dType == float or r.dType == int:
                    rvalue = builder.load(rvalue,name=r.name + "_val",align=None)

            else:
                rvalue = self.codegen(r, builder)

            if node.op == '-':

                if r.dType == int: 
                    res = builder.neg(rvalue)

                elif r.dType == float:
                    res = builder.fsub(ir.DoubleType()(0),rvalue)

            return res

        elif isinstance(node, pc_ast.Output):

            raw_data = node.children()

            data = self.codegen(raw_data, builder)

            if isinstance(raw_data, pc_ast.Array_Element):
                data = builder.load(data,name=raw_data.name + "_val",align=None)

            if raw_data.dType == float: 
                fmt_ptr = builder.gep(self.double_fmt, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=False, name="fmt_ptr")

                if isinstance(raw_data, pc_ast.Variable):
                    data = builder.load(data,name=raw_data.name + "_val",align=None)

            elif raw_data.dType == str:
                fmt_ptr = builder.gep(self.string_fmt, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=False, name="fmt_ptr")

            elif raw_data.dType == int:
                fmt_ptr = builder.gep(self.int_fmt, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=False, name="fmt_ptr")

                if isinstance(raw_data, pc_ast.Variable):
                    data = builder.load(data,name=raw_data.name + "_val",align=None)

            builder.call(self.printf, [fmt_ptr, data], name="print")
                
            fmt_ptr = builder.gep(self.newline_fmt, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=False, name="fmt_ptr")
            builder.call(self.printf, [fmt_ptr], name="print")

            return builder

        elif isinstance(node, pc_ast.If):

            condition, if_true, if_false = node.children()

            condition = self.codegen(condition, builder)

            if if_false == None:

                with builder.if_then(condition) as then:
                    for statement in if_true:
                        builder = self.codegen(statement, builder)

            else:   
                with builder.if_else(condition) as (then, otherwise):

                    with then:
                        for statement in if_true:
                            builder = self.codegen(statement, builder)


                    with otherwise:
                        for statement in if_false:
                            builder = self.codegen(statement, builder)

            return builder

        elif isinstance(node, pc_ast.While):

            condition, body = node.children()

            loop_body = self.main.append_basic_block(name="while.body")

            builder.branch(loop_body)
            loop_body_builder = ir.IRBuilder(loop_body)

            for statement in body:
                loop_body_builder = self.codegen(statement, loop_body_builder)
            
            condition = self.codegen(condition, loop_body_builder)

            loop_exit = self.main.append_basic_block(name="while.exit")
            loop_exit_builder = ir.IRBuilder(loop_exit)

            loop_body_builder.cbranch(condition, loop_body, loop_exit)

            return loop_exit_builder
        
        elif isinstance(node, pc_ast.Input):
        
            variable = self.codegen(node.variable, builder)

            #builder.call(self.realloc, [variable, ir.IntType(32)(5)]) for strings
            self.variables[node.variable.name] = 0

            if node.dType == int:
                fmt_ptr = builder.gep(self.int_fmt, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=False, name="fmt_ptr")

            elif node.dType == float:
                fmt_ptr = builder.gep(self.double_fmt, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=False, name="fmt_ptr")

            elif node.dType == str:
                fmt_ptr = builder.gep(self.string_fmt, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=False, name="fmt_ptr")

            builder.call(self.scanf, [fmt_ptr, variable], name="scan")

            return builder

if __name__ == "__main__":

    ast = PC_Parser(PC_Lexer).parse("x = 2 + 2")

    codegen = Generator()

    module = codegen.generate(ast)

    print(module)
