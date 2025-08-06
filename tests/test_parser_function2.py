from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
FUNCTION Fact(n : INTEGER) RETURNS INTEGER
   IF n = 0 THEN
      RETURN 1
   ELSE
      RETURN n * Fact(n - 1)
   ENDIF
ENDFUNCTION

DECLARE result : INTEGER
result <- Fact(5)
OUTPUT result  // 120
OUTPUT result
"""

tokens = tokenize(code)

# for v in tokens:
#     print(v)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
