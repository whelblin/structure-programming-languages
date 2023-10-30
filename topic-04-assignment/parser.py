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
    # return ["program", statements]
    return {"type":"program","statements":statements}

def parse_statement():
    current_token = get_current_token()
    if current_token == "print":
        consume_token()  # Consume 'print'
        expression = parse_expression()
        if get_current_token() != ";":
            raise Exception("Expected ';'")
        consume_token()
        # return ["print", expression]
        return {"type": "print", "expression": expression}

    elif type(current_token) is list and current_token[0] == "identifier":
        name = current_token[1]
        consume_token()
        if get_current_token() != "=":
            raise Exception("Expected '=' for assignment statement")
        consume_token()
        expression = parse_expression()
        if get_current_token() != ";":
            raise Exception("Expected ';'")
        consume_token()
        return {"type": "assignment", "name": name, "expression": expression}

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
    # return ["block", statements]
    return {"type": "block", "statements": statements}

def parse_expression():
    left_term = parse_term()
    while get_current_token() in ["+", "-"]:
        operator = get_current_token()
        consume_token()
        right_term = parse_term()
        # left_term = [op, left_term, right_term]
        left_term = {"type": "binary", "left": left_term, "operator": operator, "right": right_term}
    return left_term

def parse_term():
    left_factor = parse_factor()
    while get_current_token() in ["*", "/"]:
        operator = get_current_token()
        consume_token()
        right_factor = parse_factor()
        # left_factor = [op, left_factor, right_factor]
        left_factor = {"type": "binary", "left": left_factor, "operator": operator, "right": right_factor}
    return left_factor

def parse_factor():
    current_token = get_current_token()
    if isinstance(current_token, list) and current_token[0] == "number":
        consume_token()
        return float(current_token[1])
    elif isinstance(current_token, list) and current_token[0] == "identifier":
        consume_token()
        return {"type": "identifier", "name": current_token[1]}
    elif current_token == "-":
        operator = get_current_token()
        consume_token()  # Consume '-'
        factor = parse_factor()
        return {"type": "unary", "operator": operator, "expression": factor}
    elif current_token == "(":
        consume_token()  # Consume '('
        expression = parse_expression()
        if get_current_token() != ")":
            raise Exception("Expected ')'")
        consume_token()  # Consume ')'
        return expression
    else:
        raise Exception("Unexpected token in factor")

# Example usage:

from tokenizer import tokenize
from pprint import pprint

def test_parse():
    print("testing parse")
    program_tokens = tokenize("print 1+2; {print 3; print 4;}")
    print(program_tokens)
    assert program_tokens == [ "print", ["number", 1], "+", ["number", 2], ";", "{", "print", ["number", 3], ";", "print", ["number", 4], ";", "}"]
    ast = parse(program_tokens)
    pprint(ast, sort_dicts=False)   
    assert ast == {'type': 'program', 'statements': [
        {'type': 'print', 'expression': 
            {'type': 'binary', 'left': 1.0, 'operator': '+', 'right': 2.0}
        }, 
        {'type': 'block', 'statements': [{'type': 'print', 'expression': 3.0}, {'type': 'print', 'expression': 4.0}]}]}

def test_parse_with_identifier():
    print("testing parse with identifier")
    program_tokens = tokenize("x=4;")
    print(program_tokens)
    ast = parse(program_tokens)
    print(ast)
    program_tokens = tokenize("print x+3;")
    print(program_tokens)
    ast = parse(program_tokens)
    print(ast)

def test_parse_unary_negation():
    print("testing parse unary negation")
    tokens = tokenize("print -2-2;")
    print(tokens)
    ast = parse(tokens)
    pprint(ast, sort_dicts=False)
    assert ast == {'type': 'program',
                 'statements': [{'type': 'print',
                 'expression': {'type': 'binary',
                                'left': {'type': 'unary',
                                         'operator': '-',
                                         'expression': 2.0},
                                'operator': '-',
                                'right': 2.0}}]}

if __name__ == "__main__":
    test_parse()
    test_parse_with_identifier()
    test_parse_unary_negation()



