from parser import Parser, Expr, BinOp, Identifier, UnaryOp, BoolLiteral, Assignment
from tokenizer import Tokenizer
from typing import Optional
from itertools import product
from compiler import *

import sys

def main():
    # # Check if a filename was provided
    # if len(sys.argv) < 2:
    #     print("Usage: python3 table.py <filename>")
    #     return

    # Get the filename from command line arguments
    file_path = sys.argv[1]

    # Now you can use the file_path variable to open xor.txt
    try:
        with open(file_path, 'r') as file:
            code = file.read()
            parser = Parser(list(Tokenizer(code)))
            parser.parse()
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
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()