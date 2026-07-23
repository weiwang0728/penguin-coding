## IoT Environmental Data Collection and Intelligent Prediction System Based on MQTT Protocol PRD (Product Requirements Document)

---

### 1. Requirement Overview

This project aims to design and develop an IoT environmental data collection, transmission, storage, and intelligent prediction system based on MQTT protocol, primarily used for collecting, transmitting, and analyzing temperature, humidity, and air pressure data in the environment. The system adopts a publish-subscribe model, supporting real-time data collection, cloud transmission, local storage and intelligent prediction analysis functions based on deep learning.

Innovation points include:

- Introducing multi-source environmental data fusion technology, achieving unified collection and processing of temperature, humidity, and air pressure data;
- Integrating MQTT real-time communication, cloud storage, and local caching multi-level data management architecture;
- Providing complete IoT data processing flow for multiple scenarios including data collection, transmission, storage, and prediction;
- Introducing deep learning prediction models, achieving intelligent prediction analysis based on historical environmental data, enhancing environmental monitoring predictability.

Target users are IoT device administrators, data analysts, and system operation personnel. The system supports real-time monitoring, data visualization, intelligent prediction and anomaly alerts, possessing high reliability, scalability and practicality.

---

### 2. Functional Requirements

#### 2.0 System Entry and User Interface

- **Main Startup Script**
  - Provides main startup script `run.py`, execute `python run.py` command to start the system;
  - After startup, displays main interface menu containing all core functional modules: MQTT, Data Management, Machine Learning, System Monitoring, Web Interface;
  - Provides user-friendly interactive interface with clear operation guidance and option descriptions;
- **Command Line Interface (CLI)**
  - Provides complete CLI command interface, all core functions can be accessed through CLI commands;
  - Main command modules include: mqtt, data, ml, system, web, setup;
  - Provides command line help information (CLI command: `python main.py --help`), containing all main command modules and clear descriptions;
  - CLI command structure: `python main.py <module> <subcommand> [parameters]`.

#### 2.1 Device Connection and Authentication Management

- **MQTT Connection Management**
  - Supports connecting to Alibaba Cloud IoT Platform, achieving device authentication and connection status monitoring;
  - Supports one-device-one-secret authentication method, device triplet information (ProductKey, DeviceName, DeviceSecret) management;
  - Implements connection disconnection and reconnection mechanisms, ensuring data transmission stability;
  - Provides connection status real-time monitoring and anomaly alert functions;
- **Device Authentication and Security**
  - Supports HMAC-SHA1 signature authentication, ensuring data transmission security;
  - Implements device permission management and access control;
  - Supports TLS encrypted transmission, protecting data privacy;
  - Provides device registration, deregistration, and status management functions.

#### 2.2 Data Publishing and Transmission Module

- **Real-time Data Publishing Function**
  - Supports single random data publishing, simulating sensor data collection (CLI command: `python main.py mqtt publish --random`);
  - Supports batch data publishing, reading historical data from CSV files (CLI command: `python main.py mqtt publish --file samples/environmental_sample.csv --count <count>`, using data file: `samples/environmental_sample.csv`);
  - Supports custom data format publishing, meeting different sensor requirements;
  - Provides publishing status feedback and detailed log recording;
- **Data Format Standardization**
  - Unified JSON format data encapsulation, containing timestamp, version number, parameter values;
  - Supports data format conversion (timestamp conversion, unit standardization);
  - Implements data integrity verification and anomaly detection;
  - Provides data compression and optimized transmission functions.

#### 2.3 Data Subscription and Reception Module

- **MQTT Subscription Management**
  - Supports custom ClientID subscription, achieving multi-client parallel processing;
  - Implements Alibaba Cloud AccessKey authentication, supporting consumer group subscription mode;
  - Provides connection status monitoring and automatic reconnection mechanism;
  - Supports multi-topic subscription and message filtering functions;
  - Supports specifying subscription duration and automatic save function (CLI command: `python main.py mqtt subscribe --duration <seconds> --save`);
- **Data Reception and Processing**
  - Real-time MQTT message reception, supporting high-concurrency data processing;
  - Data format parsing and verification, ensuring data quality;
  - Local CSV file storage, supporting large-capacity data management;
  - Data integrity checking and exception handling mechanism.

#### 2.4 Data Storage and Management Module

- **Multi-level Storage Architecture**
  - Local CSV file storage, supporting large-capacity data (>100,000 records);
  - Cloud Alibaba Cloud IoT Platform storage, achieving data backup and synchronization;
  - Memory caching mechanism, improving data access performance;
  - Supports data compression, archiving, and regular cleanup;
- **Data File Management**
  - Supports multi-source data file management (temperature, humidity, air pressure independent files, data files: `data/temperature_data.csv`, `data/humidity_data.csv`, `data/pressure_data.csv`);
  - Implements data file version control and backup recovery;
  - Provides storage space monitoring and management functions;
  - Supports data migration and format conversion.

#### 2.5 Data Preprocessing and Quality Control

- **Data Cleaning Function**
  - Missing value detection and processing (interpolation, deletion, marking);
  - Anomaly value detection and filtering (statistical methods, machine learning methods);
  - Data format standardization and unit unification;
  - Timestamp unified conversion and timezone processing;
  - Provides data cleaning command (CLI command: `python main.py data clean`);
- **Data Analysis Function**
  - Supports environmental data analysis, displaying statistical information tables (CLI command: `python main.py data analyze`);
  - Provides data statistical summary (mean, variance, extreme values, etc.);
- **Data Fusion and Alignment**
  - Multi-source data merging (temperature, humidity, air pressure time series alignment, CLI command: `python main.py data merge`, using data files: `data/temperature_data.csv`, `data/humidity_data.csv`, `data/pressure_data.csv`);
  - Data integrity verification and consistency checking;
  - Supports different sampling frequency data resampling;
  - Provides data quality assessment reports.

#### 2.6 Machine Learning Prediction Module

- **Deep Learning Model Architecture**
  - 5-layer fully connected neural network, input layer 3 features (temperature, humidity, air pressure);
  - Hidden layers 64-128-256-128 neurons, output layer 1 prediction value;
  - Uses ReLU activation function, supports batch normalization and Dropout regularization;
  - Supports model saving, loading, and version management;
- **Model Training and Optimization**
  - Supports training set/validation set/test set automatic division;
  - Data standardization and normalization preprocessing;
  - Supports custom training parameters (learning rate, batch size, training epochs);
  - Loss function monitoring and early stopping mechanism, preventing overfitting;
  - Provides model training command (CLI command: `python main.py ml train --data-file samples/environmental_sample.csv --epochs <epochs>`, using data file: `samples/environmental_sample.csv`);
- **Prediction and Evaluation Function**
  - Environmental parameter prediction based on historical data (CLI command: `python main.py ml predict --temperature <temperature> --humidity <humidity> --pressure <pressure>`);
  - Prediction result output and confidence assessment;
  - Supports multiple evaluation metrics (RMSE, MAE, R², etc., CLI command: `python main.py ml evaluate`);
  - Provides prediction result visualization display.

#### 2.7 System Monitoring and Management Module

- **Real-time Monitoring Function**
  - MQTT connection status real-time monitoring;
  - Data publishing and reception status monitoring;
  - System resource usage monitoring (CPU, memory, storage, network status, CLI command: `python main.py system status`);
  - Network transmission performance and latency monitoring;
  - Supports real-time system performance monitoring (CLI command: `python main.py system monitor --duration <seconds>`);
- **Log Management and Analysis**
  - System operation log recording and hierarchical management (log files stored in `logs/` directory, containing timestamps and detailed information, format standardized and readable);
  - Error log recording and anomaly alerts;
  - Performance monitoring logs and statistical analysis;
  - User operation logs and audit tracking;
- **Configuration Management**
  - MQTT connection parameter configuration management;
  - Alibaba Cloud platform configuration and authentication information management;
  - Data storage path and format configuration;
  - Model parameter and training configuration management;
  - Provides interactive configuration wizard (CLI command: `python main.py setup`), displaying clear configuration options and input prompts.

#### 2.8 Data Visualization and Analysis Module

- **Web Interface Service**
  - Supports Web service startup (CLI command: `python main.py web --host <host> --port <port>`, default address: 127.0.0.1, default port: 8080);
  - Provides Web interface data visualization, displaying environmental data visualization charts;
  - Supports Web interface interaction functions, responding to user operations and displaying prediction results (API interface: `POST /api/ml/predict`);
- **Real-time Data Display**
  - Supports temperature, humidity, air pressure data real-time curve chart display;
  - Provides historical data trend analysis and comparison functions;
  - Supports multi-time scale data display (hour, day, week, month);
  - Anomaly data highlight display and alert prompts;
- **Statistical Analysis Function**
  - Data statistical summary (mean, variance, extreme values, etc.);
  - Correlation analysis and association rule mining;
  - Anomaly detection and pattern recognition;
  - Prediction result and actual value comparative analysis;
- **Report Generation**
  - Automatically generates data quality reports;
  - Prediction model performance evaluation reports;
  - System operation status reports;
  - Supports report export and sharing functions.

#### 2.9 Exception Handling and Fault Tolerance Mechanism

- **Network Exception Handling**
  - MQTT connection disconnection automatic reconnection mechanism;
  - Network latency and packet loss handling strategies;
  - Offline data caching and synchronization mechanism;
  - Network status monitoring and alerts;
- **Data Exception Handling**
  - Sensor data anomaly detection and handling (supports anomaly data detection and processing functions);
  - Data format error and parsing exception handling;
  - Storage space insufficient and data overflow handling;
  - Data consistency checking and repair mechanism;
- **System Exception Handling**
  - Process crash automatic restart mechanism;
  - Memory leak detection and handling;
  - Disk space monitoring and cleanup;
  - System performance degradation and recovery strategies;
  - Comprehensive error handling mechanism, providing clear error messages and solution suggestions, system will not crash due to errors.

---

### 3. Technical Requirements

- **Programming Language**: Python 3.9+
- **MQTT Communication Framework**:
  - MQTT Client: paho-mqtt (device-side publishing), stomp.py (server-side subscription)
  - Cloud Platform Integration: Alibaba Cloud LinkKit SDK
  - Message Queue: Alibaba Cloud AMQP Service
- **Data Processing and Analysis**:
  - Data Processing: pandas (data cleaning, merging, analysis)
  - Numerical Computing: numpy (array operations, mathematical computation)
  - Machine Learning: scikit-learn (data preprocessing, evaluation metrics)
- **Deep Learning Framework**:
  - Neural Network: PyTorch (model construction, training, prediction)
  - Model Optimization: Supports GPU acceleration, distributed training
- **Web Framework and Visualization**:
  - Web Service: Flask (API interfaces, Web interface)
  - Data Visualization: matplotlib, seaborn (chart drawing)
  - Real-time Display: Supports WebSocket real-time data push
- **Data Storage and Management**:
  - Local Storage: CSV file format (structured data)
  - Cloud Storage: Alibaba Cloud IoT Platform
  - Cache Mechanism: Memory cache, Redis (optional)
- **System Monitoring and Logging**:
  - Logging Framework: logging (hierarchical log recording)
  - Performance Monitoring: psutil (system resource monitoring)
  - Scheduled Tasks: schedule (scheduled data collection, model training)
- **Security and Authentication**:
  - Encrypted Transmission: TLS/SSL (MQTT secure connections)
  - Identity Authentication: HMAC-SHA1 signature, JWT Token
  - Access Control: Role-based access control
- **Testing and Deployment**:
  - Unit Testing: pytest (functional testing, performance testing)
  - Containerization: Docker (environment consistency, rapid deployment)
  - Configuration Management: Environment variables, configuration file management
- **Code Standards and Quality**:
  - Code Formatting: black (PEP8 standards)
  - Type Checking: mypy (static type checking)
  - Code Quality: flake8 (code style checking)

---

### 4. Data Requirements

#### 4.1 Data Source Specifications

- **Sensor Data Types**:
  - Temperature Data: Range -50°C to 50°C, accuracy 0.1°C, sampling frequency every 10 minutes
  - Humidity Data: Range 0% to 100%, accuracy 0.1%, sampling frequency every 10 minutes
  - Air Pressure Data: Range 800hPa to 1200hPa, accuracy 0.01hPa, sampling frequency every 10 minutes
- **Data Format Requirements**:
  - Input Format: JSON time series, CSV files
  - Output Format: Standardized JSON, CSV storage
  - Time Format: Unix timestamp (millisecond precision)
- **Data File Specifications**:
  - Environmental data sample file: `samples/environmental_sample.csv`, used for batch data publishing and model training
  - Data file format requirements: CSV files must contain the following fields: timestamp (timestamp), temperature (temperature), humidity (humidity), pressure (pressure), optional fields: device_id (device ID), quality_flag (quality flag)
  - Multi-source data files: `data/temperature_data.csv` (temperature data), `data/humidity_data.csv` (humidity data), `data/pressure_data.csv` (air pressure data), used for multi-source data merging operations
  - Data value range validation: temperature -50~50°C, humidity 0~100%, pressure 800~1200hPa

#### 4.2 Data Quality Requirements

- **Data Integrity**: Record integrity ≥99%, time series continuity verification
- **Data Accuracy**: Anomaly value detection rate ≥95%, data consistency checking
- **Data Timeliness**: Real-time data latency ≤5 seconds, historical data management

#### 4.3 Data Security Requirements

- **Transmission Security**: MQTT TLS encryption, device authentication authorization
- **Storage Security**: Local data encryption, access permission control
- **Privacy Protection**: Sensitive data masking, audit log recording

---

### 5. Performance Requirements

- **Data Processing Performance**: Supports processing 1000 data records per second, memory usage optimization
- **Storage Performance**: File read/write speed ≥10MB/s, supports data compression
- **Network Performance**: MQTT connection stability ≥99.9%, data transmission latency ≤1 second
- **Prediction Performance**: Model training time ≤30 minutes, prediction response time ≤1 second

---

### 6. Deployment Requirements

- **Environment Requirements**: Python 3.9+, operating system Windows/Linux/macOS, memory ≥4GB, storage ≥10GB
- **Network Requirements**: Stable internet connection, supports MQTT protocol (ports 1883/8883)
- **Cloud Platform Requirements**: Alibaba Cloud IoT Platform account, device triplet information configuration
- **Dependency Management**: requirements.txt file management, supports virtual environment deployment

---