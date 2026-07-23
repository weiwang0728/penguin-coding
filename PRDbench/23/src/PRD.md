### PyCombinator Programming Language Interpreter PRD

#### 1. Requirement Overview
This project aims to develop a fully functional programming language interpreter implementing the PyCombinator programming language. The interpreter should be capable of parsing, evaluating, and executing user-input code, providing an interactive programming environment. The tool is implemented through command-line interaction, with core functionalities including lexical analysis, syntax analysis, expression evaluation, Lambda function support, and a complete REPL environment. This is an educational project designed to help students understand the core concepts and implementation principles of programming language interpreters.

#### 2. Basic Functional Requirements

##### 2.1 Interactive Programming Environment (REPL)
- Provide a command-line interactive programming environment supporting user code input and immediate execution result acquisition.
- Support launching the interactive environment with `python -m src.repl`, and launching read-only mode for debugging expression parsing with `python -m src.repl --read`. In read-only mode, after entering an expression, its Python representation (using the repr function) is displayed.
- Provide friendly error prompts and exception handling, support Ctrl-C and Ctrl-D to exit the program.
- Main interface adopts prompt-based interaction, using `>` as the input prompt, supporting history records and command-line editing (if available).

##### 2.2 Lexical Analyzer (Lexer)
- Convert input strings into token sequences, supporting numeric literals (integers and floating-point numbers), identifiers (variable names and function names), keywords (`lambda`), delimiters (`(`, `)`, `,`, `:`), and whitespace characters.
- Automatically skip whitespace characters, support negative numbers and decimals, support identifiers starting with underscores.
- Provide detailed syntax error prompts, including error location and reason description.

##### 2.3 Syntax Analyzer (Parser)
- Convert token sequences into abstract syntax trees (AST), supporting literal expressions, name expressions, call expressions and Lambda expressions.
- Support nested parenthesis expressions, multi-parameter function calls, no-parameter lambda expressions, immediately invoked lambda expressions.
- Display parsing status during query execution, support interrupt operations (users can terminate parsing by inputting Ctrl+C).

##### 2.4 Expression Evaluator (Evaluator)
- Execute abstract syntax trees and return computation results, supporting three value types: numeric values, Lambda functions, and primitive functions.
- Support variable scopes, function closures, environment copying and updating.
- Return evaluation status (success/failure), output specific reasons when failing (such as type errors, undefined variables).

##### 2.5 Built-in Function Support
- Provide common mathematical operation functions: `add`, `sub`, `mul`, `truediv`, `floordiv`, `mod`, `pow`, `abs`, `max`, `min`, `int`, `float`.
- Support multi-parameter function calls, support nested function calls, support recursive function calls.

##### 2.6 Lambda Expression Support
- Support anonymous function definition and invocation, syntax format: `lambda [parameter list]: expression`.
- Support zero or more parameters, support nested lambda expressions, support higher-order functions (functions as parameters or return values), support closures (capturing external environment variables).

#### 3. Command-Line Interaction and Result Display
- Main interface adopts interactive prompts, user input requires validity verification, display Chinese prompts for erroneous input.
- All output results support formatted display, error message formatting, type errors clearly indicate type mismatch issues.
- Support debug mode, can view Python representation forms of expressions.