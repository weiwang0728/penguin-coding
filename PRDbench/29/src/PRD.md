# PRD: Food Delivery Order Dispatch System

## 1. Requirement Overview
This project aims to develop a command-line-based simulator for a food delivery dispatch system. It will implement rider management, order assignment, route planning, and delivery status monitoring through intelligent algorithms. The system utilizes an 8x8 grid coordinate system, supports concurrent delivery by multiple riders, and integrates a distance-first assignment strategy with a grid-based pathfinding algorithm to provide a complete business process simulation and decision support tool for food delivery operations.

## 2. Basic Functional Requirements

### 2.1 System Initialization and Resource Management Module
-   Automatically initialize core parameters on system startup:
    -   System Funds: 1000 (to support rider recruitment and operational costs)
    -   Rider List: Empty list (for dynamic management of rider resources)
    -   Rider ID Counter: 0 (to ensure unique rider IDs)
    -   System Running State: True (to control the main execution loop)
    -   Grid Map: An 8x8 grid representing an 800x800 coordinate system. Each 100x100 unit is a grid cell. Points at integer hundreds (e.g., 100, 200) represent restaurant/customer locations, while other points represent roads. Riders are initialized on a road.
    -   Simulated Time: The main program includes a loop where each iteration represents one unit of time (a "tick").
-   Implement an automatic rider recruitment mechanism:
    -   Trigger condition: When system funds are ≥ 300 and the number of pending orders exceeds the number of idle riders, a new rider is automatically created
    -   Recruitment Cost: 300 per rider (deducted from system funds).
    -   Initial Rider Attributes: ID (auto-incrementing), location (435, 385), speed (10 units/tick), status (0 = idle).

### 2.2 Rider Management Module
-   Rider object data structure design:
    -   Core Attributes: `rider_id` (unique identifier), `x`/`y` coordinates (current position), `speed`.
    -   Status Management: `state` (0=idle, 1=picking up, 2=delivering), `orders` (list of assigned orders), `special_case` (flag for special states).
-   Rider state transition logic:
    -   Idle (0) → Picking Up (1): When a new order is assigned.
    -   Picking Up (1) → Delivering (2): Upon arriving at the restaurant's coordinates.
    -   Delivering (2) → Idle (0): Upon completing the order delivery.
-   Rider movement algorithm implementation:
    -   Pathfinding based on the grid coordinate system (prioritizing movement along streets).
    -   Support for horizontal and vertical movement, with handling for special location cases.

### 2.3 Order Management Module
-   Order creation and coordinate transformation:
    -   User Input Format: `[restaurant_x, restaurant_y, customer_x, customer_y]` (range 0-800).
    -   Automatic Coordinate Transformation: Converts input coordinates to the center point of the corresponding grid cell.
-   Intelligent order assignment algorithm:
    -   Assignment Strategy: Closest rider first (based on Euclidean distance).
    -   Calculation Method: `√[(rider_x - restaurant_x)² + (rider_y - restaurant_y)²]`.
    -   Supports competitive assignment among multiple riders to ensure load balancing.
-   Order completion handling:
    -   Automatically remove completed orders from the rider's order list.
    -   Update the rider's status to idle, releasing the resource.
    -   Record order completion time and delivery efficiency data.

### 2.4 Path Planning and Navigation Module
-   Grid-based pathfinding algorithm:
    -   Based on an 8x8 grid system with 100x100 unit cells.
    -   Prioritizes paths along streets (where x or y coordinates align with grid lines).
    -   Supports right-angle turns and straight-line movement.
-   Special case handling:
    -   Movement strategy for when a rider is directly above or below the target.
    -   Multi-destination path optimization (for the continuous path from restaurant to customer).
    -   Mechanisms to avoid path conflicts and deadlocks.

### 2.5 System Monitoring and Status Display Module
-   Status monitoring features:
    -   Display of the current system fund balance.
    -   Rider count and detailed information for each rider.
    -   Display of each rider's location, status, and number of assigned orders.
-   Command-line map visualization:
    -   An ASCII character map display (8x8 grid).
    -   Symbol Mapping: 'R' for Rider, 'S' for Restaurant, 'C' for Customer, '.' for empty space, '#' for streets.
    -   Support for viewing rider locations and order statuses on the map.

### 2.6 User Interaction and Command System
-   Multi-level command menu system:
    -   `start`: (Order Input) Input four integer coordinates (restaurant location + customer location). Returns the grid coordinates for the restaurant and customer, whether a new rider was added, and a route map for the assigned rider including speed and time (represented as a connected line segment graph on the ASCII map).
    -   `status`: Provides a snapshot of the simulation's current state, including system funds and the status (idle, picking up, delivering) and order list for all riders.
    -   `orders`: Displays details for all orders, including start time, restaurant location, customer location, distance, time taken, and the assigned rider.
    -   `riders`: Records every status change for all riders, including details like time, location, and order number at key moments such as order acceptance, arrival at pickup, and delivery to the customer.
    -   `quit`/`exit`: Exits the program.
    -   Supports shortcut keys and command history.
-   Input validation and error handling:
    -   Coordinate range validation (0-800).
    -   Input format validation (integer type).
    -   System state consistency checks.
    -   Graceful error messaging and recovery mechanisms.

## 3. Data Requirements

### 3.1 Core System Data
-   Global variable management structure:
    -   System Funds: Integer type, supports negative values.
    -   Rider List: Dynamic array, supports CRUD operations.
    -   Rider ID Counter: Auto-incrementing integer to ensure uniqueness.
    -   System Running State: Boolean value to control the main loop.
-   Data persistence requirements:
    -   A JSON-formatted configuration file for system parameters, rider information, and order history.

### 3.2 Rider Data Model
-   Rider object attribute definitions:
    -   `rider_id`: Integer, unique identifier.
    -   `x`, `y`: Current location coordinates (integers, range 0-800).
    -   `speed`: Movement speed (integer, units/tick).
    -   `state`: Current status (integer, enum 0-2).
    -   `orders`: List of assigned orders (array, supports multiple orders).
    -   `special_case`: Boolean flag for special states.
-   Rider status enumeration:
    -   0: Idle (available for new orders).
    -   1: Picking Up (en route to the restaurant).
    -   2: Delivering (en route to the customer).

### 3.3 Order Data Model
-   Order data structure:
    -   Format: `[restaurant_x, restaurant_y, customer_x, customer_y]`
    -   Data Type: Integer array (4 elements).
    -   Coordinate Range: 0-800 (automatically converted to grid cell centers).
-   Order lifecycle management:
    -   Creation: User inputs coordinates.
    -   Assignment: Assigned to the nearest available rider.
    -   Execution: Rider follows the pickup → delivery process.
    -   Completion: Status is updated and resources are released.

### 3.4 Map and Coordinate System
-   Grid coordinate system specifications:
    -   Map Size: 800x800 units.
    -   Grid Cell Size: 100x100 units.
    -   Grid Dimensions: 8x8 (64 total cells).
    -   Coordinate Range: 0-800 (integer coordinates).
-   Coordinate conversion rules:
    -   Conversion from input coordinates to grid cell center points.
    -   Grid center point calculation: `center_x = (grid_x // 100) * 100 + 50`.
    -   Support for handling boundary cases and abnormal coordinates.

## 4. Technical Implementation Requirements

### 4.1 Development Environment and Dependencies
-   Programming Language: Python 3.6+
-   Dependency Management: Use only the Python standard library.
-   Development Tools: Support for command-line debugging and log output.

### 4.2 Core Module Architecture
-   `SystemManager`: Core class for managing funds, riders, and system state.
-   `Rider`: Class for managing rider movement, state, and orders.
-   `OrderManager`: Class for handling order creation, assignment, and completion.
-   `PathPlanner`: Class for pathfinding logic (grid-based algorithm, special cases).
-   `DisplayManager`: Class for managing status displays and map visualization.
-   `InputManager`: Class for handling command parsing and input validation.

### 4.3 Performance and Stability Requirements
-   Concurrency: Support at least 10 riders operating simultaneously.
-   Response Time: System response time < 100ms.
-   Memory Usage: Memory footprint < 100MB.
-   Stability: Support for long-duration runs (24+ hours) without memory leaks.
-   Error Recovery: Automatically recover system state in exceptional cases.

### 4.4 Code Quality and Maintainability
-   Code Standards: Adherence to PEP 8 Python coding standards.
-   Documentation: Provide detailed docstrings for functions and classes.
-   Unit Testing: Test coverage > 80% for core functional modules.
-   Error Handling: A comprehensive exception handling and logging mechanism.

## 5. Testing Requirements

### 5.1 Functional Test Cases
-   Rider management tests:
    -   Rider creation and attribute initialization.
    -   Validation of state transition logic.
    -   Accuracy testing of the movement algorithm.
-   Order management tests:
    -   Order creation and coordinate conversion.
    -   Verification of the assignment algorithm's correctness.
    -   Testing of the order completion process.
-   System integration tests:
    -   Scenarios with multiple riders delivering concurrently.
    -   System state consistency checks.
    -   Verification of the user interaction flow.

### 5.2 User Experience Testing
-   Testing the smoothness of the command-line interaction.
-   Verifying the clarity of error prompts.
-   Testing the ease of use of all functions.

## 6. Deployment and Operations Requirements

### 6.1 Runtime Environment Configuration
-   Operating System: Support for Windows, macOS, and Linux.
-   Python Version: 3.6+ (3.8+ recommended).

### 6.2 Deployment and Installation
-   Dependency Management: A `requirements.txt` file (listing only standard libraries).
-   Installation Script: Provide a one-click script for installation and configuration.
-   Configuration File: Support for customizing system parameters.
-   Documentation: Provide a complete installation guide, user manual, and API documentation.