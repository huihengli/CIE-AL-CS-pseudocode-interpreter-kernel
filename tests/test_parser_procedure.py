from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
PROCEDURE Increment(x : INTEGER)
   x <- x + 1
ENDPROCEDURE

DECLARE v : INTEGER
v <- 10
CALL Increment(v)
OUTPUT v
"""

tokens = tokenize(code)

# for v in tokens:
#     print(v)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
