# Keigo Higashino Novel Text Mining and Semantic Analysis Tool PRD 
## 1. Requirement Overview
This tool aims to provide literary researchers and text mining analysts with deep text analysis capabilities for Keigo Higashino's novels. It supports automatically extracting key entities (characters, locations, time, professions) from novel texts, statistically analyzing entity frequency distributions, building semantic vector models, and performing character relationship inference and similarity analysis. The tool is implemented through command-line interaction, with core functions including entity recognition and extraction, frequency statistical analysis, semantic vectorization modeling, relationship inference analysis, and result presentation.
## 2. Basic Functional Requirements
### 2.1 Entity Recognition and Extraction
- Provides a command-line text file input interface, supports specifying the novel file path, and automatically detects file encoding format (GBK/UTF-8).
- Uses a professional Chinese word segmentation tool to preprocess the novel text, supporting mixed recognition of Chinese and Japanese person names.
- Automatically identifies four types of key entities based on part-of-speech tagging: Person Names (nr), Geographical Names (ns), Time Expressions (t), Professional Titles (nn).
- Displays dynamic progress prompts during entity extraction (e.g., "Processing the 3rd novel: 45%"), supports interrupt operations (users can press Ctrl+C to terminate processing).
- Returns extraction status (success/failure), with specific reasons required for failures (e.g., file encoding error, word segmentation failure, insufficient memory).
- Automatically saves the last 10 entity extraction records, supports users quickly reusing historical extraction results via numbering.
- Output entity list includes entity name, type, occurrence frequency, and contextual information (8 characters before and after).
### 2.2 Frequency Statistics and Distribution Analysis
- Based on the extracted entity list, statistically analyzes the occurrence frequency of each entity type by novel, generating frequency rankings.
- Provides preset entity type filtering functions: character filtering, location filtering, time filtering, profession filtering.
- Supports user-defined frequency range filtering (input minimum frequency threshold), filtering results must include entity name, belonging novel, occurrence frequency, and entity type label.
- Allows combining filter conditions, adding dimensions such as entity type, belonging novel, etc., with support for "AND/OR" logical relationships between conditions.
- Statistical results must support ascending/descending sorting (by frequency or user-specified field) and can be displayed in pages (10 items per page, supports previous/next page navigation).
### 2.3 Semantic Vectorization and Similarity Analysis
- Supports users selecting analysis targets from extracted entities (e.g., "Yukiho", "Kyoichiro Kaga"), targets must be character entities.
- Automatically uses Word2Vec algorithm to train word vector models, model parameters: vector dimension 300, window size 5, minimum word frequency 20, worker threads 8.
- Uses cosine similarity algorithm to calculate semantic similarity between target entities and other entities, must output top 10 similarity ranking results.
- Performs deep analysis on entities with highest similarity (similarity > 0.7), outputs contextual features and relationship networks of these entities.
### 2.4 Relationship Inference and Pattern Discovery
- Supports users inputting analogy inference queries, format: "The relationship between A and B is similar to the relationship between C and whom?".
- Uses vector space analogy inference algorithm (D = C + B - A) to calculate target entity D, searches for best matches within character entity scope.
- Automatically identifies relationship patterns, outputs relationship type labels (e.g., "master-apprentice relationship", "lover relationship", "adversarial relationship").
- Performs statistical analysis on identified relationship patterns, outputs pattern frequency and distribution patterns.
### 2.5 Command-Line Interaction and Result Presentation
- Main interface uses menu-based interaction, includes function options: [1] Input novel file path [2] Entity recognition extraction [3] Frequency statistical analysis [4] Semantic similarity analysis [5] Relationship inference analysis [6] View history records [7] Exit.
- User input requires validity verification (e.g., options must be numbers 1-7, file paths must exist, entity names must be in extraction results), displays Chinese prompts for erroneous inputs.
- When generating analysis results, users can choose whether to display using text-based table format.
- All output results support saving as TXT files (users can specify save path), files must include extracted entities, statistical results, similarity matrices, relationship inference results, and text-based tables.
## 3. Data Requirements
### 3.1 Input Data
- Novel text files: Saved in txt/ folder, containing Keigo Higashino's novel works, format: .txt files, encoding: GBK or UTF-8, data scale: 50+ novels approximately 10 million characters.
- Entity attribute files: Saved in the attrs/ folder, including names.txt (person names), places.txt (geographical names), times.txt (time expressions), works.txt (professional titles), and other entity attribute files.
- Custom dictionary file: wordslist.txt file, used to improve word segmentation performance.
- External dependencies: Chinese word segmentation dictionary, Japanese person name recognition model, part-of-speech tagging model.
### 3.2 Intermediate Data
- Word segmentation results: Word-segmented text processed by professional tools, containing part-of-speech tagging information.
- Entity extraction data: Lists and frequency information of four entity types: characters, locations, time, professions.
- Manually annotated data: Entity lists verified and corrected manually, containing entity type annotations and importance scores.
### 3.3 Output Data
- Statistical reports: Entity frequency statistical tables for each novel, high-frequency entity rankings, entity distribution analysis reports.
- Semantic models: Trained word vector model files, word similarity matrices, semantic space mapping data.
- Analysis results: Character similarity analysis reports, relationship inference case collections, pattern discovery summaries.
## 4. Performance Requirements
### 4.1 Processing Capability
- Supports processing text data exceeding 10 million characters, single novel processing time not exceeding 5 minutes.
- Entity recognition accuracy: Person names ≥ 90%, Location names ≥ 85%, Time words ≥ 80%, Professions ≥ 75%.
- Semantic similarity calculation accuracy ≥ 85%, relationship inference results have good interpretability.
### 4.2 Scalability
- Supports adding new entity types, supports processing works by other authors.
- Supports integrating new algorithm models (e.g., FastText, BERT, etc.).
- Supports custom analysis dimensions and filter conditions.