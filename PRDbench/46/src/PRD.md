## PRD: Intelligent Personal Credit Assessment System for Banks(Product Requirements Document)

### 1. Overview of Requirements

1. This system provides banks and financial institutions with an intelligent personal credit assessment tool based on AI algorithms. It facilitates efficient and automated credit approval decisions through both command-line and web-based interfaces.

2. The core objective of the system is to automatically extract and process customer data, apply various algorithms (such as neural networks and logistic regression) for credit analysis, generate accurate credit scores, and present the results through multi-dimensional data visualizations and a comprehensive metric system. This will assist business personnel in making fast and scientific lending approval decisions.

3. Design Philosophy:
   - The system will support a full-cycle workflow—from data preprocessing and algorithm application to scoring and visualization—based on the UCI standard credit dataset (1000 records).
   - It will be designed for extensibility to integrate with real-world business data, enhancing the algorithms' generalization capabilities and usability.
    - It will make comprehensive use of statistical indicators such as ROC curves, LIFT charts, K-S curves, and AUC for multi-faceted comparison and selection of algorithm performance.
   - The system provides a sample data file: `sample_data/credit_data.csv` (UCI credit dataset format, optional to use).

---

### 2. Functional Requirements

#### 2.0 Program Startup and Main Menu

-   **Program Startup**
    -   After program startup, display a clear main menu containing at least 3 actionable options (e.g., "Data Import", "Algorithm Analysis", "Model Evaluation", etc.).
    -   Menu options must be clearly visible with no character encoding issues.

#### 2.1 Data Management and Intelligent Processing Module

-   **Data Import/Export**
    -   Support for batch import of raw customer credit data via CSV/Excel (UTF-8 encoded), with a field structure compatible with the UCI credit dataset format.
    -   Users can select any data file path that conforms to the format through the data import function (not limited to the sample file provided by the system).
    -   After successful import, the program must explicitly report "Import successful" and correctly display the number of imported data rows.
    -   Support for exporting processed data and AI analysis results to CSV/Excel formats.
    -   Implementation of field mapping and validity checks during data import, including:
        -   **Missing Value Detection**: Automatically detect and clearly indicate the location and quantity of missing values, providing detailed field-level missing value statistics.
        -   **Anomaly Detection**: Detect and alert about anomalous data issues (e.g., age field containing negative numbers or values exceeding 150), providing clear anomaly alerts.
        -   **Type Mismatch Alerts**: Detect and alert about type mismatch issues (e.g., numeric fields containing text), identifying all type mismatch data and providing clear alerts.

-   **Data Preprocessing**
    -   Support for handling missing values, providing at least 3 imputation method options: mean, median, and mode imputation.
    -   After missing value processing execution, display processing result statistics to verify that missing values have been correctly filled in the processed data.
    -   Automatic identification and encoding of numerical and categorical fields:
        -   Correctly identify all numerical fields (e.g., age, income, etc.).
        -   Correctly identify all categorical fields (e.g., gender, occupation, etc.).
        -   Support two encoding methods for categorical fields: one-hot encoding and label encoding.
    -   Provision of feature selection capabilities: Use Pearson correlation coefficient to calculate the correlation matrix between features, display filtering suggestions, and generate statistical distribution information for each field.
    -   Support for random sampling of customer data (with configurable proportions and random seeds).
    -   Support for data standardization/normalization and binning (with a reserved interface for techniques like WoE encoding).

#### 2.2 Algorithm Analysis and Scoring

-   **Algorithm Selection and Configuration**
    -   Provision of two mainstream credit assessment algorithms: Logistic Regression and Neural Networks (MLP).
    -   Support for algorithm parameter configuration, allowing users to make custom adjustments via the command line or configuration files.
    -   Inclusion of an extensible interface to facilitate the integration of additional algorithms, such as decision trees.

-   **Algorithm Application and Analysis**
    -   Automated execution of algorithm analysis, with output of detailed analysis logs containing at least 3 key pieces of information:
        -   Logistic Regression: execution time, parameter settings, convergence status.
        -   Neural Network: network structure, execution time, key parameters.
    -   Support for performance comparison across multiple algorithms, with output of a performance comparison table containing at least 4 metrics: accuracy, precision, recall, and F1-score.
    -   Support for saving and loading analysis results.

-   **Scoring and Prediction**
    -   Support for single-record scoring: Input one complete customer credit data record, output score results and credit rating.
    -   Support for batch data scoring: Implement batch scoring for test sets/new customer data (10+ records), output complete results including customer ID, score probability, and algorithm category.
    -   Credit rating classification rules are configurable.

#### 2.3 Model Evaluation and Visualization

-   **Evaluation Metrics and Output**
    -   Automatic generation and saving of:
        -   **ROC Curve**: Generate a clear ROC curve chart and save as PNG file, including AUC value annotation (with at least 3 decimal places) and grid lines.
        -   **K-S Curve**: Generate a K-S curve chart, clearly annotating the maximum KS distance value and its position.
        -   **LIFT Chart**: Generate a LIFT chart, clearly displaying lift values for different deciles.
        -   **Basic Metrics**: Simultaneously calculate and display 3 metrics: precision, recall, and F1-score.
        -   **Confusion Matrix**: Generate and display a confusion matrix.
    -   Output of a comparison table for key evaluation metrics (Logistic Regression vs. Neural Network), containing at least 4 metrics: accuracy, precision, recall, and F1-score.

-   **Visual Reports**
    -   Support for one-click generation of evaluation reports (including various statistical charts, key parameters, and business interpretations), exportable as HTML format.
    -   Reports must include at least 4 types of statistical charts: ROC curve, K-S curve, LIFT chart, and confusion matrix.
    -   All charts must be adaptive to data volume and labels.
    -   Support for automatic generation of a "Model Performance Summary," which clearly identifies the algorithm with the highest accuracy and provides corresponding recommendations, application suggestions, model stability analysis, etc.

-   **Parameter/Feature Interpretation**
    -   **Logistic Regression**: Output coefficient values and positive/negative impact direction for each feature, generate visualization charts for Top-N (at least top 5) feature importance.
    -   **Neural Network**: Output representative network weight information, generate feature contribution visualization charts (extensible to methods like Permutation Importance or SHAP values).

#### 2.4 System Extension and Business Integration

-   **Real-World Business Integration**
    -   Support for integration with actual bank data files (CSV, Excel formats, requiring desensitization and access control).
    -   Adaptation to real-world business field mappings and parsing of additional features.
    -   Provision of an AI prediction API (RESTful style), including:
        -   **API Availability**: Provide a health check endpoint, with API service responding normally.
        -   **Prediction Function**: Accept multi-field customer information (JSON format), return correct JSON response containing credit score and rating.

-   **Permission and Security Management**
    -   Support for role-based access control (e.g., Manager/Operator) with tiered permissions for viewing, AI analysis, data import, and prediction.
    -   Internal encryption of sensitive data in transit and minimized storage at rest; logging of all key operations.

-   **Logging and Error Handling**
    -   **Operation Logging**: Automatically record log information for all key operations (data import, algorithm analysis, etc., 3 or more operations).
    -   **Log Format**: Each log entry must contain 3 pieces of information: timestamp, operation type, and key parameters.
    -   **Error Handling**: Global exception capturing, provide user-friendly error messages without directly displaying raw exception stack traces.
    -   Support for log file rotation and review; optional automatic email alerts for critical errors.

---

### 3. Technical Requirements

-   **Programming Language**
    -   Python 3.9+

-   **Core Technology Stack**
    -   Data Processing: Pandas, NumPy
    -   Machine Learning: scikit-learn (for Logistic Regression), PyTorch/TensorFlow (for Neural Networks, with PyTorch preferred)
    -   Visualization: Matplotlib, Seaborn (for statistical charts)
    -   Metric Evaluation: `sklearn.metrics` (for AUC, ROC, K-S curve, LIFT, etc.)
    -   Configuration Management: YAML
    -   Command-Line Interface: Argparse
    -   Logging System: `logging`
    -   Data Import/Export: `csv`, `openpyxl`
    -   Report Generation: Jinja2 (for HTML)
    -   Web/API Extension (if needed): FastAPI

-   **Algorithm Usage Requirements**
    -   Use existing implementations of Logistic Regression and Neural Network algorithms from standard machine learning libraries.
    -   The system will not perform model training but will directly use algorithms for data analysis and scoring.
    -   Algorithm results must be interpretable and support parameter analysis.
    -   Support for performance comparison and result output for multiple algorithms.

-   **Code and Performance Requirements**
    -   Modular design with strict decoupling of the functional, service, and CLI layers; code must comply with PEP8 standards.
    -   Critical data processing and algorithm execution must support breakpoint continuation and interrupt recovery.
    -   Unit testing (pytest) with core process coverage ≥ 85%; interface parameters and exception flows must be validated.
    -   For a basic test dataset (1000 records), algorithm analysis and evaluation must complete in ≤ 30 seconds.

-  **Security and Compliance**
    -  Handling of sensitive fields (e.g., desensitized logs, optional field hiding on export).
    -  User authentication for Web/API interfaces via token-based authentication, following the principle of least privilege.
    -  Historical retention of key parameters and algorithm results for traceability and auditing.
