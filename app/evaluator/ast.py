from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

class Node:
    pass

class Statement:
    pass

class Expr:
    pass

class Stmt:
    pass

@dataclass
class Program(Node):
    statements: list[Node]

@dataclass
class Declare(Node):
    name: str
    type: str

@dataclass
class Assign:
    target: any  # Var or FieldAccess
    value: any   # expression

@dataclass
class Number(Node):
    value: float

@dataclass
class Var(Node):
    name: str

@dataclass
class BinaryOp(Node):
    left: Node
    operator: str
    right: Node

@dataclass
class If(Node):
    condition: Node
    body: list[Node]
    else_body: Optional[list[Node]] = None

@dataclass
class Output(Node):
    values: list[Node]

@dataclass
class String(Node):
    value: str

@dataclass
class While(Node):
    condition: Node
    body: list[Node]

@dataclass
class If(Node):
    condition: Node
    then_body: list
    else_body: list | None = None

@dataclass
class For(Node):
    var_name: str
    start: Node
    end: Node
    body: list[Node]


class RepeatUntil(Node):
    def __init__(self, body, condition):
        self.body = body  # list of statements
        self.condition = condition  # expression

@dataclass
class CaseOf(Statement):
    expr: Expr
    cases: list[tuple[Expr, list[Statement]]]  # ← 应是 Expr
    otherwise: Optional[list[Statement]]

@dataclass
class Input(Statement):
    var_name: str

@dataclass
class TypeDef:
    name: str
    fields: list[tuple[str, str]]  # [(field_name, field_type)]

@dataclass
class FieldAccess(Expr):  # 如果你有 Expr 基类
    var_name: str
    field_name: str

@dataclass
class Param:
    name: str
    type: str
    byref: bool

@dataclass
class ProcedureDef:
    name: str
    params: list[Param]
    body: list[Stmt]

@dataclass
class FunctionDef:
    name: str
    params: list[Param]
    return_type: str
    body: list[Stmt]

@dataclass
class Call:
    name: str
    args: list[Expr]

@dataclass
class CallStmt(Stmt):  # 作为语句的 CALL，比如 CALL Increment(v)
    call: Call

@dataclass
class Return(Stmt):
    expr: Optional[Expr]

@dataclass
class ArrayType:
    lowers: list[int]      # [1] 或 [1,1]
    uppers: list[int]      # [5] 或 [3,3]
    base_type: str         # "INTEGER", "REAL", etc.

@dataclass
class ArrayAccess:
    name: str
    indices: list[Expr]  # 每个维度的表达式

@dataclass
class AddressOf:
    target: Expr  # 比如 Var("x") 表示 ^x

@dataclass
class Dereference:
    pointer: Expr  # 比如 Var("p") 表示 p^

@dataclass
class PointerRef:
    var_name: str  # 表示指向哪个变量

@dataclass
class PointerType:
    base_type: str  # e.g., "INTEGER", "REAL", etc.
