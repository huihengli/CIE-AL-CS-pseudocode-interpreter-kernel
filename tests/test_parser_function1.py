from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
FUNCTION Max(a : INTEGER, b : INTEGER) RETURNS INTEGER
   IF a > b THEN
      RETURN a
   ELSE
      RETURN b
   ENDIF
ENDFUNCTION

DECLARE x : INTEGER
x <- Max(3, 5)
OUTPUT x  // 5
"""

tokens = tokenize(code)

# for v in tokens:
#     print(v)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
