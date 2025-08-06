from app.evaluator.ast import *
import datetime

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

@dataclass
class Reference:
    # 用来包装 BYREF 参数：持有 container 和 key，读写反射回原处
    container: dict
    key: str

    def get(self):
        return self.container[self.key]

    def set(self, value):
        self.container[self.key] = value

class FrameWrapper:
    def __init__(self, local: dict, outer: dict):
        self.local = local  # 形参+局部
        self.outer = outer  # 之前的 env（全局或上层 frame）

    def __getitem__(self, key):
        if key in self.local:
            val = self.local[key]
            if isinstance(val, Reference):
                return val.get()
            return val
        if key in self.outer:
            return self.outer[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        # 赋值优先写入已有的 local（包含 Reference）
        if key in self.local:
            existing = self.local[key]
            if isinstance(existing, Reference):
                existing.set(value)
                return
            self.local[key] = value
        elif key in self.outer:
            # 修改外层（例如全局变量被遮蔽然后赋值）
            self.outer[key] = value
        else:
            # 新变量默认放 local
            self.local[key] = value

    def __contains__(self, key):
        return key in self.local or key in self.outer



class Interpreter:
    def __init__(self):
        # self.variables = {}  # 用来记录变量的值
        self.env = {}
        self.var_types = {}  # 变量名 -> 类型字符串
        self.user_types = {}  # key: type name, value: dict of field names and types
        self.procedures = {}     # name -> ProcedureDef
        self.functions = {}      # name -> FunctionDef
        self.output_handler = print  # 默认用 print 输出


    def _execute_call(self, call: Call, expect_return: bool):
        name = call.name
        args = call.args

        # 先看是不是 procedure
        if name in self.procedures:
            # 处理 PROCEDURE 调用
            proc = self.procedures[name]
            frame_env = {}
            for param, arg_expr in zip(proc.params, args):
                # always BYVAL for PROCEDURE per spec
                val = self.eval(arg_expr)
                frame_env[param.name] = val
            old_env = self.env
            self.env = FrameWrapper(frame_env, self.env)
            try:
                for stmt in proc.body:
                    self.eval(stmt)
            finally:
                self.env = old_env

            return None

        # 然后看 function
        if name in self.functions:
            func = self.functions[name]
            frame_env = {}
            for param, arg_expr in zip(func.params, args):
                if param.byref:
                    target = arg_expr
                    if isinstance(target, Var):
                        if target.name not in self.env:
                            raise Exception(f"Variable '{target.name}' not declared for BYREF")
                        frame_env[param.name] = Reference(self.env, target.name)
                    elif isinstance(target, FieldAccess):
                        struct = self.env.get(target.var_name)
                        if not isinstance(struct, dict):
                            raise Exception(f"'{target.var_name}' is not structured for BYREF")
                        frame_env[param.name] = Reference(struct, target.field_name)
                    else:
                        raise Exception("BYREF requires variable or field")
                else:
                    val = self.eval(arg_expr)
                    frame_env[param.name] = val

            old_env = self.env
            self.env = FrameWrapper(frame_env, self.env)
            try:
                for stmt in func.body:
                    try:
                        self.eval(stmt)
                    except ReturnSignal as rs:
                        return rs.value
                # 如果没有 return，可以返回 None 或抛错
                return None
            finally:
                self.env = old_env

        raise Exception(f"Unknown procedure/function: {name}")


    def convert(self, value, expected_type):
        if expected_type == "INTEGER":
            return int(value)
        elif expected_type == "REAL":
            return float(value)
        elif expected_type == "STRING":
            return str(value)
        elif expected_type == "CHAR":
            if isinstance(value, str) and len(value) == 1:
                return value
            raise TypeError("CHAR must be a single character string")
        elif expected_type == "BOOLEAN":
            if isinstance(value, str):
                if value == "TRUE":
                    return True
                if value == "FALSE":
                    return False
                raise TypeError("Invalid BOOLEAN string")
            if isinstance(value, bool):
                return value
            raise TypeError("Cannot convert to BOOLEAN")
        elif expected_type == "DATE":
            if isinstance(value, str):
                try:
                    return datetime.datetime.strptime(value.strip(), "%Y-%m-%d").date()
                except ValueError:
                    raise TypeError("DATE must be in format YYYY-MM-DD")
            if isinstance(value, datetime.date):
                return value
            raise TypeError("Invalid DATE type")
        else:
            return value
        
    def default_value(self, type_name):
        if type_name == "INTEGER":
            return 0
        if type_name == "REAL":
            return 0.0
        if type_name == "STRING":
            return ""
        if type_name == "CHAR":
            return ""  # 或者某个单字符默认
        if type_name == "BOOLEAN":
            return False
        if type_name == "DATE":
            return None  # 或者某个默认 date
        # user-defined 结构体不会走这里
        return None




    def eval(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.eval(stmt)

        elif isinstance(node, ArrayAccess):
            array_name = node.name
            array_info = self.env.get(array_name)
            if array_info is None or not isinstance(array_info, dict) or not array_info.get("is_array"):
                raise Exception(f"'{array_name}' is not an array")
            indices = [self.eval(idx) for idx in node.indices]
            lowers = array_info["lowers"]
            uppers = array_info["uppers"]
            if len(indices) != len(lowers):
                raise Exception(f"Incorrect number of indices for array '{array_name}'")
            for i, ind in enumerate(indices):
                if not (lowers[i] <= ind <= uppers[i]):
                    raise Exception(f"Index {ind} out of bounds for dimension {i+1} of array '{array_name}'")
            key = tuple(indices)
            if key in array_info["data"]:
                return array_info["data"][key]
            else:
                # 未赋值返回 base type 的默认值
                base = array_info["base_type"]
                return self.default_value(base)


        elif isinstance(node, Declare):
            if isinstance(node.type, PointerType):
                self.env[node.name] = None
                self.var_types[node.name] = node.type
            elif isinstance(node.type, str) and node.type in ("INTEGER", "REAL", "STRING", "CHAR", "BOOLEAN", "DATE"):
                self.env[node.name] = self.default_value(node.type)
                self.var_types[node.name] = node.type
            elif isinstance(node.type, str) and node.type in self.user_types:
                type_def = self.user_types[node.type]
                if isinstance(type_def, PointerType):  # pointer alias via TYPE T = ^INTEGER
                    self.env[node.name] = None
                    self.var_types[node.name] = type_def
                elif isinstance(type_def, dict):  # struct
                    self.env[node.name] = {
                        field_name: self.default_value(field_type)
                        for field_name, field_type in type_def.items()
                    }
                    self.var_types[node.name] = node.type
                else:
                    raise Exception(f"Unhandled user type definition for {node.type}")
            elif isinstance(node.type, ArrayType):
                name = node.name
                # 计算并存下 bounds（可以保持 expression 形式也可以提前 eval 成 int）
                lowers = []
                uppers = []
                for l in node.type.lowers:
                    lowers.append(self.eval(l) if not isinstance(l, int) else l)
                for u in node.type.uppers:
                    uppers.append(self.eval(u) if not isinstance(u, int) else u)

                # 初始化内部表示
                self.env[name] = {
                    "is_array": True,
                    "lowers": lowers,
                    "uppers": uppers,
                    "base_type": node.type.base_type,
                    "data": {},  # 存实际元素
                }
                self.var_types[name] = node.type  # 如果你后面需要追踪原始 ArrayType 可以保留，访问时 special-case
            elif node.type in ("INTEGER", "REAL", "STRING", "BOOLEAN", "CHAR", "DATE"):
                self.env[node.name] = self.default_value(node.type)
                self.var_types[node.name] = node.type
            elif isinstance(node.type, str) and node.type in self.user_types:
                typedef = self.user_types[node.type]
                if isinstance(typedef, dict):
                    # Struct 类型
                    self.env[node.name] = {
                        field_name: self.default_value(field_type)
                        for field_name, field_type in typedef.items()
                    }
                    self.var_types[node.name] = node.type
                elif isinstance(typedef, PointerType):
                    # Pointer alias 类型
                    self.env[node.name] = None
                    self.var_types[node.name] = typedef
                elif isinstance(typedef, ArrayType):
                    # Array alias（你没用过？预留）
                    self.env[node.name] = self.init_array(typedef)
                    self.var_types[node.name] = typedef
                else:
                    raise Exception(f"Unsupported user-defined type: {typedef}")

            else:
                raise Exception(f"Unknown type '{node.type}'")

        elif isinstance(node, Assign):
            value = self.eval(node.value)

            # 普通变量
            if isinstance(node.target, Var):
                var_name = node.target.name
                if var_name not in self.env:
                    raise Exception(f"Variable '{var_name}' used before declaration.")
                else:
                    expected_type = self.var_types.get(var_name)
                    if expected_type:
                        value = self.convert(value, expected_type)
                    self.env[var_name] = value

            # 字段访问（user-defined type）
            elif isinstance(node.target, FieldAccess):
                struct_name = node.target.var_name
                field_name = node.target.field_name
                struct = self.env.get(struct_name)
                if struct is None or not isinstance(struct, dict):
                    raise Exception(f"'{struct_name}' is not a structured variable")
                user_type_name = self.var_types.get(struct_name)
                if user_type_name not in self.user_types:
                    raise Exception(f"Unknown structured type '{user_type_name}' for {struct_name}")
                field_types = self.user_types[user_type_name]
                if field_name not in field_types:
                    raise Exception(f"'{field_name}' is not a field of type '{user_type_name}'")
                expected_type = field_types[field_name]
                value = self.convert(value, expected_type)
                struct[field_name] = value

            # 数组访问
            elif isinstance(node.target, ArrayAccess):
                array_name = node.target.name
                array_info = self.env.get(array_name)
                if array_info is None or not isinstance(array_info, dict) or not array_info.get("is_array"):
                    raise Exception(f"'{array_name}' is not an array")
                # 计算索引值
                indices = [self.eval(idx) for idx in node.target.indices]
                # bounds check
                lowers = [self.eval(b) if not isinstance(b, int) else b for b in array_info["lowers"]]
                uppers = [self.eval(b) if not isinstance(b, int) else b for b in array_info["uppers"]]
                if len(indices) != len(lowers):
                    raise Exception(f"Incorrect number of indices for array '{array_name}'")
                for i, ind in enumerate(indices):
                    if not (lowers[i] <= ind <= uppers[i]):
                        raise Exception(f"Index {ind} out of bounds for dimension {i+1} of array '{array_name}'")
                # 类型转换并赋值
                base_type = array_info["base_type"]
                converted = self.convert(value, base_type)
                key = tuple(indices)
                array_info["data"][key] = converted
            
            elif isinstance(node.target, Dereference):
                # 类似解引用左值写回
                ptr = self.eval(node.target.pointer)
                if not isinstance(ptr, PointerRef):
                    raise Exception("Left side is not a pointer dereference")
                name = ptr.var_name
                if isinstance(name, str):
                    self.env[name] = value
                elif isinstance(name, tuple):
                    if len(name) == 2 and isinstance(name[1], str):
                        struct = self.env.get(name[0])
                        if struct is None or not isinstance(struct, dict):
                            raise Exception(f"'{name[0]}' is not structured")
                        struct[name[1]] = value
                    elif len(name) == 2 and isinstance(name[1], tuple):
                        array_name, idxs = name
                        array_info = self.env.get(array_name)
                        key = tuple(idxs)
                        array_info["data"][key] = value
                else:
                    raise Exception(f"Cannot assign to dereferenced pointer: {name}")


            else:
                raise Exception("Unsupported assignment target")

        elif isinstance(node, Var):
            if node.name not in self.env:
                raise Exception(f"Variable '{node.name}' was not declared.")
            return self.env[node.name]

        elif isinstance(node, Number):
            return int(node.value)
        elif isinstance(node, Output):
            output_strs = []
            for v in node.values:
                val = self.eval(v)
                if isinstance(val, bool):
                    output_strs.append("TRUE" if val else "FALSE")
                else:
                    output_strs.append(str(val))
            self.output(" ".join(output_strs))



        elif isinstance(node, BinaryOp):
            left = self.eval(node.left)
            right = self.eval(node.right)
            return self.apply_op(left, node.operator, right)
        elif isinstance(node, While):
            while self.eval(node.condition):
                for stmt in node.body:
                    self.eval(stmt)
        elif isinstance(node, If):
            if self.eval(node.condition):
                for stmt in node.then_body:
                    self.eval(stmt)
            elif node.else_body:
                for stmt in node.else_body:
                    self.eval(stmt)
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, For):
            start = self.eval(node.start)
            end = self.eval(node.end)
            for i in range(start, end + 1):  # 包含 end
                self.env[node.var_name] = i
                for stmt in node.body:
                    self.eval(stmt)
        elif isinstance(node, RepeatUntil):
            while True:
                for stmt in node.body:
                    self.eval(stmt)
                if self.eval(node.condition):
                    break

        elif isinstance(node, CaseOf):
            case_val = self.eval(node.expr)
            matched = False
            for val_node, stmts in node.cases:
                if self.eval(val_node) == case_val:
                    for stmt in stmts:
                        self.eval(stmt)
                    matched = True
                    break
            if not matched:
                for stmt in node.otherwise:
                    self.eval(stmt)

        elif isinstance(node, Input):
            user_input = input(f"Enter value for {node.var_name}: ")
            expected_type = self.var_types.get(node.var_name)

            try:
                if expected_type == "INTEGER":
                    value = int(user_input)
                elif expected_type == "REAL":
                    value = float(user_input)
                elif expected_type == "STRING":
                    value = str(user_input)
                elif expected_type == "CHAR":
                    if len(user_input) != 1:
                        raise ValueError("CHAR must be a single character")
                    value = user_input
                elif expected_type == "BOOLEAN":
                    val = user_input.strip()
                    if val == "TRUE": #之前的写法是val in ("false", 0),但是考试不允许,只能是全大写
                        value = True
                    elif val == "FALSE": #之前的写法是val in ("false", 0),但是考试不允许,只能是全大写
                        value = False
                    else:
                        raise ValueError("Invalid boolean input")
                elif expected_type == "DATE":
                    value = datetime.datetime.strptime(user_input.strip(), "%Y-%m-%d").date()
                else:
                    value = user_input
            except Exception as e:
                raise ValueError(f"Invalid input for {expected_type}: {e}")

            self.env[node.var_name] = value

        elif isinstance(node, FieldAccess):
            struct = self.env.get(node.var_name)
            if struct is None or not isinstance(struct, dict):
                raise Exception(f"'{node.var_name}' is not a structured variable")
            return struct.get(node.field_name)
        
        elif isinstance(node, TypeDef):
            # 记录结构体定义：把字段列表变成名字->类型的 dict
            # 假设 node.fields 是 [(field_name, field_type), ...]
            self.user_types[node.name] = {fname: ftype for fname, ftype in node.fields}

        elif isinstance(node, ProcedureDef):
            self.procedures[node.name] = node

        elif isinstance(node, FunctionDef):
            self.functions[node.name] = node

        elif isinstance(node, CallStmt):
            return self._execute_call(node.call, expect_return=False)

        elif isinstance(node, Call):
            name = node.name.upper()  # 统一大小写判断内建
            # ---- 内建 string / numeric functions ----
            if name == "RIGHT":
                s = self.eval(node.args[0])
                x = self.eval(node.args[1])
                if not isinstance(s, str):
                    raise TypeError("RIGHT expects a string as first argument")
                x = int(x)
                return s[-x:] if x <= len(s) else s
            elif name == "LENGTH":
                s = self.eval(node.args[0])
                if not isinstance(s, str):
                    raise TypeError("LENGTH expects a string")
                return len(s)
            elif name == "MID":
                s = self.eval(node.args[0])
                start = self.eval(node.args[1])
                length = self.eval(node.args[2])
                if not isinstance(s, str):
                    raise TypeError("MID expects a string as first argument")
                start = int(start)
                length = int(length)
                if start < 1:
                    raise ValueError("MID start must be >= 1")
                return s[start - 1 : start - 1 + length]
            elif name == "LCASE":
                c = self.eval(node.args[0])
                if not (isinstance(c, str) and len(c) == 1):
                    raise TypeError("LCASE expects a single character")
                return c.lower()
            elif name == "UCASE":
                c = self.eval(node.args[0])
                if not (isinstance(c, str) and len(c) == 1):
                    raise TypeError("UCASE expects a single character")
                return c.upper()
            elif name == "INT":
                x = self.eval(node.args[0])
                try:
                    return int(float(x))
                except Exception:
                    raise TypeError("INT expects a numeric argument")
            elif name == "RAND":
                x = self.eval(node.args[0])
                try:
                    upper = float(x)
                except Exception:
                    raise TypeError("RAND expects a numeric argument")
                import random
                return random.random() * upper

            # ---- 不是内建的就走用户定义的 function/procedure ----
            return self._execute_call(node, expect_return=True)


        elif isinstance(node, Return):
            value = self.eval(node.expr) if node.expr is not None else None
            raise ReturnSignal(value)
        
        elif isinstance(node, AddressOf):
            # 取地址：返回指向变量名的轻量引用
            # 只允许对 Var / FieldAccess / ArrayAccess 取地址，根据你定义可以只支持 Var
            if isinstance(node.target, Var):
                return PointerRef(var_name=node.target.name)
            elif isinstance(node.target, FieldAccess):
                # 可以取结构体字段的地址：表示“结构体.field”
                return PointerRef(var_name=(node.target.var_name, node.target.field_name))
            elif isinstance(node.target, ArrayAccess):
                # 数组元素地址
                indices = [self.eval(idx) for idx in node.target.indices]
                return PointerRef(var_name=(node.target.name, tuple(indices)))
            else:
                raise Exception(f"Cannot take address of {type(node.target)}")
            
        elif isinstance(node, Dereference):
            ptr = self.eval(node.pointer)
            if not isinstance(ptr, PointerRef):
                raise Exception("Attempt to dereference a non-pointer")
            name = ptr.var_name
            # 支持三种地址形式：变量 / struct.field / array element
            if isinstance(name, str):
                return self.env.get(name)
            elif isinstance(name, tuple):
                if len(name) == 2 and isinstance(name[1], str):
                    # struct field
                    struct = self.env.get(name[0])
                    if struct is None or not isinstance(struct, dict):
                        raise Exception(f"'{name[0]}' is not structured")
                    return struct.get(name[1])
                elif len(name) == 2 and isinstance(name[1], tuple):
                    # array element
                    array_name, idxs = name
                    array_info = self.env.get(array_name)
                    if not array_info or not array_info.get("is_array"):
                        raise Exception(f"'{array_name}' is not an array")
                    key = tuple(idxs)
                    if key in array_info["data"]:
                        return array_info["data"][key]
                    else:
                        return self.default_value(array_info["base_type"])
            raise Exception(f"Invalid pointer reference: {ptr}")




        else:
            raise Exception(f"Unknown node type: {type(node)}")
        
    def apply_op(self, left, op, right):
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right  # 还是整数除法，按你原本实现
        elif op == '&':
            return str(left) + str(right)
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '=':
            return left == right
        elif op == '<>':
            return left != right
        elif op == '>=':
            return left >= right
        elif op == '<=':
            return left <= right
        else:
            raise Exception(f"Unsupported operator: {op}")
