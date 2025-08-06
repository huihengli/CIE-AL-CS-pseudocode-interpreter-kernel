from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
TYPE Student
    DECLARE name : STRING
    DECLARE age : INTEGER
ENDTYPE

DECLARE s : Student
s.name <- "Alice"
OUTPUT s.name
"""

tokens = tokenize(code)

# for v in tokens:
#     print(v)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
