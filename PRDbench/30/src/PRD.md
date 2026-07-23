# PRD: Knowledge Graph Completion System

## 1. Overview of Requirements

This project requires the implementation of a knowledge graph completion system based on the TransE algorithm, adhering to the following core requirements:
1.  **Pure Python Implementation**: An end-to-end implementation using only Python for data processing, model training, and evaluation.
2.  **Local Execution**: All functionalities must be executable locally via a command-line interface (CLI), with support for mainstream operating systems.
3.  **Complete Functional Loop**: A closed-loop workflow comprising five core modules: Data Loading, Model Training, Link Prediction, Evaluation, and Result Output.
4.  **Verifiability**: Each functional module must produce clear, verifiable outputs or intermediate files to support phased validation.

## 2. Basic Functional Requirements

### 1. Data Loading and Preprocessing

**Function Description**:
-   Load the four primary files of the FB15K-237 dataset.
-   Establish bidirectional maps between entity/relation names and their corresponding IDs.
-   Validate data integrity and consistency.

**Input Files**:
- `src/data/entity2id.txt` - Entity mapping file (each line: entity_name\tID)
- `src/data/relation2id.txt` - Relation mapping file (each line: relation_name\tID)
- `src/data/train.txt` - Training data file (each line: head_entity\ttail_entity\trelation)
- `src/data/test.txt` - Test data file (each line: head_entity\ttail_entity\trelation)

**Output Files**:
- `entity2id.txt` - Entity mapping file
- `relation2id.txt` - Relation mapping file

**Implementation Methods**:
-   Implement a parser to handle the various input file formats.
-   Construct mapping tables for entity and relation IDs.
-   Implement an exception detection mechanism to handle missing IDs and invalid triples.

### 2. TransE Model Training

**Function Description**:
-   Initialize and normalize entity and relation vector embeddings.
-   Allow configuration of training process parameters.
-   Generate negative samples for training and calculate the loss.
-   Monitor the training process.

**Implementation Methods**:
-   Initialize entity and relation embeddings using a uniform distribution.
-   Implement strategies for batch sampling and negative sample generation.
-   Employ a margin-based loss function with Stochastic Gradient Descent (SGD) for optimization.
-   Record loss values in real-time and save checkpoints for the best-performing model.

### 3. Link Prediction and Evaluation

**Function Description**:
-   Support multiple link prediction tasks.
-   Calculate dissimilarity scores and rank candidates.
-   Calculate standard evaluation metrics.

**Implementation Methods**:
-   Implement a function to calculate L2 distance as the dissimilarity score.
-   Develop a mechanism to generate Top-N ranked prediction results.
-   Implement the calculation logic for Mean Rank and Hits@10 evaluation metrics.

### 4. Result Output

**Function Description**:
-   Persist the trained model embeddings.
-   Visualize the training process.
-   Generate a final evaluation report.

**Implementation Methods**:
-   Implement a function to export the trained embeddings to files.
-   Use Matplotlib to plot and save the training loss curve.
-   Generate a final evaluation report in JSON format.

## 3. Data Requirements

### 1. Input Data Specifications

| File Type | Format Requirements |
|-----------------|------------------------------------------|
| Entity Mapping | Each line: `entity_name\tID`              |
| Relation Mapping | Each line: `relation_name\tID`            |
| Training/Test Data | Each line: `head_entity\ttail_entity\trelation` |

**Quality Requirements**:
-  Entity and relation IDs must be contiguous and gapless.
-  There must be no overlapping triples between the training and test sets.
-  All entities and relations within triples must exist in the mapping files.

### 2. Output Data Specifications

| Output Type | Format Description                           |
|-----------------|-------------------------------------------|
| Entity Vector File | Each line: ID followed by a 50-dimensional floating-point vector.          |
| Relation Vector File | Each line: ID followed by a 50-dimensional floating-point vector.           |
| Loss Curve Plot | A PNG image file.                                  |
| Evaluation Report | Key-value pairs of evaluation metrics in JSON format.                |
