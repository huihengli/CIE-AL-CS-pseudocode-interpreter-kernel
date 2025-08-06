from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE x : INTEGER
x <- 8
IF x < 5 THEN
    OUTPUT "Small"
ELSE
    OUTPUT "Big"
ENDIF
DECLARE comp : INTEGER
INPUT comp
OUTPUT comp
IF x <> comp THEN
    OUTPUT "NOT EQUAL"
ELSE
    OUTPUT "EQUAL"
ENDIF
"""

tokens = tokenize(code)

# for t in tokens:
#     print(t)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
