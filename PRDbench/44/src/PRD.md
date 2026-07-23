# Beijing Subway Fare Calculation System PRD
## 1. Requirements Overview
This project aims to develop a command-line interface (CLI)-based Beijing Subway fare calculation system, integrating graph theory algorithms with fare calculation functions. The system should support user input of starting and ending stations, calculate the optimal route using Dijkstra's shortest path algorithm, and automatically calculate fares according to Beijing Subway fare structure. It should also offer path visualization and multi-format export capabilities, providing passengers with a convenient service for querying subway travel expenses.
## 2. Basic Functional Requirements
### 2.1 Subway Network Modeling Module
- Support the import of the full network dataset in the Beijing Subway network, including station names, identifiers, and line affiliations.
- Implement subway network modeling based on graph theory, establishing a weighted undirected graph data structure.
- Provide station distance data management, supporting maintenance of  adjacency relationships between stations.
- Implement special processing for transfer stations, supporting path computation at multi-line interchange points.
### 2.2 Path Calculation Module
- Integrates Beijing Subway network data (loaded from `subway_data.json` file, including station names, connectivity, distances, etc.)
- Implements Dijkstra's algorithm to calculate the shortest path between stations with the following weight factors:
  - Base Weight: Actual inter-station distance (unit: meters)
  - Optimization Factor: Time complexity optimization via priority queue implementation
  - Path Backtracking: Support generation of complete path sequences
- Provides various path query functions:
  - Shortest-Distance Path: Minimizing total travel distance
  - Minimum-Transfer Path: Minimizing the number of transfers
  - Comprehensive Optimal Path: Balancing distance and transfers using a composite scoring metric
- Supports configuration of maximum transfer limits and line preference settings (configurable via command-line arguments `--max_transfers` and `--line_preference`)
- Supports special handling of complex transfer stations: Correctly handles path calculation at multi-line interchange points, including special processing for transfer time and distance
### 2.3 Fare Calculation Module
- Implements a fare calculation algorithm based on Beijing Subway fare structure, recognizing the following fare tiers:
  - Basic Tier: 0-6 kilometers (3 yuan)
  - Progressive Tier: 6-12 kilometers (4 yuan), 12-22 kilometers (5 yuan), 22-32 kilometers (6 yuan)
  - Extended Tier: Over 32 kilometers (1 yuan per additional 20 kilometers, e.g., 32-52 kilometers: 7 yuan, 52-72 kilometers: 8 yuan)
- Provides accurate fare conversion based on the calculated distance:
  - Distance-to-fare mapping conversion
  - Special handling of boundary cases: Boundary values themselves are calculated according to the next higher price tier (left-closed, right-open interval rule)
    - 6 kilometers (6000 meters) calculated as 4 yuan (entering 6-12 kilometers tier)
    - 12 kilometers (12000 meters) calculated as 5 yuan (entering 12-22 kilometers tier)
    - 22 kilometers (22000 meters) calculated as 6 yuan (entering 22-32 kilometers tier)
    - 32 kilometers (32000 meters) calculated as 7 yuan (entering extended tier over 32 kilometers)
  - Support for ceiling rounding support for fractional distances
### 2.4 Path Visualization and Export Module
- Implement path visualization based on route information and generate the following content:
  - Complete station sequence (list of station names, displayed in order from start to end)
  - Total distance summary (displayed in both meters and kilometers, using meters for short distances and kilometers for long distances)
  - Transfer details (transfer station identification and all subway line names involved)
  - Computed fare result (formatted as "Fare: X yuan")
- Support generating path reports in various formats:
  - Console-formatted text (including path details and fare information, displaying line segments and transfer stations)
  - Structured data format (JSON format for programmatic integration, containing fields such as query information, path, distance, fare, estimated time, transfer count, involved lines)
- Implement path summary generation, automatically extracting key information:
  - Total travel distance (converted from meters to kilometers)
  - Total fare calculation
  - Number of transfers required
  - Estimated travel time (based on distance and transfer count: approximately 1.5 minutes per kilometer, approximately 5 minutes per transfer)
### 2.5 Command-Line Interface (CLI) System
- Implements a simple command line interface, supporting standard input/output operations
- Provides real-time input validation, including:
  - Station name standardization verification (based on official Beijing Subway station names)
  - Input format validation (supporting "Starting Station; Ending Station" format, using semicolon as separator)
  - Station existence verification (ensuring the entered station exists in the system)
  - Logical validation (e.g., "Starting station cannot be the same as the ending station")
- Supports command-line argument configuration:
  - `--output_file`: Specify output file path, supporting export of query results to file
  - `--format`: Specify output format, supporting `text` (text format) and `json` (JSON format)
  - `--mode`: Specify path query mode, supporting `shortest_distance` (shortest distance), `least_transfer` (minimum transfers), `comprehensive` (comprehensive optimal)
  - `--max_transfers`: Set maximum transfer limit
  - `--line_preference`: Set line preference (e.g., "Line 1")
  - `--check_data`: Execute data integrity check and exit
- Supports continuous query functionality: Automatically enters the next query cycle after completing one query, without requiring program restart
- Supports multi-level error handling mechanisms:
  - Input format error prompt (e.g., "Input format incorrect, please use 'Starting Station; Ending Station' format")
  - Nonexistent station prompt (e.g., "Starting station 'XXX' does not exist, please check the station name")
  - Path calculation exception handling
  - Fare calculation exception handling
### 2.6 Data Management Module
- Supports comprehensive management of Beijing Subway network data, with data source from `subway_data.json` file, including:
  - Station data: station names, numbers, and lines
  - Connection data: adjacent station distances and bidirectional connection relationships
  - Line data: line names, station sequences, and transfer information
- Implements data integrity check functions (can be triggered via `--check_data` command-line argument):
  - Validation of station data coverage (verifying whether representative stations of main lines are included in the system)
  - Integrity check of connection relationships
  - Accuracy check of distance data
- Provides data update mechanisms:
  - Support for adding new lines
  - Station information modification functionality
  - Distance data update capability
## 3. Technical Implementation Requirements
### 3.1 Core Algorithm Implementation
- **Graph Data Structure**: Implement `Graph` class, supporting node and edge management
- **Priority Queue**: Implement `MinPQ` class, optimizing Dijkstra's algorithm based on heap data structure
- **Shortest Path Algorithm**: Implement `ShortestPath` class, using Dijkstra's algorithm for optimal path calculation
- **Fare Calculation**: Implement `Sum_money` function to calculate corresponding fare based on distance
### 3.2 Data Structure Design
- **Station Mapping**: Implement `station_to_number` dictionary for mapping station names to numbers
- **Network Graph**: Implement `graph` dictionary representing a weighted undirected graph with adjacency lists
- **Path Storage**: Array structure for storing calculated path sequences
- **Fare Structure**: Array or dictionary for storing mappings from distance segments to fare
### 3.3 Performance Optimization Requirements
- **Time Complexity**: Optimize Dijkstra's algorithm using priority queue to O((V+E)logV)
- **Space Complexity**: Control memory usage of graph data structure within 100MB
- **Response Time**: Single path query response time should not exceed 1 second
- **Sequential Query Processing**: Support single-user multiple continuous query operations
## 4. Data Requirements
### 4.1 Subway Network Data
- **Station Data**: Cover all main lines of Beijing Subway with all stations
- **Connection Data**: Include actual distances and connection relationships between stations
- **Line Information**: Cover main lines like Line 1, Line 2, Line 4, Line 5, Line 6, Line 8, Line 10, Line 13, Line 14, Line 15, Changping Line, Yizhuang Line, Fangshan Line, Airport Line
### 4.2 Fare Structure Data
- **Basic Fare**: 3 yuan for 0-6 kilometers, 4 yuan for 6-12 kilometers, 5 yuan for 12-22 kilometers, 6 yuan for 22-32 kilometers
- **Extended Fare**: Over 32 kilometers, 1 yuan incremented for every 20 kilometers
- **Boundary Handling**: Support fare logic for rounding up distance
### 4.3 Data Quality Requirements
- **Accuracy**: Distance data between stations consistent with actual operational data
- **Completeness**: Cover all operational stations and connection relationships
- **Consistency**: Station names consistent with official naming
- **Maintainability**: Support data updates and expansions
## 5. Acceptance Criteria
### 5.1 Functional Acceptance
- All core functions run normally, including path calculation, fare calculation, and result display
- Fare calculation accuracy consistent with Beijing Subway official standards
- Correct path calculation, able to find the shortest path
- User-friendly interaction with clear error prompts
### 5.2 Performance Acceptance
- Response time meets requirements, single query not exceeding 1 second
- Reasonable memory usage within anticipated range
- Stable program operation, supporting long-term continuous use
### 5.3 Quality Acceptance
- Good code quality with complete comments and clear structure
- Sufficient test coverage, including unit testing and integration testing
- Complete and accurate documentation, with user instructions and API documentation
- Comprehensive error handling, capable of gracefully handling various exceptions