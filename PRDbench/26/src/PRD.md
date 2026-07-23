# Office Automation System (OA) - Overall Design Based on Workflow Technology PRD (Product Requirements Document)

## 1. Requirement Overview

1. This OA system targets government agencies, educational institutions, enterprises, and public institutions. It adopts a multi-layer architecture with key characteristics being high modularity, strong scalability, and support for high concurrency and high security. By integrating advanced workflow technology, it aims to digitalize, visualize, and automate the entire process management of organizational business processes.

2. The core objective of the system is to cover common organizational scenarios such as document circulation, approval, schedule/meeting management, bulletin boards, and user task management, supporting flexible process customization, strict permission control, and full-process traceability.

3. Security is a fundamental design principle of this system, employing a comprehensive security framework such as a fine-grained permission system and data encryption to meet the information security compliance requirements of politically sensitive or classified environments.

4. The workflow engine will support complex process orchestration, visual process monitoring, automatic node assignment, exception alerts, and real-time tracking and tracing of business process execution status and historical records.

5. The system uses the database file `oa_system.db` to store all business data.

## 2. Functional Requirements

### 2.1 User and Permission Management Module

User and Organizational Structure Management

Supports multi-level organization/department modeling, position systems, and batch import/export of personnel.

Supports decoupled mapping between positions/roles and permission points, with clear permission inheritance/override policies.

Access Control System (RBAC + ABAC)

Resource granularity includes documents, tasks, process nodes, meetings, announcements, etc.

User permissions are dynamically combined based on roles and attributes (e.g., level, position, department), enabling precise authorization down to the button level.

The system must verify user permissions, block unauthorized operations, and display a clear "insufficient permissions" message.


Permission Change and Approval

Users initiate permission change requests, which are approved by administrators.

Personal Information Management

Supports password change functionality, requiring input of both the current and new passwords, including password verification and confirmation steps, with a confirmation message displayed upon successful password change ("Password changed successfully").
Supports user logout functionality, displays a logout confirmation message, and clears the login status.

### 2.2 Workflow Management Subsystem

Process Definition and Template Management

Visual process modeling tool (drag-and-drop, node parameter editing), allowing saving as process templates.

Supports modeling of parallel flows, conditional branches, loops, and sub-processes, accommodating highly complex business processes.

Pre-configured standard process templates for common scenarios like document approval, leave requests, expense reimbursement, and item requisition.

The workflow template list must display at least 2 pre-configured templates, with each template showing at least 5 columns of information: ID, Name, Code, Category, and Status.

Process Instantiation and Execution

Supports users creating new documents/business processes based on templates, with dynamic process instantiation.

Supports process initiation, automatic task assignment at nodes (based on organizational structure/dynamic rules).

Supports multiple signers per node, co-signing/or-signing, additional signers, forwarding, withdrawal, rejection, and urgent processing operations.

Process Monitoring and Tracking

Administrators can monitor the running status of all process instances in real-time, with visual display of current nodes, progress, and historical paths; abnormal nodes are highlighted.

Historical process trail query, process cold start/suspension/resumption, process timeout warnings, and support for export (CSV).

Document Tracking and Full-Process Logging

Full traceability of each processing step, including responsible person, operation time, and results; allows retrospective checking.

Automatic synchronization of document status; supports comparison and rollback of historical versions, preventing tampering.

### 2.3 Business Function Modules

Document Circulation / Creation and Approval

Supports creation of various document types (requests, reports, outgoing documents, incoming documents, contracts, etc.), automatically routed according to defined processes.

Supports document template/attachment upload and body text editing.

Approval and comment entry by internal/external users, with traceable records.

User Task List (To-Do)

Real-time generation of pending task lists, supports one-click access to task details, card-style display of processes, and batch operations.

Filterable (by process type, time, priority level), supports message notifications.

Meeting Management Module

Create, schedule, and publish meetings; supports inviting multiple participants, setting agendas, uploading meeting minutes, and managing attachments.

Supports meeting check-in, topic decision-making, real-time voting, automatic generation of meeting summaries, and prompts for unread/unsigned items.

Bulletin Board Module

Supports scheduled release of announcements/regulations/notifications, with tiered visibility settings (targeting departments/positions/all users).

Reading confirmation for announcements, supports comments and feedback, and statistics on read rates.

Process Operation Monitoring Dashboard

Statistics on multi-dimensional operational data such as process initiation volume, circulation time, processing bottlenecks at nodes, common exceptions, and approval efficiency.

Data exportable, supports custom reports.

### 2.4 Security and Compliance Assurance

Fine-Grained Permission Control

All functional and data access requires EXPLICIT permission verification; supports secondary verification for sensitive operations.

Dynamic permission changes take effect immediately, blocking unauthorized operations in real-time.

Data Encryption / Channel Security

All transmissions use HTTPS + TLS 1.2 or higher encryption; core data areas employ database encryption (optional field-level encryption, Transparent Data Encryption - TDE).

Supports data masking (for sensitive fields like name, ID number, contact information) and auditing.

Log Auditing and Compliance

Persistent retention of all key operation logs for both users and administrators.

Supports storage and access isolation of logs by role and data type.

Error Handling
The system must handle invalid parameters gracefully, display clear error messages (e.g., "User does not exist"), and ensure the program continues to run without crashing.

### 2.5 Database and Storage

Business Data Model

Encompasses relational models for Users, Departments, Roles, Permissions, Documents (body + attachments), Process Definitions, Process Instances, Operation Logs, Announcements, Meetings, Files, etc.

Table structure design must meet requirements for high scalability, high consistency, and high concurrency.

Database Access and Abstraction

All data access is validated through the business layer, using ORM methods (e.g., SQLAlchemy, Django ORM).

Supports database sharding and partitioning (optional for large-scale organizations), read-write separation, and regular backup of critical data.

File/Attachment Storage

Supports local encrypted storage, with metadata linked to business data.