# Intelligent Analysis and Optimization System for the Catering Supply Chain

This project is a command-line tool based on Python, designed to provide catering businesses with a lightweight and efficient solution for full lifecycle management and analysis of dishes. By analyzing dish, ingredient, and sales data, the system helps users gain insight into cost structures, optimize the supply chain, and make more informed business decisions.

## Features

- **Dish Data Management**: Supports CRUD operations (create, read, update, delete) on dish information, as well as batch import via CSV.
- **Cost and Profit Analysis**: Automatically calculates ingredient cost, cost ratio, and gross profit margin for each dish.
- **Allergen Intelligent Detection**: Automatically identifies and marks dishes containing common allergens based on the ingredient list.
- **Sales Trend Insights**: Provides multi-dimensional statistics of dish sales and turnover by day, week, and month to reveal sales trends.
- **Dish Similarity Matching**: Uses fuzzy matching algorithms to identify dishes with similar names and perform aggregated analysis.
- **Modern CLI Experience**: Built on top of the `rich` and `questionary` libraries, provides a menu-driven, user-friendly, and visually appealing command-line interface.

## Environment Setup and Installation

To run this system, you need a Python 3.7+ environment. It is recommended to use a virtual environment to avoid package version conflicts.

### 1. Clone or Download the Project

Extract or clone the project files to your local machine.

### 2. Create and Activate a Virtual Environment

Open your command line or terminal, navigate to the project root directory, and execute the following commands:

```bash
# Create a virtual environment named .venv
python -m venv .venv

# Activate the virtual environment (Windows)
.venv\Scripts\activate

# Activate the virtual environment (macOS / Linux)
# source .venv/bin/activate
```

After activation, you should see `(.venv)` in your command prompt.

### 3. Install Dependencies

Within the activated virtual environment, use `pip` to install all required third-party libraries:

```bash
pip install -r requirements.txt
```

This will automatically install all core libraries, such as `pandas`, `questionary`, `rich`, `thefuzz`, etc.

## How to Run

Make sure you have set up the environment and installed dependencies as described above.

1.  **Prepare Data**: When the system starts, it loads CSV files from the `data/` directory. Please ensure the following files exist and are correctly formatted:
    *   `dishes.csv`: Basic dish information
    *   `ingredients.csv`: Composition of dish ingredients
    *   `orders.csv`: Historical order data
    *   `approximate_dishes.csv`: (Optional) List of approximate/similar dishes for similarity analysis

    The project includes a set of sample data which you can use directly or modify as needed.

2.  **Start the Program**: In the project root directory, run the command:

    ```bash
    python main.py
    ```

3.  **Begin Using**: After the program starts, you will see an interactive main menu. Use the arrow keys to navigate the menu and press Enter to confirm your selection.

## Usage Guide

The system is mainly divided into four functional modules, which you can access from the main menu.

### Module 1: Dish Data Management

- **Add New Dish**: Follow the prompts to enter dish name, category, price, and cooking time.
- **Delete/Modify Dishes**: First, a list of all current dishes will be shown. You will need to enter the ID of the dish you want to operate on. A secondary confirmation will be required for deletions to avoid mistakes.
- **Query Dishes**: You can perform fuzzy searches by dish name or category. The system will return all matching results in a tabular format.
- **Batch Import Dishes**: Provide the path to a CSV file containing dishes. The CSV must include `name`, `category`, `price`, and `cooking_time` columns. The program will handle and display the import progress automatically.

### Module 2: Ingredient and Cost Analysis

- **Analyze Cost of Single Dish**: After entering a dish ID, the system provides a detailed cost report, including total cost, gross profit margin, and cost proportion of each ingredient.
- **Identify Dishes With Allergens**: The system will automatically scan all dish ingredients and list all detected dishes containing common allergens (e.g., nuts, seafood), along with the allergen(s) present.

### Module 3: Sales Data Analysis

- Select the time dimension you wish to analyze (day/week/month), and the system will immediately generate a sales trend report, clearly showing total sales and total revenue for each time period.

### Module 4: Dish Similarity Matching

- This feature helps discover and analyze “similar dishes”. For example, "Kung Pao Chicken" and "Kung Pao Chicken (New)" may refer to the same dish.
- You need to provide a source file path (default: `data/approximate_dishes.csv`) which contains a list of similar names.
- The system matches these names with the main dish library, groups the matched dishes accordingly, then calculates each group’s total order volume, weighted average price, and sales volatility coefficient—assisting you in SKU optimization.

## Running Tests

This project uses `pytest` for unit testing. If you want to verify code correctness, you can run the test suite.

In the project root directory, execute:

```bash
pytest
```

The test scripts will automatically discover and run all test cases in the `tests/` directory.
