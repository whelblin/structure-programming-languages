The first generation of our language tools will execute a very simple language. 

The language supports "print" statements with math expressions.

Here are some examples:

```
print 1;
print 1+2;
print 1+2*3;
print (1+2)*3;
```

The output of running this program should be:

```
1
3
7
9
```

The EBNF of our language is as follows:

```
<program>       ::= { <statement> }
<statement>     ::= "print" <expression> ";"
                  | <block>
<block>         ::= "{" { <statement> } "}"
<expression>    ::= <term> { ("+" | "-") <term> }
<term>          ::= <factor> { ("*" | "/") <factor> }
<factor>        ::= <number> | "(" <expression> ")"
<number>        ::= [0-9]+
```

## The tokenizer

We can look for tokens in the grammar that we can scan for in our tokenizer. We find the keyword `print`, the concept of a number, the operator tokens *, /, +, -, (, ), the statement terminator ';' and the block statement group delimiters { and }.

That gives us the following tokenizer patterns: 

```
patterns = [
    [r"print","print"],
    [r"number","number"],
    [r"\d+(\.\d*)?", "NUMBER"],
    [r"\+","+"],
    [r"-","-"],
    [r"\*","*"],
    [r"/","/"],
    [r"\(","("],
    [r"\)",")"],
    [r"\{","{"],
    [r"\}","}"],
    [r"\;",";"],
```

You are encouraged to play with the file `tokenizer.py` to see what tokens are produced by various strings. 

For instance, the string "3+4*(2-5)" should product the token stream (noting that whitespace isn't relevant):

```
    [
     ["NUMBER", "3"],"+",["NUMBER", "4"],"*",
     "(",["NUMBER", "2"],"-",["NUMBER", "5"],")",
    ]
```

## Parsing

The purpose of the parser is to take token streams and use the rules of the grammar to generate unambigous descriptions of the steps to be taken to execute the intended state transformations and other operations described in the programs. 

The file `parser.py` accepts a token stream and emits an abstract syntax tree (AST) that, when evaluated, will either run the program or generate the (possibly virtual) machine instructions to run the program. 

So for the program: 

```
print 3+4*(2-5);
```

we first get the token string:

```
[
    'print', ['NUMBER', '3'], '+', ['NUMBER', '4'], '*', 
    '(', ['NUMBER', '2'], '-', ['NUMBER', '5'], ')', ';'
]
```

Feeding this to the parser, we get the AST:

```
['program', 
    [['print', 
        ['+', ['NUMBER', '3'], 
            ['*', ['NUMBER', '4'], 
                ['-', ['NUMBER', '2'], ['NUMBER', '5']]]]]]]
```

Notice that because this is prefix notation, we don't need parentheses, etc. This is just a representation of work to be done. 

If you look at the code of the parser, you can see that it reflects the EBNF grammar used to describe the language. In this case because it's a simple grammar, the parser was written manually using a method called "recursive descent parsing." In this case we write basically a parsing function for each EBNF rule, and send the token list into the topmost rule (in this case called simply, "parse()"). That function then calls lower functions that in turn call lower functions (hence the "descent" part of the name.)

If the parsing happens to find something like parentheses that imply a nested part of the grammar, the parser simply calls the function appropriate to call the enclosed section. This is often a call to parse a grammar element that the parser is already parsing, so a recursive call to a contained section is appropriate. This is where the "recursive" part of the name comes in. 

It's important to know that recursive descent parsing is limited in the kinds of languages it can parse. The parser needs to be able to know which sub-components to descend into based on the next token in the stream. 

There are a number of programming language concepts (for instance, sometimes expression grammar rules) that are formed with left-recursive grammars. The book covers this to some extent. In larger languages, other methods are used to programmatically generate parsers that can handle left-recursive grammars.

Here's an (informal) example of left-recursive rules:

```
    <expression> ::= <expression> '+' <term>
    <expression> ::= <expression> '-' <term>
    <expression> ::= <term>
    <term> ::= <term> '*' <factor>
    <term> ::= <term> '/' <factor>
    <term> ::= <factor>
    <factor> ::= NUMBER
```

Notice the use of left-recursion to allow repetition of things like `1+2+3`. 

In my experience, however, many programming languages are easily implemented using recursive descent parsing, and it's frequently easy to write the grammar in such a way as to avoid left-recursion. If you look at the grammar for our little language, you'll find it has no left-recursive rules. This is partially accomplished by using the ENBF repeated-section capabilities.  

## Execution/Evaluation

In interpretive languages, we often refer to "evaluation" as the attempt to interpret the intention and results of an expression or program. 

An interpretive evaluation engine starts at the top of the abstract syntax tree and recursively visits all the nodes in the tree (except in the case of conditional branches, where only one branch may be visited depending on the condition). At each node, the intention of the node is assessed. If the node has sub-branches, those sub-branches are generally evaluated, so that their results can be used in the evaluation of the result of the current branch. The result is then returned to whatever node evaluation function requested this node's result, and so forth. Calls go from the top of the tree to the bottom, and results are passed from the bottom back to the top, with each node's action generally doing one of several things. Major activites include: 

   - computing a result based on lower results
   - storing a result -- e.g. modifying state
   - conditionally or repetitively executing a statement or block
   - calling or declaring a function

We have an execution engine for our little language in `evaluator.py`. Its `evaluate()` function accepts an AST and executes each node as described below. 

Recall that the AST we're working with is:

Feeding this to the parser, we get the AST:

```
['program', 
    [['print', 
        ['+', ['NUMBER', '3'], 
            ['*', ['NUMBER', '4'], 
                ['-', ['NUMBER', '2'], ['NUMBER', '5']]]]]]]
```

So the code

```
evaluate(['program', 
            [['print', 
                ['+', ['NUMBER', '3'], 
                    ['*', ['NUMBER', '4'], 
                        ['-', ['NUMBER', '2'], ['NUMBER', '5']]]]]]]
)
```

produces 

```
21
```

Which is the result of our initial program:

```
```

## Conclusion

Feel free to examine the code for the tokenizer, the parser, and the evaluator.  There will be a short homework problem based on these three code modules. 




