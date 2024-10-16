# Boolean Expression Compiler

This project implements a simple Boolean expression compiler, including a tokenizer, parser, interpreter, and compiler. The system processes boolean expressions, evaluates them based on variable assignments, and generates truth tables. It supports commands to show the results of boolean expressions, generate truth tables, and simplify expressions.

## Repository Structure

The project consists of five main files:

### 1. `tokenizer.py`
This module contains the `Tokenizer` class responsible for breaking down input source code into tokens, which are the smallest units of the language (such as identifiers, operators, and literals). The tokenizer is the first step in the compilation process and prepares the source code for parsing.

**Main functionalities:**
- Tokenizing variables, boolean literals (`True`, `False`), and operators (`and`, `or`, `not`).
- Tokenizing parentheses for expression grouping.
- Providing a stream of tokens for the parser.

### 2. `parser.py`
The `Parser` module is responsible for constructing an Abstract Syntax Tree (AST) from the tokenized input. It interprets the structure of the boolean expressions and captures them in a hierarchical format that the interpreter and compiler can process.

**Main functionalities:**
- Declaring variables and processing assignments.
- Building the AST for binary operations (`and`, `or`) and unary operations (`not`).
- Handling show commands (`show`, `show_ones`) to indicate which expressions to output.

### 3. `interpreter.py`
The `interpreter.py` file evaluates the parsed expressions based on variable assignments. It includes functionality to simplify expressions by substituting variable values and reducing the expression tree.

**Main functionalities:**
- Simplifying boolean expressions based on given truth assignments.
- Evaluating boolean expressions into `True`/`False` values.
- Generating truth tables with possible variable combinations.

### 4. `compiler.py`
The `compiler.py` file ties everything together. It compiles the source code by using the tokenizer, parser, and interpreter to generate and evaluate boolean expressions. This is where the primary interaction occurs for generating the truth tables and processing the `show` commands.

**Main functionalities:**
- Combining variable assignments and evaluating truth table outputs.
- Processing `show_ones` and `show` commands.
- Producing results in a format that represents the truth table of boolean expressions.

### 5. `table.py`
This module provides utility functions for formatting and displaying the results of the evaluation, such as generating truth tables and formatting binary outputs. It takes the results of boolean expressions and presents them in a structured form.

**Main functionalities:**
- Formatting truth tables for both `show_ones` and `show` commands.
- Mapping variable assignments to their respective evaluations.
