from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE x : INTEGER
DECLARE y : REAL
INPUT x
OUTPUT x
y <- x
OUTPUT y
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
