from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE a : BOOLEAN
DECLARE b : BOOLEAN
a <- TRUE
b <- FALSE
OUTPUT a AND b
OUTPUT a OR b
"""

tokens = tokenize(code)

for t in tokens:
    print(t)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
