## Golf Tourist Consumer Behavior Survey and Data Analysis System PRD (Product Requirements Document)

---

### 1. Requirement Overview

1. This system is a quantitative research and multidimensional consumer behavior analysis tool designed for golf tourism practitioners and researchers. It integrates "customizable survey questionnaires, data collection, statistical analysis, user persona generation, and analysis report export" into one platform, with a focus on behavioral patterns and market segmentation of the "golf tourist" demographic.
2. The product supports survey questionnaire template design, onsite/online data collection, data validation, and automated analysis, outputting structured and actionable user and market insights using SPSS statistical methods.
3. Core application scenarios of the system:
    - Automated survey questionnaire generation and data collection
    - Multidimensional data analysis of consumer behavior (descriptive statistics, factor analysis, cluster analysis)
    - Segmentation and persona output for golf tourists (demographics, tourist attitudes, motivations, current consumption, destination factors, etc.)
    - Visualization of analysis results and report export, providing references for product optimization and market decisions

---

### 2. Functional Requirements

#### 2.1 Questionnaire Design and Data Collection

- **Questionnaire Template Management**
    - Provides customizable questionnaire templates, supporting 5 core modules:  
      *Tourism perception & attitude, tourism motivation, current consumption status, destination selection influencing factors, personal basic information*
    - Each module can add questions (supported types: single-choice, multiple-choice, scale/rating, open text)
    - Supports importing expert question banks (CSV/JSON format) and local template saving/export

- **Online Data Collection**
    - User side performs automatic validation of mandatory fields, format, and option range
    - Automatically records submission time, location/practice venue, and collector (investigator) identification during data collection

- **Data Management and Cleaning**
    - Collected data can be exported as standard CSV format (UTF-8, fixed field order)
    - Built-in data integrity checks: out-of-range value inspection
    - Supports data desensitization (automatic masking of personal privacy information):
        - Name desensitization: retain only the first character of the surname, mask the rest (e.g., "Zhang San" -> "Zhang*")
        - Phone number desensitization: retain the first 3 and last 4 digits, mask the middle digits (e.g., "13812345678" -> "138****5678")
        - Non-privacy information (such as gender, age group, etc.) remains unchanged
    - Data is traceable (with metadata labels of questionnaire template, collection location, and collection date)

#### 2.2 Consumer Behavior Analysis Engine

- **Descriptive Statistical Analysis**
    - Automatically calculate mean, standard deviation, proportion, etc. for demographic characteristics (gender/age/income/golf experience), tourism consumption frequency, consumption amount, and other fields
    - Outputs results as tables and bar/pie chart visualizations

- **Factor Analysis Function**
    - Supports performing exploratory factor analysis (PCA/principal component analysis, factor loading matrix output) on scale questions (such as tourism motivation and attitude)
    - Outputs each respondent’s score for each factor

- **Cluster Analysis Feature**
    - Supports hierarchical cluster analysis
    - Clustering features can be selected (combinations of demographic attributes, consumption characteristics, attitude factors, etc.)
    - Automatically outputs characteristic comparison tables for each cluster and description of key variables

- **User Segmentation and Persona Generation**
    - Groups respondents by cluster/factor scores to automatically generate "user persona" briefs (aggregated demographic features, dominant motivations, consumption tendencies, destination preferences, etc.)
    - Persona output as structured JSON and customizable Chinese descriptions (for use in report PPTs, etc.)

#### 2.3 Analysis Results Visualization and Report Export

- **Data Visualization**
    - Supports automated generation of multiple chart types (bar charts, pie charts)

- **Report Generation and Export**
    - Automatically generates standard survey analysis reports including: abstract, sample distribution, key analysis conclusions, user persona tables, visual charts
    - Supports export in Word and Markdown formats
    - Exported reports include analysis model/parameter description, sample description, etc.

- **Permissions and Log Management**
    - Supports multi-role authorization (Regular users: questionnaire design/data entry; Analysts: analysis and export; Administrators: template management/system settings)
    - All operations have log records

---

### 3. Technical Requirements

- **Programming Language**
    - Python 3.10+

- **Core Dependencies and Tech Stack**
    - Backend business and data analysis:
        - Data processing and analysis: Pandas, NumPy, scipy
        - Statistical modeling: scikit-learn (factor analysis, clustering), statsmodels (correlation, hypothesis testing)
        - Natural language processing (optional): Jieba (word segmentation, automated persona description generation)
    - Questionnaire design and data collection:
        - Web-based collection: Flask/FastAPI + Bootstrap/Vue.js (QR code/page interaction)
        - Command line collection/management: Typer + rich (interactive prompts and styled output)
        - Data persistence: SQLAlchemy + SQLite
    - Visualization and report generation:
        - Chart visualization: Matplotlib, Seaborn
        - Cluster case visualization: Plotly (dynamic interaction optional)
        - Report export: python-docx, pdfkit, markdown2
    - System management and logs:
        - Logging system: loguru
        - Permission management/data encryption: Passlib (password encryption), PyCryptodome
        - Data validation: Pydantic

- **Data Security and Compliance**
    - Supports privacy desensitization by field; questionnaire and data storage must comply with GDPR and the "Personal Information Protection Law"
    - Full-process encrypted storage and transmission for data, important actions have log tracking
    - Provides system data backup and one-click recovery mechanisms

- **Development and Quality Constraints**
    - Code structure must be modular, supporting plugin-style questionnaire type extension
    - Core functions must have unit tests (pytest), test coverage ≥80%
    - Production deployment is recommended to support Docker containerization
    - User interfaces (CLI/WEB) should be user-friendly, with input format explanations and exception feedback for interaction steps

- **Performance Requirements**
    - Supports analysis of ≥5000 questionnaires per batch, average time for complete batch analysis ≤30s (8-core/16GB RAM environment)
    - System supports concurrent data sync from multiple investigation sites; Web collection peak concurrency ≥100 users/minute without data loss

---