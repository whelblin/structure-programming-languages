# Refactoring the Abstract Syntax Tree

## Introduction

In this particular discussion, we will cover a small but useful improvement in the representation of the abstract syntax tree (AST). 

_(Side note: as I write this note I'm traveling about 540 MPH in a Boeing 767 just south of Greenland. It's good to be mobile!)_

We will also cover adding unary negation to the AST and evaluator toward the end if this essay. 

## Updating the AST Representation

So we initially looked at syntax trees encoded in list structures, and that looked like this: 

```
    ["+", 
        ["/", 8, 4], 
        ["*", 2, 3]]
```
This approach of storing the minimum amount of information necessary to execute the program (or to generate code) has a lot of advantages. First, it's simple to understand and read. Second, it's relatively compact -- especially so if more compact representations are chosen. Finally, it's reasonably efficient to implement, producing interpreters that perform satisfactorily. One difficulty is that the various subtrees are only understood by their position in the parent node. For instance, in an assignment operation, which is the indicator of the assignment destination and which is the value to be assigned? This becomes even more problematic when other properties are added to the nodes, such as statement line numbers and coverage information for debugging purposes. Remembering what goes where can be problematic.

### Alternate Representations

There are good arguments for other kinds of approaches. Producing a class for each kind of activity, for instance, allows one to use the visitor pattern to write tree processing routines that don't have instruction lookup loops: for each tree node, just execute the action method for that node, and let each object have members representing the subtrees. For a production system, this can be very attractive. 

For initial implementations, though, it is not always easy to design class hierarchies in advance of knowing how everything works, and before understanding the properties required to add the features necessary for each of the nodes. As a compromise, one can use dictionaries to hold the syntax trees. The tree above becomes: 

```
    {
        "type": "binary", 
        "operator": +, 
        "left": {
            "type": "binary", 
            "operator": *, 
            "left": 8, 
            "right": 4
            }, 
        "right": {
            "type": "binary", 
            "operator": *, 
            "left": 2, 
            "right": 3
            }
    }
```

This is definitely more wordy, and probably slightly slower to execute when the program is run, but it is less ambiguous, easier to read and debug, and easier to add representations for additional features. 

### Parser Updates

To convert our parser to emit a dictionary-based AST, we will emit the following AST elements in place of their (commented-out) previous forms: 

For an entire program (or module): 

```
    # return ["program", statements]
    return {"type":"program","statements":statements}
```

For print statements:

```
        # return ["print", expression]
        return {"type": "print", "expression": expression}
```

For blocks (i.e. grouped sets of statements, in this case delimited by "{}" braces):

```
    # return ["block", statements]
    return {"type": "block", "statements": statements}
```

For the expression/term/factor tree:

        # left_term = [op, left_term, right_term]
        left_term = {"type": "binary", "left": left_term, "operator": operator, "right": right_term}

        # left_factor = [op, left_factor, right_factor]
        left_factor = {"type": "binary", "left": left_factor, "operator": operator, "right": right_factor}

You can find these changes as well as the updated tests in the `parser.py` code in this topic directory. 

Two quick notes. First, we use `pprint` to print dictionaries. The "pretty print" function makes them look nice, especially if you turn _off_ the `sort_dicts` option that puts the various keys into an un-useful alphabetic order. So use: 

```
from pprint import pprint
```

and
```
    pprint(ast, sort_dicts=False)
```

For nice looking, readable printouts. 

The second quick note is that there is code for unary negation here and there in the files. Read the bonus notes on unary negation below before examining those elements too closely. 

### Updating the Evaluator

Of course, since we are now emitting a hierarchical dictionary, we need to update the evaluation code.  This is pretty easy, since the same information is represented. In this case, the significance of each element is represented explicitly by the keys of the elements, rather than following conventions like "the first element is the numerator, the second is the denominator" and so forth. 

For each AST node, we now get the node type explicitly: 

```
        # op = node[0] 
        t = node["type"]
```

We can then handle the node appropriately according to type. When we get a binary operation type, we can dispatch the operation as we did before.

The evaluation becomes: 

```
def evaluate(node):
    if type(node) is dict:
        # op = node[0]
        t = node["type"]
        if t == "program":
            for statement in node["statements"]:
                evaluate(statement)
            return None
        if t == "print":
            return evaluate_print(evaluate(node["expression"]))
        if t == "binary":
            return evaluate_binary_operation(
                    node["operator"], 
                    node["left"], 
                    node["right"])
    if type(node) in [float, int]:
        return node
    raise Exception(f"Unknown content in AST={node}")
```

Here you can compare this to the previous version using positional indication of the contents of each node. 

You can find this code in `evaluate.py` along with updated tests. 

## Adding Unary Negation

As long as we are updating the parser and the AST, now might be a good time to look at unary negation. A few preliminary comments are required first. 

It's initially tempting to try to include unary negation (i.e. "negative signs") in the token generation for numbers. It's not hard to add the possibility of an initial "-" to the regex, but if you do so, then you are open to some problems. 

First, consider "1 -2"

Is this the token 1, followed by a token -2, or is it a 1/-/3 sequence? Remember, the tokenizer doesn't care about the big picture. It just looks at each individual token as they appear. 

A tokenizer looking at the "-2..." point (and remember, the tokenizer only looks forward) would have to make an impossible decision if it was trying to decide between "-" / "2" and "-2". 

Next, if you could correctly recognize negative numerical constants, you still could not negate more complex forms. For instance, what about this? 

```
- (3 - 2)

```

Or 

```
- ( - (4 - 2))
```

Or, once we have variables, 

```
-x
-(x-y)
```

And so forth. 

### Injecting Unary Operators

To do this, we need to implement the unary negation operator as a low-level, tightly bound operator. For instance, unary negation needs to bind more tightly than the subtraction sign. `-2-2` needs to be -4, not zero. 

We also should realize that there are other unary operators. Square root, for instance. We don't want to deal with these now, but it's important to note. 

So let's implement an AST form for unary operators: 

        {"type": "unary", "operator": operator, "expression": expression}

Then let's add a parser action to generate that when we find a negation (not a minus) sign in the token sequence. 

```
    elif current_token == "-":
        operator = get_current_token()
        consume_token()  # Consume '-'
        factor = parse_factor()
        return {"type": "unary", "operator": operator, "expression": factor}
```

Note that here the value being operated on is only a _factor_, not a complete (tightly bound) expression. If we don't do it this way, then precedence rules don't work. 

This code can be found in `parser.py` as well as a test function. 

Note that we don't need any changes in the tokenizer; the tokenizer doesn't have any opinion about what order the tokens should come in. It just needs them to be unambiguously determined as we read them left to right. 

### Unary Operator Evaluation 

Finally, we have to update the evaluator. Here we add a clause in the node interpreter to handle unary operations, and the negation unary operator: 

First the unary operation node:

```
        if t == "unary":
            return evaluate_unary_operation(
                    node["operator"], 
                    node["expression"], 
            )
```

And then the operation handler:

```
unary_operations = {
    "-": lambda x: -x,
}

def evaluate_unary_operation(op, x):
    assert op in unary_operations
    x = evaluate(x)
    return unary_operations[op](x)
```

Admittedly, this treatment of the unary negation operation is probably overly complicated if negation is the only unary operation to be implemented. Here we're doing it this way to demonstrate the principles involved rather than from a practical need to use the operation dispatch for this one operation. 

As usual we have added this code, and the test functions, to `evaluator.py`. 

## Conclusion

We've updated the AST and added unary negation. So far, things seem to be working. We have a few more details to add to the tokenizer and AST before this particular code can start carrying the weight of a "real" language, but we're getting very close. I also have a few code clean-ups to do, but they are just convenience items to enable debugging and easier refactoring.

See you next time!

