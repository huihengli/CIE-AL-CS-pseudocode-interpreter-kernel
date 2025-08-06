import re
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str

def tokenize(code: str) -> list[Token]:
    token_specification = [
        ("COMMENT", r"//[^\n]*"),  # 整行注释
        ("COLON", r":"),
        ("ASSIGN", r"<-"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACKET", r"\["),
        ("RBRACKET", r"\]"),
        ("COMMA", r","),
        ("CARET", r"\^"),
        ("STRCOMB", r"&"),
        ("NEQ", r"<>"),
        ("GTE", r">="),
        ("LTE", r"<="),
        ("OPERATOR", r"[+\-*/><=]"),
        ("NUMBER", r"\d+(\.\d+)?"),  # 支持实数
        ("STRING", r'"[^"\n]*"'),
        ("KEYWORD", r"\b(OUTPUT|IF|THEN|ELSE|ENDIF|WHILE|ENDWHILE|DECLARE|INTEGER|REAL|STRING|INPUT|FOR|TO|NEXT|REPEAT|UNTIL|OTHERWISE|ENDCASE|CHAR|DATE|BOOLEAN|TYPE|ENDTYPE|PROCEDURE|ENDPROCEDURE|FUNCTION|ENDFUNCTION|RETURN|RETURNS|CALL|ARRAY|OF|CASE OF)\b"),
        ("DOT", r"\."),
        ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
        ("NEWLINE", r"\n"),
        ("SKIP", r"[ \t]+"),
        ("MISMATCH", r"."),
    ]

    tok_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specification)
    token_re = re.compile(tok_regex)

    code_no_comments = []
    for line in code.splitlines():
        if '//' in line:
            line = line.split('//', 1)[0]  # 去掉注释
        code_no_comments.append(line)
    code = '\n'.join(code_no_comments)


    tokens = []

    for match in token_re.finditer(code):
        kind = match.lastgroup
        value = match.group()
        if kind in ("SKIP", "NEWLINE", "COMMENT"):
            continue
        elif kind == "MISMATCH":
            raise RuntimeError(f"Unexpected token: {value}")
        else:
            tokens.append(Token(kind, value))
    return tokens
