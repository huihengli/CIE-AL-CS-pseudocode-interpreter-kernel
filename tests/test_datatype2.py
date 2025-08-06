from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE b : BOOLEAN
DECLARE c : CHAR
DECLARE d : DATE

INPUT b
INPUT c
INPUT d

OUTPUT b
OUTPUT c
OUTPUT d
"""

tokens = tokenize(code)

# for t in tokens:
#     print(t)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
