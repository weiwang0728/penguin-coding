# Test Execution Guide

## Why Do We Need to Run `python src/main.py init` First?

### 1. **Database Table Creation**
```python
def init():
    # Create database tables
    create_tables()  # This creates all necessary database table structures

    # Create default scales
    scale_manager.create_default_scales()
```

### 2. **System Dependencies**
- **Database tables**: The system uses SQLite database to store data and needs to create table structure first
- **Default scales**: The system comes with 3 standard psychological scales, providing basic data for subsequent tests
- **Configuration initialization**: Ensures all configurations and paths are set correctly

### 3. **Importance of Test Execution Order**

#### Wrong Execution Method:
```bash
# ❌ Directly import scale - will fail
python src/main.py scales import-csv evaluation/test_scale.csv
# Error: Database tables don't exist, cannot save scale data
```

#### Correct Execution Method:
```bash
# ✅ Initialize system first
python src/main.py init
# Creates database tables: scales, scale_items, participants, responses, etc.

# ✅ Then import scale
python src/main.py scales import-csv evaluation/test_scale.csv
# Now can successfully save to database
```

### 4. **What the init Command Does Specifically**

1. **Create database table structure**:
   - `scales` table: Store scale basic information
   - `scale_items` table: Store scale items
   - `participants` table: Store participant information
   - `responses` table: Store questionnaire responses
   - `analysis_results` table: Store analysis results

2. **Create default scales**:
   - College Student Attention Stability Scale (8 items)
   - College Student Self-Control Scale (10 items)
   - College Student Emotional Stability Scale (6 items)

3. **Verify system integrity**:
   - Check database connection
   - Verify configuration files
   - Ensure output directories exist

### 5. **Test Scenario Analysis**

#### Typical Shell Interaction Test Flow:
```bash
# Step 1: System preparation
python src/main.py init                    # Required: Create basic environment

# Step 2: Execute specific function
python src/main.py scales import-csv file.csv  # Test target function

# Step 3: Verify results
python src/main.py scales list             # Confirm import success
```

#### Why init Cannot Be Skipped:
- **Database error**: No table structure, cannot save data
- **Configuration missing**: System configuration not initialized
- **Dependency missing**: Missing default scales and other basic data

### 6. **Test Independence Considerations**

Although every test needs init, this is a **system-level prerequisite**, not a test design issue:

- **Real user scenario**: Users also need to initialize when first using the system
- **System architecture requirement**: Database-based systems must create table structure first
- **Function dependency**: Many functions depend on the existence of default scales

### 7. **Optimization Recommendations**

For frequent testing, consider:

```bash
# One-time initialization
python src/main.py init

# Then run multiple tests
python src/main.py scales import-csv test1.csv
python src/main.py scales import-csv test2.csv
python src/main.py data import-participants participants.csv
```

### 8. **Test Result Verification**

Signs of successful init command:
- ✅ Display "System initialization complete!"
- ✅ List created default scales
- ✅ No error information output
- ✅ Exit code is 0

This design ensures the **authenticity** and **reliability** of tests, simulating actual user workflows.