import re

patterns = [     
    [r"\s+", None],       # Whitespace
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
    [r"\;",";"],
    [r"\d+(\.\d*)?", "number"],   # numeric literals
    [r'"([^"]|"")*"', "string"],  # string literals
    [r"[a-zA-Z_][a-zA-Z0-9_]*", "identifier"],  # identifiers
    [r".", "error"],  # unexpected content
]

# general numeric literal conversion
def number(s):
    if "." in s:
        return float(s)
    else:
        return int(s)

# The lex/tokenize function
def tokenize(characters):
    print("tokenizing", characters)
    tokens = []
    pos = 0
    while pos < len(characters):
        for regex, token in patterns:
            pattern = re.compile(regex)
            match = pattern.match(characters, pos)
            if match:                
                break
        assert match # this should never fail
        pos = match.end()
        if token == None:
            continue
        assert token != "error", "Syntax error: illegal character at " + match.group(0)
        if token == "number":
            tokens.append([token, number(match.group(0))])
            continue
        if token == "string":
            # omit closing and beginning strings, replace two quotes with one quote
            tokens.append([token, match.group(0)[1:-1].replace('""', '"')])
            continue
        if token == "identifier":
            tokens.append([token, match.group(0)])
            continue
        tokens.append(token)
    return tokens


def test_simple_tokens():
    print("testing simple tokens")
    examples = "+,-,*,/,(,),{,},;".split(",")
    for example in examples:
        assert tokenize(example) == [example]

def test_number_tokens():
    print("testing number tokens")
    for s in ["1", "22", "12.1", "0", "12.", "123145"]:
        assert tokenize(s) == [
            ["number", number(s)]
        ], f"Expected {[['number', s]]}, got {tokenize(s)}."

def test_string_tokens():
    print("testing string tokens")
    for s in ['"example"', '"this is a longer example"', '"an embedded "" quote"']:
        # adjust for the embedded quote behaviour
        r = s[1:-1].replace('""','"')
        assert tokenize(s) == [
            ["string", r]
        ], f"Expected {[['string', r]]}, got {tokenize(s)}."

def test_identifier_tokens():
    print("testing identifier tokens")
    for s in ["x", "y", "z", "alpha", "beta", "gamma"]:
        assert tokenize(s) == [
            ["identifier", s]
        ], f"Expected {[['identifier', s]]}, got {tokenize(s)}."

def test_whitespace():
    print("testing whitespace")
    for s in ["1", "1  ", "  1", "  1  "]:
        assert tokenize(s) == [["number", 1]]

def test_multiple_tokens():
    print("testing multiple tokens")
    assert tokenize("1+2") == [["number", 1], "+", ["number", 2]]
    assert tokenize("1+2-3") == [["number", 1], "+", ["number", 2], "-", ["number", 3]]
    assert tokenize("3+4*(5-2)") == [
        ["number", 3],
        "+",
        ["number", 4],
        "*",
        "(",
        ["number", 5],
        "-",
        ["number", 2],
        ")",
    ]
    assert tokenize("3+4*(5-2)") == tokenize("3 + 4 * (5 - 2)")
    assert tokenize("3+4*(5-2)") == tokenize("  3  +  4 * (5 - 2)  ")
    assert tokenize("3+4*(5-2)") == tokenize(" 3 + 4 * (5 - 2) ")


def test_keywords():
    print("testing keywords")
    for keyword in ["print","if","else","while"]:
        assert tokenize(keyword) == [keyword]

if __name__ == "__main__":
    test_simple_tokens()
    test_number_tokens()
    test_string_tokens()
    test_identifier_tokens()
    test_whitespace()
    test_multiple_tokens()
    test_keywords()
    print(tokenize("print 3+4*(5-2);"))
