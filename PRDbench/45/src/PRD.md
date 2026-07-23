# Chord DHT Simulation System PRD
## Requirements Overview
The objective of this system is to develop a comprehensive simulation platform based on the Chord Distributed Hash Table protocol to achieve distributed data storage and retrieval functionality in a P2P network environment. The system employs a consistent hashing scheme and finger table-based routing optimization, integrated with the SHA-1 hash function to ensure uniform data distribution and efficient searches. The platform provides a command line interface that supports dynamic node management, real-time data manipulation, network topology visualization, and other key features. Integration of concurrency engine, network maintenance modules, and performance monitoring components is necessary to guarantee stability and high efficiency in large-scale node environments. Furthermore, the system should offer detailed network status statistics and visualization to aid algorithm verification and performance analysis. The system is entirely based on local simulation and does not necessitate a physical network environment, making it suitable for scenarios related to teaching, research, and algorithm testing in distributed systems.
## Functional Requirements
### 2.0 Program Startup Function
#### 2.0.1 Startup Interface Display
- **Function Description**: Display welcome interface when the program starts.
- **Display Content**:
  - ASCII art title: Use pyfiglet library to generate ASCII art with "CHORD" text.
  - Developer information: Display developer name and identifier.
- **Output Format**: After displaying the ASCII art title and developer information, proceed to the parameter configuration interface.

### 2.1 Network Initialization Function
#### 2.1.1 Network Parameter Configuration
- **Function Description**: Users can set the fundamental parameters of the Chord ring.
- **Input Parameters**:
  - `m`: Number of hash space bits, determining the ring size as 2^m.
  - `num_nodes`: Initial node count.
  - `num_data`: Number of simulated data items initially inserted.
- **Validation Constraints**:
  - The count of nodes must not exceed the maximum ring capacity (2^m).
  - The value of m has to be a positive integer.
- **Error Prompt**: When the number of nodes exceeds the ring capacity, display the error message "Numbers of nodes cant be bigger than ring size." and request re-input.
- **Output**: Creates a Chord network of the specified scale.
#### 2.1.2 Bootstrap Node Initialization
- **Function Description**: Automatically generates the first node in the network as the bootstrap node.
- **Implementation Logic**:
  - Randomly select a node ID or create sequentially.
  - Initialize the node's finger table and predecessor and successor pointers.
  - Designate as the network entry point.
#### 2.1.3 Bulk Node Creation
- **Function Description**: Concurrently create multiple nodes and add them to the network.
- **Performance Optimization**:
  - Use a process pool for parallel creation of node objects.
  - Use multithreading to concurrent insertion of nodes nodes into the network.
  - Support bulk processing of a large number of nodes.
- **Process Display**: The program should display the network creation process, including bootstrap node initialization information and bulk node joining information.
- **Time Statistics**: After network creation is complete, display time statistics in the format "Network created in X seconds".
### 2.2 Node Management Function
#### 2.2.1 Dynamic Node Addition
- **Function Description**: Add new nodes to the network at runtime.
- **Input**: Node ID (integer)
- **Processing Flow**:
  1. Verify node ID uniqueness and validity.
  2. Locate the correct position for the new node through the bootstrap node.
  3. Update predecessor and successor relationships  of affected nodes.
  4. Redistribute data keys.
  5. Update finger tables.
- **Exception Handling**: Detect duplicate node IDs and display error messages.
- **Error Prompt**: When a node ID already exists, display the error message "Node is already in the network."
- **Success Prompt**: After a node is successfully added, display the node ID and time statistics.
- **Network Integrity Verification**: After inserting a new node, ensure all existing data can still be successfully found, verifying network integrity and correct finger table updates.
#### 2.2.2 Node Departure
- **Function Description**: Safely remove a specified node from the network.
- **Input**: Node ID to remove.
- **Processing Flow**:
  1. Transfer data stored in the node to its successor.
  2. Update pointers of predecessor and successor nodes.
  3. Update all relevant finger tables in the network.
  4. Delete the node from the node list.
- **Data Consistency**: Ensure no data loss.
- **Success Prompt**: After a node is successfully deleted, display deletion success message and time statistics.
- **Network Connectivity Verification**: After deleting a node, ensure remaining nodes can still successfully find all data, verifying network connectivity and data integrity. Data should be correctly migrated to the successor node.
#### 2.2.3 Node Status Management
- **Function Description**: Maintain comprehensive status information for each node.
- **Node Attributes**:
  - `node_id`: Unique node identifier.
  - `predecessor`: Predecessor node reference.
  - `successor`: Successor node reference.
  - `fingers_table`: Array of finger tables.
  - `data`: Local storage of key-value dictionary.
- **Status Update**: Dynamically manage node relationships and finger tables.
### 2.3 Data Operations Function
#### 2.3.1 Data Insertion
- **Function Description**: Insert key-value data into the DHT network.
- **Input**: Data string (as key and value).
- **Processing Flow**:
  1. Compute the hash value of the data key using the SHA-1 hash function.
  2. Locate the node responsible for data storage based on the hash value.
  3. Store data in the target node's local dictionary.
- **Hash Algorithm**: SHA-1, supports configurable bit truncation.
- **Load Balancing**: Ensure data is evenly distributed across nodes based on hash values.
- **Success Prompt**: After data is successfully inserted, display information in the format "Saving Key:key with Hash:hashed_key -> Node:node_id" and display time statistics.
#### 2.3.2 Data Lookup
- **Function Description**: Look up specified data in the DHT network.
- **Input**: Data string to Look up.
- **Processing Flow**:
  1. Compute the hash value of the search key.
  2. Start from any node and use the finger table for routing.
  3. Locate the node responsible for the key.
  4. Return the search result.
- **Routing Optimization**: Utilize the finger table for O(log N) complexity lookups.
- **Result Feedback**: Display data location and search path information.
- **Success Prompt**: When data is found, display information in the format "Found 'data' in node X with key Y".
- **Failure Prompt**: When data does not exist, display a message in the format "'data' not exist in the network".
#### 2.3.3 Batch Data Generation
- **Function Description**: Automatically generate large volumes of simulated data for testing.
- **Data Types**: Simulated file names (with varying extensions).
- **Data Format**: `file_<number>.<extension>`
- **Supported Extensions**: .txt, .png, .doc, .mov, .jpg, .py
- **Performance Statistics**: Record average time for batch insertion.
- **Display Format**: Display average time information for batch data insertion in the format "X seconds per item" or "X seconds ---" (where X is the average time).
### 2.4 Network Maintenance Function
#### 2.4.1 Finger Table Stabilization
- **Function Description**: Periodically update all nodes' finger tables to ensure routing correctness.
- **Trigger Conditions**:
  - After node joins or departures.
  - Regular maintenance (every 15 seconds).
  - Manual triggering.
- **Repair Algorithm**:
  - Traverse all nodes in the network.
  - Recompute target nodes for each finger table entry.
  - Update finger table pointers.
#### 2.4.2 Network Consistency Check
- **Function Description**: Validate the correctness of the network structure.
- **Check Items**:
  - Mutual consistency of predecessor-successor relationships.
  - Accuracy of finger tables.
  - Correctness of data distribution.
- **Automatic Repair**: Automatically initiate a repair process if inconsistencies are detected.
### 2.5 Information Display Function
#### 2.5.1 Network Statistics
- **Function Description**: Display overall statistical information about the network.
- **Statistics Content**:
  - Active node count
  - Maximum node capacity
  - Parameter m value
  - Bootstrap node ID
- **Formatted Output**: Structured text presentation.
#### 2.5.2 Node Details
- **Function Description**: Display the complete status of an individual node.
- **Information Content**:
  - Node ID, predecessor, successor.
  - Full finger table.
  - All stored key-value data.
- **Debugging aid**: Facilitate troubleshooting and algorithm verification.
#### 2.5.3 Network Topology Visualization
- **Function Description**: Generate graphical representation of the network structure.
- **Implementation Method**:
  - Generate a Graphviz DOT format file.
- **Output File**: Generate `graph.dot` file in the current working directory.
- **File Format**: The file content should include Graphviz format identifiers such as "digraph G".
- **Graph Content**:
  - Connections between nodes.
  - ‌Per-node finger table.
  - Data stored by nodes.
### 2.6 User Interface Function
#### 2.6.1 Command Line Menu System
- **Function Description**: Provide a user-friendly interactive menu.
- **Menu Options**:
  1. Insert a new node into the network.
  2. Lookup data within the network.
  3. Insert data into the network.
  4. Print network diagram.
  5. Print network information.
  6. Remove a node from the network.
  7. Exit the program.
- **Loop Execution**: Support continuous operations until user chooses to exit. After each operation completes, automatically return to the main menu and wait for the next user selection.
- **Graceful Exit**: When selecting the exit option (option 7), the program should exit cleanly without exceptions or error messages.
#### 2.6.2 Input Validation and Error Handling
- **Function Description**: Perform input validation and error handling for the user.
- **Validation Constraints**:
  - Node ID must be a valid integer.
  - Node ID must be unique.
  - Node ID must not exceed ring capacity.
  - Menu selection must be a valid option (1-7).
- **Error Prompt**: Display clear error messages and operation suggestions.
  - When an invalid menu selection is made, display "Invalid choice." and re-display the menu.
  - When an invalid node ID is entered, display "Invalid node id." and request re-input.
### 2.7 Performance Monitoring Function
#### 2.7.1 Operation Timing Metrics
- **Function Description**: Measure execution time for various operations.
- **Monitored Operations**:
  - Network creation time.
  - Node insertion time.
  - Data lookup time.
  - Data insertion time.
  - Node removal time.
- **Time Precision**: Second precision, supports decimals.
#### 2.7.2 Concurrent Performance Testing
- **Function Description**: Support concurrent operations to test system performance.
- **Concurrency Scenarios**:
  - Concurrent node creation.
  - Concurrent data insertion.
  - Concurrent lookup operations.
- **Performance Metrics**: Average response time, throughput statistics.
## Technical Requirements
### 3.1 Development Environment and Dependencies
#### 3.1.1 Environment Specification
- **Python Version**: Python 3.7+, compatible with mainstream operating systems (Windows/macOS/Linux).
- **Core Dependency Libraries**:
  - `hashlib`: SHA-1 hash function calculation (Python standard library).
  - `concurrent.futures`: Concurrent processing with process pools (Python standard library).
  - `threading`: Multithreading support (Python standard library).
  - `pydotplus >= 2.0.2`: Graphviz graph generation.
  - `Pillow >= 10.3.0`: Image processing and display.
  - `pyfiglet >= 0.8`: ASCII art generation.
  - `graphviz >= 0.13.2`: Graph visualization engine.
- **Installation Command**: Single-command installation script `pip install -r requirements.txt`.
#### 3.1.2 System Resource Requirements
- **Memory Requirement**: Base operating memory ≥ 512MB, large-scale networks (>1000 nodes) ≥ 2GB.
- **CPU Requirement**: Supports multi-core concurrent processing, recommended 4 cores or more.
- **Storage Space**: Temporary file storage space ≥ 100MB.
- **Recursion Depth**: System recursion limit set to 10,000,000, supporting deep search.
### 3.2 Algorithm Performance Metrics‌
#### 3.2.1 Network Operation Efficiency Requirements
- **Node Join Time**: Single node join time ≤ 1 second (in a 100 node network).
- **Data Lookup Complexity**: Average lookup hops ≤ O(log N), maximum hops ≤ 2×log N.
- **Finger Table Repair Time**: Whole network finger table repair ≤ 5 seconds (in a 100 node network).
- **Concurrent Processing Capacity**: Support processing ≥ 50 concurrent operations simultaneously.
#### 3.2.2 Hash Uniformity Verification
- **Data Distribution Variance**: Per-node data variance across nodes ≤ 20% of average.
- **Hash Collision Probability**: SHA-1 hash collision  probability ≤ 2^(-m/2).
- **Load Balancing Ratio**: Maximum node load/minimum node load ≤ 2.0.
- **Lookup Success Rate**: 100% success rate for data lookups.
#### 3.2.3 Network Consistency Guarantees
- **Node Relationship Consistency**: 100% accuracy in mutual verification of predecessor-successor relationships.
- **Data Migration Integrity**: 100% success rate for data transfer when a node leaves.
- **Finger Table Accuracy**: Correctness of finger table pointing ≥ 95% (in dynamic network environments).
- **Network Connectivity**: 100% routability between any two nodes.
### 3.4 System Stability and Reliability
#### 3.4.1 Exception Handling Mechanism
- **Network Anomaly Recovery**: Automatically trigger network repair during node failure, recovery time ≤ 10 seconds.
- **Memory Leak Protection**: Memory growth ≤ 10% during long-term operation (≥2 hours).
- **Concurrency Safety**: Thread-safe access to data structures in a multithreaded environment.
- **Recursion Overflow Protection**: Stack overflow protection mechanism for deep searches.
#### 3.4.2 Performance Monitoring and Statistics
- **Operation Time Recording**: Accurate timing recording for all key operations (second-level precision).
- **Performance Benchmarks**: Establish standard test cases, support performance regression verification.
- **Resource Usage Monitoring**: Real-time monitoring and reporting of CPU, memory usage.
- **Concurrent Performance Testing**: Support for stress testing, verifying system concurrency processing limits.
### 3.5 Code Quality and Maintenance
#### 3.5.1 Coding Standards
- **Modular Design**: Modular core functionality, individual class code lines ≤ 300.
- **Function Complexity Control**: Function length ≤ 50, cyclomatic complexity ≤ 10.
- **Variable Naming Conventions**: Use underscore-separated naming, and variable names should be self-descriptive.
- **Comment Coverage**: Critical algorithms and functions should have ≥ 80% comment coverage.
#### 3.5.2 Test Coverage Requirements
- **Unit Test Coverage**: Core algorithm test coverage should be ≥ 90%.
- **Integration Test Scenarios**: Full network lifecycle testing, including dynamic node join and leave.
- **Boundary Condition Testing**: Testing for extreme scenarios (m=1, m=20, single-node networks, etc.).
- **Concurrent Testing Validation**: Validate data consistency in a multithreaded environment.
#### 3.5.3 Deployment and Distribution
- **Dependency Management**: Complete requirements.txt file with version locking.
- **Runbook**: Detailed README.md including installation, configuration, and usage instructions.
- **Configuration Flexibility**: Support configuration files or command line parameter changes for network and performance parameters.
- **Log Recording**: Comprehensive log files for key operations, performance data, and exception information.
### 3.6 Data Structure and Storage Specification
#### 3.6.1 Core Data Structure Definition
```python
class Node:
    node_id: int                    # Unique node identifier, range [0, 2^m-1]
    predecessor: Node               # Predecessor node reference
    successor: Node                 # Successor node reference
    fingers_table: List[Node]       # Finger table, length is m
    data: Dict[int, str]            # Locally stored key-value pairs
    m: int                          # Hash space bits (class variable)
    ring_size: int                  # Ring size, equal to 2^m (class variable)
class Network:
    nodes: List[Node]              # List of all active nodes in the network
    m: int                         # Hash space parameter
    ring_size: int                 # Ring capacity
    first_node: Node               # Bootstrap node reference
```
#### 3.6.2 Data Storage and Hash Specification
- **Key-Value Storage Format**:
  - Key: Integer type, generated by the SHA-1 hash function, range [0, 2^m-1].
  - Value: String type, stores original data content.
  - Storage Location: Local dictionary `data` of each node.
  - Distribution Rule: Key K is stored in the first node with an ID ≥ K.
- **Hash Function Implementation Specification**:
  - Algorithm: SHA-1, outputs a 160-bit hash value.
  - Input: UTF-8 encoded string data.
  - Truncation: Take the first m bits as the node ID or data key.
  - Byte Order: Big-endian processing.
#### 3.6.3 Persistence and Temporary File Management
- **Visualization Files**:
  - `graph.dot`: Graphviz DOT format network topology description.
  - File Life Cycle: Retained during program runs, optionally cleared upon exit.
- **Log File Specification**:
  - Operation Logs: Timestamp + operation type + parameters + results.
  - Performance Logs: Operation timing statistics, supports CSV export.
  - Error Logs: Complete recording of exception stack information.