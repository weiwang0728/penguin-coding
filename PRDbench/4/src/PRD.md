### Satellite Store Business Planning and Forecasting System PRD

#### 1. Requirement Overview

This system is an advanced business management tool tailored for chain restaurant enterprises, designed to integrate predictive analytics for store order volumes, cost structure analysis, and profit forecasting. It provides actionable insights to support strategic decision-making for store operations. The system is built on a command-line interface, allowing users to input essential parameters, adjust key operational variables, and generate comprehensive store performance evaluation reports. The package also includes relevant README documentation and unit tests for implementation.

#### 2. Functional Requirements

#### 2.1 Data Input and Parameter Configuration

- Support creating, loading, and saving project files in JSON format; project files are stored under the `src/data/projects/` directory.

- Input modules include essential business data such as: geographic details (city, region, business district type), physical location (latitude and longitude coordinates), category composition (three-level category proportions), and key cost parameters (ingredient, packaging, labor, rent, etc.).

- The system validates input parameters with range checks and offers logical consistency prompts, alongside industry-standard benchmark values for critical metrics.

- Supports bulk data import functionality (CSV format), using `src/data/template.csv` as the import template. Relevant key metrics are automatically extracted during import. The template file includes a full column definition and example data for user reference.

#### 2.2 Order Volume Forecasting Engine

- The forecasting model is built on a multi-step conversion chain: exposure prediction (based on location factors) → in-store conversion rate (based on category match) → order conversion rate (based on price sensitivity), forming a robust three-tier prediction model.
- Supports setting a platform subsidy rate parameter (default 5%) to simulate the impact of platform subsidies on customer unit price, following a price elasticity coefficient model (default 1.5).

- The system employs a time series decomposition algorithm (STL) to generate order volume fluctuation curves for different time periods, including weekdays, weekends, and holidays.

- Support a flexible category influence factor system (default 1.0), enabling users to simulate the impact of changes in category structure on overall order volumes.

#### 2.3 Cost Structure Analysis

- Automatically distinguishes between fixed and variable costs, including key expense categories such as rent, equipment depreciation, core personnel salaries, ingredients, packaging, commissions, and promotional expenses.
- Includes a contribution margin analysis tool to calculate the unit contribution of individual products and categories, providing insights into profitability and cost efficiency.
- Supports tiered cost structures (e.g., ingredient discounts for bulk purchasing, delivery subsidies for achieving certain thresholds).
- Generates break-even analysis reports, visually depicting the breakeven points under different order volume scenarios.
- The system provides actionable insights for operational optimization, automatically suggesting 3-5 key areas for improvement based on data-driven analysis.

#### 2.4 Result Output and Reporting

- Displays key performance indicators such as average daily order volume, customer unit price, gross profit margin, net profit, and payback period.

- Generates dynamic break-even analysis reports, including sensitivity rankings (by degree of impact), and lists at least three key factors affecting profitability.

- Supports exporting feasibility analysis reports in Markdown format, including key data visualizations and break-even (cost-volume-profit) analysis charts.