# Genealogy Data Management and Relationship Analysis System PRD

## 1. Requirement Overview

This system aims to achieve full lifecycle management of family member information and intelligent analysis of complex kinship relationships through command-line interaction. The system constructs a family relationship network based on tree data structure, supporting basic member information CRUD operations, multi-dimensional kinship relationship queries, family statistical analysis, and data persistent storage. Core business scenarios include family member archive management, blood relationship tracing, family demographic statistical analysis, etc., providing digital support tools for family history research, genealogy compilation, population statistics and related fields.

## 2. Functional Requirements

### 2.1 Member Basic Information Management Module

#### 2.1.1 Member Information Entry Function
- **Data Field Specifications**: The system supports entry of the following standardized fields:
  - Basic Identity Information: Name (string type), Gender (enum value: Male/Female)
  - Lifecycle Information: Birth Date (YYYYMMDD format), Death Date (YYYYMMDD format, fill 0 if not deceased), Birthplace (string type)
  - Physical Characteristics: Height (floating point number, unit: cm)
  - Social Attributes: Education (enum value: Elementary/Junior High/High School/Bachelor/Master/PhD), Occupation (string type), Highest Position (string type)
  - Relationship Attributes: Relative Name (used to establish family relationships), Relationship Type (enum value: 0-spouse relationship, 1-child relationship)

- **Data Validation Mechanisms**:
  - Date Format Validation: Birth/Death dates must comply with YYYYMMDD format, system validates format using regular expression `^\d{8}$`
  - Numerical Range Validation: Height range limited to 50-300cm, prompts user to re-enter if beyond range
  - Education Level Validation: Education field must match predefined enum values, using dictionary mapping for numerical conversion (Elementary=1, Junior High=2...PhD=6)
  - Relationship Logic Validation: If specifying relative relationship when adding new member, need to verify whether target relative exists in system

#### 2.1.2 Member Information Storage Function
- **Storage Format**: Uses CSV format for structured storage, field order: Name, Birthplace, Birth Date, Death Date, Height, Education, Occupation, Highest Position, Relative, Relationship, Gender
- **File Management**:
  - Default Data File: `data.csv`, automatically created during first run
  - Incremental Storage: New member information uses append mode writing, avoiding overwriting existing data
  - Data Integrity: Uses pandas DataFrame for data processing, ensuring CSV format standardization and completeness

### 2.2 Family Relationship Network Construction Module

#### 2.2.1 Tree Structure Construction Algorithm
- **Data Structure Design**:
  - `Member` Class Definition: Each family member corresponds to a Member object, containing attributes:
    - `idx`: Member's index position in data list
    - `kids`: Child member index list (supports multiple children families)
    - `spouse`: Spouse member index (-1 indicates no spouse)
  - Root Node Selection: Default first entered member as family tree root node, relationship type set to -1

- **Relationship Establishment Logic**:
  - Spouse Relationship: Bidirectionally establish spouse pointers, simultaneously share kids list to achieve shared children
  - Parent-Child Relationship: Add child index to parent Member's kids list
  - Relationship Search: Locate target member's position in family list through name matching

#### 2.2.2 Relationship Query Algorithm Implementation
- **Parent Generation Query Algorithm**:
  - Input Parameters: Target member index, query generations, gender filter conditions
  - Query Logic: Recursively traverse family list, search for superior members whose kids list contains target member
  - Generation Control: Control queried ancestor generations through recursion depth parameter (1st generation = parents, 2nd generation = grandparents)
  - Gender Filtering: Filter query results according to user specified gender (0-unrestricted, 1-male, 2-female)

- **Child Generation Query Algorithm**:
  - Query Logic: Start from target member's kids list, recursively traverse all descendants of specified generations
  - Result Collection: Use list to collect qualified descendant member indices, supports cross-generation queries
  - Gender Filtering: Perform secondary filtering on query results by gender

- **Spouse Query Algorithm**:
  - Direct Query: Obtain spouse information through Member object's spouse attribute
  - Exception Handling: Return "Cannot find spouse" prompt when spouse is -1

### 2.3 Basic Information Retrieval Module

#### 2.3.1 Multi-dimensional Query Function
- **Query Dimensions**: Supports member retrieval according to following 9 dimensions:
  1. Name exact matching query
  2. Birthplace fuzzy matching query
  3. Birth date exact matching query
  4. Education level matching query
  5. Occupation keyword query
  6. Highest position matching query
  7. Gender classification query

- **Query Algorithm**:
  - Traversal Mechanism: Use `circle()` function for linear traversal of all member data
  - Data Type Processing: Perform type conversion matching for numerical fields (birth date, death date, height)
  - Result Aggregation: Collect indices of all matching members into result list, supports multiple result queries like same names
  - Exception Handling: Return -1 identification code when no matching results found

### 2.4 Statistical Analysis Module

#### 2.4.1 Basic Statistical Functions
- **Height Statistics**:
  - Average Height Calculation: Use pandas' mean() function to calculate entire family's average height to one decimal place
  - Data Processing: Automatically filter invalid height data (such as 0 values or abnormal values)

- **Education Statistics**:
  - Statistical Content: Convert education text into numeric levels (Primary=1, Middle School=2, High School=3, Undergraduate=4, Master's=5, Doctorate=6), and calculate average, highest, and lowest education level
  - Output Requirement: The system should display the average, highest, and lowest education level information

#### 2.5.2 Demographic Statistics Function
- **Gender Ratio Statistics**:
  - Statistical Logic: Traverse gender field, separately count male and female numbers
  - Ratio Simplification: Use greatest common divisor algorithm to simplify male:female ratio (e.g., 6:4 simplified to 3:2)
  - Result Format: Output simplified gender ratio in "Male:Female" format

### 2.6 Tree Display Module

#### 2.6.1 Genealogy Visualization Output
- **Display Format**: Uses text tree structure to display family relationships:
  - Level Indentation: Each next generation increases 2 space indentation
  - Member Identification: Display as "--Name" format
  - Spouse Relationship: Directly display spouse name after member name (e.g.: "--Zhang San Li Si")
  - Line Break Processing: Each member occupies one line, clearly displaying hierarchical relationships

- **Traversal Algorithm**:
  - Depth-First Traversal: Start from root node, recursively traverse each member's children
  - Level Recording: Record current traversal depth through layer parameter, control indentation format
  - Display Control: Real-time output to console during traversal process, providing immediate genealogy display

## 3. Technical Requirements

### 3.1 Development Environment and Dependencies
- **Python Version Requirements**: Python 3.7+, ensuring compatibility with pandas, tkinter and other libraries
- **Core Dependency Libraries**:
  - `pandas >= 1.0.0`: Used for CSV file operations and DataFrame data processing
  - `tkinter`: Python standard library, provides graphical interface support (only for existing GUI compatibility maintenance)
  - `os`: File system operations and path management

### 3.2 Data Storage Architecture

- **Data Integrity Assurance**:
  - Atomic Operations: Use pandas' to_csv() method to ensure file writing atomicity
  - Exception Recovery: Maintain original data unchanged when file operations fail, avoiding data loss
  - Encoding Unification: All file operations use UTF-8 encoding, supporting Chinese character processing

### 3.3 Algorithm Complexity Requirements
- **Query Performance**:
  - Basic Information Query: O(n) linear time complexity, where n is total family members
  - Relationship Query: O(h×k) time complexity, where h is family tree height, k is average children count
  - Statistical Calculation: O(n) linear time complexity, supports real-time statistics for thousand-scale families

- **Space Complexity**:
  - Memory Occupation: O(n) space complexity, each member occupies fixed-size Member object
  - Storage Efficiency: CSV file size approximately 200 bytes per member, supports large-scale family data storage

### 3.4 Error Handling and Exception Management
- **Input Validation**:
  - Format Validation: Strict validation of date formats, numerical ranges, enum values, etc.

- **Exception Handling Mechanisms**:
  - Query Exceptions: User-friendly error prompts when members don't exist or query conditions are invalid