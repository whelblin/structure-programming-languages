# Implementing Control Structures

## Introduction

In this discussion, we will implement _if/else_ and _while_ control structures. 

## Tokenizer

We note that we already have the necessary keywords recognized in the tokenizer. Let's check the tests to make sure we're getting the right results: 

```
def test_keywords():
    print("testing keywords")
    for keyword in ["print","if","else","while"]:
        assert tokenize(keyword) == [keyword]
```

Looks good. 

## Adding _if_ statements

Note: For now, we're basically treating a 0 value as false and anything else as true. 

The _if_ statement basically needs a condition and one or two statements. The first statement is evaluated if the condition is true, and the second statement is evaluated if an _else_ keyword is present followed by that statement, and if the condition is false. 

### Parsing the _if_ keyword

The _if_ keyword starts a statement, so let's add some code for that into the statement recognition code. Here we look for the _if_ keyword, followed by a conditional expression in parentheses.

```
    if current_token == "if":
        consume_token()  # Consume 'if'
        if get_current_token() != "(":
            raise Exception("Expected '('")
        consume_token()
        condition = parse_expression()
        if get_current_token() != ")":
            raise Exception("Expected ')'")
        consume_token()
        then_statement = parse_statement()
```

Let's go ahead and add some code to see if we have a following _else_ keyword, and if so, parse the subsequent statement. 

```
        if get_current_token() != "else":
            consume_token()
            else_statement = parse_statement()
        else:
            else_statement = None
```

And now let's return the node entry for the parse tree.

        return {"type": "if", 
            "condition": condition,
            "then" : then_statement,            
            "else" : else_statement,
        }

Here's some test code for the _if_ statement, testing a few variations with and without else clauses and block statements. 

```
def test_if_statement():
    tokens = tokenize("if (1) j = 2;")
    print(tokens)
    ast = parse(tokens)
    pprint(ast, sort_dicts=False)
    assert ast == {
        'type': 'program',
        'statements': [{
            'type': 'if',
            'condition': 1.0,
            'then': {
                'type': 'assignment', 
                'name':  'j', 
                'expression': 2.0},
            'else': None }]}
    tokens = tokenize("if (1) j = 2; else j = 0;")
    print(tokens)
    ast = parse(tokens)
    pprint(ast, sort_dicts=False)
    assert ast == {
        'type': 'program',
        'statements': [{
            'type': 'if',
            'condition': 1.0,
            'then': {
                'type': 'assignment', 
                'name':  'j', 
                'expression': 2.0},
            'else': {
                'type': 'assignment', 
                'name':  'j', 
                'expression': 0.0}}]}
    tokens = tokenize("if (1) {j=1; k=2;} else {j=0; k=1;}")
    print(tokens)
    ast = parse(tokens)
    pprint(ast, sort_dicts=False)
    assert ast == {
        'type': 'program',
        'statements': [{'type': 'if',
                 'condition': 1.0,
                 'then': {'type': 'block',
                          'statements': [{'type': 'assignment',
                                          'name': 'j',
                                          'expression': 1.0},
                                         {'type': 'assignment',
                                          'name': 'k',
                                          'expression': 2.0}]},
                 'else': {'type': 'block',
                          'statements': [{'type': 'assignment',
                                          'name': 'j',
                                          'expression': 0.0},
                                         {'type': 'assignment',
                                          'name': 'k',
                                          'expression': 1.0}]}}]}
```

### Executing the _if_ keyword

At this point we need to go execute that parse tree. 

In the evaluator, we have to implement the handler for the _if_ node type. Let's start by recognizing the node and calling the handler: 

```
        if t == "if":
            return evaluate_if(
                node["condition"],
                node["then_statement"],
                node["else_statement"]
            )
```

And then implement the handler function: 

```
def evaluate_if(condition, then_statement, else_statement):
    if evaluate(condition):
        return evaluate(then_statement)
    else:
        if else_statement:
            return evaluate(else_statement)
        else:
            return None
```

We also need to implement `block` which looks a lot like `program`: 

```
        if t == "block":
            for statement in node["statements"]:
                most_recent_value = evaluate(statement)
            return most_recent_value
```

While we're here, let's update _print_ handling, removing the recursive evaluation from the dispatch code into the handler function. Here's the dispatch code:  

```
        if t == "print":
            return evaluate_print(node["expression"])
```

And the handler: 

```
def evaluate_print(x):
    x = evaluate(x)
    print(x)
    return x
```

Of course we have some test code. Recall that we have made most of the statements return the last expression evaluated. 

```
def test_evaluate_if():
    tokens = tokenize("if (1) j = 2;")
    ast = parse(tokens)
    assert evaluate(ast) == 2

    tokens = tokenize("if (1) j = 2; else j = 0;")
    ast = parse(tokens)
    assert evaluate(ast) == 2

    tokens = tokenize("if (1) {j=1; k=2;} else {j=0; k=1;}")
    ast = parse(tokens)
    assert evaluate(ast) == 2

    tokens = tokenize("if (0) {j=1; k=2;} else {j=0; k=1;}")
    ast = parse(tokens)
    assert evaluate(ast) == 1
```

Now we have a working `if` statement!


## Adding _while_ statements

### Preliminary requirements. 

Before we implement the _while_ statement, we need to consider that in order to use a _while_ statement, we must be able to modify the state. If we can't, we either will never execute the statement (if the condition is false) or we will execute the statement forever (if the condition is true.) It is only if we can modify the outcome of the condition within the loop (or have it modified by some external fact) that we can use the while loop for anything useful. 

We need to make sure we're ready for this, so let's add this test code to the evaluator: 

```
def test_mutable_environment():
    tokens = tokenize("""
    x = 23;
    x = x - 1;
    x = x - 1;
    y = x;
    x = x - 1 + y;
    """)
    assert evaluate(parse(tokens)) == 41
```

That works, so we're ready to go. 

## Parsing the _while_ keyword. 

The _while_ keyword also starts a statement, so let's add that code to the parser, too. It's actually easier than the _if_ code. Again, we look for a condition in parentheses, followed by a statement. 

```
    if current_token == "while":
        consume_token()  # Consume 'while'
        if get_current_token() != "(":
            raise Exception("Expected '('")
        consume_token()
        condition = parse_expression()
        if get_current_token() != ")":
            raise Exception("Expected ')'")
        consume_token()
        do_statement = parse_statement()
```

And now let's return the node entry for the parse tree.

        return {"type": "while", 
            "condition": condition,
            "do" : do_statement,            
        }

Here's some test code for the _while_ statement, testing a few variations with and without else clauses and block statements. 

```
def test_while_statement():
    tokens = tokenize("k = 3; while (k) k = k - 1;")
    print(tokens)
    ast = parse(tokens)
    pprint(ast, sort_dicts=False)
```

### Executing the _while_ keyword

In the evaluator, we have to implement the handler for the _while_ node type. Again, let's start by recognizing the node and calling the handler: 

```
        if t == "while":
            return evaluate_while(
                node["condition"],
                node["do"],
            )
```

And then implement the handler function: 

```
def evaluate_while(condition, do_statement):
    result = None
    while evaluate(condition):
        result = evaluate(do_statement)
    return result
```

Remember that it's not really normal for a statement to return a value, and the language parser doesn't allow using that value, but it's convenient for testing purposes. Like other statements, _while_ returns the last statement evaluated, unless no statement was evaluated at all, in which case it returns _None_. 

So let's create some test code: 

```
def test_evaluate_while():
    tokens = tokenize("k = 3; while (k) k = k - 1;")
    print(evaluate(parse(tokens)))
    assert evaluate(parse(tokens)) == 0
```

Of course this will all get a lot more useful when we implement logical operators and comparison operators. We'll do that pretty soon!

By all means grab a copy of this code and try it out!



