### Command Line Board Game Battle and Data Statistics System PRD
#### 1. Requirement Overview
The aim of this project is to develop a multifunctional board game application in a command line environment, supporting two-player matches for Gomoku and Chinese Chess, and integrating battle data recording and analysis features. The system should implement complete board game rules logic, real-time battle interaction, structured data storage, and player behavior statistics based on game theory and time series analysis, providing a competition platform for board game enthusiasts while supporting in-depth battle data mining.

#### 2. Basic Functional Requirements
##### 2.1 Game Lobby Module
- Display the main game menu on startup, supporting five function choices: "Start New Battle," "Continue Battle," "View Historical Data," "Data Analysis Center," and "Exit System."
- Player input verification mechanism, supporting numeric selection and handling of erroneous input (including error prompts in Chinese).
- System state persistence, automatically recording unfinished battles at the time of last exit (if any).

##### 2.2 System Configuration Module
- Support player information management (create/delete player IDs, store up to 10 player profiles).
- Provide board display style switching (compact/standard/expanded modes).
- Support manual clearing of all system data, reverting to default state.

##### 2.3 Gomoku Battle Module
- Support a 15×15 standard board, drawn using ASCII characters ('+' for empty positions, '●' for black pieces, '○' for white pieces).
- Implement a move coordinate input system (e.g., format "A10"), including coordinate validity checks (boundary checks, non-repeated moves).
- Victory determination algorithm: use depth-first search (DFS) to implement horizontal/vertical/diagonal pre-checks for four-in-a-row (3-move advanced warning) and five-in-a-row endgame determination.
- Support undo function (only the last move) and forfeit operation, with operation log recording.

##### 2.4 Chinese Chess Battle Module
- Implement a 9×10 standard board, including Chu River and Han border markers and the initial layout of pieces (King/General, Advisor, Elephant, Horse, Chariot, Cannon, Soldier).
- Piece movement rule engine: full implementation of 16 chess pieces' movement logic like "Horse moves in day" (block horse's leg), "Elephant flies field" (block elephant's eye), "Cannon skips over" etc.
- Special rule handling: include endgame rules like "Kings can't face each other," "Soldiers cross the river," and "Stalemate."
- Implement a simple situation evaluation using the minimax algorithm (used only for tips in the last 10 moves, not for AI battles).

##### 2.5 Battle Data Recording Module
- Design a structured data model including 12 metadata such as battle ID, game type, player IDs (2 players), start time, end time, total moves, victory result, key move sequence.
- Store data using an SQLite database, with automatic table creation and transaction management.
- Real-time battle logging (cache every 5 moves), with a data recovery mechanism triggered upon abnormal exit.
- Support viewing historical battle records, displaying a complete list of battle information.

##### 2.6 Data Analysis Center
- Player activity analysis: implement "7-day battle frequency ranking" based on a sliding window algorithm (similar to the Frequency metric in the RFM model).
- Win rate statistics: support win rate calculation by game type, time period (weekly/monthly), opponent level.
- Game behavior analysis: use sequence pattern mining algorithm (SPMF) to identify high-frequency move sequences, generating an "Opening Heatmap" (output ASCII visual heatmap needed).
- Data export function: support exporting analysis results to CSV format (including field description header).