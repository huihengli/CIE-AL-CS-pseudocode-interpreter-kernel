from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
TYPE TIntPointer = ^INTEGER
DECLARE x : INTEGER
DECLARE p : TIntPointer
x <- 42
p <- ^x
OUTPUT p^
p^ <- 100
OUTPUT x
"""

tokens = tokenize(code)

# for v in tokens:
#     print(v)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
