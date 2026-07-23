### US Stock Quantitative Analysis & Multidimensional Indicator Diagnostic Tool PRD

#### 1. Overview of Requirements
This tool aims to provide US stock quantitative analysts with comprehensive data querying and deep analysis capabilities. It supports user-defined SQL queries on US stock market data, enables stock screening (by market capitalization category and other dimensions) based on query results, and diagnoses the causes of volatility for specified financial/trading indicators (such as return volatility, PE ratio deviation) across multiple dimensions. The tool operates via command-line interaction, with core functionalities including SQL query management, market capitalization tier-based screening, variance decomposition for dimensional contribution analysis, and result presentation.

#### 2. Basic Functional Requirements

##### 2.1 SQL Query Management
- Provides a command-line SQL entry interface, supports multi-line input and syntax checking (implementing keyword check and bracket match validation using Python’s `sqlparse` library).
- Offers documentation for supported SQL statements, including sample usage and expected result previews.
- Displays dynamic progress indicators while executing queries (e.g., "Executing query: 30%"), and allows operation interruption (users can terminate queries with Ctrl+C).
- Returns query status (success/failure); on failure, outputs specific reasons (such as error position in syntax, non-existent fields, or data source connection failure).
- Automatically saves the last 10 valid SQL query records, allowing users to quickly reuse historical queries by reference number.
- Data sources support user-specified local CSV files (the file path is configured through the command line), and all query fields must strictly correspond to the CSV headers. The supported data file format must include the following fields: Stock Ticker, Company Name, Market Capitalization, Sector, Exchange, Daily Return Volatility, Price-Earnings Ratio (PE), and Region.

##### 2.2 Stock Market Capitalization Tier-Based Screening
- Provides preset market cap category screening based on the "Market Cap" field in query results, referencing NYSE official definitions: Micro-cap (<$300M), Small-cap ($300M≤Market Cap<$2B), Mid-cap ($2B≤Market Cap<$10B), Large-cap ($10B+).
- Allows users to set custom market cap ranges (input upper/lower limit values); screening results must include stock ticker, company name, market cap, and category label.
- Supports combined screening criteria; users can add dimensions such as sector (e.g., "Technology"), exchange (e.g., "NASDAQ"), etc. (based on respective fields in the SQL query results), with "AND/OR" logical relationships between conditions.
- Screening results must support ascending/descending sorting (by market cap or user-specified fields) and paginated display (10 items per page, with navigation for next/previous pages).

##### 2.3 Multidimensional Indicator Volatility Diagnosis
- Supports users in selecting indicators for analysis from the query results (such as "Daily Return Volatility," "Price-Earnings Ratio PE," "Market Capitalization"), limited to numeric fields. The system must automatically identify and list all numeric fields for user selection.
- Automatically extracts non-numeric fields from SQL results as candidate analysis dimensions (such as "Sector," "Market Cap Category," "Region," "Exchange"). Users can select 1-3 dimensions for combined analysis by reference number. The system must automatically recognize and present all non-numeric fields for user selection.
- Uses Multivariate Variance Decomposition algorithm to calculate each dimension’s contribution to indicator volatility, outputting explained variance proportions (e.g., "Sector: 42%, Market Cap Category: 28%, Interaction Effects: 15%").
- Performs in-depth analysis on the top contributing dimension (contribution > 30%), presenting the mean and standard deviation of the indicator for each sub-category under that dimension (e.g., "In the Sector dimension, Technology sector volatility mean is 1.2% (σ=0.3%), Healthcare sector volatility mean is 0.8% (σ=0.2%)").

##### 2.4 Command-Line Interaction & Result Presentation
- Main interface uses a menu-driven interaction scheme with options: [1] Enter CSV File Path [2] SQL Query [3] Stock Screening [4] Indicator Volatility Analysis [5] View Query History [6] Exit.
- User input requires validity checks (for example, menu selection must be a number between 1-6, SQL fields must exist in the data source, and dimension selections must be among candidates). Invalid input should trigger error messages in English (such as "Error: Please enter a number between 1-6"). If the input is invalid, the program should prompt "Invalid input, please try again." and remain at the current menu.
- When generating analysis results, users may choose to display them as a textual (psql-style) table.
- All output results can be saved as TXT files (user may specify save path); the output file must contain the query SQL, screening conditions, analysis dimensions, contribution data, and the textual table. Saved report files must include complete analysis context information and results.

#### 3. Technical Implementation Requirements
- Implemented in Python, relying on the following libraries: pandas (for data processing), sqlparse (for SQL syntax validation), statsmodels (for variance decomposition analysis), tabulate (for table formatting), and pandasql (for executing SQL queries).
- Supports multi-line SQL input, ending input with a blank line.
- Supports Ctrl+C to interrupt an ongoing query operation.
- Query history is saved in a file named history.json, with up to 10 recent entries retained.
