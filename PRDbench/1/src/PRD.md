### Intelligent Analysis and Optimization System for Restaurant Supply Chains PRD

#### 1. Requirement Overview

This system aims to provide restaurant enterprises with a comprehensive dish lifecycle management solution. By integrating fundamental dish data, ingredient composition, sales performance and supply chain information, it achieves dish cost analysis and supply chain optimization. The system must support command-line interaction, be fully implemented in Python to encompass complete business logic, cover functional modules including data management, ingredient analysis, sales statistics and intelligent recommendation.

#### 2. Basic Functional Requirements

##### 2.1 Dish Data Management Module
- Supports CRUD operations for basic dish information (name, category, selling price, cooking time)
- Provides standardized dish data template import (CSV format), supports batch upload
- Supports multi-criteria search functionality based on dish ID, name and category
- Supports confirmation mechanism for dish deletion operations

##### 2.2 Ingredient Composition Analysis Module
- Supports uploading dish ingredient lists, including ingredient name, usage amount, unit, and cost unit price
- Provides dish cost structure analysis, calculating ingredient cost proportions and gross profit margin (accurate to one decimal place)
- Supports allergen identification functionality, capable of marking dishes containing the eight major allergen categories (e.g., crustaceans, nuts, eggs, soybeans)

##### 2.3 Sales Data Analysis Module
- Supports order data import, containing dish ID, sales quantity, sales time, and settlement price
- Implements dish sales trend analysis, statistically analyzes sales volume changes by day/week/month dimensions

##### 2.4 Dish Similarity Matching Module
- Implements a similarity algorithm for dishes based on name
- Supports uploading approximate item source files, automatically identifies and categorizes similar dish groups
- Statistically analyzes cumulative order volume, average settlement price, and sales fluctuation coefficient for similar dish groups

##### 2.5 Command-Line Interaction Functionality
- Implements a main menu navigation system, supports seamless switching between modules
- Provides data import/export progress visualization (text progress bar)
- Supports displaying analysis results as text tables or simple ASCII charts
- Implements confirmation mechanisms for critical operations and error handling processes, including invalid input prompts

#### 3. Technical Implementation Requirements

##### 3.1 Environment and Documentation
- Provide clear documentation (README.md), including project introduction, environment setup instructions (how to install dependencies), and program startup commands
- Support starting the program and displaying the main menu via `python src/main.py`

##### 3.2 Program Operability
- The program can successfully start and display the main menu
- Support interactive CLI operations and smooth navigation between modules

##### 3.3 Unit Testing
- Provide executable unit tests, support execution via `pytest`
- The test framework should run successfully, and all discovered test cases should pass