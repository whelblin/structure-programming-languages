binary_operations = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
}

def evaluate_binary_operation(op, x, y):
    assert op in binary_operations
    x = evaluate(x)
    y = evaluate(y)
    return binary_operations[op](x,y)

unary_operations = {
    "-": lambda x: -x,
}

def evaluate_unary_operation(op, x):
    assert op in unary_operations
    x = evaluate(x)
    return unary_operations[op](x)

environment = {}

def evaluate_assignment(name, x):
    x = evaluate(x)
    environment[name] = x
    print(environment)

def evaluate_print(x):
    print(x)
    return x

def evaluate(node):
    if type(node) is dict:
        # op = node[0]
        t = node["type"]
        if t == "program":
            for statement in node["statements"]:
                most_recent_value = evaluate(statement)
            return most_recent_value
        if t == "print":
            return evaluate_print(evaluate(node["expression"]))
        if t == "binary":
            return evaluate_binary_operation(
                    node["operator"], 
                    node["left"], 
                    node["right"])
        if t == "unary":
            return evaluate_unary_operation(
                    node["operator"], 
                    node["expression"] 
            )
        if t == "assignment":
            return evaluate_assignment(
                    node["name"],
                    node["expression"]
            )
        if t == "identifier":
            name = node["name"]
            return environment[name]
    if type(node) in [float, int]:
        return node
    raise Exception(f"Unknown content in AST={node}")

from tokenizer import tokenize
from parser import parse
from pprint import pprint

def test_evaluate_operations():
    print("test evaluate operations")
    assert evaluate({"type":"binary", "operator":"+", "left":1, "right":2}) == 3
    assert evaluate({"type":"binary", "operator":"-", "left":9, "right":2}) == 7
    assert evaluate({"type":"binary", "operator":"*", "left":4, "right":2}) == 8
    assert evaluate({"type":"binary", "operator":"/", "left":9, "right":3}) == 3

def test_evaluate_print():
    evaluate({"type":"print","expression":
                {"type":"binary", "operator":"/", "left":9, "right":3}})

def test_evaluate_unary_negation():
    assert evaluate({"type":"unary",
              "operator": "-",
              "expression":{"type":"binary", "operator":"-", "left":4, "right":2}
              }) == -2

    print("testing parse unary negation")
    tokens = tokenize("print -2-2;")
    print(tokens)
    ast = parse(tokens)
    evaluate(ast)
    tokens = tokenize("print -(2-2);")
    print(tokens)
    ast = parse(tokens)
    evaluate(ast)
    tokens = tokenize("print -(2)-(2);")
    print(tokens)
    ast = parse(tokens)
    evaluate(ast)

def test_evaluate_assignment():
    tokens = tokenize("x=4;y=5;")
#    print(tokens)
    ast = parse(tokens)
#    print(ast)
    evaluate(ast)
    tokens = tokenize("print x+3;")
#    print(tokens)
    ast = parse(tokens)
    pprint(ast, sort_dicts=False)
    evaluate(ast)
    print("result = ",[evaluate(ast)])
    assert evaluate(ast) == 7

if __name__ == "__main__":
    # test_evaluate_operations()
    # test_evaluate_print()
    # test_evaluate_unary_negation()
    test_evaluate_assignment()

