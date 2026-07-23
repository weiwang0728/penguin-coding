# Cheng Qingdao District 1 Lottery System PRD

## 1. Overview

The Cheng Qingdao District 1 Lottery System is a command-line tool designed for internal regional activities, supporting multi-prize draws based on an employee list. The system implements functionalities for list import and management, custom lottery rule configuration, weighted random sampling draws, result visualization, and fairness verification, ensuring the lottery process is transparent, traceable, and statistically random.

## 2. Core Functional Requirements

### 2.1 Employee List Management Module

- Supports importing employee lists in CSV/text format. The file must include name, employee ID, participation points (integer), and length of employment (months). If any field is missing or the format is incorrect, a Chinese error message is displayed and the import is terminated.
- After import, the system displays summary statistics: total number of people, department-wise headcount ratios (department is parsed from the first 2 digits of the employee ID), and participation points distribution (maximum/minimum/average values).
- Provides a preview function to display the top 10 records sorted by length of employment (ascending/descending), and supports precise employee query by employee ID.

### 2.2 Lottery Rule Configuration Module

- Supports adding multiple prizes (maximum of 5). Each prize must be configured with: prize name (must be unique), number of items (positive integer), weight calculation rule (choose one: uniform weighting/points-based weighting/tenure-based weighting), and whether repeated wins are allowed (boolean).
- Weighting rule explanation: For uniform weighting, every employee has an equal chance; for points weighting, the probability is proportional to participation points; for tenure weighting, the probability is proportional to length of employment (weight formula: individual weight = individual metric value / total metric value).
- After configuration, a rule summary is displayed, including the prize list, total number of prizes, and whether there is a risk of repeated winners (reminds the user if so); after user confirmation, the system enters the draw process.

### 2.3 Lottery Execution Module

- Draws are performed in prize order (users can adjust prize order), using the A-Res algorithm (Algorithm A-Res) for weighted random sampling, with results calculated in real time.
- If repeated wins are not allowed, winners are automatically removed from the candidate pool for subsequent prizes. If there are not enough candidates left for a prize, the draw for that prize is terminated and a prompt is given.
- During the draw, dynamic progress is displayed (e.g., "Drawing First Prize (1/3)..."). If a single draw takes more than 3 seconds, a "Drawing, please wait..." message is shown.

### 2.4 Result Presentation and Verification Module

- Provides an independent function to view draw results. Winners are grouped by prize, with different terminal text colors for each prize (First Prize: red, Second Prize: blue, Third Prize: green, others: default color). Each group includes index, name, employee ID, department, points, and length of employment.
- Automatically generates a fairness report for the lottery, including: the mean participation points of prize winners compared to the overall mean (Z-test, showing p-value), and department-wise winner ratios compared to department proportions (Chi-square test, showing χ² value and p-value). If p > 0.05, the result is marked as "Statistically consistent with randomness".
- Supports saving draw results and fairness reports as TXT files, file name formatted as "LotteryResults_YYYYMMDD_HHMMSS.txt".