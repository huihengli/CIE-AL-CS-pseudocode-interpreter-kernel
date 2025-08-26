from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
TYPE Student
    PUBLIC DECLARE name : STRING
    PRIVATE DECLARE age : INTEGER

    PUBLIC PROCEDURE ShowName()
        OUTPUT self.name
    ENDPROCEDURE
ENDTYPE
"""

tokens = tokenize(code)

# for t in tokens:
#     print(t)

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.eval(ast)
