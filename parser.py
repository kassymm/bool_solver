from dataclasses import dataclass, field
from tokenizer import Token, TokenType, Tokenizer

@dataclass
class TreeNode:
    pass

@dataclass
class Expr(TreeNode):
    pass

@dataclass
class Program(TreeNode):
    statements: list[TreeNode]


@dataclass
class BinOp(Expr):
    op: str
    left: Expr
    right: Expr


@dataclass
class Identifier(Expr):
    name: str

@dataclass
class BoolLiteral(Expr):
    value: bool

@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr


@dataclass
class Declaration(TreeNode):
    vars: list[str]

@dataclass
class Assignment(TreeNode):
    var: str
    expr: Expr

@dataclass
class Show(TreeNode):
    vars: list[str]
    show_ones: bool = False


def print_ast(tree: Expr, depth: int = 0) -> None:
    indent = "    " * depth
    match tree:
        case Program(statements):
            print(indent + "Program")
            for statement in statements:
                print_ast(statement, depth + 1)
        case BinOp(op, left, right):
            print(indent + op)
            print_ast(left, depth + 1)
            print_ast(right, depth + 1)
        case UnaryOp(op, operand):
            print(indent + op)
            print_ast(operand, depth + 1)
        case Identifier(name):
            print(indent + str(name))
        case BoolLiteral(value):
            print(indent + str(value))
        case Declaration(vars):
            print(indent + "var " + ", ".join(vars))
        case Assignment(var, expr):
            print(indent + f"{var} =")
            print_ast(expr, depth + 1)
        case Show(vars, show_ones):
            print(indent + ("show ones " if show_ones else "show ") + ", ".join(vars))
        case _:
            raise RuntimeError(f"Can't print a node of type {tree.__class__.__name__}")


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.next_token_index: int = 0
        self.declared: list[str] = []
        self.assigned: list[str] = []
        self.identifier_map: dict[str, Expr] = {}
        self.shows: list[Show] = []

    def eat(self, expected_token_type: TokenType) -> Token:
        next_token = self.tokens[self.next_token_index]
        self.next_token_index += 1
        if next_token.type != expected_token_type:
            raise RuntimeError(f"Expected {expected_token_type}, ate {next_token!r}")
        return next_token
    
    def peek(self, skip: int = 0) -> TokenType | None:
        peek_at = self.next_token_index + skip
        return self.tokens[peek_at].type if peek_at < len(self.tokens) else None
    
    def peek_token(self, skip: int = 0) -> TokenType | None:
        peek_at = self.next_token_index + skip
        return self.tokens[peek_at] if peek_at < len(self.tokens) else None
    
    def parse(self) -> Program:
        statements = []
        while self.peek() is not None and self.peek() != TokenType.EOF:
            if self.peek() == TokenType.VAR:
                statements.append(self.parse_declaration())
                # print(statements)
            elif self.peek() == TokenType.SHOW or self.peek() == TokenType.SHOW_ONES:
                statements.append(self.parse_show())
                # print(statements)
            elif self.peek() == TokenType.IDENTIFIER:
                statements.append(self.parse_assignement())
                # print(statements)
            else:
                raise RuntimeError(f"Unexpected token: {self.peek()}")
        return Program(statements)
    
    def parse_declaration(self) -> Declaration:
        """
        <declaration> ::= "var" <identifier> {<identifier>} ";"
        """
        self.eat(TokenType.VAR)
        vars = []
        while self.peek() == TokenType.IDENTIFIER:
            var = self.eat(TokenType.IDENTIFIER)
            var_name = var.value
            if var_name in self.identifier_map:
                raise RuntimeError(f"Variable {var_name} was declared or assigned before")
            identifier_node = Identifier(name=var_name)
            vars.append(var_name)
            self.declared.append(var_name)
            self.identifier_map[var_name] = identifier_node
        self.eat(TokenType.SEMICOLON)
        return Declaration(vars)
    
    def parse_assignement(self) -> Assignment:
        """
        <assignment> ::= <identifier> "=" <expr> ";"
        """
        var = self.eat(TokenType.IDENTIFIER)
        var_name = var.value
        if var_name in self.identifier_map:
            raise RuntimeError(f"Varibale {var} was declared or assigned before")
        # identifier_node =  Identifier(name=var_name)
        # self.identifier_map[var_name] = identifier_node
        self.assigned.append(var_name)
        self.eat(TokenType.ASSIGN)
        expr = self.expr()
        self.identifier_map[var_name] = expr
        self.eat(TokenType.SEMICOLON)
        return Assignment(var_name, expr)

    def parse_show(self) -> Show:
        """
        <show> ::= ("show" | "show ones") <identifier> {<identifier>} ";"
        """
        show_ones = (self.peek() == TokenType.SHOW_ONES)
        self.eat(TokenType.SHOW_ONES if show_ones else TokenType.SHOW)
        vars = []
        while self.peek() == TokenType.IDENTIFIER:
            vars.append(self.eat(TokenType.IDENTIFIER).value)
        self.eat(TokenType.SEMICOLON)
        out = Show(vars,show_ones)
        self.shows.append(out)
        return out

    
    def element(self) -> Expr:
        """
        <element> ::= "True" | "False" | <identifier>
        """
        token = self.eat(self.peek())
        if token.type == TokenType.TRUE:
            return BoolLiteral(True)
        elif token.type == TokenType.FALSE:
            return BoolLiteral(False)
        elif token.type == TokenType.IDENTIFIER:
            if token.value in self.identifier_map:
                return self.identifier_map[token.value]
            else:
                raise RuntimeError(f"Varible {token.value} in the experssion was not declared or assigned before")
        else:
            raise RuntimeError(f"Unexpected token type: {token.type}")

    def expr(self) -> Expr:
        """
        <expr> ::= <negation> | <conjunction> | <disjunction> | <paren-expr>
        """
        if self.peek() == TokenType.NOT:
            return self.negation()
        left = self.paren_expr()
        if self.peek() == TokenType.AND:
            return self.conjunction(left)
        elif self.peek() == TokenType.OR:
            return self.disjunction(left)
        return left
    
    def paren_expr(self) -> Expr:
        """
        <paren-expr> ::= <element> | "(" <expr> ")"
        """
        if self.peek() == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        return self.element()
    
    def negation(self) -> UnaryOp:
        """
        <negation> ::= "not" <paren-expr>
        """
        self.eat(TokenType.NOT)
        operand = self.paren_expr()
        return UnaryOp("not", operand)

    def conjunction(self, left: Expr) -> BinOp:
        """
        <conjunction> ::= <paren-expr> "and" <paren-expr> | <paren-expr> "and" <conjunction>
        """
        self.eat(TokenType.AND)
        right = self.paren_expr()
        node = BinOp("and", left, right)
        if self.peek() == TokenType.AND:
            return self.conjunction(node)
        return node
    
    def disjunction(self, left: Expr) -> BinOp:
        """
        <disjunction> ::= <paren-expr> "or" <paren-expr> | <paren-expr> "or" <disjunction>
        """
        self.eat(TokenType.OR)
        right = self.paren_expr()
        node = BinOp("or", left, right)
        if self.peek() == TokenType.OR:
            return self.disjunction(node)
        return node

    def __repr__(self) -> str:
        return f"Parser({self.tokens!r})"
    

if __name__ == "__main__":
    code = """
    # We declare two variables: x and y
    var x y;
    # We assign (x or y) and (not (x and y)) to z
    z = (x or y) and (not (x and y));
    w = x and y and z;
    # We show the truth table of z
    show z;
    """
    # path = "hw01_instances/ag25_24.txt"
    # with open(path, 'r') as file:
    #     file_content = file.read()
    # code = file_content
    parser = Parser(list(Tokenizer(code)))
    # parser.parse()
    print_ast(parser.parse())
    print("Decalred variables ", parser.declared)
    print("Assigned variables ", parser.assigned)