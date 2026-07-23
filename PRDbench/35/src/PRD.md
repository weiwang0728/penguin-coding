# Enterprise Fixed Asset Management System PRD (Product Requirements Document)
---
### 1. Requirements Overview

This project aims to design and develop an enterprise fixed asset management system to achieve comprehensive digital management of the entire lifecycle of fixed assets within the enterprise. It will comprehensively enhance the efficiency, accuracy, and traceability of asset management, effectively solving problems such as information silos, non-standardized processes, and inaccurate data in traditional asset management.

---

### 2. Functional Requirements
#### 2.1 User and Permission Management
- **User Authentication and Login Management**
  - Input of user unique identifier (username), password, role type, affiliated department, and account status (Active/Locked);  
  - User login, logout, and identity verification;   
  - Password encrypted storage, default password "123456", Token validity period 1 day;
- **User Information Management** 
  - Create, Read, Update, Delete (CRUD) operations for users, supporting role assignment (SYSTEM/IT/ASSET/STAFF); 
  - Users must be associated with a department, the admin user and the currently logged-in user cannot be deleted;
  - User list query: SYSTEM permission users can view the full user list, with each user's information including name, department, role, and is_active fields. STAFF permission users cannot access the user management interface.
  - User lock/unlock function: SYSTEM permission users can lock or unlock user accounts; locked users cannot log in.
  - Password change functionality, verifying the correctness of the old password, and encrypting and storing the new password;
- **Hierarchical Permission Control**
- System Administrator (SYSTEM): Possesses the highest system permissions, can manage all users and departments;   
- IT Administrator (IT):  Responsible for system technical maintenance and user management; 
- Asset Administrator (ASSET):  Responsible for asset management, allocation, and approval;   
- Regular Staff (STAFF):  Can apply for asset allocation and view asset information relevant to themselves.
#### 2.2 Department Organizational Structure Management
- **Multi-level Department Tree Structure**   
- Supports unlimited levels of department structure; each department can have a parent department;
- Department name management, provides root department query functionality;  
- Uses MPTT tree structure for efficient hierarchical querying and management.
- **Department Asset Administrator Configuration**
- Each department can designate a user with ASSET permissions as the asset administrator;  
- Supports searching for asset administrators in superior departments; implementing a permission inheritance mechanism;   
- If the current department lacks an asset administrator, automatically searches superior departments.
#### 2.3 Asset Category and Attribute Management
- **Asset Category Tree Management**
- Supports unlimited levels of asset category structure, with unique validation for category names;   
- CRUD operations for categories; checks for associated assets when deleting a category;   
- Provides category tree query interfaces, supporting hierarchical display and management.
- **Custom Attribute Extension**
- Supports adding custom attributes for all assets, with unique validation for attribute names;  
- Batch update functionality for attribute values, supporting flexible business requirement expansion;    
- Management of associations between custom attributes and asset categories.
#### 2.4 Asset Full Lifecycle Management
- **Basic Asset Information Management**   
- Asset Name (required), Asset Description, Asset Value (required), Service Life (default 5 years);   
- Asset Category (required), Asset Status (IDLE/IN_USE/IN_MAINTAIN/RETIRED/DELETED);   
- Accountable Person (User), Entry Time, Custom Attributes.
- **Asset Tree Structure Management**   
- Supports parent-child relationship management for assets; assets can form a tree structure; 
- Child assets inherit the status and accountable person of the parent asset; supports batch operations on entire asset trees;   
- Prevents circular references, ensuring data integrity.
- **Asset Value Calculation and Depreciation**   
- Automatically calculates current asset value: Current Value = Original Value × (Remaining Service Life / Total Service Life);    
- Calculates depreciation annually; value of retired assets is 0; supports real-time calculation.
- **Asset Operation Processes**   
- Asset CRUD, Asset Query (supports multi-condition combined queries), Asset Allocation, Asset Retirement;   
- Query for available assets, Query for asset history records;    
- Query results are filtered by department permissions, ensuring data security.
#### 2.5 Request Application and Handling Process
- **Request Type Definition**   
- Allocation Request (REQUIRE):** Apply to allocate a certain type of asset;  
- Maintenance Request (MAINTAIN):** Apply to maintain an asset.*   
- Transfer Request (TRANSFER):** Apply to transfer an asset to another use;   
- Return Request (RETURN):** Apply to return an asset to the storage.
- **Request Process Management**   
- Initiation:** User initiates a Request application; the system checks for Request conflicts;   
- Handling:** Asset administrator reviews and processes the Request, supporting batch processing;  
- Completion:** Request status is updated to Success or Failure, recording the processing result.
- **Request Conflict Handling**  
- Prevents the same user from initiating multiple pending Requests for the same asset;   
- Provides conflict prompt information, ensuring process standardization.
- **Request Query and Management**  
- Query for pending Requests, Query for submitted Requests;  
- Request deletion functionality, supporting full lifecycle management of requests.
#### 2.6 History Records and Operation Tracking
- **Asset Change History Records**   
- Records all change operations for assets: Change Time, Change user, Change Type, Change Details;   
- Supports history record querying, providing complete change traceability.
- **System Operation Logs**   
- Records user login, logout, and important operations (Create, Update, Delete);  
- Supports log querying and export, providing system audit functionality;  
- Operation logs are associated with user permissions, ensuring data security.
#### 2.7 Data Permissions and Security Control
- **Role-based Permission Verification**   
- Data access permission control; users can only access data from their own departmen;  
- Asset lists are filtered by department; request processing follows department permissions.
- **Data Integrity Assurance**   
- Model field validation, business logic validation, permission validation;  
- Data integrity checks to prevent data inconsistency;   
- Supports data backup and recovery, ensuring data security.
### 3. Technical Requirements
- **Programming Language:** Python 3.7+
- **Authentication & Security**:
 - Hierarchical permission control, data access permission filtering
 - Operation log recording, system audit functionality
- **Tree Structure Management**:
    *   Supports unlimited levels for departments and asset categories
*   Prevents circular references, ensures data integrity*   
**History Records & Tracking:**
   - Operation log recording, supports query and export
    - Complete change traceability functionality
### 4. Data Model Design
#### 4.1 Core Data Tables
- **User Table (User):** Basic user information, role, department association*   
- **Department Table (Department):** Multi-level department tree structure*   
- **Asset Category Table (AssetCategory):** Multi-level asset category tree structure*   
- **Asset Table (Asset):** Basic asset information, status, value, category association  - **Custom Attribute Table:** Supports asset attribute extension
- **Request Table (Issue):** Request application and processing records
#### 4.2 Data Initialization
- Create admin superuser, root department, root asset category
- Create basic custom attributes, test data, and users
---