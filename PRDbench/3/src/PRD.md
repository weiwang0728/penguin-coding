##### Intelligent Set-Meal Management System for Food & Beverage Merchants PRD

#### 1. Requirement Overview

This system is a command-line tool designed for food & beverage merchants to manage the full lifecycle of set-meals. It calculates the precise cost of meal ingredients—including processing losses—while taking nutritional balance standards and inventory optimization strategies into account. The system can automatically generate single- or double-serving set-meals that comply with pricing constraints and provide detailed cost breakdowns and profit evaluations. Key features include ingredient data management, dynamic cost calculation, intelligent set-meal combination, and visualized output of results. The tool aims to help merchants balance cost control with product appeal.

##### 2. Basic Functional Requirements

##### 2.1 Ingredient & Basic Cost Data Management
- Support manual entry or CSV import of ingredient information. Fields include: Ingredient ID, Name (e.g., "Wuchang Rice"), Category (Staple/Protein/Vegetable/Seasoning), Unit (kg/piece/serving), Purchase Unit Price (CNY/unit), Processing Loss Rate (%; e.g., 8% for leafy greens, 5% for meat, following food science "ingredient processing loss rate" standards), and Stock Quantity.
​- Maintain an additional cost items database, including packaging boxes (with preset unit prices by set-meal type: ¥1.5 for an individual combo and ¥2.8 for a dual-person combo), disposable utensils (optional, 0.8 RMB/set), etc. Support manual addition of custom additional cost items (e.g., sauce packet 0.5 RMB/serving).
- Provide ingredient data query functionality, supporting search by name or category, displaying the current unit price, loss rate, and remaining stock quantity (integer, unit consistent with the ingredient unit).

##### 2.2 Meal set-meal Cost Calculation Module
​- Support creating a new set-meal by importing an item list (containing item names, corresponding ingredients, and quantities). Ingredient quantities should allow up to two decimal places (e.g., "Rice 0.15 kg").
​- Automatically match ingredient unit prices and loss rates to calculate the actual cost per ingredient item: Item Cost = Quantity × Purchase Unit Price × (1 + Loss Rate / 100). Results are rounded to two decimal places.
Automatically summarize the total set-meal cost: Total Cost = Σ(Item Ingredient Costs) + Σ(Amounts of selected additional cost items). The system lists all available additional cost items (e.g., packaging boxes, disposable utensils) and allow users to choose whether to include them. Selected additional cost items are automatically added to the total cost.
​- Output a cost detail report, including: Combo Name, Ingredient List (Name/Quantity/Unit Price/Loss Rate/Item Cost), Additional Cost List (Name/Amount), Total Cost.

##### 2.3 Intelligent Set-meal Generation Module
​- Support selection of set-meal type (single-serving/double-serving) and configuration of basic parameters: single-serving price 28–40 CNY, double-serving price 40–60 CNY; discount rate (e.g., 0.9, allowing decimal input from 0.1 to 1.0, default 1.0); inventory priority (High/Medium/Low, where High prioritizes ingredients with stock >50 units).
​- Apply the core recommendations from the 2022 Chinese Dietary Guidelines to define nutritional constraints: a single-serving meal must include at least one staple food (≥0.1 kg), one protein ingredient (≥0.08 kg), and one vegetable (≥0.1 kg); for a double-serving meal, staples ≥0.2 kg, protein ≥0.15 kg, and vegetables ≥0.2 kg.
​- Automatically generate set-meals based on cost and nutritional constraints: iterate through the ingredient database to select ingredients that meet the nutritional categories, sort them by inventory priority, and create 3–5 candidate set-meals (each including staple food + protein + vegetables; multiple ingredients per category are allowed, and one seasoning ingredient may be included).
​- Calculate the recommended selling price for candidate set-meals: Recommended Price = Total Cost × (1 + Target Profit Margin), with a default target profit margin of 30% (adjustable manually between 20%–50%). The final price should be rounded to the nearest integer and comply with the set-meal type pricing constraints (e.g., if a single-serving meal calculates to 27.6 CNY, it is automatically rounded up to 28 CNY).
​- Additional cost items are not considered during combo generation.

##### 2.4 Combo Evaluation & Result Output
- Provide an independent set-meal evaluation module, allowing users to re-evaluate and compare saved combos.
- Support viewing detailed information for saved set-meals, including cost breakdown, nutrition score, profit margin, and other key metrics.
- Provide a combo comparison function to display the evaluation results of multiple set-meals simultaneously, helping merchants make optimal choices.
- Support export and print of set-meal evaluation results.
- Evaluate generated candidate combos on two dimensions: Profit Indicator (Profit Margin = (Selling Price × Discount - Total Cost) / Total Cost × 100%) and Nutrition Score (based on Dietary Guidelines: 5 points for ≥3 ingredient types, plus 1 point for each additional type, with a maximum of 8 points).
- Nutrition score calculation: base score is 5 (for ≥3 ingredient types); add 1 point for each additional type, up to 8 points total.
​- Sort candidate combos in descending order by profit margin. Display sorted results: Combo Number, Included Item List (Ingredient Name + Quantity, merge identical ingredients), Total Cost, Suggested Selling Price, Discounted Price, Profit Margin, Nutrition Score.
​- Allow users to select and save a set-meal. The saved data should include: Set-Meal ID, Name (automatically generated as ‘[Type] Nutrition Set-Meal X’, where X is the sequence number), Product List, Cost Breakdown, Selling Price, Discount, and Creation Timestamp.
​- Command-line output must use formatted tables (using Python's tabulate library), including borders and headers, with aligned data.

##### 2.5 Interaction & Data Validation
​- Validate all user inputs for correctness (e.g., Loss Rate 0-30%, Quantity > 0, Discount 0.1-1.0). Display Chinese prompts for invalid input (e.g., "Loss rate must be a number between 0 and 30") and allow re-entry.
- Support exiting the current operation at any time (enter "q" to return to the previous menu). The system adopts a three-level menu structure: Main Menu (Data Management / Cost Calculation / Combo Generation / Combo Evaluation / Exit) → Function Menu → Operation Menu.
​- Validate CSV format during import (field matching, correct data types). Display specific error line numbers and reasons upon import failure.