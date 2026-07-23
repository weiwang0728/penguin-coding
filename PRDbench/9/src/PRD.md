# Business Travel Intelligent Planning System PRD

## 1. Requirements Overview

This project aims to develop a command-line interactive intelligent business travel planning system that integrates transportation data and itinerary management functions. The system must support users input of multi-city business travel requirements, generate time-optimal/cost-optimal/balanced transportation plans through an improved weighted directed graph algorithm, provide priority sorting suggestions based on decision fatigue theory, and possess itinerary conflict detection and multi-format export capabilities, offering comprehensive travel decision support for business professionals.

## 2. Basic Functional Requirements

### 2.1 Itinerary Information Management Module

- Supports user input for departure city, multiple destination cities, and stay duration (accurate to the hour, supports both integers and decimals, e.g., 24 or 2.5 hours)
- Supports adding time window constraints (e.g., "Must arrive in Shanghai before 14:00 for a meeting", requiring specification of earliest/latest arrival time)
- Provides itinerary template saving functionality, allowing storage of frequently used business travel routes (e.g., "Beijing-Tianjin-Hebei Three-Day Exhibition Tour")
- Supports saving and loading of created itineraries

### 2.2 Multi-Objective Transportation Plan Generation Module

- Integrates simulated high-speed rail, flight, and normal train data (data supports automatic default generation):
  - High-speed rail: 5-7 services per route, departure time 6:00-20:00, average speed 250km/h, ticket price 0.4-0.6 RMB/km
  - Flight: 3-5 flights per route, departure time 7:00-21:00, average speed 800km/h (including 60 minutes for takeoff/landing), ticket price 0.8-1.5 RMB/km
  - Normal trains (for distances >300km): 1-2 services, mostly departing at night or early morning, average speed 120km/h, ticket price 0.2-0.3 RMB/km
  - All transportation data includes: train/flight number, departure and arrival time, price, seat type, reliability score, comfort score
- Must provide city data, including 50+ major cities (covering top-tier, municipalities, provincial capitals, and important prefecture-level cities) with name, code, and latitude/longitude information

- Implements an improved Dijkstra algorithm to calculate optimal paths between cities, with weighting factors including:
  - Base weight: travel duration (unit: minutes)
  - Penalty terms: number of transfers × 60 minutes + departures before 6:00 × 120 minutes
  - Adjustment factors: user preference coefficients (time sensitivity/cost sensitivity)

- Provides three optimization objective plans:
  - Time-optimal: minimizes total travel time (including transfer waiting)
  - Cost-optimal: minimizes total transportation expenditure (applying price elasticity coefficients)
  - Balanced plan: calculates time-cost comprehensive score using the TOPSIS method

- Supports setting maximum number of transfers (1-3 times) and transportation preference (high-speed rail preferred/flight preferred/no preference)

### 2.3 Intelligent Itinerary Conflict Detection Module

- Implements an itinerary time conflict detection algorithm using Allen's interval algebra, identifying the following conflict types:
  - Hard conflicts: insufficient transfer time (transfer between high-speed rail and flight or vice versa requires ≥90 minutes; transfer between same type requires ≥60 minutes)
  - Soft conflicts: rest time between consecutive itinerary segments is less than 4 hours (per fatigued driving safety standards)

- Provides visual prompts for identified conflicts (such as timeline overlap markers) and explicitly labels the type of conflict (hard or soft)
- Automatically generates conflict resolution solutions:
  - Suggestions for time adjustments (e.g., "Advance Beijing-Shanghai high-speed rail to G107")
  - Suggestions for itinerary splitting (e.g., "Add an overnight stay in Nanjing")

### 2.4 Decision Support Recommendation Module

- Build a decision evaluation model based on Prospect Theory, calculating for each plan:
  - Value function: v(x) = x^α (for gains), or -λ(-x)^β (for losses)
  - Weight function: π(p) = p^γ / [p^γ + (1-p)^γ]^(1/γ)

- Implement a multi-attribute decision matrix, providing quantified scores or percentage values for the following metrics:
  - Time efficiency (30% weight)
  - Economic cost (25% weight)
  - Comfort index (20% weight, based on seat space / punctuality rate)
  - Reliability score (15% weight, based on historical delay data)
  - Transfer convenience (10% weight, based on transfer distance within stations)

- Clearly prioritize all plans according to the comprehensive score.

### 2.5 Itinerary Export and Sharing Module

- Supports generating multiple itinerary report formats:
  - Markdown format (including itinerary timeline and transportation details)

- Implements itinerary summary generation function, automatically extracting key information:
  - Total travel distance (calculated based on geographic distance using Haversine formula)
  - Total duration/total cost statistics
  - Key node reminders (e.g., "Tomorrow 08:30 Beijing South Station G109")

### 2.6 Command Line Interaction System

- Implements a multi-level command menu system:
  - Main menu: provides at least 6 options (create new itinerary, load saved itinerary, use itinerary template, view current itinerary, system settings, exit system)
  - Itinerary planning menu: offers features such as adding segments, setting time constraints, route planning, conflict detection, decision analysis, saving itinerary, and exporting itinerary
- Provides real-time input validation, including:
  - City name specification check (based on GB/T 2260 administrative division codes, provide error prompts for invalid city names and require re-entry)
  - Date format validation (supports standard formats "YYYY-MM-DD", "YYYY-MM-DD HH:MM", as well as relative dates like "tomorrow", "the day after tomorrow")
  - Menu selection validation (provide error prompts for invalid choices and redisplay the menu)
  - Time logic validation (e.g., "Arrival time cannot be earlier than departure time")

## 3. Testing Requirements

### 3.1 Unit Testing
- Unit test files (such as `test_*.py`) must be provided under the `src/tests/` directory.
- Test cases should be executable via the pytest framework.
- All unit test cases should pass (status PASSED).
