# Assuming the tokens are generated and stored in a list called 'tokens'.
# We'll use a global pointer 'current_token_index' to keep track of the current token being processed.

tokens = []  # Example: ["print", ["number", 1], "+", ["number", 2], ";", "{", ...]
current_token_index = 0

def get_current_token():
    global current_token_index
    if current_token_index < len(tokens):
        return tokens[current_token_index]
    return None

def consume_token():
    global current_token_index
    current_token_index += 1

def parse(program_tokens):
    global tokens
    global current_token_index
    current_token_index = 0
    tokens = program_tokens
    statements = []
    while get_current_token() is not None:
        statements.append(parse_statement())
    return ["program", statements]

def parse_statement():
    current_token = get_current_token()
    if current_token == "print":
        consume_token()  # Consume 'print'
        expr = parse_expression()
        if get_current_token() != ";":
            raise Exception("Expected ';'")
        consume_token()
        return ["print", expr]
    elif current_token == "{":
        return parse_block()
    else:
        raise Exception("Unexpected token in statement")

def parse_block():
    consume_token()  # Consume '{'
    statements = []
    while get_current_token() != "}":
        statements.append(parse_statement())
    consume_token()  # Consume '}'
    return ["block", statements]

def parse_expression():
    left_term = parse_term()
    while get_current_token() in ["+", "-"]:
        op = get_current_token()
        consume_token()
        right_term = parse_term()
        left_term = [op, left_term, right_term]
    return left_term

def parse_term():
    left_factor = parse_factor()
    while get_current_token() in ["*", "/"]:
        op = get_current_token()
        consume_token()
        right_factor = parse_factor()
        left_factor = [op, left_factor, right_factor]
    return left_factor

def parse_factor():
    current_token = get_current_token()
    if isinstance(current_token, list) and current_token[0] == "number":
        consume_token()
        return float(current_token[1])
    elif current_token == "(":
        consume_token()  # Consume '('
        expr = parse_expression()
        if get_current_token() != ")":
            raise Exception("Expected ')'")
        consume_token()  # Consume ')'
        return expr
    else:
        raise Exception("Unexpected token in factor")

# Example usage:

from tokenizer import tokenize

def test_parse():
    print("testing parse")
    program_tokens = tokenize("print 1+2; {print 3; print 4;}")
    assert program_tokens == ["print", ["number", 1], "+", ["number", 2], ";", "{", "print", ["number", 3], ";", "print", ["number", 4], ";", "}"]
    ast = parse(program_tokens)
    print(ast)
    assert ast == ['program', [['print', ['+', 1.0, 2.0]], ['block', [['print', 3.0], ['print', 4.0]]]]]

if __name__ == "__main__":
    test_parse()



