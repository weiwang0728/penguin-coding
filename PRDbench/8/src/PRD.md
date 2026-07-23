# Software Development Project Management Information System PRD (Product Requirements Document)

---

## 1. Requirements Overview

This project aims to construct a "Software Development Project Management Information System" oriented towards software development enterprises, achieving informatized and process-driven efficient management throughout the entire project lifecycle. The system deeply integrates the nine major knowledge areas of project management (integration, scope, schedule, cost, quality, human resources, communication, risk, procurement) and incorporates the characteristics of software development processes, supporting full lifecycle management from requirements, planning, execution, configuration, acceptance to delivery. It enhances project production efficiency, improves delivery quality, reduces management costs, and builds sustainable competitiveness for enterprises.

The system emphasizes the design of core subsystems including requirements management, planning management, and configuration management. All functions are primarily process-driven and wizard-based, supporting both agile and traditional development methods, assisting enterprises in achieving scientific, measurable, and traceable project management.

---

## 2. Functional Requirements

### 2.1 Organization and Project Management

- **Organizational Structure Management**
    - Multi-department/multi-project team structure modeling, supporting department/team adjustments
    - Department information includes: department name, description, manager, creation time, update time
    - Supports creating, editing, and deleting departments
    - Personnel information management, position/skill tag maintenance

- **User Management**
    - User information includes: username, password, full name, email, phone, department, position, role, status
    - Supports creating, editing, and deleting users
    - Role management: super administrator, regular user, etc.

- **Project Full Lifecycle Management**
    - Project data maintenance (name, description, type, importance level, status, etc.)
    - Project status includes: planning, in_progress, testing, completed, closed, cancelled
    - Project start/end, phase division, status changes, archiving and retrieval

---

### 2.2 Requirements Management Subsystem

- **Requirements Collection and Decomposition**
    - Supports requirement source classification: customer (customer), market (market), internal (internal), regulation (regulation)
    - Requirement levels: epic, feature, user story
    - Requirement priorities: low, medium, high, critical
    - Requirement information includes: title, description, project ID, source, level, priority, creator ID, status

- **Requirements Workflow**
    - Requirement lifecycle states include: new, reviewing, approved, pending_dev, in_dev, testing, completed, rejected
    - Supports creation, editing, and deletion of requirements
    - Supports requirement state transition and review operations
    - Change control: requirement change process, change reason/impact analysis/approval workflow

- **Requirements Traceability**
    - Historical status records, traceable to responsible persons and operation time
    - Automatic association between requirements and tasks, use cases, and defects
    - Supports requirement detail viewing and traceability

---

### 2.3 Planning Management Subsystem

- **Planning and Progress Management**
    - Plan information includes: plan name, project ID, start date, end date, status, progress, task list, resource list
    - Supports creation, editing, and deletion of plans
    - Supports multi-level plan decomposition by phase/milestone/task
    - Task assignment, multiple responsible persons, task priority adjustment
    - Task information includes: task name, description, responsible person, estimated hours, actual hours, status, completion percentage
    - Progress reporting supports fields such as actual work hours, estimated completion time, completion percentage
    - Supports task creation and progress update operations


---

### 2.4 Quality and Defect Management

- **Quality Management**
    - Configuration of quality objectives and key metrics (e.g., defect density, test coverage, KPIs)
    - Quality baselines and phase-by-phase quality review records, issue summaries
    - Supports viewing of quality metrics and quality reports

- **Defect Tracking**
    - Defect information includes: title, description, project ID, severity, priority, reporter ID, status, creation time
    - Severity: low, medium, high, critical
    - Priority: low, medium, high, critical
    - Supports creating, editing, and deleting defects
    - Supports defect status management
    - Automatic association of defects with requirements, tasks, and submission records

---

### 2.5 System Interaction Interface

- **Main Menu System**
    - On program startup, a clear main menu is displayed, including entry points for all functional modules.
    - Main menu options include: User Management, Organization Structure Management, Project Management, Requirement Management, Planning Management, Quality Management.
    - Supports interactive command line operations, providing clear operational guidance.

- **Operation Processes**
    - All functional modules support basic operations such as create, edit, delete, and view.
    - Provides state transition functionality to support lifecycle management of all entities.
    - Supports data validation and error prompts to ensure data integrity.


## 3. Technical Requirements

### 3.1 System Architecture

- **Architecture Pattern**
    - Data Center: Uses database or .json file approach for stable data storage and retrieval

### 3.2 Data Design

- **Core Data Table Design**
    - Includes: User table, Role table, Project table, Department (Organization) table, Requirements table, Task table, Defect table, Configuration Items table, Planning table, etc.
    - Additional tables can be designed for approval processes, cost statistics, etc. as needed.

    - Each data table must contain corresponding fields as described in the functional requirements (e.g., department name, description, responsible person, creation time, update time, etc.)
    - Core entities require support for historical change tracking, supporting fields for status, operator, and operation time.

### 3.3 Testing and Initialization

- You should design the data storage format yourself and ensure the above functionalities are implemented.
- During system initialization, provide some sample data for testing purposes.

