import sys
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter
from app.evaluator.tokenizer import tokenize  # 如果你有词法分析模块

def main():
    if len(sys.argv) < 2:
        print("Usage: ciecs <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    if not filename.endswith(".pseudo"):
        print("Error: File must have a .pesudo extension")
        sys.exit(1)


    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    # 词法分析
    tokens = tokenize(code)

    # 语法分析
    parser = Parser(tokens)
    ast = parser.parse()

    # 执行
    interpreter = Interpreter()
    interpreter.eval(ast)

if __name__ == "__main__":
    main()
