### Test Task Data Analysis and Visualization Tool PRD

#### 1. Requirement Overview
This tool is designed for the automated processing and multidimensional analysis of test task spreadsheet data. It supports users in uploading test task spreadsheets (CSV/Excel format) via the command line. The system automatically performs data extraction, cleaning, transformation, and aggregation, and generates standardized summary tables and visual statistical charts. The core value lies in achieving standardized management and efficiency analysis of test task data, aiding the test team in optimizing test processes through data-driven methods.

#### 2. Basic Functional Requirements
##### 2.1 Table Data Import and Parsing
- Users can input the file path via the command line to import test task spreadsheets in CSV or Excel format.
- Uploaded files must be in a fixed format, containing the following fields: Task ID, Task Name, Test Project, Device Duration, Test Status, Test Type.
- Automatically skip the first row (header row) of the original table, extracting data from the second row onward.
- Supports detecting and handling common data anomalies: filling in missing values (mark Task ID missing as "UNKNOWN-timestamp"), filtering non-numeric device duration data (converting to 0 and logging).

##### 2.2 Data Processing and Transformation
- **Task Data Aggregation**: Group by Task ID, display different test projects under the same Task ID in separate rows, automatically sum device duration.
- **Test Content Standardization**: Based on device duration n and test status, automatically generate a standardized description: "The test was conducted for {n} hours, no anomalies so far" (n to two decimal places).
- **Feedback Column Generation**: Add a new Feedback column for test project status and an Anomaly Indicator column, execute standard processing for feedback column content:
  - Simplify text (e.g., "The test has no anomalies" → "No anomalies").
  - Extract non-Chinese content (use regular expression `[^\u4e00-\u9fa5]` to extract special symbols/English/numbers into the new column "Anomaly Indicator").

##### 2.3 Task Efficiency Analysis
- Calculate key performance indicators (KPIs):
  - Task Completion Rate = Number of Successful Tasks / Total Number of Tasks.
  - Test Effectiveness Index = Number of Effective Test Items / (Effective + Ineffective Test Items), calculated based on the Test Type column (effective, ineffective).
  - Average Device Duration = Total Device Duration / Number of Test Projects (apply descriptive statistical methods).
- Support layered statistics by task priority (must be parsed from Task ID, format like "TASK-H[High]-20231001").

##### 2.4 Visualization Report Generation
- Generate and save two types of statistical pie charts as PNG files:
  - Task Status Distribution Chart: shows the proportion of success/failure (green = success, red = failure).
  - Test Effectiveness Distribution Chart: shows the proportion of effective/ineffective/unmarked (green = effective, red = ineffective, yellow = unmarked).
- Chart optimization requirements:
  - Implement using the matplotlib library.
  - Auto-optimize legend positions (to avoid data obstruction).
  - Add data labels (show percentage and raw values).
  - Support custom chart titles (specified via command line parameters).

##### 2.5 Command-Line Interaction and Result Output
- Provide an interactive menu: 1. Import Table Data 2. View Summary Table 3. Generate Statistical Charts 4. Export Processed Results (support CSV/Excel format) 5. Exit System.
- Support both command-line interactive mode and batch processing mode.
- Support shortcut key operations (number key to select function, 'q' key to return to the previous menu).
- Result output requirements:
  - Display the summary table in the command line as a formatted table (using the tabulate library).
  - Show file save path after successful chart generation.
  - Real-time printing of operation logs (including timestamp, operation type, processing result).

##### 2.6 Data Verification and Exception Handling
- Implement data integrity verification:
  - Check non-null for mandatory fields (Task ID, Test Project).
  - Verify device duration value range (>=0 and <10 hours).
  - Validate Task ID format (regular expression `^TASK-[HML]-(\d{8})$`).
- Exception handling mechanism:
  - Provide message prompts when files do not exist.
  - Automatically flag and log format error data to an error log file.
  - Automatically enable batch processing mode if memory is insufficient.