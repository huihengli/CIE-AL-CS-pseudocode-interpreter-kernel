from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE s : STRING
s <- "ABCDEFGH"
OUTPUT RIGHT(s, 3)
OUTPUT LENGTH(s)
OUTPUT MID(s, 2, 3)
OUTPUT LCASE("A")
OUTPUT UCASE("b")
OUTPUT "Hello" & "!" 
"""

tokens = tokenize(code)

# for t in tokens:
#     print(t)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
