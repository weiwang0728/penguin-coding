# MinNE Layered Network Simulation and Protocol Stack Implementation Platform PRD

## 1. Requirement Overview

This platform aims to build a complete layered network simulation system, implementing virtualization modeling of various network devices (hosts, switches, routers) through Python, supporting end-to-end data transmission under complex network topologies. The system is based on socket communication, implementing a complete network protocol stack from the physical layer to the application layer, covering core network technologies such as frame synchronization positioning, CRC-16 error detection and control, Dijkstra dynamic routing algorithm, port address learning, flow control,etc. The platform supports reliable transmission of Chinese, English text, and image files, providing a complete technical solution for network protocol research, teaching experiments, and simulation testing.

## 2. Basic Functional Requirements

### 2.1 Network Device Simulation Module

#### 2.1.1 Host Device Simulation
- **Device Identification and Port Assignment**: Each host is assigned a unique device number (e.g., "1", "2", "4", "7"), application layer port format is `1{device_id}300`, network layer port format is `1{device_id}200`
- **Application Layer Implementation**: Based on AbstractLayer abstract class, implements bidirectional message sending and receiving between console and network layer, supports data reception with buffer size `IN_NE_BUFSIZE`
- **Message Processing Capability**: Application layer needs to distinguish sources (console/network layer), implement blocking reception and non-blocking sending, ensuring ordered message transmission

#### 2.1.2 Switch Device Simulation
- **Port Address Table Management**: Implements SwitchTable class, maintains mapping relationship between local physical layer ports and remote application layer ports (format: `dict[local_port, dict[remote_port, lifetime]]`)
- **Address Learning Mechanism**: When receiving data frames, automatically extracts source address and updates port address table, sets lifetime to `REMOTE_MAX_LIFE`, decrements all entry lifetimes by 1 during each frame processing, automatically deletes expired entries
- **Forwarding Decision Logic**:
  - Unicast: Queries port address table based on destination address, finds corresponding local port for forwarding
  - Broadcast: Forwards data to all physical layer ports except receiving port
  - Flooding: Forwards to all ports (except receiving port) when destination address is unknown

#### 2.1.3 Router Device Simulation
- **Routing Table Structure**: Implements RouterTable class, contains two-level mapping: WAN environment (router_id -> Path structure) and LAN environment (host_id -> exit_port)
- **Dijkstra Algorithm Implementation**: Dynamic routing calculation, maintains shortest paths to each destination, includes fields: next (next hop), exit (exit port), cost (cost), optimized (optimization status)
- **Routing Information Exchange**: Supports routing packet format `device:dst-cost|dst-cost|...:$` packaging and unpacking, implements distributed synchronous updates of routing tables
- **Address Mapping and Lookup**: Supports 5-digit port number format address resolution, implements reverse mapping query from application layer to physical layer ports

### 2.2 Network Protocol Stack Implementation Module

#### 2.2.1 Frame Structure and Encoding/Decoding
- **Frame Format Definition**: Adopts fixed frame structure, containing:
  - Frame locator: 8-bit fixed pattern `01111110`
  - Source port: 16-bit binary encoding
  - Session status: 2 bits (NORMAL="00", FIN="01", REQ_TXT="10", REQ_IMG="11")
  - Acknowledgement flag: 1 bit (ACK="1", NAK="0")
  - Sequence number: 1 bit alternating sequence number
  - Data segment: 32-bit variable length data
  - Destination port: 16-bit binary encoding
  - CRC check: 16-bit cyclic redundancy check code
- **Transparent Transmission Processing**: Implements bit stuffing algorithm, detects 5 consecutive '1's and inserts '0', ensuring uniqueness of frame locator
- **Frame Construction and Parsing**: Provides FrameBuilder and FrameParser classes, supports complete processing flow of frame construction, validation, and parsing

#### 2.2.2 Error Detection and Control
- **CRC-16 Check Implementation**: Uses generator polynomial 0xA001, performs cyclic redundancy check on frame content, detects bit errors during transmission
- **Check Code Calculation**: Based on standard CRC-16 algorithm, initial value 0xFFFF, supports check code generation for binary data of any length
- **Error Control Protocol**:
  - Stop-and-Wait ARQ: Sender sends frame then waits for ACK confirmation, timeout retransmission
  - Sequence Number Mechanism: Uses 0/1 alternating sequence numbers, prevents duplicate frame reception
  - NAK Feedback: Receiver sends NAK when detecting errors, triggers immediate retransmission

#### 2.2.3 Flow Control Mechanism
- **Sending Rate Constraint**: Sets maximum sending interval, prevents sender speed from being too fast causing receiver buffer overflow
- **Buffer Management**: Sets inter-network-element communication buffer (`INTER_NE_BUFSIZE`) and intra-network-element communication buffer (`IN_NE_BUFSIZE`) respectively
- **Congestion Control Strategy**: Based on packet loss rate and delay feedback, dynamically adjusts sending window size, implements adaptive flow control

### 2.3 Data Transmission and File Processing Module

#### 2.3.1 Multimedia Data Support
- **Text Data Processing**: Supports UTF-8 encoded Chinese, English, punctuation symbol transmission, bidirectional conversion between string and binary
- **Image File Transmission**: Supports PNG format image binary transmission, implements large file frame segmentation processing and reassembly
- **Data Fragmentation Mechanism**: When data length exceeds single frame capacity (32 bits), automatically fragments into multiple frames for transmission, supports fragment reassembly and out-of-order processing

#### 2.3.2 Session Management and File Storage
- **Session Status Management**: Implements complete session lifecycle, including connection establishment, data transmission, connection termination
- **Automatic File Saving**: Received image files automatically saved to resource directory, file naming format is `received-{timestamp}.png`
- **Transmission Progress Tracking**: Provides file transmission progress feedback, supports transmission status query and exception handling

### 2.4 Network Topology Configuration and Management Module

#### 2.4.1 Topology Configuration System
- **JSON Configuration Format**: Adopts structured JSON configuration file (devicemap.json), defines device types, connection relationships, routing information
- **Phased Configuration Management**: Supports independent configurations for 4 experimental stages, including device mapping table, physical layer configuration, batch script version management
- **Configuration Validation Mechanism**: Automatically validates configuration file completeness and consistency at startup, including port conflict detection, connectivity verification

#### 2.4.2 Device Discovery and Mapping
- **Device Type Recognition**: Automatically recognizes three device types: hosts, switches, routers and allocates corresponding functional modules
- **Port Mapping Management**: Maintains device number to port number mapping relationship, supports dynamic port allocation and conflict detection
- **Topology Relationship Maintenance**: Real-time maintenance of physical connection relationships between devices, supports dynamic awareness of topology changes

### 2.5 Command Line Interface and Control Module

#### 2.5.1 Startup Control System
- **Phased Startup**: Specifies simulation stage (2-4) through command line parameters, automatically loads corresponding configuration and starts relevant functional modules
- **Batch Processing Integration**: Supports automatic execution of Windows batch files, implements one-click startup and shutdown operations
- **Error Handling Mechanism**: Automatic detection and prompting of exception situations during startup such as port occupancy, configuration errors

#### 2.5.2 Interactive Console
- **Real-time Command Interaction**: Provides command line interface, supports device status query, parameter adjustment, manual data sending
- **Status Display Function**: Real-time display of key information such as routing tables, port address tables, device connection status
- **Debug Mode Support**: Provides detailed debug information output, supports single-step execution and breakpoint debugging