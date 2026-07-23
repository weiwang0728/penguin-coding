# PRD: Library Management System

## 1. Overview of Requirements
This project aims to develop a command-line-based library management system that integrates book management, user management, and circulation management functionalities. The system must support two roles—administrator and regular user—and enable CRUD (Create, Read, Update, Delete) operations on book information through database interactions. It will provide basic permission controls, along with the ability to track circulation status and export data, offering comprehensive business management support for a library.

**Program Startup Requirements**: Upon startup, the program should display a clear main menu with at least 4 actionable options, including: user login, user registration, system information, help information, exit system, etc.

## 2. Basic Functional Requirements

### 2.1 User Management Module

-   Support for user registration, requiring input of 4 basic information items (student ID, name, password, contact details). Upon successful registration, display a success message and correctly save user information to the database.
-   Support for user login authentication, distinguishing between regular user and administrator privilege levels.
    -   After successful login, regular users should see a regular user menu interface containing options such as borrow, return, query, etc.
    -   After successful login, administrators should see an administrator menu interface containing options such as user management, book management, system statistics, etc.
-   Provision of user information management functions, allowing administrators to perform CRUD operations on user accounts.
-   Implementation of a password encryption mechanism using the MD5 hashing algorithm to protect user privacy (passwords are stored as 32-bit MD5 hashes, completely different from plaintext).
-   Support for user permission settings, allowing administrators to modify user privilege levels.

### 2.2 Book Information Management Module

-   Integration of basic book data, including 7 parameters: title, book ID, author, category, publisher, publication time, and stock quantity.
-   Implementation of CRUD operations for book information, allowing administrators to add, delete, update, and query books.
    -   **Book Addition**: Administrators can add books by entering all 7 book information items (title, book ID, author, category, publisher, publication time, stock quantity). Books are successfully added to the database with all 7 items correctly saved.
    -   **Book Modification**: Administrators can modify book information. Modification operations correctly update the database, and queries confirm that information has been changed, displaying a modification success confirmation.
    -   **Book Deletion**: Administrators can delete books. Deletion operations have a confirmation mechanism, and after confirmation, records are correctly removed (only books with no circulation records can be deleted).
-   Provision of book search functionality with support for multi-condition queries:
    -   Fuzzy search by title (supporting partial matches, returns all books containing the keyword).
    -   Exact search by author (exact match, returns all books by the specified author).
    -   Filter search by category (returns all books in the specified category).
    -   Exact search by book ID (exactly returns the unique book information corresponding to the specified book ID).
    -   Search by publisher (returns all books from the specified publisher).
-   Implementation of a book inventory management mechanism that automatically maintains the available and reserved quantities.
-   Support for batch import and export of book information (supports JSON and CSV formats).

### 2.3 Circulation Management Module

-   Implementation of book borrowing functionality, including the following business rules:
    -   User identity verification (user must be logged in; unauthenticated users cannot access borrowing functionality; the system should correctly block access and provide authentication prompts).
    -   Book inventory check (available quantity > 0; books with 0 stock cannot be borrowed; the system should correctly block access and prompt insufficient stock).
    -   Duplicate borrowing check (a user cannot borrow the same book twice; the system should correctly block access and prompt that the book has already been borrowed by the current user).
    -   Borrowing limit check (regular users up to 5 books, administrators up to 10 books; the system should correctly enforce borrowing limits and prompt when the limit is reached).
    -   After successful borrowing, stock quantity decreases by 1, borrowing records are correctly created containing student ID, book ID, borrow time, borrow status, and other information, displaying a borrowing success message.
-   Provision of book return functionality, which automatically updates inventory status and circulation records (after successful return, stock quantity increases by 1, circulation record status is updated to returned, return time is correctly recorded, displaying a return success message).
-   Implementation of a book reservation feature, supporting a queuing mechanism for books that are currently out of stock (after successful reservation, the book's reservation count increases by 1, reservation records include queue number, displaying reservation success message and queue number).
-   Automatic maintenance of circulation status, including borrowed status, return time, and reservation queue (circulation records contain student ID, book ID, borrow time, borrow status, and other information).

### 2.4 Query and Statistics Module

-   Implementation of a personal circulation history query, displaying a user's currently borrowed items and past records (clearly categorized display).
-   Provision of a book status query to display detailed book information and its circulation status.
-   Implementation of system-wide statistics, allowing administrators to view:
    -   Total number of books and users.
    -   Current number of loans and reservations.
    -   A list of books with insufficient stock (books with stock quantity less than 3, displaying book title and current stock quantity).
    -   Circulation frequency statistics (displayed sorted by circulation frequency).
-   Support for visualizing circulation data by generating statistical charts (using matplotlib to generate at least 2 types of charts: bar charts, pie charts, etc.), charts saved as PNG format to the data/charts directory.

### 2.5 System Management Module

-   Role-based access control:
    -   Regular User Permissions: Borrow, return, reserve, and query (can only access these 4 functions).
    -   Administrator Permissions: User management, book management, circulation management, system statistics, data export, and regular user functions (can access all 6 functions).
-   Implementation of data backup and recovery functionality, with support for periodic automatic backups, backup files saved to the data/backup directory.
-   Provision of a system logging feature to record at least 3 types of key operations (user login, book borrowing, data modification, etc.), containing operation time, user, operation content, and other information.
-   Support for data import and export in formats such as JSON and CSV (supports exporting user data and book data, supports importing data files in JSON and CSV formats).

### 2.6 Command-Line Interaction System

-   Implementation of a multi-level command menu system, supporting at least 3 levels of menu navigation (main menu - administrator menu - book management, etc.), with support for shortcut keys.
-   Provision of real-time input validation, including:
    -   Student ID format validation (length: 1-20 characters, cannot be empty, cannot exceed 20 characters, cannot contain special characters).
    -   Password strength verification (length: 6-32 characters, cannot be empty, cannot be less than 6 characters, cannot exceed 32 characters).
    -   Check for book ID uniqueness (check if book ID already exists when adding books).
    -   Date format validation (requires YYYY-MM-DD format, validates date validity).
-   Implementation of an operation confirmation mechanism for critical actions (at least 2 types of operations such as deleting books, deleting users require user confirmation).
-   Provision of a help information feature, supporting at least 3 types of help information: input format instructions, function descriptions, shortcut key prompts, etc.

## 3. Data Requirements

### 3.1 Database Design

#### 3.1.1 User Table (`user`)

```sql
CREATE TABLE user (
    StudentId VARCHAR(20) PRIMARY KEY COMMENT 'Student ID',
    Name VARCHAR(20) NOT NULL COMMENT 'Name',
    Password VARCHAR(32) NOT NULL COMMENT 'Password (MD5 encrypted)',
    IsAdmin INT DEFAULT 0 COMMENT 'Is Administrator (0: Regular User, 1: Administrator)',
    tel VARCHAR(30) COMMENT 'Contact Information',
    CreateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    UpdateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update Time'
);```

#### 3.1.2 Book Table (book)

```sql
CREATE TABLE book (
    BookName VARCHAR(30) NOT NULL COMMENT 'Book Title',
    BookId CHAR(30) PRIMARY KEY COMMENT 'Book ID',
    Auth VARCHAR(20) NOT NULL COMMENT 'Author',
    Category VARCHAR(10) COMMENT 'Category',
    Publisher VARCHAR(30) COMMENT 'Publisher',
    PublishTime DATE COMMENT 'Publication Time',
    NumStorage INT DEFAULT 0 COMMENT 'Stock Quantity',
    NumCanBorrow INT DEFAULT 0 COMMENT 'Available for Loan',
    NumBookinged INT DEFAULT 0 COMMENT 'Number of Reservations',
    CreateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    UpdateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update Time'
);
```

#### 3.1.3 User Loan Table (user_book)

```sql
CREATE TABLE user_book (
    StudentId CHAR(10) NOT NULL COMMENT 'Student ID',
    BookId CHAR(6) NOT NULL COMMENT 'Book ID',
    BorrowTime DATE NOT NULL COMMENT 'Borrow Time',
    ReturnTime DATE COMMENT 'Return Time',
    BorrowState BIT(1) DEFAULT b'0' COMMENT 'Borrow Status (0: Returned, 1: Borrowed)',
    BookingState INT DEFAULT 0 COMMENT 'Reservation Queue (0: Not Reserved, >0: Queue Position)',
    CreateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    UpdateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update Time',
    PRIMARY KEY (StudentId, BookId)
);
```

### 3.2 Data Validation Rules
#### 3.2.1 User Data Validation
-   **Student ID**: Non-empty, unique, 1-20 characters, alphanumeric.
-   **Name**: Non-empty, 1-20 characters, supports Chinese and English.
-   **Password**: Non-empty, 6-32 characters, recommended to be alphanumeric.
-   **Contact**: Optional, 1-30 characters, supports phone/email formats.
-   **Administrator Flag**: 0 or 1, defaults to 0.

#### 3.2.2 Book Data Validation
-   **Book ID**: Non-empty, unique, 1-30 characters, ISBN format recommended.
-   **Book Title**: Non-empty, 1-30 characters, supports Chinese and English.
-   **Author**: Non-empty, 1-20 characters, supports Chinese and English.
-   **Category**: Optional, 1-10 characters, standard classification system recommended.
-   **Publisher**: Optional, 1-30 characters.
-   **Publication Time**: Optional, valid date format (YYYY-MM-DD).
-   **Stock Quantity**: Non-negative integer, defaults to 0.
-   **Available Quantity**: Non-negative integer, cannot exceed stock quantity.
-   **Reservation Quantity**: Non-negative integer, cannot exceed stock quantity.

#### 3.2.3 Circulation Data Validation
-   **Student ID**: Must exist in the `user` table.
-   **Book ID**: Must exist in the `book` table.
-   **Borrow Time**: Non-empty, valid date format, defaults to the current date.
-   **Return Time**: Optional, valid date format, must be later than the borrow time.
-   **Borrow Status**: 0 (Returned) or 1 (Borrowed), defaults to 1.
-   **Reservation Status**: Non-negative integer, 0 indicates not reserved.

### 3.3 Business Constraints
#### 3.3.1 Circulation Constraints
-   **Borrowing Limit**: Regular users up to 5 books; administrators up to 10 books.
-   **Loan Period**: Default 30 days, configurable.
-   **Overdue Handling**: Items are automatically marked as overdue after the loan period expires.
-   **Reservation Priority**: A first-come, first-served queue based on reservation time.

#### 3.3.2 Inventory Constraints
-   Available quantity cannot exceed stock quantity: `NumCanBorrow` ≤ `NumStorage`.
-   Reservation quantity cannot exceed stock quantity: `NumBookinged` ≤ `NumStorage`.
-   A reservation queue is used when stock is insufficient, supporting reservations up to the stock quantity.
-   The reservation queue is automatically processed upon book return, notifying users in order.
-   Inventory warning mechanism: Books with stock quantity less than 3 should be marked as insufficient stock and displayed in system statistics.

#### 3.3.3 Data Integrity Constraints
-   Foreign key constraints ensure data consistency (e.g., `StudentId` and `BookId` in `user_book` must exist in their respective tables).
-   Transactions are used for borrow, return, and reservation operations to ensure data integrity.
-   Database locking mechanisms are used to prevent concurrency conflicts.

### 3.4 Data Backup and Recovery

-   A mechanism for regular data backups (e.g., daily automatic backups), backup files saved to the data/backup directory (format: library_backup_*.db or library_backup_*.sql).
-   Functionality to support data recovery from backup files.
-   Data import/export functionality supporting JSON and CSV formats (export user data as CSV format, export book data as JSON format; supports importing data files in JSON and CSV formats, such as evaluation/test_users.json and other standard format files).
-   Logging and auditing functionality to record all key operations and exceptions, log files saved to logs/system.log.

## 4. Technical Implementation Requirements

### 4.1 Core Function Implementation Details

#### 4.1.1 Database Connection Management

-  **Connection Pooling**: Use a connection pool to improve database access efficiency.
-  **Transaction Handling**: Ensure atomicity, consistency, isolation, and durability (ACID) of data operations.
-  **Exception Handling**: A robust mechanism for capturing and handling exceptions (gracefully handle database connection exceptions, display friendly error messages, program does not crash).
-  **Connection Closing**: Ensure database connections are properly closed to prevent leaks.
-  **Database Initialization**: Upon program startup, clearly report database connection status, be able to normally access user table, book table, and circulation table, and display table structure information.

#### 4.1.2 Business Logic Implementation

-  **Data Validation**: Verification of input data formats and business rules (including input exception handling: illegal characters, overly long strings, special symbols, and at least 3 types of exception inputs; the system will not crash due to exception inputs).
-  **Business Rule Checks**: Enforcement of loan limits, inventory checks, and other constraints.
    -   Identity verification check: Unauthenticated users cannot access borrowing functionality.
    -   Inventory check: Books with 0 stock cannot be borrowed.
    -   Duplicate borrowing check: The same user cannot borrow the same book twice.
    -   Quantity limit check: Regular users up to 5 books, administrators up to 10 books.
-  **Status Management**: Management of book and circulation statuses.
-  **Concurrency Control**: Use of database locks and transactions to ensure data consistency.

#### 4.1.3 User Interface

-   **Command-Line Menu System**: Multi-level menus with support for returning to the previous menu.
-   **Input Validation**: Real-time validation of user inputs.
-   **Error Prompts**: User-friendly error messages.
-   **Operation Confirmation**: Critical operations require user confirmation.

#### 4.1.4 Data Security

-   **Password Encryption**: Use the MD5 hashing algorithm to encrypt passwords (passwords are stored as 32-bit MD5 hashes, completely different from plaintext).
-   **SQL Injection Protection**: Use parameterized queries to prevent SQL injection.
-   **Permission Verification**: Verify user permissions before every operation.
-   **Data Backup**: Regularly back up important data.
-   **File Operation Exception Handling**: Correctly catch FileNotFoundError, PermissionError, and other exceptions, return None or False, provide error prompts, and the program continues to run stably.

#### 4.1.5 Chart Generation

-   Use Matplotlib to generate basic statistical charts.
-   Support for at least 2 types of charts: bar charts, pie charts, etc.
-   Save charts in PNG format to the data/charts directory.
-   Generate chart data based on database query results.

### 4.2 Testing Requirements

-   **Unit Testing**: Cover all core functional modules with test coverage ≥80%.
-   **Integration Testing**: Verify collaboration between modules and business workflows.
-   **Functional Testing**: Ensure all functions work as expected.
-   **Data Testing**: Verify the correctness and integrity of data operations.

## 5. Deployment and Operation

### 5.1 Environment Preparation

1.  Install Python 3.8+ and ensure the environment is correctly configured.
2.  Install MySQL 8.0+ and configure the database server.
3.  Create the database and user, and set connection permissions.
4.  Install project dependencies using pip.

### 5.2 Initialization Steps

1.  Import the database schema by executing `init_data.sql`.
2.  Import initial sample data file `data/sample_data.json` or real data.
3.  Configure the database connection by modifying parameters in `config/database.py`.
4.  Create output directories: create `data/charts`, `data/backup`, `logs`, and other output directories.
5.  Run system tests to ensure all functions work properly.

### 5.3 Running the System

```bash
# Install dependencies
pip install -r requirements.txt

# Configure the database connection
# Edit the config/database.py file

# Initialize the database
python -c "from utils.database import init_database; init_database()"

# Run the system
python main.py
```

### 5.4 Maintenance Requirements

-   **Regular Data Backup**: Automatically back up the database daily.
-   **System Log Monitoring**: Monitor the system's operational status and exceptions.
-   **Regular Cleanup**: Clear outdated chart files.
-   **Security Updates**: Apply security patches and update dependencies in a timely manner.

## 6. Acceptance Criteria

### 6.1 Functional Acceptance

-   All basic functions operate normally (user management, book management, circulation, etc.).
-   Data operations are accurate and error-free (CRUD operations yield correct results).
-   Business rules are correctly enforced (loan limits, inventory management, etc.).
-   Chart generation functions work correctly, generating and saving basic statistical charts.
-   Exceptions (e.g., input errors, network issues) are handled properly.

### 6.2 Performance Acceptance

-   Reasonable system response time (query operations < 2 seconds).
-   Stable under concurrent access (supports 10+ simultaneous users).
-   Good data query efficiency (complex queries < 5 seconds).
-   Reasonable memory usage (system memory footprint < 500MB).

### 6.3 Security Acceptance

-   Effective user permission controls (users can only access their permitted functions).
-   Data security is ensured (password encryption, SQL injection protection, etc.).
-   Complete input validation (all user inputs are validated).
-   Error messages do not leak sensitive system information.

### 6.4 Usability Acceptance
-   User-friendly interface (clear menus, explicit prompts).
-   Clear error prompts (error messages are easy to understand).
-   Complete help information (detailed operational guidance is provided).
-   Good system stability (no anomalies during long-term operation).
