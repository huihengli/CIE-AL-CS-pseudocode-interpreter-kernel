from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE A : ARRAY[1:3] OF INTEGER
DECLARE B : ARRAY[1:3, 1:3] OF INTEGER
A[1] <- 5
B[2,2] <- 3
OUTPUT A[1]
OUTPUT B[2,1]
OUTPUT B[2,2]
"""

tokens = tokenize(code)

# for t in tokens:
#     print(t)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
