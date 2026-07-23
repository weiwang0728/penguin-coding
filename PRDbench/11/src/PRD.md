# 1. Overview of Requirements

This project aims to develop a localized data processing and automated testing platform targeting data engineering or business analytics teams. The objective is to enable developers or analysts to implement a series of common data processing, transformation, and validation operations in local environments using Python, and rapidly verify algorithm correctness through automated test scripts. The platform requires no frontend interface, with all functionalities implemented through command-line interaction, facilitating integration into CI/CD or data pipeline scripts.

# 2. Functional Requirements

1. **Data Processing Module**

   - **Numeric Comparator**: Provides a universal numeric comparison function that returns -1/0/1, suitable for business scenarios such as sorting and threshold judgment.
   - **Conditional Filter**: Supports custom condition functions to filter input data lists, retaining data items that meet the criteria. Applicable for data cleaning, log filtering, etc.
   - **Dynamic Adder Generator**: Dynamically generates addition functions based on input parameters, commonly used for parameterized configuration or batch data correction.
   - **Unique List Extractor**: Extracts first-occurring unique elements from original data while maintaining original order. Suitable for data deduplication requirements such as logs, user IDs, etc. 
   - **Recursive Replacer**: Recursively replaces specified elements within nested data structures. Applicable to scenarios like configuration templates, text processing, complex data migration, etc.
   - **Batch Mapper & Replacer**: Supports batch mapping and replacement for multiple element groups. Suitable for business needs like bulk vocabulary, labels, ID mapping, etc.
   
2. **Automated Testing and Feedback**

   - **Automated Unit Testing**: Each functional module includes independent unit tests covering normal, abnormal, and boundary scenarios. All test cases are uniformly managed in the `tests/` directory.
   - **Local Score Feedback and Reporting**: Provides local scoring scripts that automatically statistics module pass rates, outputting detailed scores and total scores to facilitate team member self-check and quality control.

3. **Command-Line Interaction Experience**

   - **One-Click Execution and Testing**: Users can execute all functions and tests with a single command-line command, requiring no graphical interface, making it suitable for automated integration. 
   - **Parameterized Submission & Identity Marking**: Supports specifying user identity (such as employee ID, name) through command-line parameters, facilitating team collaboration and result archiving.

4. **User Guide and Documentation**

   - **Detailed Operation Documentation**: Provides `README.md` containing environment setup, module description, testing methods, command-line usage, FAQs, etc.