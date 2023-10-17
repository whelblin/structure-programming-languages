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

def evaluate_print(x):
    print(x)
    return None

def evaluate(node):
    if type(node) is list:
        op = node[0]
        if op == "program":
            for statement in node[1]:
                evaluate(statement)
            return None
        if op == "print":
            return evaluate_print(evaluate(node[1]))
        if op in binary_operations:
            return evaluate_binary_operation(op, node[1], node[2])
    if type(node) in [float, int]:
        return node
    raise Exception(f"Unknown content in AST={node}")

def test_evaluate_operations():
    print("test evaluate operations")
    print(evaluate(["+", 1, 2]))
    assert evaluate(["+", 1, 2]) == 3
    assert evaluate(["-", 9, 2]) == 7
    assert evaluate(["*", 4, 2]) == 8
    assert evaluate(["/", 9, 3]) == 3

def test_evaluate_print():
    evaluate(["print",["+", 9, 12]])

if __name__ == "__main__":
    test_evaluate_operations()
    test_evaluate_print()
