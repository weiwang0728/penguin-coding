### BUPT-Air Intelligent Air Conditioning Management System PRD
#### 1. Requirement Overview
This system aims to provide centralized intelligent management capabilities for multi-room air conditioning environments. It supports user login to corresponding room air conditioners via ID card recognition. Based on a master-slave architecture, it enables unified scheduling of AC units, intelligent temperature adjustment, real-time cost calculation, and operation log management. The system implements core functionalities through Web API interfaces and is designed as a monolithic application with a built-in database and web server, allowing for local deployment and operation without complex external dependencies.

#### 2. Basic Functional Requirements

##### 2.1 Master Scheduler Management

Provides master control start/stop interfaces and supports cooling/heating mode switching. When switching modes, the temperature settings of all slave units are automatically reset (if set to cooling mode and slave temperature is >25°C, reset to 22°C; if set to heating mode and slave temperature is <=25°C, reset to 28°C).

Supports configuration of three scheduling algorithms: Random Scheduling (randomly selects requests), First-Come-First-Served (processes requests in chronological order), and Wind Speed Priority (prioritizes high wind speed requests).

Provides master status query functionality, returning information such as current operating mode, processing capacity, scheduling algorithm, and standby status.

Supports configuration of the processing capacity parameter (maximum number of requests processed per second, default is 3). Excess requests beyond the capacity are automatically discarded.

Implements a request queue management mechanism, prioritizing start/stop requests to prevent system exceptions due to queue overflow.

##### 2.2 Slave Temperature Control

Implements slave registration and identification based on ID card numbers. Supports querying the status information of the corresponding slave unit via the ID card number.

Provides temperature adjustment interfaces, supporting temperature increase/decrease operations.

Supports wind speed level adjustment (levels 0-3). Level 0 indicates the powered-off state. Levels 1-3 correspond to low, medium, and high wind speeds respectively.

Implements slave unit power on/off control. When powered off, the wind speed is automatically set to 0. When powered on, the current target temperature setting is maintained.


Supports slave information management, including operations such as adding a slave, deleting a slave, and querying slave status.

Supports batch deletion of slave units, clearing all slave status data to facilitate system reset or testing.

##### 2.3 Intelligent Scheduling Algorithm

Implements a request collection mechanism, fetching all pending requests from the database every second and sorting them according to the configured scheduling algorithm.

Supports priority processing logic: power on/off requests (wind speed changing from zero to non-zero or from non-zero to zero) take precedence over regular adjustment requests.

Provides intelligent decision-making functionality, automatically adjusting the wind speed based on the difference between the current temperature and the target temperature, and automatically reducing the wind speed to 0 when the target temperature is reached.

Implements a mode adaptation mechanism: in cooling mode, set wind speed to 0 when the current temperature is below the target temperature; in heating mode, set wind speed to 0 when the current temperature is above the target temperature.

Supports request queue limits to prevent system overload caused by exceeding the master's processing capacity.

##### 2.4 Temperature Monitoring and Calculation

Implements a temperature change calculation model based on thermodynamic principles, considering the influence of external temperature on the indoor temperature.

Provides temperature initialization functionality, supporting the setting of the external temperature as the initial temperature value.

Implements an intelligent adjustment mechanism: automatically sends an adjustment request when the temperature deviates from the target temperature by more than 1°C and more than 1 second has passed since the last request.

Supports temperature calculation on/off control, allowing the automatic adjustment function to be turned on or off.

Provides temperature monitoring destruction functionality, stopping the temperature calculation thread and releasing resources.

##### 2.5 Real-time Cost Calculation

Implements energy consumption calculation based on wind speed level, calculated per second: low-speed wind consumes 0.8/60 standard power units per second, medium speed consumes 1.0/60 per second, and high speed consumes 1.3/60 per second.

Provides real-time cost calculation functionality, charging 5 yuan per standard power unit. Energy consumption and cost data are updated every second. The cost calculation formulas are: 
low speed—cost per second = 0.8/60*5 yuan;
medium speed—cost per second = 1.0/60*5 yuan;
high speed—cost per second = 1.3/60*5 yuan.

Supports cost calculation on/off control, allowing the cost calculation thread to be started or stopped.

Implements cumulative statistics, recording the total energy consumption and total cost for each slave unit.

Manages data persistence through ORM (Object-Relational Mapping), ensuring data consistency during the cost calculation process.

##### 2.6 Operation Log Management

Records all control requests and response results, including information such as request time, response time, and operation parameters.

Supports time range query functionality, allowing users to specify start and end dates to query historical records.

Provides slave statistics functionality, summarizing power on/off counts, total costs, and detailed adjustment records by slave unit ID.

Implements cost statistics functionality, calculating the total cost within a specified time range based on actual usage duration and wind speed levels.

Supports report generation, outputting a complete report containing the query time range, slave statistics, cost statistics, and detailed records.

#### 3. Data Management Requirements

##### 3.1 Slave Status Management

Maintains a basic slave information table containing fields such as Slave ID, ID Card Number, Target Temperature, Current Temperature, Current Wind Speed, Cumulative Energy Consumption, and Cumulative Cost.


Supports real-time updates of slave status. Operations like temperature changes, wind speed adjustments, and cost accumulation are promptly synchronized to the database.

Provides slave status query interfaces, supporting querying a single slave's status by ID or querying the status of all slaves.

Implement data persistence functionality so that after a system restart, slave status data (including cumulative cost amount) can be restored from the database.

##### 3.2 Request Queue Management

Maintains a request information table, recording information such as Request ID, Slave ID, Requested Temperature, Requested Wind Speed, and Request Time.

Implements request lifecycle management, tracking the entire process from request creation to processing completion.

Supports a request cleanup mechanism; processed requests are automatically removed from the queue.

Implement data persistence functionality so that after a system restart, slave status data (including cumulative cost amount) can be restored from the database.

##### 3.3 Operation Log Recording

Maintains an operation log table, recording information such as Log ID, ID Card Number, Slave ID, Wind Speed, Current Temperature, Target Temperature, Request Time, and Response Time.

Supports log query functionality, filtering log records by criteria like time range and slave ID.

Implements log statistics functionality, providing summary information such as power on/off counts, usage duration, and cost statistics.

#### 4. System Integration Requirements

##### 4.1 Web API Interface

Provides RESTful API interfaces that support cross-origin access for easy integration with front-end applications.

Implements interface version management to ensure backward compatibility of APIs.

Provides interface status monitoring, including connection testing and error handling functionalities.

##### 4.2 Concurrent Processing

Adopts a multi-threaded architecture where modules like master scheduling, cost calculation, and temperature monitoring operate independently.

Implements thread pool management to control the number of concurrent threads and avoid system resource overload.

Supports thread-safe data access to ensure data consistency in a multi-threaded environment.

##### 4.3 Exception Handling

Provides a comprehensive exception handling mechanism, covering exceptions like data access errors, request processing failures, and calculation errors.

Implements error logging to facilitate problem troubleshooting and system maintenance.

Supports graceful degradation, ensuring core functionalities remain operational even if some non-critical functions encounter exceptions.