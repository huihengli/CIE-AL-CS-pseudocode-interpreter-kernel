from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE a : INTEGER
DECLARE b : INTEGER
a <- 1
b <- 1
OUTPUT a + b
OUTPUT a - b
"""

tokens = tokenize(code)

for t in tokens:
    print(t)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
