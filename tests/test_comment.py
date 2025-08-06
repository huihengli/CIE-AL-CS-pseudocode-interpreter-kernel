from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
DECLARE x : INTEGER   // 这是注释
x <- 42   // 给 x 赋值
OUTPUT x // 输出 x 的值
// OUTPUT "234234"
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)
