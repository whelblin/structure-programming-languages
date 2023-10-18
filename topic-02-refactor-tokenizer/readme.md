# Refactoring the Tokenizer

## Introduction

Tonight we're going to cover improvements in the tokenizer. We won't be adding specific functionality, but we will be building additional robustness into the existing capabilities that we will use in as we add features. 

_(Side note: as I write this note (but not the code -- that's already done) I'm traveling about 190 MPH in an Italian high-speed train through some mountainous areas. Isn't technology great?)_

## Improving the existing patterns

We followed a model for the tokenizer where simple tokens (i.e tokens that just represented themselves) were simply represented as the token value (e.g. "+"). This also works for keywords like "print" and "if", so let's add those:

```
patterns = [     
    [r"print", "print"],  # print keyword
    [r"if", "if"],        # if keyword
    [r"else", "else"],    # else keyword
    [r"while", "while"],  # while keyword
    [r"\+", "+"],
    [r"-", "-"],
    [r"\*", "*"],
    [r"/", "/"],
    [r"\(", "("],
    [r"\)", ")"],
    [r"\{", "{"],
    [r"\}", "}"],
    [r"\;", ";"],
]
```

## Additional simple tokens

For good measure we have gone ahead and added a few more simple tokens:

```
    [r"==", "=="],
    [r"!=", "!="],
    [r"<=", "<="],
    [r">=", ">="],
    [r"<", "<"],
    [r">", ">"],
    [r"=", "="],
    [r"\[", "["],
    [r"\]", "]"],
    [r",", ","],
```

We don't use these tokens in our current language, but we will use them eventually. 

A side note: we trivially changed the handling of tokens in the tokenize function. Since we don't have to deal with the problem of possibly not matching (more on that later) we decided to simply append each token to a growing list of tokens that is eventually returned. 


I also represented tokens that have values (like numbers) with complex tokens containing the token _type_ (like "number") and the token _value_ (like 1.23) as ["NUMBER",123]. Since we also need to do this with strings and identifiers, we have updated the pattern table to have patterns for _number_, _string_, and _identifier_ tokens. Let's cover each in turn.  


## Numerical literals

Recall that numbers are matched by this pattern: 

```
    [r"\d+(\.\d*)?", "number"],   # numeric literals
```

Note that we have changed to lowercase token names. 


The current number-handling code in the tokenizer looks like this: 

```
        if token == "number":
            tokens.append([token, number(match.group(0))])
            continue
```

This is pretty much the same as the previous code, except that we are directly appending the token to the token stream. 


## String literals

So we will go ahead and add a string token, that will match string literals enclosed in quotes, and will allow embedded quotes by using two quotes together. 

To manage this, we will add this pattern: 

```
    [r'"([^"]|"")*"', "string"],  # string literals
```

And we will add this code to the tokenizer:

```
        if token == "string":
            # omit closing and beginning strings, replace two quotes with one quote
            tokens.append([token, match.group(0)[1:-1].replace('""', '"')])
            continue
```

There is of course test code for this feature in the source code. 

## Identifiers

We want to eventually be able to recognize identifiers, for several uses. Depending on where they appear, they might be variable names or function names (or function calls). 

Keep in mind that we have already scanned for all the keyword tokens, so anything token matched here shouldn't be a keyword. This is why we have to make sure this rule (which is the only ambiguous case, where a second rule might match something) is checked after checking all the keywords. 

So we want a complex token for identifers. We will use `["identifier","foobar"]` as the type/value pair for this complex token. 

So we will add the following pattern: 

    [r"[a-zA-Z_][a-zA-Z0-9_]*", "identifier"],  # identifiers

Then, this code will emit the identifier when found: 

        if token == "identifier":
            tokens.append([token, match.group(0)])
            continue

## Whitespace

Next, let's tackle whitespace. Previously, we eliminated whitespace in a preliminary step between token identification steps. It occurred to me that we could just establish whitespace as an inconsequential token and throw it away when we found it. So we added a whitespace rule: 

```
    [r"\s+", None],       # Whitespace
```

This allows us to handle whitespace simply in code: 

```
        if token == None:
            continue
```

Finally, if none of our regular expressions has matched, including the whitespace expression, we previously had an "if we didn't find a match" error handler. We have replaced that with a very general "matches-anything" regular expression at the end of the pattern list that generates an "error" token. 

```
    [r".", "error"],  # unexpected content
```

This is handled very simply in the code by looking for an "error" token and if found, complaining about it with an assertion. We could raise an exception here later, but we will eventually want a more general error handling capability, so for now an assertion will do. 

```
        assert token != "error", "Syntax error: illegal character at " + match.group(0)
```

Again, we will be improving on this error handler, and may add a few more features to the tokenizer, but this should cover the major features we will need as we move forward. 

This code is checked into the repo at `.../topic-02-refactoring/evaluator.py` and includes tests for all of these features. 

## Parser fixes

We have only made two changes to the parser here. 

The first is to change the "NUMBER" token to "number" to align with the upcoming "string" and "identifier" tokens, and the second was to emit the numeric literal directly into the AST instead of emiting the "numeric" token. Since the AST can hold number literals directly, this wasn't necessary. 

This code now looks like this: 

```
    if isinstance(current_token, list) and current_token[0] == "number":
        consume_token()
        return float(current_token[1])
```

The tests were updated to reflect these changes.

## Evaluator fixes

Since the "number" token is no longer emitted into the AST, the `evaluator.py` code is updated to deal with the possibility of number literals at node points in the AST. 

This code looks like this:

```
    if type(node) in [float, int]:
        return node
```

It yields the same results as before, but the AST is smaller and cleaner. 

## Adding a code runner

There is now a `runner.py` program which is a small utility to glue together the stages of tokenizing, parsing, and evaluation. It can be run at the console as a REPL (try `print 1+2;`) or by putting a file on the command line. We have included `example.t` as a very simple program to try. 

## Conclusion 

This is a cleaner and more refined program interpretation stack. Next time we will expand the AST concept to allow us to start adding more sophisticated features to our language. 





We will update the parser more extensively in the near future. 

