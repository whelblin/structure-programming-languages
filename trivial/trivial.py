def resolve(s, e):
    #return e.get(s, None)
    if s in e:
        return e[s]
    else:
        return None

def evaluate(v, env):
    if type(v) is list:
        if len(v) == 0:
            return None
        assert type(v[0]) is str
        f = resolve(v[0], env)
        assert callable(f)
        values = [evaluate(value, env) for value in v[1:]]
        return f(values, env)
    if type(v) is str:
        return resolve(v, env) 
    return v 

env = {
    'x': 3,
    'y': 4,
    '+': lambda v, e: sum(v),
    '-': lambda v, e: v[0] - v[1],
    '*': lambda v, e: v[0] * v[1],
    '/': lambda v, e: v[0] / v[1],
}

def test_evaluate():
    print("test evaluate")
    assert evaluate(1, env) == 1
    assert evaluate(1.2, env) == 1.2
    assert evaluate('x', env) == 3
    assert evaluate(['+', 11, 22], env) == 33
    assert evaluate(['+', ['+', 11, 22], 22], env) == 55
    assert evaluate(['-', 33, 22], env) == 11
    assert evaluate(['*', 33, 2], env) == 66
    assert evaluate(['/', 33, 3], env) == 11

def test_resolve():
    print("test resolve")
    env = {
        'x': 3,
        'y': 4
    }
    assert resolve('x', env) == 3
    assert resolve('y', env) == 4

if __name__ == "__main__":
    test_evaluate()
    test_resolve()
    print("done")