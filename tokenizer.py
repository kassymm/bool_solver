from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any
from string import digits
from typing import Generator


class TokenType(StrEnum):
    AND = auto()
    OR = auto()
    NOT = auto()
    TRUE = auto()
    FALSE = auto()
    KEYWORD = auto()
    IDENTIFIER = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()
    SHOW = auto()
    SHOW_ONES = auto()
    VAR = auto()
    ASSIGN = auto()
    SEMICOLON = auto()
    COMMENT = auto()


@dataclass
class Token:
    type: TokenType
    value: Any = None


class Tokenizer:
    def __init__(self, code: str) -> None:
        self.code = code
        self.ptr: int = 0

    def consume_word(self) -> str:
        start = self.ptr
        while self.ptr < len(self.code) and (self.code[self.ptr].isalpha() 
                                             or self.code[self.ptr] in digits
                                             or self.code[self.ptr] == '_'):
            self.ptr += 1
        return self.code[start: self.ptr]

    def next_token(self) -> Token:
        while self.ptr < len(self.code) and self.code[self.ptr] in " \t\r\n":
            self.ptr += 1

        if self.ptr == len(self.code):
            return Token(TokenType.EOF)

        char = self.code[self.ptr]

        if char == '#':
            while self.ptr < len(self.code) and self.code[self.ptr] != "\n":
                self.ptr += 1
            return self.next_token()

        if char == '(':
            self.ptr += 1
            return Token(TokenType.LPAREN)
        elif char == ')':
            self.ptr += 1
            return Token(TokenType.RPAREN)
        elif char == '=':
            self.ptr += 1
            return Token(TokenType.ASSIGN)
        elif char == ";":
            self.ptr += 1
            return Token(TokenType.SEMICOLON)
        
        elif char == '_' or char.isalpha():
            word = self.consume_word()
            if word == "True":
                return Token(TokenType.TRUE)
            elif word == "False":
                return Token(TokenType.FALSE)
            elif word == "not":
                return Token(TokenType.NOT)
            elif word == "and":
                return Token(TokenType.AND)
            elif word == "or":
                return Token(TokenType.OR)
            elif word == "var":
                return Token(TokenType.VAR)
            elif word == "show":
                return Token(TokenType.SHOW)
            elif word == "show_ones":
                return Token(TokenType.SHOW_ONES)
            else:
                return Token(TokenType.IDENTIFIER, word)
        else:
            raise RuntimeError(f"Can't tokenize {char!r}")

    def __iter__(self) -> Generator[Token, None, None]:
        while (token := self.next_token()).type != TokenType.EOF:
            yield token
        yield token


if __name__ == "__main__":
    code = """
    # We declare two variables: x and y
    var x y;
    # We assign (x or y) and (not (x and y)) to z
    z = (x or y) and (not (x and y));
    # We show the truth table of z
    show z;
    """
    tokenizer = Tokenizer(code)
    for tok in tokenizer:
        print(f"{tok.type}, {tok.value}")
