from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE x : INTEGER
x <- 0
REPEAT
    OUTPUT x
    x <- x + 2
UNTIL x = 10
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
