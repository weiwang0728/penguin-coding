### Retail Brand High-Value Store Operations Analytics for Retail Brands PRD

#### 1. Requirements Overview

This project aims to develop a Python-based command-line tool for comprehensive operational analytics of high-value retail brand stores.
 The tool shall extract and consolidate core store information from multi-source simulated datasets, perform data cleansing (including deduplication) and feature-engineering transformations (with RFM customer-segmentation model applied) 
and time-series decomposition, deliver output in structured tabular format with drill-down detailed data access links. The end-to-end workflow shall encompass data extraction, cleansing, analysis, and visualization to enable granular management of high-value stores (defined as a_value_type='High Value') for operational teams.

#### 2. Basic Functional Requirements

##### 2.1 Multi-Source Data Extraction and Integration

- Support configuration of simulated data sources, including the store dimension table (store primary key `store_key`, store ID `store_id`, brand information `brand_name`, organizational structure `org_path`, private domain type `private_domain_type`), sales details table (transaction date `trans_date`, store primary key `store_key`, transaction amount `amount`, business group `biz_id`), and warehouse information table (business group `biz_id`, warehouse code `git_repo`).

- Implement multi-table join logic: link the store dimension table and the sales detail table via `store_key`, link the sales detail table with the warehouse information table via `biz_id`.

- Enable conditional filtering: retain only stores with  `a_value_type='High Value'`, and the private domain type `private_domain_type` values 'Headquarters Direct' or 'Regional Focus'.

##### 2.2 Data Cleansing and Deduplication

- Missing Value Handling: Fill empty brand_name in store dimension table with default value 'Unknown Brand', and remove records where amount is NULL in sales detail table.

- Outlier filtering: Identify and remove abnormal transaction data from the sales detail table where `amount` is ≤0 or `trans_date` is earlier than the store opening date (simulated field `opening_date`).

- Deduplication: Perform data deduplication using a composite key (`biz_id` + `trans_date` + `store_id`), retaining the latest transaction record (selecting the first row sorted by `trans_date` in descending order).

##### 2.3 Feature Engineering and Metrics Calculation

- RFM metrics calculation: Using sales detail table data, calculate the store's recency (Recency, unit: days), transaction frequency (Frequency, unit: average monthly transactions), and monetary value (Monetary, unit: average monthly transaction amount).

- Time series decomposition: Apply STL (Seasonal and Trend decomposition using Loess) decomposition to the store's average monthly transaction amount, extracting trend, seasonal, and residual components as supplementary features for high-value attributes.

- High-value attribute label generation: Combine RFM metrics and STL trend components to generate label fields `value_tag` (e.g., "Growth High Value," "Stable High Value," "Potential High Value").

##### 2.4 RFM Customer Segmentation Analysis

- RFM Segmentation Implementation: Classify customers into high/medium/low tiers for each RFM dimension (Recency, Frequency, Monetary) based on configurable industry thresholds. Generate 8 store segment types (e.g., "High-Value Customer", "‌Important Retention Customer", "Important Development Customer‌") through combinatorial analysis.

- Segmentation result statistics: Calculate the store count proportion and transaction amount contribution proportion for each segment type. Enable filtering store data by segment type.

##### 2.5 Command-Line Result Display and Interaction

- Tabular Data Display: Rows organized by business group (`biz_id`) and transaction date (`trans_date`), with columns including store ID, brand, organizational structure, private domain type, RFM segmentation type, average monthly transaction amount, and `value_tag`.

- Data Detail Link Generation: Add a "Data Detail Link" column at the table's end, formatted as "repo://{git_repo}/detail?store_id={store_id}&date={trans_date}". Links are copyable for accessing simulated data detail pages.

- Interactive Query: Support filtering by segmentation type (e.g., "High-Value Customer") or date ranges, and real-time updates of filtered results in table format.