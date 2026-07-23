#!/usr/bin/env python3
"""
Test Coverage Analyzer
Analyzes test files in the src/tests/ directory and generates test coverage reports
"""

import os
import ast
import json
import sys
from pathlib import Path

def analyze_test_file(file_path):
    """Analyze the content of a single test file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        # Find all test methods
        test_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_methods.append(node.name)

        # Analyze imported modules
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.extend([alias.name for alias in node.names])

        return {
            'file': os.path.basename(file_path),
            'test_methods': test_methods,
            'imported_functions': imports
        }
    except Exception as e:
        return {
            'file': os.path.basename(file_path),
            'error': str(e),
            'test_methods': [],
            'imported_functions': []
        }

def generate_coverage_report(tests_dir):
    """Generate test coverage report"""
    report = {
        'timestamp': '2025-08-14T10:56:00+08:00',
        'tests_directory': tests_dir,
        'expected_functions': [
            'compare_numbers',
            'filter_data',
            'create_adder',
            'extract_unique',
            'recursive_replace',
            'batch_map_replace'
        ],
        'test_files': [],
        'coverage_summary': {}
    }

    # Scan test directory
    tests_path = Path(tests_dir)
    if not tests_path.exists():
        report['error'] = f"Test directory does not exist: {tests_dir}"
        return report

    # Analyze all test files
    for test_file in tests_path.glob('test_*.py'):
        file_analysis = analyze_test_file(test_file)
        report['test_files'].append(file_analysis)

    # Generate coverage summary
    all_test_methods = []
    all_imported_functions = []

    for file_info in report['test_files']:
        all_test_methods.extend(file_info.get('test_methods', []))
        all_imported_functions.extend(file_info.get('imported_functions', []))

    # Check test coverage for each expected function
    for func in report['expected_functions']:
        test_method_name = f'test_{func}'
        report['coverage_summary'][func] = {
            'has_test_function': test_method_name in all_test_methods,
            'is_imported': func in all_imported_functions,
            'fully_covered': test_method_name in all_test_methods and func in all_imported_functions
        }

    # Calculate overall coverage statistics
    fully_covered_count = sum(1 for coverage in report['coverage_summary'].values() if coverage['fully_covered'])
    total_functions = len(report['expected_functions'])

    report['overall_stats'] = {
        'total_functions': total_functions,
        'fully_covered_functions': fully_covered_count,
        'coverage_percentage': round((fully_covered_count / total_functions) * 100, 1) if total_functions > 0 else 0,
        'total_test_files': len(report['test_files']),
        'total_test_methods': len(all_test_methods)
    }

    return report

def main():
    if len(sys.argv) != 3:
        print("Usage: python test_coverage_analyzer.py <tests_dir> <output_file>")
        sys.exit(1)

    tests_dir = sys.argv[1]
    output_file = sys.argv[2]

    report = generate_coverage_report(tests_dir)

    # Save report to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Test coverage report generated: {output_file}")
    print(f"Overall coverage: {report['overall_stats']['coverage_percentage']}%")

if __name__ == '__main__':
    main()