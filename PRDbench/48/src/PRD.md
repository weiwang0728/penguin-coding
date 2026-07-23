# Maze Problem Project PRD (Product Requirements Document)

## 1. Requirement Overview

The goal of this project is to develop a Python-based maze generation and solving system, providing a complete solution to maze problems. The system should support various maze generation algorithms (DFS, PRIM) and pathfinding algorithms (DFS, BFS, A*) and have features for maze data management and performance analysis. It aims to provide a comprehensive platform for algorithm learning, teaching demonstrations, and practical applications of maze problems.

## 2. Basic Functional Requirements

### 2.1 Maze Generation Module

- Implement DFS maze generation algorithm:
  - Construct two matrices for the maze size: `maze_map` (maze shape) and `maze_state` (visit status)
  - Use a `memory` list to record DFS states, randomly selecting unvisited adjacent nodes from the starting point for expansion
  - Ensure the generated maze is acyclic and connected, must support custom starting position functionality
  - Input parameters: `size` (maze dimensions), `start_point` (starting point coordinates, default [0,0])
  - Output: maze matrix (numpy.ndarray, dtype=uint8, values only 0 and 1), generation time statistics, start coordinates, end coordinates

- Implement PRIM maze generation algorithm:
  - Construct a vector with a depth of 5 for the maze size, including visit flags and wall statuses
  - Use `memory` to record opened walls, randomly selecting nodes to ensure maze connectivity
  - Convert the wall status matrix into a standard maze format, must support custom starting position functionality
  - Input parameters: `size` (maze dimensions), `start_point` (starting point coordinates, default [0,0])
  - Output: maze matrix (numpy.ndarray, dtype=uint8, values only 0 and 1), generation time statistics, start coordinates, end coordinates

- Provide maze post-processing features (wall removal functionality):
  - Randomly remove a specified number of walls, the number of removals should be close to the specified value (allow ±1 error), and verify maze connectivity after removal
  - Input parameters: `wall_count` (number of walls to remove), `maze_matrix` (original maze matrix)
  - Output: optimized maze matrix (must verify that walls have been removed, i.e., 1 becomes 0)

### 2.2 Maze Solving Module

- Implement DFS pathfinding algorithm:
  - Establish coordinate-marked maps and visit status matrices, utilizing stack structures for depth-first search
  - Record search paths and visited nodes, supporting backtracking mechanisms
  - Input parameters: `maze_matrix` (maze matrix), `start_point` (starting point coordinates), `end_point` (ending point coordinates)
  - Output: must contain 4 required components: path coordinate list (non-empty), number of nodes explored, search time, path length
  - Path validity requirements: all coordinates in the path must be on paths (value 0), adjacent coordinates must have distance 1 (continuity), start and end points must be correct
  - Performance characteristics: high efficiency for single-path scenarios, relatively low memory usage

- Implement BFS pathfinding algorithm:
  - Establish coordinate-marked maps and visit status matrices, utilizing queue structures for breadth-first search
  - Gradually expand the search range, recording the shortest path, must guarantee finding the shortest path (path length does not exceed DFS)
  - Input parameters: `maze_matrix` (maze matrix), `start_point` (starting point coordinates), `end_point` (ending point coordinates)
  - Output: must contain 4 required components: shortest path coordinate list, number of nodes explored statistics, search time statistics, path length statistics, and data types must be correct
  - Performance characteristics: ensures finding the shortest path, suitable for multi-path mazes

- Implement A* pathfinding algorithm:
  - Establish coordinate-marked maps and visit status matrices, using priority queues for heuristic search
  - Combine actual costs with heuristic functions to optimize search efficiency, must implement heuristic function (e.g., Manhattan distance or Euclidean distance)
  - Must guarantee finding an optimal path of the same length as BFS, and on large mazes the number of nodes explored should be significantly less than BFS (on average less than 50-80% of BFS)
  - Input parameters: `maze_matrix` (maze matrix), `start_point` (starting point coordinates), `end_point` (ending point coordinates)
  - Output: must contain 4 required components: optimal path coordinate list, number of nodes explored statistics, search time statistics, path length statistics
  - Performance characteristics: ensures finding the optimal path, high search efficiency, suitable for complex mazes

### 2.3 Data Management Module

- Implement maze data saving functionality:
  - Support saving in numpy format (.npy), preserving maze matrices and metadata, with customizable save paths
  - Input parameters: `maze_matrix` (maze matrix), `save_path` (save path), `metadata` (optional metadata)
  - Output: save status, file size information

- Implement maze data loading functionality:
  - Support loading in numpy format (.npy), validate file format and integrity, auto-parse maze metadata
  - Input parameters: `load_path` (load path)
  - Output: maze matrix, metadata information, load status

- Implement maze data validation functionality:
  - Check maze matrix format (validate data type, value range, shape, etc.), validate reachability from start to end, check maze connectivity
  - Must be able to identify the following format errors: matrices containing non-0/non-1 values, matrices with incorrect data types, matrices with incorrect shapes, mazes that are not reachable from start to end
  - Input parameters: `maze_matrix` (maze matrix), `start_point` (starting point coordinates, optional), `end_point` (ending point coordinates, optional)
  - Output: validation results (success/failure status), error messages (if any, must include clear error descriptions)
  - Data files: The system must support loading and validating the `evaluation/inputs/disconnected_maze.npy` file (for connectivity check testing)

### 2.4 Performance Analysis Module

- Implement algorithm performance comparison functionality:
  - Capture time performance statistics, analyze space complexity, compare the number of nodes explored, and path length
  - Input parameters: `maze_matrix` (maze matrix), `algorithms` (list of algorithms to compare, e.g., DFS, BFS, A*), `iterations` (number of test iterations)
  - Output: must contain a complete performance comparison report (time performance statistics, explored node count comparison, path length comparison for all algorithms) and algorithm recommendation suggestions (recommendations must be based on performance data and align with algorithm characteristics, e.g., BFS suitable for finding shortest paths, A* suitable for complex mazes, etc.)

- Implement maze complexity evaluation functionality:
  - Calculate path length, count branching points, dead-end statistics, complexity scoring
  - Input parameters: `maze_matrix` (maze matrix)
  - Output: must contain complete assessment information: complexity score, detailed statistical information (path length, number of branch points, number of dead ends), difficulty level, and the complexity score must correctly reflect maze size and complexity (e.g., a 30x30 maze's complexity score should be higher than a 10x10 maze)

### 2.5 Technical Implementation Requirements

- Code structure requirements:
  - Core modules (must exist and be importable): `maze_generator.py` (maze generator), `path_finder.py` (pathfinder), `maze_validator.py` (maze validator)
  - Algorithm modules (must exist and be importable): `dfs_generator.py`, `prim_generator.py`, `dfs_solver.py`, `bfs_solver.py`, `astar_solver.py`
  - Utility modules (must exist and be importable): `data_manager.py` (data management), `performance.py` (performance analysis)
  - Note: The above 10 core module files must all exist and be successfully importable, with no ImportError exceptions
  - Other modules: `config.py` (configuration management), test modules, example modules, etc.

- Technology stack requirements:
  - Programming language: Python 3.8+
  - Core dependencies: numpy==1.23.4 (numerical computation)
  - Development environment: local Python environment, no front-end UI required

- Data format requirements:
  - Maze matrix format: numpy.ndarray, data type uint8 (0 for paths, 1 for walls)
  - Coordinate system: must uniformly use [row, column] format, data type numpy.ndarray or list, all coordinate-related functions (start, end, path coordinates) must have completely consistent format
  - Path data structure: list of coordinates, representing the sequence from start to end
  - File storage format: .npy (numpy binary format), .json (configuration file format)

- Error handling requirements:
  - Must gracefully handle the following exceptional inputs: negative maze size, out-of-bounds start coordinates, invalid maze matrices (containing non-numeric types), empty maze matrices, incorrect data types
  - For all exceptional inputs, must return meaningful error messages, and the program must not crash

- Acceptance standards:
  - Functional acceptance: all algorithms are correctly implemented and can generate valid mazes, pathfinding algorithms can find correct paths
  - Performance acceptance: maze generation time within a reasonable range, pathfinding algorithm efficiency meets expectations
  - Quality acceptance: code conforms to Python coding standards, all test cases pass, documentation is complete and accurate