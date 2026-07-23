# Logistics Center Site Selection System PRD

## 1. Requirement Overview
This project aims to develop a logistics center site selection optimization system based on mathematical modeling and machine learning, providing scientific logistics distribution network planning solutions for McDonald's chain stores in Anhui Province. The system integrates the centroid method and K-means clustering algorithm, combined with geographic information system analysis. Through multi-dimensional data modeling and visualization display, it provides data-driven site selection recommendations for logistics distribution decisions, achieving the dual objectives of minimizing distribution costs and maximizing service efficiency.

## 2. Basic Functional Requirements

### 2.1 Data Management Module
- Support reading McDonald's store geographic location and weight data from Excel files, containing four core fields: address, longitude, latitude, and weight
- Implement data quality validation mechanisms, including longitude and latitude coordinate validity checks (longitude: 73-135, latitude: 3-54), weight data non-negativity verification, and data integrity validation (no null values)
- Provide data preprocessing functions: weight normalization processing (converted to probability distribution), coordinate standardization (using StandardScaler), outlier detection and processing
- Support multiple data format compatibility, ensuring seamless integration with existing Excel files

### 2.2 Single Centroid Method Site Selection Module
- Implement centroid method algorithm based on weighted average, calculation formulas:
  - Centroid Longitude = Σ(longitude_i × weight_i) / Σ(weight_i)
  - Centroid Latitude = Σ(latitude_i × weight_i) / Σ(weight_i)
- Provide global optimal site selection results, outputting optimal logistics center geographic coordinates
- Implement visualization display functions: scatter plot drawing (store points in blue, centroid point in red), axis labels (longitude, latitude), legend annotation
- Support Chinese font display, ensuring correct rendering of chart labels

### 2.3 K-means Clustering Analysis Module
- Implement automatic optimal cluster number determination function:
  - Silhouette coefficient analysis: calculate silhouette coefficients for different K values (2-92)
  - Optimal K value selection: select K value with maximum silhouette coefficient as final cluster number
  - Visualization analysis: plot relationship between K values and silhouette coefficients, assisting decision-making
- Provide K-means clustering algorithm implementation:
  - Use scikit-learn's KMeans algorithm for clustering analysis
  - Standardize longitude and latitude coordinates (using StandardScaler) to ensure clustering effectiveness
  - Calculate center point coordinates for each cluster
  - Assign each store to nearest cluster center
- Output clustering results: cluster center coordinates, cluster member assignment, results exported as Excel files

### 2.4 Partition Centroid Calculation Module
- Independently calculate centroid for each cluster area, applying single centroid method algorithm within each cluster
- Provide comparative analysis between global centroid and partition centroids, displaying differences in different site selection strategies
- Support multi-scenario site selection plan comparison, providing data support for decision-making

### 2.5 Result Visualization Module
- Implement clustering result visualization functions:
  - Scatter plot: display store distribution of different clusters in different colors
  - Cluster centers: display each cluster center position with red X markers
  - Color bar: display cluster numbers, facilitating distinction
  - Chinese font support: ensure all labels display correctly
- Provide analysis chart generation functions:
  - Silhouette coefficient graph: relationship curve between K values and silhouette coefficients
  - Centroid comparison graph: position comparison between global centroid and partition centroids
  - Support chart saving as high-quality image formats

### 2.6 Data Export Module
- Support Excel file export functions:
  - Clustering results: each cluster in independent worksheet, containing all store coordinates of that cluster
  - Centroid coordinates: export longitude and latitude information of all centroid points
  - Analysis report: containing algorithm parameters, result summary, performance metrics
- Provide console output functions: global centroid coordinates, optimal cluster number K value, each cluster center coordinates, silhouette coefficient analysis results

## 3. Data Requirements

### 3.1 Input Data Format
- **Store data file** (total_data.xlsx): contains four fields - address (string), longitude (floating-point number, range 73-135), latitude (floating-point number, range 3-54), weight (positive integer)
- **Data quality requirements**: completeness (all fields cannot be empty), accuracy (longitude and latitude coordinates must be accurate), reasonableness (weight values reflect actual distribution requirements), consistency (coordinate system unified as WGS84)

### 3.2 Output Data Format
- **Clustering result file** (cluster_points.xlsx): each cluster in one worksheet (Cluster 1, Cluster 2, …), containing longitude coordinate and latitude coordinate columns
- **Analysis result output**: console output of global centroid coordinates, optimal cluster number K value, each cluster center coordinates, silhouette coefficient analysis results

### 3.3 Data Scale and Performance Requirements
- **Data scale**: 92 McDonald's stores, entire geographic scope of Anhui Province, 4-dimensional data (address, longitude, latitude, weight), clustering range 2-92
- **Performance requirements**: single clustering analysis time <30 seconds, memory usage <500MB, coordinate precision retained to 6 decimal places, support batch data processing

## 4. System Architecture

### 4.1 Module Division
```
Logistics Center Site Selection System
├── Data Management Module
│   ├── Data Reading
│   ├── Data Preprocessing
│   └── Data Validation
├── Algorithm Calculation Module
│   ├── Single Centroid Method
│   ├── K-means Clustering
│   └── Silhouette Coefficient Analysis
├── Visualization Module
│   ├── Scatter Plot Drawing
│   ├── Clustering Result Display
│   └── Analysis Chart Generation
└── Result Output Module
    ├── Excel Export
    ├── Console Output
    └── Image Saving
```

### 4.2 Technology Stack and Dependencies
- **Programming Language**: Python 3.8+
- **Core Libraries**: pandas (data processing), numpy (numerical computation), scikit-learn (machine learning algorithms), matplotlib (data visualization), openpyxl (Excel file operations)
- **Configuration Requirements**: Chinese font file support, sufficient disk space, environment supporting matplotlib graphic display