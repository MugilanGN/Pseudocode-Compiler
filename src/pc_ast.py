class Expression:
    __slots__ = ('expr')
    
    def __init__(self,expr):
        self.expr = expr
        
    def children(self):
        nodelist = (self.expr)
        return nodelist

class Assignment:
    __slots__ = ('op','dType','lvalue','rvalue')
    
    def __init__(self, op, dType, lvalue, rvalue):
        self.op = op
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.dType =  dType
        
    def children(self):
        nodelist = (self.lvalue, self.rvalue)
        return nodelist
    
class BinaryOp:
    __slots__ = ('op','left','right')
    
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    
    def children(self):
        nodelist = (self.left, self.right)
        return nodelist
    
class UnaryOp:
    __slots__ = ('op','right')
    
    def __init__(self, op, right):
        self.op = op
        self.right = right
    
    def children(self):
        return (self.right)
    
class Constant:
    __slots__ = ('dType','value')
    
    def __init__(self, dType, value):
        self.dType = dType
        self.value = value
        
    def children(self):
        return None
    
class Variable:
    __slots__ = ('name')
    
    def __init__(self, name):
        self.name = name
        
    def children(self):
        return None
    
class Output:
    __slots__ = ('data')
    
    def __init__(self, data):
        self.data = data
        
    def children(self):
        return (self.data)
    
class Input:
    __slots__ = ('variable')
    
    def __init__(self, variable):
        self.variable = variable
        
    def children(self):
        return None
    
class If:
    __slots__ = ('condition', 'if_true', 'if_false')
    
    def __init__(self, condition, if_true, if_false):
        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false
        
    def children(self):
        return (self.condition, self.if_true, self.if_false)
    
class While:
    __slots__ = ('condition', 'body')
    
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        
    def children(self):
        return (self.condition, self.body)
    
class For:
    __slots__ = ('assignment','final','body')
    
    def __init__(self, assignment, final, body):
        self.assignment = assignment
        self.final = final
        self.body = body
        
    def children(self):
        return (self.assignment, self.final, self.body)