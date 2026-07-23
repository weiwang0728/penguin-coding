# Local Search Engine System PRD Based on TF-IDF Algorithm

## 1. Overview of Requirements
This project aims to develop a local search engine system based on the TF-IDF algorithm, implementing a complete workflow from web crawler to information retrieval. The system adopts a classical search engine architecture, comprising three core components: web crawler, information organization, and query system. It supports Chinese word segmentation, provides both command-line and Web interface access, utilizes the lightweight SQLite database to ensure ease of deployment and portability, and offers a complete solution for information retrieval and text mining.

## 2. Basic Functional Requirements

### 2.1 Web Crawler Module
- **Web Crawling Functionality**
  - Recursively crawls relevant web pages starting from a specified seed URL
  - Supports configurable crawl quantity limit (default: 1,000 pages, configurable range: 1-10,000)
  - Automatically extracts links from web pages, implements breadth-first search algorithm
  - Filters invalid pages (404, 403 error pages) and duplicate URLs
- **Content Extraction and Processing**
  - Uses the requests library to download web content, handles web page encoding automatically
  - Uses BeautifulSoup to parse HTML content, extracts page titles and main text
  - Focuses on extracting content in `<p>` tags within `<article>` tags, filters out blank documents
  - Uses regular expressions to extract `<a href>` links, handles relative and absolute paths automatically
- **Queue Management and Control**
  - Uses deque (double-ended queue) to manage URLs to be crawled, uses set to record visited URLs
  - Supports timeout setting (default: 30 seconds) to avoid prolonged waiting
  - Provides crawl progress display and error logging functionality

### 2.2 Information Organization and Indexing Module
- **Database Design and Storage**
  - Document table (doc): stores web page URLs and titles, automatically generates document IDs
  - Vocabulary table (word): builds inverted index, records word positions in documents
  - Supports transaction commit to ensure data consistency
- **Chinese Word Segmentation and Index Building**
  - Uses jieba for Chinese word segmentation, supports mixed Chinese and English content
  - Constructs inverted index structures to optimize search performance
  - Supports vocabulary updates and appends to achieve incremental index building
- **Data Management Features**
  - Create and delete data tables, query total document count
  - Query related document lists based on vocabulary
  - Supports data persistence and backup/restore

### 2.3 Query System Module
- **TF-IDF Algorithm Implementation**
  - TF (Term Frequency): calculates frequency of a word in a document
  - IDF (Inverse Document Frequency): calculates inverse document frequency
  - Relevance score calculation: `score = tf * log(N/df)`, where N is total number of documents, df is the number of documents containing the word
- **Search Functionality**
  - Supports mixed Chinese and English search, uses jieba for keyword segmentation
  - Supports multi-keyword search, implements cumulative scoring mechanism
  - Sorts results in descending order of TF-IDF score, returns up to 20 most relevant results
  - Implements document deduplication and sorting, handles cases with no search results
- **Interface Design**
  - Command line interface: `python3 -m search <keyword> <database_path>`
  - Function interface: `run(keyword)` returns a list of search results containing URL and title
  - Supports search keyword length limit (no more than 100 characters)

### 2.4 Presentation Module
- **Presentation Features**
  - Displays search results, including URL and title information
- **Service Management**
  - Supports service start and stop
  - Provides basic error handling and status monitoring

### 2.5 System Monitoring and Logging Module
- **Crawling Monitoring**
  - Real-time display of crawl progress
  - Error logging and exception handling
  - Performance statistics and resource usage monitoring
- **Search Monitoring**
  - Search request statistics and response time monitoring
  - User behavior analysis and query pattern statistics
  - System performance metrics collection

## 3. Technical Requirements

### 3.1 Development Environment
- **Programming Language**: Python 3.6+
- **Core Dependencies**:
  - Network requests: requests==2.21.0
  - HTML parsing: beautifulsoup4==4.6.3
  - Chinese word segmentation: jieba==0.39
  - Web framework: Flask==1.0.2
- **Database**: SQLite3 (lightweight, no extra configuration needed)

### 3.2 Algorithm Implementation
- **TF-IDF Algorithm** (Term Frequency-Inverse Document Frequency)
- **Breadth-First Search Algorithm** (web crawling)
- **Inverted Index Structure** (information retrieval optimization)

### 3.3 System Requirements
- Supports Linux/macOS/Windows multiplatform
- Minimum memory requirement: 2GB
- Minimum disk space: 10GB
- Network connectivity (required during crawling stage)

## 4. Data Requirements

### 4.1 Input Data
- **Seed URL**: Complete HTTP/HTTPS URL format, e.g., `https://blog.csdn.net`
- **Crawling Configuration**: Number of pages to crawl (default 1,000, range 1-10,000), timeout setting (default 30 seconds)
- **Search Keywords**: Supports Chinese and English, multi-keyword combinations, maximum length of 100 characters

### 4.2 Output Data
- **Search Results**: List of documents with URL and title, format as `[(url, title), ...]`
- **Database File**: SQLite3 format, including document and vocabulary tables, supports data persistence

## 5. System Architecture

### 5.1 Code Structure
```
search-engine/
├── spider/           # Crawler module
│   ├── __init__.py
│   ├── __main__.py
│   └── spider.py
├── search/           # Search module
│   ├── __init__.py
│   ├── __main__.py
│   ├── search.py
│   └── WEBUI/        # Web interface
├── database/         # Database module
│   ├── __init__.py
│   ├── db.py
│   └── word.db
├── requirements.txt
└── README.md
```

### 5.2 Module Interface Design
- **Crawler Module Interface**: `python3 -m spider <seed_url> <database_path> [-c <count>]`
- **Search Module Interface**: `python3 -m search <keyword> <database_path>`
- **Web Service Interface**: `python3 -m search` (start Web service)

### 5.3 Data Flow
1. **Crawling Phase**: Seed URL → webpage download → content extraction → link extraction → queue management
2. **Indexing Phase**: document storage → Chinese word segmentation → inverted index construction → data persistence
3. **Searching Phase**: keyword input → word segmentation → TF-IDF calculation → result sorting → return results

## 6. Testing and Quality Assurance

### 6.1 Testing Requirements
- **Unit Testing**: crawler functionality testing, search algorithm testing, database operation testing
- **Integration Testing**: end-to-end search flow testing, performance testing, error handling testing
- **Local Testing**: supports running on local file system, does not rely on external network services, provides test data sets

### 6.2 Error Handling
- Network connection exception handling (timeout, connection failure, etc.)
- Database operation exception handling (lock table, insufficient disk space, etc.)
- Input parameter validation (URL format, keyword length, etc.)
- Graceful error messages and logging

### 6.3 Configuration Management
- Supports configuration file and environment variable configuration
- Command line parameter configuration and default value settings
- Dynamic adjustment of runtime parameters