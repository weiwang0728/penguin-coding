Huffman Tree and Code Generation System PRD

---

## I. Requirement Overview

This project aims to implement a Python-based Huffman Tree and Huffman Coding Generation System. Users can input data through multiple methods (including text files, randomly generated text, manual entry of key values, etc.). The system will automatically count the frequency of key values or characters, construct a Huffman tree, and output the corresponding Huffman coding table. All features are to be accessed via command-line or program interface—no front-end UI or graphical interface will be involved. The system supports data import, editing, Huffman tree and code generation, result export (such as images, tables), and offers robust stability, fault tolerance, and testability.

---

## II. Functional Requirements

### 2.1 Data Input and Editing

1. **Text Import**: Supports getting text content from local TXT files and automatically counts character frequencies.
2. **Random Text Generation**: Supports generating random text of a specified length, including types such as numbers, letters, strings, and Chinese characters.
3. **Manual Text Entry**: Supports  entering text strings.
4. **Key Value Input and Editing**: Supports manual entry of key values (list of weights), and allows addition, deletion, modification, and reset operations.

### 2.2 Huffman Tree and Code Generation

1. **Frequency Statistics**: Automatically counts the frequency of each character in the input text and generates a key value table.
2. **Huffman Tree Construction**: Based on the provided key values or character frequencies, constructs a Huffman tree. The internal structure utilizes Python dictionaries or similar data structures.
3. **Huffman Code Generation**: Generates the prefix code table by traversing the Huffman tree (ensuring each character or key value corresponds to a unique code), and prints out the resulting code table.

### 2.3 Data Export

1. **Huffman Code Table Export**: Supports exporting the code table as Excel (.xls or .csv) files.
2. **Huffman Tree Structure Export**: Supports exporting the Huffman tree structure as text (JSON format, with options for level-order or pre-order traversal), for subsequent analysis or visualization.

### 2.4 Fault Tolerance and User Experience

1. **Input Validity Check**: Checks the number of key values, ensuring no fewer than two; otherwise, construction of the Huffman tree is refused. Checks for file read errors, format issues, etc., and outputs clear error messages.
2. **Run Logs and Prompts**: The system outputs the result or status of each operation step, making the process easy for users to follow.

### 2.6 Unit Testing

The system must support unit testing using the `pytest` framework. Tests must cover at least:
- Testing Huffman tree construction (`test_build_huffman_tree`)
- Testing Huffman code generation (`test_generate_huffman_codes`)
- Exception handling: when only one key/character is provided, a `ValueError` must be raised (`test_build_tree_with_insufficient_nodes`)
