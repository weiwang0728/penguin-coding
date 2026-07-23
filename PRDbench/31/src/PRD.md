## Intelligent Analysis System for College Students' Self-Control and Attention Stability PRD (Product Requirements Document)

---

### 1. Requirement Overview

1. This system is designed for psychological research and application scenarios, supporting the digitized and intelligent collection of structured data, scale management, feature analysis, and multi-path relationship visualization, specifically regarding college students' study self-control, emotional stability, and study attention stability.  
2. Supports custom scale creation, reliability and validity analysis, group difference exploration, predictive path analysis, and multidimensional results report export, suitable for education/psychology researchers, assessment agencies, and data analysts.  
3. Compatible with both command-line and Web interfaces (optional module). The core workflow includes: scale development and validation - large-sample survey data entry - psychological feature and relationship modeling - in-depth path analysis and visualization - research conclusion report generation.  
4. Enables team project collaboration and data access management, ensuring compliant and controlled management of scale resources and research data.

---

### 2. Functional Requirements

#### 2.1 Scale Customization and Reliability & Validity Analysis Module

- **Scale Design Management**  
  - Supports creation, editing, import/export (CSV/JSON format) of custom psychological scales (e.g., College Student Study Attention Stability Scale, Emotional Stability Scale, Self-Control Scale).
  - Flexible scale structure definition: content, items, dimensional attribution, scoring method (Likert scale), reverse items.
  - Supports scale version management and batch publishing.

- **Item Analysis and Exploratory Factor Analysis (EFA)**  
  - Automatically performs item distribution, mean/variance, extreme grouping, correlation, and other item analyses.
  - Implements KMO and Bartlett's Sphericity Test, supports EFA based on correlation matrix (supports principal component analysis, maximum variance rotation).
  - Outputs factor loading matrix, factor attribution for each item, and proportion of variance explained results tables.
  - The KMO value should range from 0 to 1, and the Bartlett's test must output a significance p-value.

- **Reliability and Validity Testing**  
  - Supports calculation of Cronbach's alpha coefficient, test-retest reliability, etc.
  - Integrates homogeneity, discrimination, validity of factor structure, and item removal suggestions.
  - Visualizes scale reliability and validity (bar chart/form).

---

#### 2.2 Subject Data Collection and Data Management

- **Data Collection**  
  - Supports batch import of subject information (anonymized/name + student ID), entry of multiple scale responses (batch CSV import via command-line + optional web entry interface).
  - Supports detection and correction suggestions for skip/missing item data anomalies.
  - Automatically divides datasets by group labels such as grade, gender, and major.

- **Data Version and Permission Management**  
  - Implements version control for batch/multi-center sampling of subjects.
  - Supports hierarchical project member permissions (owner/analyst/entry clerk/visitor), allowing controlled and visible access to data.

---

#### 2.3 Feature Grouping and Difference Analysis

- **Basic Feature Analysis**  
  - One-click generation of descriptive statistics (mean, standard deviation, quantile, skewness, kurtosis, and at least five such indicators) and grouped bar/box plots.
  - Descriptive statistical charts should be generated as PNG files, and the images should clearly reflect the characteristics of the data distribution.
  - Supports group comparisons (independent samples t-test, ANOVA), customizable grouping: gender, grade, major.
  - t-tests should output the means of the two groups, t-value, degrees of freedom, and p-value.
  - ANOVA should output the F-value and p-value.
  - Automatically outputs statistical significance (p-value), effect size, and visualization of inter-group mean differences.

- **Trend and Cross-sectional Analysis**  
  - Grade-related trend analysis (regression slope, significance), with output of trend fitting diagrams.

---

#### 2.4 Advanced Relationship and Path Analysis

- **Index Correlation and Predictive Analysis**  
  - Supports automatic generation and visualization (heatmap) of multivariate Pearson/Spearman correlation matrices.
  - Supports custom regression models (linear/multiple/Logistic) to analyze the predictive effects of "Reading Attention/Attention Control/Explicit Attention/Attention Concentration" on self-control, with standardized coefficients and p-values output.

- **Hierarchical Prediction and Path Structure Modeling (Mediation Analysis)**  
  - Implements structural equation modeling (SEM/path analysis), allows customization of model structures (e.g., Emotional Stability -> Attention Factors -> Self-Control).
  - Visualizes path coefficient diagrams (automatic path diagram layout), direct/indirect effects, supports bootstrap confidence interval testing.
  - Outputs model fit indices (CFI, TLI, RMSEA, SRMR).

---

#### 2.5 Report and Visualization Export

- **Intelligent Report Generation**  
  - One-click export of analysis summary reports including sample description, difference tests, main effects and path coefficient tables, significance interpretation (supports bilingual Chinese/English).
  - Supports custom report templates and batch generation.

- **Chart and Data Export**  
  - Supports export of all analysis charts as high-definition PNG, PDF, and SVG formats; raw/analysis data supports CSV export.
  - Customizable chart style, resolution, and color themes.

---

### 3. Technical Requirements

- **Programming Language: Python 3.9+**

- **Core Technology Stack**  
  - Scale structure and data ORM: SQLAlchemy + SQLite/PostgreSQL  
  - Scale and data parsing/management: Pandas, Pydantic (structure validation), Marshmallow (optional)
  - Statistical analysis and modeling: statsmodels, scikit-learn, pingouin (psychological statistics), semopy or lavaan (SEM/path analysis)
  - Visualization: Matplotlib, Seaborn, Plotly (interactive), networkx (path diagrams)
  - Reliability & validity analysis: pingouin, factor_analyzer
  - Command-line interaction: Typer (CLI interface), PromptToolkit (enhanced interactive experience)
  - Permission and log management: loguru (logging), bcrypt (password encryption), FastAPI (if Web input is used)
  - Unit testing and code standards: pytest, black, mypy

- **Code Standards and Security**  
  - Adopts layered modular design; decouples scale management, data management, analysis modeling, and visualization
  - Complete exception handling; all key operations automatically recorded in audit logs
  - Data de-identification, identity authentication, fine-grained permission management; supports encrypted data storage
  - Supports performance optimization for batch data processing and scalable large-sample concurrent analysis

- **Performance and Compatibility**  
  - Supports single batch analysis of 500+ samples, common statistical operations <=3s response time, path analysis <=10s
  - Supports local deployment and cloud extension, compatible with multiple platforms (Win/Mac/Linux)

- **Other Requirements**  
  - Supports multi-language configuration (Simplified Chinese/English)
  - Provides detailed API documentation, data dictionary, and sample datasets
  - Provides >=80% unit test coverage, with automated test scripts for all main processes
  - Optional Web input/results viewing module based on FastAPI + Vue3 (if needed)

---