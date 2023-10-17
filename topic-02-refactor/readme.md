# Refactoring the Tokenizer & AST

## Introduction

Tonight we're going to cover improvements in the tokenizer and the abstract syntax tree. We won't be adding specific functionality, but we will be building additional robustness into the existing capabilities that we will use in as we add features. 

_(Side note: as I write this note (but not the code -- that's already done) I'm traveling about 190 MPH in an Italian high-speed train through some mountainous areas. Isn't technology great?)_

## Tokenizer Improvements

### Improving the existing patterns

Initially I had followed a model for the tokenizer where simple tokens (i.e tokens that just represented themselves) were simply represented as the token value (e.g. "+"). This also works for keywords like "print" and "if". 

I also represented tokens that have values (like numbers) with complex tokens containing the token _type_ (like "number") and the token _value_ (like 1.23) as ["NUMBER",123]. Since we also need to do this with strings and identifiers, we have updated the pattern table to look (in part) like this: 

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
    [r"\d+(\.\d*)?", "number"],   # numeric literals
]

### Additional simple tokens

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

We don't use these in our current language, but we will use them eventually. 

A side note: we trivially changed the handling of tokens to simply append them to a growing list of tokens that is eventually returned. 

The current number-handling code in the tokenizer looks like this: 

```
        if token == "number":
            tokens.append([token, number(match.group(0))])
            continue
```

### Strings

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

### Identifiers

We want to eventually be able to recognize identifiers, for several uses. Depending on where they appear, they might be variable names or function names (or function calls). 

Keep in mind that we have already scanned for all the keyword tokens, so anything token matched here shouldn't be a keyword. This is why we have to make sure this rule (which is the only ambiguous case, where a second rule might match something) is checked after checking all the keywords. 

So we want a complex token for identifers. We will use `["identifier","foobar"]` as the type/value pair for this complex token. 

So we will add the following pattern: 

    [r"[a-zA-Z_][a-zA-Z0-9_]*", "identifier"],  # identifiers

Then, this code will emit the identifier when found: 

        if token == "identifier":
            tokens.append([token, match.group(0)])
            continue

### Whitespace

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

## Abstract Syntax Tree (AST) Refactoring

_(Side Note: The train is arriving! To be continued later!)

