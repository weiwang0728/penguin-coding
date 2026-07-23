# Test Execution Order Guidance

## Guidance Statement for Evaluation Prompt

When executing tests, please plan the test sequence according to the dependencies defined in the `test_dependencies.json` file: If a test point is marked as a target in the dependencies file, you must first complete all prerequisite test points listed in its source field to ensure that the required data and preconditions for the test are satisfied.

## Detailed Explanation

Key elements of this statement:

1. **Trigger Condition**: A test point is marked as a target in the dependencies file
2. **Execution Rule**: Must first complete all prerequisite test points listed in its source field
3. **Purpose**: Ensure that the required data and preconditions for the test are satisfied

## Usage Example

Suppose you want to execute test point "2.3.5b":
1. Check `test_dependencies.json` and find that 2.3.5b is a target
2. Its source is "2.3.5a"
3. Therefore, you must first execute test point 2.3.5a
4. If 2.3.5a also has dependencies, recursively execute its prerequisite dependencies
5. Only after all dependencies are satisfied can you execute 2.3.5b

This ensures the correct test sequence and data integrity.