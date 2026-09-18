from dataclasses import dataclass

class LexError(Exception): pass

@dataclass
class Token:
    kind: str
    value: str

KEYWORDS = {"braid","step","run","with"}

def tokenize(text):
    tokens = []
    i = 0
    while i < len(text):
        c = text[i]
        if c in " \t\r\n":
            i += 1; continue
        if c == "#":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        if c == '"':
            i += 1
            start = i
            while i < len(text) and text[i] != '"':
                i += 1
            if i >= len(text):
                raise LexError("unterminated string")
            tokens.append(Token("STRING", text[start:i]))
            i += 1; continue
        if c in "{}:":
            tokens.append(Token(c, c)); i += 1; continue
        if c.isalnum() or c == "_":
            start = i
            while i < len(text) and (text[i].isalnum() or text[i] in "_-"):
                i += 1
            word = text[start:i]
            tokens.append(Token("KW" if word in KEYWORDS else "IDENT", word))
            continue
        raise LexError("unexpected char: " + repr(c))
    return tokens
