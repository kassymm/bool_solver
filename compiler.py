from parser import Parser, Expr, BinOp, Identifier, UnaryOp, BoolLiteral, Assignment
from tokenizer import Tokenizer
from typing import Optional
from itertools import product



# Function to reduce the expression tree with a given variable assignment
def reduce_expr(node: Expr, var: str, value: bool) -> Expr:
    """
    Reduce the expression by substituting var = value and simplifying the tree.
    """
    match node:
        case Identifier(name):
            if name == var:
                return BoolLiteral(value)
            return node
        case BoolLiteral(_):
            return node
        case UnaryOp("not", operand):
            reduced_operand = reduce_expr(operand, var, value)
            if isinstance(reduced_operand, BoolLiteral):
                return BoolLiteral(not reduced_operand.value)
            return UnaryOp("not", reduced_operand)
        case BinOp(op, left, right):
            # Recursively reduce left and right nodes
            reduced_left = reduce_expr(left, var, value)
            reduced_right = reduce_expr(right, var, value)

            
            if isinstance(reduced_left, BoolLiteral):
                if op == "and":
                    return BoolLiteral(False) if reduced_left.value == False else reduced_right
                if op == "or":
                    return BoolLiteral(True) if reduced_left.value == True else reduced_right

            if isinstance(reduced_right, BoolLiteral):
                if op == "and":
                    return BoolLiteral(False) if reduced_right.value == False else reduced_left
                if op == "or":
                    return BoolLiteral(True) if reduced_right.value == True else reduced_left       
            
            return BinOp(op, reduced_left, reduced_right)
        case _:
            raise ValueError(f"Unknown node type: {type(node)}")
        
def backtrack_reduce(show_expr: Expr, 
                    declared_vars: list[str],
                    index: int,
                    assignment: dict[str, bool],
                    results: list[dict[str, bool]]):

    if index == len(declared_vars): # shouldn't reach this, but let it be
        if isinstance(show_expr, BoolLiteral) and show_expr.value:
            results.append(assignment.copy())
        return
    current_var = declared_vars[index]

    assignment[current_var] = False
    reduced_expr_false= reduce_expr(show_expr, current_var, False)
    backtrack_reduce(reduced_expr_false, declared_vars, index + 1, assignment, results)
    assignment[current_var] = True
    reduced_expr_true = reduce_expr(show_expr, current_var, True)
    backtrack_reduce(reduced_expr_true, declared_vars, index + 1, assignment, results)


    del assignment[current_var]

def solve(parser: Parser, show_var: str) -> list[dict[str, bool]]:
    show_expr = parser.identifier_map.get(show_var)
    if show_expr is None:
        return RuntimeError(f"Show variable {show_var} is not found")
    results = []
    backtrack_reduce(show_expr, parser.declared, 0, {}, results)
    return results

def evaluate_expression(node: Expr) -> Optional[bool]:
    """
    Evaluate the expression and return a boolean value or None if it can't be simplified fully.
    """
    match node:
        case BoolLiteral(value):
            return value
        case UnaryOp("not", operand):
            operand_val = evaluate_expression(operand)
            return not operand_val if operand_val is not None else None
        case BinOp("and", left, right):
            left_val = evaluate_expression(left)
            right_val = evaluate_expression(right)
            if left_val is False or right_val is False:
                return False
            if left_val is True and right_val is True:
                return True
            return None  # Cannot fully evaluate yet
        case BinOp("or", left, right):
            left_val = evaluate_expression(left)
            right_val = evaluate_expression(right)
            if left_val is True or right_val is True:
                return True
            if left_val is False and right_val is False:
                return False
            return None  # Cannot fully evaluate yet
        case Identifier(_):
            return None  # Return None for unassigned variables
        case _:
            raise ValueError(f"Unknown node type: {type(node)}")
        

def combine(parser: Parser, show_vars: list[str]) -> list[dict[str, bool]]:
    combined = []
    for show_var in show_vars:
        truth_assignments = solve(parser, show_var)
        combined.extend(truth_assignments)
    unique = []
    seen = set()
    for assignment in combined:
        assignment_tuple = tuple(assignment[var] for var in parser.declared)
        if assignment_tuple not in seen:
            seen.add(assignment_tuple)
            unique.append(assignment)
    return unique

def evaluate(parser, show_vars: list[str], combined: list[dict[str, bool]]) -> dict[tuple, list[int]]:
    results_map = {}
    for assignment in combined:
        binary_evaluations = []
        for show_var in show_vars:
            show_expr = parser.identifier_map[show_var]
            reduced_expr = show_expr
            for var, value in assignment.items():
                reduced_expr = reduce_expr(reduced_expr, var, value)
            # by this point reduced_expr should be BoolLiteral
            is_true = reduced_expr.value
            binary_evaluations.append(1 if is_true else 0)
        assignment_key = tuple(assignment[var] for var in parser.declared)
        results_map[assignment_key] = binary_evaluations
    return results_map

def format(parser: Parser, show_vars: list[str], results_map: dict[tuple, list[int]]) -> str:
    formatted = []
    n = len(parser.declared)
    for assignment_key, evaluations in results_map.items():
        assignment_binaries = [1 if value else 0 for value in assignment_key]
        combined_binaries = assignment_binaries + evaluations
        formatted.append("".join(str(bit) for bit in combined_binaries))
    return "\n".join(formatted)

def process_show_ones(parser: Parser, show_vars: list[str]) ->str:
    combined = combine(parser, show_vars)
    results_map = evaluate(parser, show_vars, combined)
    final_output = format(parser, show_vars, results_map)
    return final_output



def show_ones_mapping(show_ones_output: str, n: int, m: int) -> dict[str, str]:
    show_ones_map = {}
    for line in show_ones_output.strip().splitlines():
        key = line[:n]
        value = line[n:]
        show_ones_map[key] = value
    return show_ones_map

def process_show(parser: Parser, show_vars: list[str], show_ones_map: dict[str, str]) ->str:
    n = len(parser.declared)
    m = len(show_vars)  
    # Generate all 2^n possible binary string combinations for the declared variables
    all_combinations = [f"{i:0{n}b}" for i in range(2**n)]
    formatted_output = []
    for binary_string in all_combinations:
        # Check if this binary string is in the `show_ones` output
        if binary_string in show_ones_map:
            last_m_bits = show_ones_map[binary_string]
        else:
            last_m_bits = [0] * m  # Use m 0s for missing entries

        # Combine the first n bits (binary_string) with the last m bits
        combined_binaries = list(binary_string) + [str(bit) for bit in last_m_bits]

        # Convert to a space-separated string and add to the output
        formatted_output.append("".join(combined_binaries))

    # Return the formatted truth table as a string
    return "\n".join(formatted_output)

if __name__ == "__main__":
    import os
    import time 
    # code = """
    # # We declare two variables: x and y
    # var x y;
    # # We assign (x or y) and (not (x and y)) to z
    # z = (x or y) and (not (x and y));
    # t = x or y;
    # w = x;
    # # We show the truth table of z
    # show_ones z t;
    # """
    # path = "hw01_instances/random0092.txt"
    directory = 'hw01_instances'
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        with open(path, "r") as file:
            file_content = file.read()
        code = file_content
        print(f"\nFile {path}")
        start_time = time.time()
        parser = Parser(list(Tokenizer(code)))
        parser.parse()
        if len(parser.declared) > 24:
            print("more than 24 vars")
            continue
        for show_node in parser.shows:
            show_vars = show_node.vars
            # print(show_vars)
            results = process_show_ones(parser, show_vars)
            if show_node.show_ones:
                print(results)
            else:
                # Process the full truth table for show command
                show_ones_map = show_ones_mapping(results, len(parser.declared), len(show_vars))
                show_results = process_show(parser, show_vars, show_ones_map)
                print(show_results)

        end_time = time.time()
        # Calculate and print the execution time
        execution_time = end_time - start_time
        print(f"Execution time for {filename}: {execution_time:.4f} seconds")