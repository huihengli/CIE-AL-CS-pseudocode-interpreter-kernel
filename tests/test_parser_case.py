from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE x : INTEGER
CASE OF x
    1: OUTPUT "one"
    2: OUTPUT "two"
OTHERWISE
    OUTPUT "Other"
ENDCASE
"""

tokens = tokenize(code)

for t in tokens:
    print(t)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
