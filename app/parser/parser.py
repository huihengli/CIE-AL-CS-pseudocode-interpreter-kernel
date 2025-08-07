# app/parser/parser.py

from app.evaluator.tokenizer import Token
from app.evaluator.ast import *
from typing import List

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.user_types = {}

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, expected_type=None, expected_value=None):
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of input")

        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected token type {expected_type}, got {token.type}")
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected token value {expected_value}, got {token.value}")

        self.pos += 1
        return token

    def parse(self) -> Program:
        statements = []
        while self.current():
            # print("PARSE LOOP TOKEN:", self.current())
            # print("REMAINING TOKENS:", self.tokens[self.pos:self.pos+3])
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements=statements)

    def parse_statement(self):
        token = self.current()
        # print("Current token:", token)

        if token.type == "KEYWORD":
            if token.value == "DECLARE":
                return self.parse_declare()
            elif token.value == "OUTPUT":
                return self.parse_output()
            elif token.value == "WHILE":
                return self.parse_while()
            elif token.value == "INPUT":
                return self.parse_input()
            elif token.value == "IF":
                return self.parse_if()
            elif token.value == "FOR":
                return self.parse_for()
            elif token.value == "REPEAT":
                return self.parse_repeat()
            elif token.value == "CASE OF":
                return self.parse_case()
            elif token.value == "INPUT":
                return self.parse_input()
            elif token.value == "TYPE":
                return self.parse_type_definition()
            if token.value == "PROCEDURE":
                return self.parse_procedure_definition()
            elif token.value == "FUNCTION":
                return self.parse_function_definition()
            elif token.value == "CALL":
                return self.parse_call()  # 会返回 CallStmt
            elif token.value == "RETURN":
                return self.parse_return()
            else:
                raise SyntaxError(f"Unknown keyword: {token.value}")
        elif token.type in ("IDENTIFIER", "CARET"):
            saved_pos = self.pos

            try:
                # 尝试解析完整的左值表达式
                lval = self.parse_expression()

                # 如果后面是 <- ，说明是赋值语句
                if self.current() and self.current().type == "ASSIGN":
                    # 回滚到最初位置，由 parse_assign 正常解析
                    self.pos = saved_pos
                    return self.parse_assign()
                else:
                    raise SyntaxError(f"Unexpected expression start: {token}")
            except Exception as e:
                self.pos = saved_pos
                raise SyntaxError(f"Unexpected expression start: {token}")


        else:
            raise SyntaxError(f"Unknown start of statement: {token}")


    def parse_declare(self):
        self.eat("KEYWORD", "DECLARE")
        var_name = self.eat("IDENTIFIER").value
        self.eat("COLON")

        # inline pointer: ^INTEGER etc.
        if self.current() and self.current().type == "CARET":
            self.eat("CARET")
            base_token = self.eat("KEYWORD")
            if base_token.value not in ("INTEGER", "REAL", "STRING", "CHAR", "BOOLEAN", "DATE"):
                raise SyntaxError(f"Unknown base type for pointer: {base_token.value}")
            ptr_type = PointerType(base_type=base_token.value)
            return Declare(name=var_name, type=ptr_type)

        # array type: ARRAY[1:3] OF INTEGER
        if self.current() and self.current().type == "KEYWORD" and self.current().value == "ARRAY":
            self.eat("KEYWORD", "ARRAY")
            self.eat("LBRACKET")
            lowers = []
            uppers = []
            while True:
                low = int(self.eat("NUMBER").value)
                self.eat("COLON")
                high = int(self.eat("NUMBER").value)
                lowers.append(low)
                uppers.append(high)
                if self.current() and self.current().type == "COMMA":
                    self.eat("COMMA")
                else:
                    break
            self.eat("RBRACKET")
            self.eat("KEYWORD", "OF")
            base_token = self.eat(self.current().type)
            base_type = base_token.value
            if base_type not in ("INTEGER", "REAL", "STRING", "CHAR", "BOOLEAN", "DATE") and base_type not in self.user_types:
                raise SyntaxError(f"Unknown base type for array: {base_type}")
            return Declare(name=var_name, type=ArrayType(lowers=lowers, uppers=uppers, base_type=base_type))

        # 普通 / user-defined type
        if self.current() and self.current().type in ("KEYWORD", "IDENTIFIER"):
            var_type_token = self.eat(self.current().type)
            if var_type_token.value in ("INTEGER", "REAL", "STRING", "CHAR", "BOOLEAN", "DATE"):
                return Declare(name=var_name, type=var_type_token.value)
            elif var_type_token.value in self.user_types:
                return Declare(name=var_name, type=var_type_token.value)
            else:
                raise SyntaxError(f"Unknown type: {var_type_token.value}")

        raise SyntaxError(f"Unexpected type in declaration: {self.current()}")






    def parse_assign(self):
        target = self.parse_lvalue()  # 可以是 Var / FieldAccess / ArrayAccess
        self.eat("ASSIGN")
        value = self.parse_expression()
        return Assign(target=target, value=value)


    
    def parse_if(self):
        self.eat("KEYWORD", "IF")
        condition = self.parse_expression()  # 解析 IF 的条件
        self.eat("KEYWORD", "THEN")

        body = []
        while self.current() and not (
            self.current().type == "KEYWORD" and 
            self.current().value in ("ELSE", "ENDIF")
        ):
            body.append(self.parse_statement())

        else_body = None
        if self.current() and self.current().type == "KEYWORD" and self.current().value == "ELSE":
            self.eat("KEYWORD", "ELSE")
            else_body = []
            while self.current() and not (
                self.current().type == "KEYWORD" and 
                self.current().value == "ENDIF"
            ):
                else_body.append(self.parse_statement())

        self.eat("KEYWORD", "ENDIF")
        return If(condition=condition, body=body, else_body=else_body)
    
    def parse_output(self):
        self.eat("KEYWORD", "OUTPUT")
        values = []

        while self.current() and self.current().type != "KEYWORD":
            expr = self.parse_expression()
            values.append(expr)

            # 支持逗号分隔多个输出项
            if self.current() and self.current().type == "COMMA":
                self.eat("COMMA")
                continue
            else:
                break

        return Output(values=values)



    def parse_while(self):
        self.eat("KEYWORD", "WHILE")
        condition = self.parse_expression()

        body = []
        while self.current() and not (
            self.current().type == "KEYWORD" and 
            self.current().value == "ENDWHILE"
        ):
            body.append(self.parse_statement())

        self.eat("KEYWORD", "ENDWHILE")
        return While(condition=condition, body=body)
    
    def parse_if(self):
        self.eat("KEYWORD", "IF")
        condition = self.parse_expression()
        self.eat("KEYWORD", "THEN")

        then_body = []
        while self.current() and not (
            self.current().type == "KEYWORD" and self.current().value in ("ELSE", "ENDIF")
        ):
            then_body.append(self.parse_statement())

        else_body = []
        if self.current().type == "KEYWORD" and self.current().value == "ELSE":
            self.eat("KEYWORD", "ELSE")
            while self.current() and not (
                self.current().type == "KEYWORD" and self.current().value == "ENDIF"
            ):
                else_body.append(self.parse_statement())

        self.eat("KEYWORD", "ENDIF")
        return If(condition=condition, then_body=then_body, else_body=else_body or None)

    def parse_for(self):
        self.eat("KEYWORD", "FOR")

        var_token = self.eat("IDENTIFIER")
        var_name = var_token.value

        assign_token = self.eat("ASSIGN")
        
        start_expr = self.parse_expression()

        self.eat("KEYWORD", "TO")

        end_expr = self.parse_expression()

        # body
        body = []
        while self.current() and not (
            self.current().type == "KEYWORD" and self.current().value == "NEXT"
        ):

            body.append(self.parse_statement())

        self.eat("KEYWORD", "NEXT")
        self.eat("IDENTIFIER", var_name)  # 可选：确保 NEXT 后面跟的是同一个变量名

        return For(var_name, start_expr, end_expr, body)
    
    def parse_repeat(self):
        self.eat("KEYWORD", "REPEAT")

        body = []
        while self.current() and not (
            self.current().type == "KEYWORD" and self.current().value == "UNTIL"
        ):
            body.append(self.parse_statement())

        self.eat("KEYWORD", "UNTIL")
        condition = self.parse_expression()

        return RepeatUntil(body, condition)

    def parse_case(self):
        self.eat("KEYWORD", "CASE OF")
        case_expr = self.parse_expression()

        cases = []
        otherwise_body = None

        while self.current() and not (
            self.current().type == "KEYWORD" and self.current().value == "ENDCASE"
        ):
            token = self.current()

            if token.type == "NUMBER":
                # 匹配 1:
                tok = self.eat()
                if tok.type == "NUMBER":
                    value = Number(tok.value)
                elif tok.type == "STRING":
                    value = String(tok.value.strip('"'))
                elif tok.type == "IDENTIFIER":
                    value = Var(tok.value)
                else:
                    raise SyntaxError(f"Unexpected case value: {tok}")

                self.eat("COLON")

                # 读取当前 case 分支下的所有语句，直到遇到下一个 case/otherwise/endcase
                case_body = []
                while self.current() and not (
                    (self.current().type == "NUMBER") or
                    (self.current().type == "KEYWORD" and self.current().value in ("OTHERWISE", "ENDCASE"))
                ):
                    case_body.append(self.parse_statement())

                cases.append((value, case_body))

            elif token.type == "KEYWORD" and token.value == "OTHERWISE":
                self.eat("KEYWORD", "OTHERWISE")
                otherwise_body = []
                while self.current() and not (
                    self.current().type == "KEYWORD" and self.current().value == "ENDCASE"
                ):
                    otherwise_body.append(self.parse_statement())

            else:
                raise SyntaxError(f"Unexpected token in CASE OF block: {token}")

        self.eat("KEYWORD", "ENDCASE")
        return CaseOf(expr=case_expr, cases=cases, otherwise=otherwise_body)

    def parse_input(self):
        self.eat("KEYWORD", "INPUT")
        var_token = self.eat("IDENTIFIER")
        return Input(var_token.value)

    def parse_type_definition(self):
        self.eat("KEYWORD", "TYPE")
        type_name = self.eat("IDENTIFIER").value

        # 指针别名：TYPE T = ^INTEGER
        if self.current() and self.current().type == "OPERATOR" and self.current().value == "=":
            self.eat("OPERATOR", "=")
            if self.current() and self.current().type == "CARET":
                self.eat("CARET")
                base_token = self.eat("KEYWORD")
                if base_token.value not in ("INTEGER", "REAL", "STRING", "CHAR", "BOOLEAN", "DATE"):
                    raise SyntaxError(f"Unknown base type for pointer alias: {base_token.value}")
                ptr_type = PointerType(base_type=base_token.value)
                self.user_types[type_name] = ptr_type  # 注册 alias
                return TypeDef(name=type_name, fields=[])  # 你可以选择用一个简略的 TypeDef 表示
            else:
                raise SyntaxError(f"Expected '^' after '=', got {self.current()}")

        # 结构体形式：TYPE Name ... ENDTYPE
        fields = []
        while self.current() and not (self.current().type == "KEYWORD" and self.current().value == "ENDTYPE"):
            # 只允许 DECLARE field : Type
            self.eat("KEYWORD", "DECLARE")
            field_name = self.eat("IDENTIFIER").value
            self.eat("COLON")

            # 可能是 inline pointer type for field
            field_type = None
            if self.current() and self.current().type == "CARET":
                self.eat("CARET")
                base_token = self.eat("KEYWORD")
                if base_token.value not in ("INTEGER", "REAL", "STRING", "CHAR", "BOOLEAN", "DATE"):
                    raise SyntaxError(f"Unknown base type for pointer field: {base_token.value}")
                field_type = PointerType(base_type=base_token.value)
            elif self.current() and self.current().type == "KEYWORD":
                tt = self.eat("KEYWORD").value
                if tt in ("INTEGER", "REAL", "STRING", "CHAR", "BOOLEAN", "DATE"):
                    field_type = tt
                elif tt in self.user_types:
                    field_type = tt
                else:
                    raise SyntaxError(f"Unknown field type: {tt}")
            elif self.current() and self.current().type == "IDENTIFIER":
                # user-defined type name
                field_type = self.eat("IDENTIFIER").value
                if field_type not in self.user_types:
                    raise SyntaxError(f"Unknown field type: {field_type}")
            else:
                raise SyntaxError(f"Expected type name for field '{field_name}', got {self.current()}")

            fields.append((field_name, field_type))

        self.eat("KEYWORD", "ENDTYPE")
        # 注册结构体 type definition
        self.user_types[type_name] = {name: typ for name, typ in fields}
        return TypeDef(name=type_name, fields=fields)


    def parse_possible_field_access(self):
        # 先吃一个 IDENTIFIER（基础变量名）
        base = self.eat("IDENTIFIER").value
        target = Var(base)
        # 支持 s.name 形式
        while self.current() and self.current().type == "DOT":
            self.eat("DOT")
            field = self.eat("IDENTIFIER").value
            target = FieldAccess(var_name=base, field_name=field)
            # 如果要支持更深层嵌套可以 update base/target accordingly
        return target

    def parse_param(self):
        byref = False
        # if self.current().type == "KEYWORD" and self.current().value == "BYREF":
        #     self.eat("KEYWORD", "BYREF")
        #     byref = True

        name = self.eat("IDENTIFIER").value

        if not (self.current() and self.current().type == "COLON"):
            raise SyntaxError(f"Expected ':' after parameter name '{name}', got {self.current()}")
        self.eat("COLON")

        if self.current() and self.current().type in ("KEYWORD", "IDENTIFIER"):
            type_name = self.eat(self.current().type).value
        else:
            raise SyntaxError(f"Expected type name after colon for parameter '{name}', got {self.current()}")

        return Param(name=name, type=type_name, byref=byref)


    def parse_param_list(self):
        params = []
        if self.current() and self.current().type == "LPAREN":
            self.eat("LPAREN")
        else:
            return params  # 没有括号就认为没有参数

        while self.current() and self.current().type != "RPAREN":
            params.append(self.parse_param())
            if self.current() and self.current().type == "COMMA":
                self.eat("COMMA")
            else:
                break

        if self.current() and self.current().type == "RPAREN":
            self.eat("RPAREN")
        else:
            raise SyntaxError(f"Expected ')' to close parameter list, got {self.current()}")

        return params


    def parse_procedure_definition(self):
        self.eat("KEYWORD", "PROCEDURE")
        name = self.eat("IDENTIFIER").value

        # 解析可选的参数列表
        params = []
        if self.current() and self.current().type == "LPAREN":
            params = self.parse_param_list()

        body = []
        while not (self.current() and self.current().type == "KEYWORD" and self.current().value == "ENDPROCEDURE"):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.eat("KEYWORD", "ENDPROCEDURE")
        return ProcedureDef(name=name, params=params, body=body)


    def parse_function_definition(self):
        self.eat("KEYWORD", "FUNCTION")
        name = self.eat("IDENTIFIER").value

        params = []
        if self.current() and self.current().type == "LPAREN":
            params = self.parse_param_list()

        self.eat("KEYWORD", "RETURNS")
        if self.current() and self.current().type in ("KEYWORD", "IDENTIFIER"):
            return_type = self.eat(self.current().type).value
        else:
            raise SyntaxError(f"Expected return type, got {self.current()}")

        body = []
        while not (self.current() and self.current().type == "KEYWORD" and self.current().value == "ENDFUNCTION"):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.eat("KEYWORD", "ENDFUNCTION")
        return FunctionDef(name=name, params=params, return_type=return_type, body=body)


    def parse_call(self):
        is_statement = False
        if self.current().type == "KEYWORD" and self.current().value == "CALL":
            self.eat("KEYWORD", "CALL")
            is_statement = True

        name = self.eat("IDENTIFIER").value

        args = []
        if self.current() and self.current().type == "LPAREN":
            self.eat("LPAREN")
            while self.current() and self.current().type != "RPAREN":
                args.append(self.parse_expression())
                if self.current() and self.current().type == "COMMA":
                    self.eat("COMMA")
                else:
                    break
            self.eat("RPAREN")

        call_node = Call(name=name, args=args)
        if is_statement:
            return CallStmt(call=call_node)
        return call_node


    def parse_return(self):
        self.eat("KEYWORD", "RETURN")
        if self.current() and self.current().type not in ("KEYWORD",):
            expr = self.parse_expression()
        else:
            expr = None
        return Return(expr=expr)

    
    def parse_expression(self):
        # 前缀取地址 ^x
        if self.current() and self.current().type == "CARET":
            self.eat("CARET")
            target = self.parse_expression()
            return AddressOf(target=target)


        # 先处理左侧：变量、字段访问、或者函数调用
        if self.current() and self.current().type == "IDENTIFIER":
            node = self.parse_possible_field_access()

            # 可能的函数调用
            if isinstance(node, Var) and self.current() and self.current().type == "LPAREN":
                name = node.name
                args = []
                self.eat("LPAREN")
                while self.current() and self.current().type != "RPAREN":
                    args.append(self.parse_expression())
                    if self.current() and self.current().type == "COMMA":
                        self.eat("COMMA")
                    else:
                        break
                self.eat("RPAREN")
                node = Call(name=name, args=args)

            # 数组访问
            if isinstance(node, Var) and self.current() and self.current().type == "LBRACKET":
                name = node.name
                self.eat("LBRACKET")
                indices = [self.parse_expression()]
                while self.current() and self.current().type == "COMMA":
                    self.eat("COMMA")
                    indices.append(self.parse_expression())
                self.eat("RBRACKET")
                node = ArrayAccess(name=name, indices=indices)

            # 后缀解引用 node^
            if self.current() and self.current().type == "CARET":
                self.eat("CARET")
                node = Dereference(pointer=node)

            # 一元与二元操作
            OPERATOR_TOKS = ("OPERATOR", "GTE", "LTE", "NEQ", "STRCOMB", "LOGICOP")
            if self.current() and self.current().type in OPERATOR_TOKS:
                tok = self.eat(self.current().type)
                if tok.type == "NEQ":
                    op = "<>"
                elif tok.type == "GTE":
                    op = ">="
                elif tok.type == "LTE":
                    op = "<="
                elif tok.type == "STRCOMB":
                    op = "&"
                elif tok.value == "AND":
                    op = "AND"
                elif tok.value == "OR":
                    op = "OR"
                else:
                    op = tok.value
                right = self.parse_expression()
                return BinaryOp(left=node, operator=op, right=right)

            return node
        else:
            UnaryOpToks = ("NOT")
            if self.current() and self.current().type == "LOGICOP" and self.current().value in UnaryOpToks:
                tok = self.eat(self.current().type)
                op = tok.value
                right = self.parse_expression()
                return UnaryOp(operator=op, operand=right)


        # 不是标识符的左操作数：数字/字符串/括号
        token = self.current()
        if not token:
            raise SyntaxError("Unexpected end of expression")

        if token.type == "NUMBER":
            self.eat("NUMBER")
            left = Number(token.value)
        elif token.type == "STRING":
            self.eat("STRING")
            left = String(token.value.strip('"'))
        elif token.type == "LPAREN":
            self.eat("LPAREN")
            left = self.parse_expression()
            self.eat("RPAREN")
        else:
            raise SyntaxError(f"Invalid left operand: {token}")


    def parse_lvalue(self):
        if self.current().type != "IDENTIFIER":
            raise SyntaxError(f"Expected lvalue identifier, got {self.current()}")
        name = self.eat("IDENTIFIER").value

        # 基础 node 是变量
        node = Var(name)

        # 字段访问：s.name
        if self.current() and self.current().type == "DOT":
            self.eat("DOT")
            field = self.eat("IDENTIFIER").value
            node = FieldAccess(node.name, field)

        # 数组访问：A[i]
        if self.current() and self.current().type == "LBRACKET":
            self.eat("LBRACKET")
            indices = [self.parse_expression()]
            while self.current() and self.current().type == "COMMA":
                self.eat("COMMA")
                indices.append(self.parse_expression())
            self.eat("RBRACKET")
            node = ArrayAccess(name=node.name, indices=indices)

        # 指针解引用：p^ / p^^
        while self.current() and self.current().type == "CARET":
            self.eat("CARET")
            node = Dereference(pointer=node)

        return node


