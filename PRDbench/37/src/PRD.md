Company Team Building Event Smart Lottery System PRD
## 1. Requirement Overview

This system is designed for company team building events (including annual parties, department dinners, and other scenarios), supporting multi-round, multi-rule lottery processes. The system needs to integrate list management, customizable prize configuration, and a complex lottery rule engine (including group avoidance, special rules, and fallback mechanisms). It implements lottery process control and result display through command-line interaction, ensuring lottery fairness and scenario adaptability.
## 2. Basic Functional Requirements
### 2.1 List Management Module
- Supports two list loading modes: loading built-in default team building list (containing name, department group information); uploading custom txt list (format: each line "Name,Department Group", e.g., "Zhang San,Technology Department").
- List verification function: automatically detects and prompts duplicate names, format error data; supports manually removing invalid data or terminating upload.
- Group information extraction: parses department groups from the list, supports viewing current valid group list and number of people in each group.
### 2.2 Prize Configuration Module
- Prize library management: supports preset prize library (e.g., "Third Prize - Movie Tickets", "Second Prize - Shopping Cards", "First Prize - 1 Day Annual Leave") and custom prize addition (input prize name, quantity, associated lottery person).
- Group avoidance rule configuration: sets "avoidance groups" for each prize (e.g., prize "Technology Department Exclusive Coupon" needs to avoid "Product Department" group), supports multiple group selection.
- Prize sorting function: adjusts lottery round sequence by inputting serial numbers in command line, defaults to arrangement by addition order.
### 2.3 Lottery Process Control
- Multi-round lottery execution: starts lottery according to configured sequence, each round displays current prize name, quantity, and rule description.
- Manual control function: supports inputting "pause" command to interrupt lottery during process, inputting "continue" to resume; inputting "terminate" to end current round and skip.
- Real-time progress display: dynamically displays "Currently drawing the Xth winner" during lottery, real-time refresh of winning results (format: "Congratulations [Name] ([Department]) for winning [Prize Name]").
### 2.4 Lottery Rule Engine
- Basic filtering logic: during each lottery round, automatically excludes previous winners and members of current prize's "avoidance groups".
- Special lottery person rules: when lottery person is specified as "Li Bin", only filters previous winners, does not apply "avoidance groups" rules.
- Fallback mechanism (Cheng Ru group protection): if neither of two consecutive lottery persons' (Chen Qixian, Jin Duo) results contain "Cheng Ru group" members, the next lottery person's (Ma Jiaqi) prize pool is forcibly limited to "Cheng Ru group" members (even if this group is the current prize's avoidance group).
- Anti-duplication verification: system maintains winner list in real time, ensuring the same person cannot win repeatedly (regardless of prize type).
### 2.5 Result Management and Display
- Real-time result display: after each lottery round, displays current round results in winning order; after all rounds completed, summarizes and displays complete winner list by "prize level from high to low" and "winning time order within same prize" (including name, department, prize name).
- Result export function: supports exporting complete winner list as txt file (path: current directory/awards_result_YYYYMMDD.txt), format as CSV (Name,Department,Prize Name,Winning Time).