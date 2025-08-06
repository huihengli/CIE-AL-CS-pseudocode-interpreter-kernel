from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE x : INTEGER
x <- 0
WHILE x < 10
    OUTPUT x
    x <- x+ 1
ENDWHILE
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
