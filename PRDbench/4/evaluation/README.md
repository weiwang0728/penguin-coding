# Satellite StoreBusiness Planning and Forecasting System

This system is a business tool designed for satellite stores of chain restaurant companies, It integrates single-store forecasting, cost structure analysis, and profit calculation, to provide data support for store operation decisions.

## FunctionSpecialness

- **project management**: SupportSupportNewBuild、Load、Save Project, to manage planning for different stores more flexibly.
- **Interactive Parameter Input**: PassCommandLineInterfaceallow users to input allrequired business parameters.
- **CSV Batch Import**: SupportSupportbatch import through a predefined CSV templateprojectData.
- **Single-store Forecasting Engine**: Forecast single-store performance based on location, category mix, and pricing factors.
- **Cost and Profit Analysis**: Automatically split fixed and variable costs, perform CVP analysis and contribution margin analysis.
- **Sensitivity Analysis**: Automatically analyze changes in key variables(such as costs and average ticket price)and their impact on profit.
- **PDFReportExport**: OneKeyGenerateContainsCoreCoreIndicatorMark、analysis charts and optimization recommendations in a feasibility report.

## Environment Configuration

1.  **Clone or downloadproject**:
    ```bash
    git clone <your-repo-url>
    cd StoreTool
    ```

2.  **Create and activate a Python virtual environment**:
    RecommendationUseUse Python 3.9 orUpdateHighEdition��.

    in Windows on:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

    in macOS / Linux on:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    After activating the virtual environment, run the following command to install all required libraries.projectrequired model files will also be downloaded automatically at startup.
    ```bash
    pip install -r src/requirements.txt
    ```

## How to Use

1.  **StartProgram**:
    inproject root directoryunder, Run the following command to start the application: 
    ```bash
    python src/main.py
    ```

2.  **Main Menu**:
    ProgramStartafter, you will see the main menu, you can choose: 
    - **Create New Project**: start planning a new store.
    - **Load Project**: load a project from a previously saved `.json` file.
    - **Import Project from CSV**: batch create one or more projects based on the `src/data/template.csv` template.
    - **Exit**: CloseProgram.

3.  **project operations**:
    After loading a project, you can: 
    - **Edit Parameters**: modify each store parameter by category, such asincluding basic information and cost structure.
    - **ExecuteAnalysis**: run the forecasting and analysis engine, view core metrics and sensitivity analysis results.
    - **Save Project**: save the current project configuration to a `.json` file.
    - **ExportPDFReport**: in `evaluation` generate a complete PDF feasibility analysis report in the `evaluation` folder.

## CSV Template Description

you canin `src/data/template.csv` find the data import template.please prepare your data according to this file structure and format.

- `project_name`: Project Name
- `city`: City
- `area`: Area
- `business_circle_type`: Business Circle Type (e.g., Core Business District, Transit-Level Business District, Community Area)
- `longitude`, `latitude`: Longitude and Latitude
- `category1_name`, `category2_name`, `category3_name`: Category Names
- `category1_ratio`, `category2_ratio`, `category3_ratio`: Revenue Share for Each Category (the three values should sum to 1.0)
- `avg_item_price`: Average Ticket Price
- `ingredient_cost_ratio`: Ingredient cost as a share of selling price
- `packaging_cost_ratio`: Packaging cost as a share of selling price
- `monthly_rent`: Monthly Rent
- `monthly_labor_cost`: Monthly Labor Cost (core staff operations)
- `monthly_marketing_cost`: Monthly Marketing Cost
- `commission_rate`: Platform Commission Rate