from app.evaluator.tokenizer import Token

def test_token():
    t = Token("KEYWORD", "DECLARE")
    print(t)

if __name__ == "__main__":
    test_token()
