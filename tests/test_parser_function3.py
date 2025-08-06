from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
FUNCTION AddOne(n : INTEGER) RETURNS INTEGER
   RETURN n + 1
ENDFUNCTION

FUNCTION DoublePlusOne(x : INTEGER) RETURNS INTEGER
   RETURN AddOne(x * 2)
ENDFUNCTION

DECLARE result : INTEGER
result <- DoublePlusOne(4)
OUTPUT result
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)
