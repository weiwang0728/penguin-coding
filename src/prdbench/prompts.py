"""PRDBench prompt templates for Development and Debug stages."""

DEVELOPMENT_PROMPT = """Please develop a complete Python project (ID:{ID}) located at {project_path} according to the requirements specified in the project documentation (src/PRD.md), and with reference to the expected test metrics (evaluation/detailed_test_plan.json).

### Requirements
1. Strictly implement all functional requirements described in PRD.md, ensuring that every feature is fully realized and that no requirements are omitted.
2. Closely follow the testing schemes defined in detailed_test_plan.json, ensuring that your implementation process and interfaces fully comply with the testing specifications, so that QA testing can be carried out directly using detailed_test_plan.
3. Submit all project code and related files completely under the src/ directory, ensuring that the project structure is clear and maintainable.
4. Do not ask any intermediate questions during the development process. Complete the entire project and submit directly.
"""

DEBUG_PROMPT = """Please debug and fix the Python project (ID:{ID}) located at {project_path}.

The project was developed according to the requirements in src/PRD.md and the test metrics in evaluation/detailed_test_plan.json, but some tests are failing.

### Instructions
1. Read src/PRD.md to understand the project requirements.
2. Read evaluation/detailed_test_plan.json to understand the expected test cases.
3. Examine the existing code in the src/ directory.
4. Run the tests from detailed_test_plan.json to identify failures.
5. Fix all issues in the src/ directory until the tests pass.
6. Do not modify evaluation/detailed_test_plan.json.
7. Do not ask any intermediate questions. Fix all issues and submit directly.
"""

EVALUATION_PROMPT = """Please evaluate the implementation of {project_dir} by running code-level tests and generating an evaluation report according to the evaluation criteria. The evaluation criteria are provided in evaluation/metric_en.json, and the project code is located in the src/ directory.

You should independently design and execute tests for each test point described in evaluation/metric_en.json. You may freely create auxiliary files, test scripts (such as pytest files), and input data as needed to thoroughly test the code against each metric. However, you must not modify the content of the metrics in evaluation/metric_en.json, nor alter any code in the {project_dir}/src/ directory.

### Path Instructions
- The project code is located in the {project_dir}/src/ directory. **DO NOT MODIFY THE PROJECT CODE.**
- The evaluation criteria are located in the {project_dir}/evaluation/metric_en.json file. **DO NOT MODIFY THE METRIC FILE.**
- You are allowed and encouraged to create or modify auxiliary files, test scripts, and input data under the {project_dir}/evaluation directory (excluding metric_en.json), to help you test the code against the evaluation criteria.
- The evaluation report must be saved to {project_dir}/reports/round{round}.jsonl in JSON format.

### Tips
- If the code is unable to run after reasonable testing efforts, please document this in the report.
- You may write and execute your own pytest scripts or other testing scripts to comprehensively evaluate the code according to each metric.
- You may prepare or generate any necessary input files or data for your tests, as long as you do not modify the metric_en.json or src code.

### Example
The detailed evaluation report must be saved to reports/round{round}.jsonl in JSON format. Entries in the report should follow this structure:
{{
"metric": "1.3 Menu Navigation - Export Results Submenu",
"description": "Test whether the export submenu displays the correct options when accessed.",
"score": 0,
"explanation": "No export submenu is present in the actual implementation. The code does not provide menu navigation functionality, so this feature could not be tested."
}},
{{
"metric": "3.2 Unit Test - Generate Huffman Codes",
"description": "Verify that the generate_huffman_codes function produces the expected encoding dictionary.",
"score": 2,
"explanation": "A custom pytest file was written to test generate_huffman_codes. The test passed and produced the expected results."
}}

For each metric in evaluation/metric_en.json, you must attempt to design and execute a test (using auxiliary scripts, pytest, or other methods as appropriate). Document your testing process, results, and any issues encountered in the evaluation report. Assign a score for each metric according to your findings.

### Final Reminder
You are free to create or modify any auxiliary files, input data, or test scripts within the evaluation directory (except metric_en.json) to facilitate comprehensive testing. **Do NOT modify the project code in src or the metrics in metric_en.json.**
For every metric, design and execute a test. If a feature is missing or incompatible, document this in the report and score accordingly. **Do not skip any metrics.**
The output report should be saved to {project_dir}/reports/round{round}.jsonl in JSON format.
"""
