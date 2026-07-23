### Command-Line Data Preprocessing and Analysis Tool PRD

#### 1. Overview of Requirements
This tool aims to provide comprehensive data preprocessing and analysis capabilities in a command-line environment, supporting Excel data import, multi-mode data transformations, statistical analysis, rule-based splitting and export functions. Users can complete the entire processing workflow from raw data cleaning to formatted output through command interactions, meeting the basic requirements of Exploratory Data Analysis (EDA) in the data science field.

#### 2. Basic Functional Requirements

##### 2.1 Data Import and Metadata Parsing
- Support reading .xlsx/.xls format files, automatically identifying worksheet count and names.
- Parse and display data metadata: field names, data types (numerical/categorical/date), missing value proportion.
- Provide data preview functionality, displaying first N rows of data (N configurable, default 10 rows).
- Support selecting specific worksheets or batch importing multiple worksheet data.

##### 2.2 Data Format Operation Functions
- **Row-Column Transformation Module**:
  - Support row-to-column conversion (aggregation key specification and value column selection).
  - Support column-to-row conversion (row-by-row mode), automatically recognizing common delimiters (comma/semicolon/space/Tab).
  - Allow adding intermediate connectors, prefix text, suffix text during transformation process.
  - Provide "text marking" option in row-by-row mode, supporting single quote/double quote/no marking three modes.
  - **Configuration Parameters**: Delimiter selection, connector setting, and text marking mode selection


- **Data Formatting Module**:
  - Support enumerated value replacement (requires user-provided key-value mapping table).
  - Provide numerical formatting (decimal places, percentage, scientific notation).
  - Support date type standardization (ISO 8601/custom format).
  - String processing (case conversion, space removal, special character filtering).
  - **Configuration Parameters**: mapping file path, decimal places setting, date format selection, string processing mode

##### 2.3 Data Content Cleaning Functionality
- **Missing Value Handling**:
  - Provide missing value statistics (by field and record dimensions).
  - Support deleting missing values or filling (mean/median/mode/custom value).

- **Outlier Detection**:
  - Implement IQR (Interquartile Range) algorithm to identify numerical field outliers.
  - Provide Z-score normalization conversion (requires user-specified threshold).
  - Support outlier marking or replacement handling.

##### 2.4 Statistical Analysis Functionality
- **Descriptive Statistics**:
  - Numerical fields: calculate mean, median, standard deviation, range, quartiles.
  - Categorical fields: calculate frequency, frequency rate, mode, and unique value count.

- **Data Distribution Analysis**:
  - Generate numerical field frequency distribution tables (support equal-width/equal-frequency binning).
  - Calculate inter-field correlation coefficients (Pearson/Spearman methods optional).

##### 2.5 Data Splitting and Export
- Support splitting datasets by specified categorical field values.
- Check and use legal field values as new worksheet names, output independent Excel files.
- Option to apply configured formatting rules during export.
- Support batch export to CSV format (requires specifying delimiter and encoding).

##### 2.6 Command-Line Interaction and State Management
- Implement interactive command menu system, supporting direct switching between functions without returning to main menu.
- Provide operation history record viewing, supporting historical result saving, loading, and display.
- All user inputs require validity validation, error inputs provide Chinese prompts.
- **Main Menu Structure**: Includes core function entries such as "Data Import", "Data Format Operation", "Data Content Cleaning", "Statistical Analysis", and "Data Splitting & Export".