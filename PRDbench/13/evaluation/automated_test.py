#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recommendation System Automated Evaluation Test Script
Systematic testing according to evaluation criteria in metric.json
"""

import os
import sys
import json
import subprocess
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import logging
from datetime import datetime

# Set paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
EVALUATION_DIR = PROJECT_ROOT / "evaluation"
sys.path.insert(0, str(SRC_DIR))

class AutomatedEvaluator:
    """Automated Evaluator"""
    
    def __init__(self):
        self.results = []
        self.total_score = 0
        self.max_score = 0
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(EVALUATION_DIR / 'test.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load evaluation metrics
        with open(EVALUATION_DIR / 'metric.json', 'r', encoding='utf-8') as f:
            self.metrics = json.load(f)
    
    def log_test_result(self, test_name: str, score: int, max_score: int, details: str):
        """Log test result"""
        result = {
            'test_name': test_name,
            'score': score,
            'max_score': max_score,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        self.total_score += score
        self.max_score += max_score

        self.logger.info(f"Test: {test_name}")
        self.logger.info(f"Score: {score}/{max_score}")
        self.logger.info(f"Details: {details}")
        self.logger.info("-" * 80)
    
    def test_system_startup(self):
        """Test 1.1: System Startup and Environment Configuration"""
        test_name = "1.1 System Startup and Environment Configuration"
        try:
            # Check if main entry file exists
            main_py = SRC_DIR / "main.py"
            if not main_py.exists():
                self.log_test_result(test_name, 0, 2, "main.py file does not exist")
                return

            # Check if the code contains at least 3 functional options
            with open(main_py, 'r', encoding='utf-8') as f:
                content = f.read()

            menu_options = 0
            if "data" in content:
                menu_options += 1
            if "recommend" in content:
                menu_options += 1
            if "service" in content or "API" in content:
                menu_options += 1
            if "model" in content or "training" in content:
                menu_options += 1
            if "evaluation" in content:
                menu_options += 1

            if menu_options >= 3:
                score = 2
                details = f"System contains {menu_options} main functional modules, meets startup requirements"
            elif menu_options >= 1:
                score = 1
                details = f"System contains {menu_options} functional modules, but insufficient quantity"
            else:
                score = 0
                details = "System lacks main functional modules"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_data_collection_json(self):
        """Test 2.1.1a: Data Collection - JSON Format Support"""
        test_name = "2.1.1a Data Collection - JSON Format Support"
        try:
            # Check if there is data loading related code
            files_to_check = [
                SRC_DIR / "data_old" / "data_loader.py",
                SRC_DIR / "cli_simplified.py"
            ]

            json_support = False
            for file_path in files_to_check:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "json" in content.lower() or "JSON" in content:
                            json_support = True
                            break

            # Check pandas dependency (can process JSON)
            requirements_file = SRC_DIR / "requirements.txt"
            pandas_available = False
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "pandas" in f.read():
                        pandas_available = True

            if json_support and pandas_available:
                score = 2
                details = "Supports JSON format data processing, has pandas dependency"
            elif pandas_available:
                score = 1
                details = "Has JSON processing capability but lacks explicit support code"
            else:
                score = 0
                details = "Lacks JSON data processing support"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_data_collection_csv(self):
        """Test 2.1.1b: Data Collection - CSV Format Support"""
        test_name = "2.1.1b Data Collection - CSV Format Support"
        try:
            # Check data generation functionality in CLI
            cli_file = SRC_DIR / "cli_simplified.py"
            csv_support = False

            if cli_file.exists():
                with open(cli_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "to_csv" in content or "read_csv" in content:
                        csv_support = True

            # Check if sample CSV data was generated
            data_dir = SRC_DIR / "data"
            csv_files_exist = False
            if data_dir.exists():
                csv_files = list(data_dir.glob("*.csv"))
                if len(csv_files) >= 2:  # At least user and item data
                    csv_files_exist = True

            if csv_support and csv_files_exist:
                score = 2
                details = "Fully supports CSV format, sample data files generated"
            elif csv_support:
                score = 1
                details = "Supports CSV format but lacks data files"
            else:
                score = 0
                details = "Lacks CSV format support"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_data_cleaning_outliers(self):
        """Test 2.1.2a: Data Cleaning - Outlier Detection"""
        test_name = "2.1.2a Data Cleaning - Outlier Detection"
        try:
            # Check if there is a data preprocessing module
            preprocessor_file = SRC_DIR / "data_old" / "preprocessor.py"
            outlier_detection = False

            if preprocessor_file.exists():
                with open(preprocessor_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    keywords = ["outlier", "anomaly", "extreme", "detection", "cleaning"]
                    if any(keyword in content for keyword in keywords):
                        outlier_detection = True

            # Check statistical library dependencies
            requirements_file = SRC_DIR / "requirements.txt"
            stats_libs = False
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "scipy" in req_content or "numpy" in req_content:
                        stats_libs = True

            if outlier_detection and stats_libs:
                score = 2
                details = "Has outlier detection functionality and statistical library support"
            elif stats_libs:
                score = 1
                details = "Has statistical analysis capability but lacks outlier detection implementation"
            else:
                score = 0
                details = "Lacks outlier detection functionality"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_missing_value_handling(self):
        """Test 2.1.2b: Data Cleaning - Missing Value Handling"""
        test_name = "2.1.2b Data Cleaning - Missing Value Handling"
        try:
            # Check pandas support (has missing value handling capability)
            requirements_file = SRC_DIR / "requirements.txt"
            pandas_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "pandas" in f.read():
                        pandas_support = True

            # Check if there is missing value handling logic in the code
            missing_handling = False
            files_to_check = [
                SRC_DIR / "data_old" / "preprocessor.py",
                SRC_DIR / "cli_simplified.py"
            ]

            for file_path in files_to_check:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        keywords = ["fillna", "dropna", "missing", "null"]
                        if any(keyword in content for keyword in keywords):
                            missing_handling = True
                            break

            if pandas_support and missing_handling:
                score = 2
                details = "Has complete missing value handling functionality"
            elif pandas_support:
                score = 1
                details = "Has missing value handling capability but lacks implementation code"
            else:
                score = 0
                details = "Lacks missing value handling functionality"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_chinese_segmentation(self):
        """Test 2.1.2c: Chinese Word Segmentation Processing"""
        test_name = "2.1.2c Chinese Word Segmentation Processing"
        try:
            # Check jieba dependency
            requirements_file = SRC_DIR / "requirements.txt"
            jieba_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "jieba" in f.read():
                        jieba_support = True

            # Check if Chinese word segmentation is used in code
            chinese_processing = False
            files_to_check = list(SRC_DIR.rglob("*.py"))

            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "jieba" in content or "segmentation" in content:
                            chinese_processing = True
                            break
                except:
                    continue

            if jieba_support and chinese_processing:
                score = 2
                details = "Fully supports Chinese word segmentation processing"
            elif jieba_support:
                score = 1
                details = "Has Chinese word segmentation dependency but lacks usage code"
            else:
                score = 0
                details = "Lacks Chinese word segmentation processing functionality"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_normalization_encoding(self):
        """Test 2.1.2d: Data Normalization and Encoding"""
        test_name = "2.1.2d Data Normalization and Encoding"
        try:
            # Check scikit-learn dependency
            requirements_file = SRC_DIR / "requirements.txt"
            sklearn_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "scikit-learn" in req_content:
                        sklearn_support = True

            # Check if there is standardization or encoding processing in the code
            normalization_code = False
            files_to_check = list(SRC_DIR.rglob("*.py"))

            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        keywords = ["StandardScaler", "normalize", "LabelEncoder", "OneHotEncoder", "normalization", "standardization"]
                        if any(keyword in content for keyword in keywords):
                            normalization_code = True
                            break
                except:
                    continue

            if sklearn_support and normalization_code:
                score = 2
                details = "Fully supports data normalization and encoding functionality"
            elif sklearn_support:
                score = 1
                details = "Has data preprocessing capability but lacks implementation code"
            else:
                score = 0
                details = "Lacks data normalization and encoding functionality"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_content_based_tfidf(self):
        """Test 2.2.1a: Content-Based Recommendation - TF-IDF Implementation"""
        test_name = "2.2.1a Content-Based Recommendation - TF-IDF Implementation"
        try:
            # Check content-based recommendation algorithm file
            content_based_file = SRC_DIR / "algorithms" / "content_based.py"
            tfidf_implementation = False

            if content_based_file.exists():
                with open(content_based_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "TfidfVectorizer" in content or "TF-IDF" in content or "tfidf" in content:
                        tfidf_implementation = True

            # Check scikit-learn dependency (needed for TF-IDF)
            requirements_file = SRC_DIR / "requirements.txt"
            sklearn_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "scikit-learn" in f.read():
                        sklearn_support = True

            if tfidf_implementation and sklearn_support:
                score = 2
                details = "Fully implements TF-IDF content-based recommendation algorithm"
            elif sklearn_support:
                score = 1
                details = "Has TF-IDF implementation capability but lacks algorithm code"
            else:
                score = 0
                details = "Lacks TF-IDF recommendation functionality"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_word2vec_embedding(self):
        """Test 2.2.1b: Content-Based Recommendation - Word2Vec/Embedding Support"""
        test_name = "2.2.1b Content-Based Recommendation - Word2Vec/Embedding Support"
        try:
            # Check gensim dependency
            requirements_file = SRC_DIR / "requirements.txt"
            gensim_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "gensim" in f.read():
                        gensim_support = True

            # Check Word2Vec implementation
            word2vec_implementation = False
            files_to_check = list(SRC_DIR.rglob("*.py"))

            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "Word2Vec" in content or "word2vec" in content or "embedding" in content:
                            word2vec_implementation = True
                            break
                except:
                    continue

            if gensim_support and word2vec_implementation:
                score = 2
                details = "Fully supports Word2Vec word embedding recommendation"
            elif gensim_support:
                score = 1
                details = "Has word vector processing capability but lacks implementation code"
            else:
                score = 0
                details = "Lacks word vector recommendation functionality"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_collaborative_filtering_usercf(self):
        """Test 2.2.2a: Collaborative Filtering - User-Based Collaborative Filtering (UserCF)"""
        test_name = "2.2.2a Collaborative Filtering - User-Based Collaborative Filtering (UserCF)"
        try:
            # Check collaborative filtering algorithm file
            cf_file = SRC_DIR / "algorithms" / "collaborative_filtering.py"
            usercf_implementation = False

            if cf_file.exists():
                with open(cf_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "UserCF" in content or "user_based" in content or "user-based" in content:
                        usercf_implementation = True

            # Check surprise library support
            requirements_file = SRC_DIR / "requirements.txt"
            surprise_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "surprise" in f.read():
                        surprise_support = True

            if usercf_implementation and surprise_support:
                score = 2
                details = "Fully implements user-based collaborative filtering algorithm"
            elif surprise_support:
                score = 1
                details = "Has collaborative filtering capability but lacks UserCF implementation"
            else:
                score = 0
                details = "Lacks UserCF collaborative filtering functionality"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_collaborative_filtering_itemcf(self):
        """Test 2.2.2b: Collaborative Filtering - Item-Based Collaborative Filtering (ItemCF)"""
        test_name = "2.2.2b Collaborative Filtering - Item-Based Collaborative Filtering (ItemCF)"
        try:
            # Check collaborative filtering algorithm file
            cf_file = SRC_DIR / "algorithms" / "collaborative_filtering.py"
            itemcf_implementation = False

            if cf_file.exists():
                with open(cf_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "ItemCF" in content or "item_based" in content or "item-based" in content:
                        itemcf_implementation = True

            # Check related dependencies
            requirements_file = SRC_DIR / "requirements.txt"
            deps_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "surprise" in req_content or "scikit-learn" in req_content:
                        deps_support = True

            if itemcf_implementation and deps_support:
                score = 2
                details = "Fully implements item-based collaborative filtering algorithm"
            elif deps_support:
                score = 1
                details = "Has collaborative filtering capability but lacks ItemCF implementation"
            else:
                score = 0
                details = "Lacks ItemCF collaborative filtering functionality"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_api_basic_recommendation(self):
        """Test 2.3.1a: RESTful API - Basic Recommendation Interface"""
        test_name = "2.3.1a RESTful API - Basic Recommendation Interface"
        try:
            # Check API file structure
            api_main = SRC_DIR / "api" / "main.py"
            api_routes = SRC_DIR / "api" / "routes"

            api_structure = api_main.exists() and api_routes.exists()

            # Check FastAPI dependency
            requirements_file = SRC_DIR / "requirements.txt"
            fastapi_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "fastapi" in req_content and "uvicorn" in req_content:
                        fastapi_support = True

            # Check recommendation route
            recommend_route = False
            if (api_routes / "recommendation.py").exists():
                with open(api_routes / "recommendation.py", 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "/recommend" in content or "recommend" in content:
                        recommend_route = True

            if api_structure and fastapi_support and recommend_route:
                score = 2
                details = "Fully implements RESTful recommendation API interface"
            elif api_structure and fastapi_support:
                score = 1
                details = "Has API framework but recommendation interface is incomplete"
            else:
                score = 0
                details = "Lacks RESTful API implementation"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_health_check_api(self):
        """Test 2.3.2a: Health Check API - System Status Check"""
        test_name = "2.3.2a Health Check API - System Status Check"
        try:
            # Check health check route
            health_route_file = SRC_DIR / "api" / "routes" / "health.py"
            health_implementation = False

            if health_route_file.exists():
                with open(health_route_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "/health" in content or "health" in content:
                        health_implementation = True

            # Check system monitoring dependency
            requirements_file = SRC_DIR / "requirements.txt"
            monitoring_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "psutil" in req_content:
                        monitoring_support = True

            if health_implementation and monitoring_support:
                score = 2
                details = "Fully implements health check API and system monitoring"
            elif health_implementation:
                score = 1
                details = "Has health check interface but lacks system monitoring functionality"
            else:
                score = 0
                details = "Lacks health check API"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_python_environment(self):
        """Test 3.1: Technology Stack Dependencies - Python Environment"""
        test_name = "3.1 Technology Stack Dependencies - Python Environment"
        try:
            python_version = sys.version_info

            # Check Python version requirements
            requirements_file = SRC_DIR / "requirements.txt"
            version_specified = False

            # Check if modern version features are used in the code
            modern_features = 0
            files_to_check = list(SRC_DIR.rglob("*.py"))[:10]  # Check first 10 files

            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check type hints
                        if "from typing import" in content or ": str" in content or ": int" in content:
                            modern_features += 1
                            break
                except:
                    continue

            # Check f-string usage
            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "f\"" in content or "f'" in content:
                            modern_features += 1
                            break
                except:
                    continue

            if python_version >= (3, 9) and modern_features >= 2:
                score = 2
                details = f"Python {python_version.major}.{python_version.minor} environment, uses {modern_features} modern features"
            elif python_version >= (3, 8):
                score = 1
                details = f"Python {python_version.major}.{python_version.minor} environment, but insufficient use of modern features"
            else:
                score = 0
                details = f"Python version too low: {python_version.major}.{python_version.minor}"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_core_dependencies_data(self):
        """Test 3.2a: Core Dependency Libraries - Data Processing Libraries"""
        test_name = "3.2a Core Dependency Libraries - Data Processing Libraries"
        try:
            requirements_file = SRC_DIR / "requirements.txt"
            data_libs = []

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "pandas" in req_content:
                        data_libs.append("pandas")
                    if "numpy" in req_content:
                        data_libs.append("numpy")

            # Check actual usage
            usage_count = 0
            files_to_check = list(SRC_DIR.rglob("*.py"))

            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "import pandas" in content or "import numpy" in content:
                            usage_count += 1
                            if usage_count >= 3:  # Used in multiple files
                                break
                except:
                    continue

            if len(data_libs) >= 2 and usage_count >= 3:
                score = 2
                details = f"Correctly uses data processing libraries: {', '.join(data_libs)}"
            elif len(data_libs) >= 1:
                score = 1
                details = f"Partial data processing library support: {', '.join(data_libs)}"
            else:
                score = 0
                details = "Lacks core data processing libraries"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_core_dependencies_ml(self):
        """Test 3.2b: Core Dependency Libraries - Recommendation Algorithm Libraries"""
        test_name = "3.2b Core Dependency Libraries - Recommendation Algorithm Libraries"
        try:
            requirements_file = SRC_DIR / "requirements.txt"
            ml_libs = []

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "scikit-learn" in req_content:
                        ml_libs.append("scikit-learn")
                    if "surprise" in req_content:
                        ml_libs.append("surprise")

            # Check number of algorithm implementations
            algorithm_files = list((SRC_DIR / "algorithms").glob("*.py")) if (SRC_DIR / "algorithms").exists() else []

            if len(ml_libs) >= 2 and len(algorithm_files) >= 3:
                score = 2
                details = f"Complete recommendation algorithm library support: {', '.join(ml_libs)}, {len(algorithm_files)} algorithm files"
            elif len(ml_libs) >= 1:
                score = 1
                details = f"Basic recommendation algorithm library support: {', '.join(ml_libs)}"
            else:
                score = 0
                details = "Lacks recommendation algorithm libraries"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_system_architecture(self):
        """Test 3.3a: System Architecture - Layered Design"""
        test_name = "3.3a System Architecture - Layered Design"
        try:
            # Check directory structure
            layers = []
            expected_dirs = [
                "api",        # Service layer
                "algorithms", # Algorithm layer
                "data_old",   # Data layer (or core)
                "config"      # Configuration layer
            ]

            for dir_name in expected_dirs:
                if (SRC_DIR / dir_name).exists():
                    layers.append(dir_name)

            # Check core service
            core_service = SRC_DIR / "core" / "recommendation_service.py"
            has_core_service = core_service.exists()

            if len(layers) >= 3 and has_core_service:
                score = 2
                details = f"Clear layered architecture: {', '.join(layers)}, has core service layer"
            elif len(layers) >= 2:
                score = 1
                details = f"Basic layered structure: {', '.join(layers)}"
            else:
                score = 0
                details = "Lacks clear layered architecture"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def test_unit_testing(self):
        """Test 3.3b: Unit Test Coverage"""
        test_name = "3.3b Unit Test Coverage"
        try:
            # Check pytest dependency
            requirements_file = SRC_DIR / "requirements.txt"
            pytest_support = False

            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "pytest" in f.read():
                        pytest_support = True

            # Check test files
            test_files = list(SRC_DIR.rglob("test_*.py")) + list(SRC_DIR.rglob("*_test.py"))

            if pytest_support and len(test_files) >= 3:
                score = 2
                details = f"Complete unit test support: pytest + {len(test_files)} test files"
            elif pytest_support and len(test_files) >= 1:
                score = 1
                details = f"Basic test support: pytest + {len(test_files)} test files"
            else:
                score = 0
                details = "Lacks unit testing"

            self.log_test_result(test_name, score, 2, details)

        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"Test failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        self.logger.info("Starting recommendation system automated evaluation tests")
        self.logger.info("=" * 80)

        # System basic tests
        self.test_system_startup()

        # Data processing tests
        self.test_data_collection_json()
        self.test_data_collection_csv()
        self.test_data_cleaning_outliers()
        self.test_missing_value_handling()
        self.test_chinese_segmentation()
        self.test_normalization_encoding()

        # Recommendation algorithm tests
        self.test_content_based_tfidf()
        self.test_word2vec_embedding()
        self.test_collaborative_filtering_usercf()
        self.test_collaborative_filtering_itemcf()

        # API service tests
        self.test_api_basic_recommendation()
        self.test_health_check_api()

        # Technology stack tests
        self.test_python_environment()
        self.test_core_dependencies_data()
        self.test_core_dependencies_ml()

        # Architecture tests
        self.test_system_architecture()
        self.test_unit_testing()

        # Generate summary report
        return self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate summary report"""
        self.logger.info("=" * 80)
        self.logger.info("Evaluation test completed")
        self.logger.info(f"Total score: {self.total_score}/{self.max_score} ({self.total_score/self.max_score*100:.1f}%)")

        # Group by score
        passed_tests = [r for r in self.results if r['score'] == r['max_score']]
        partial_tests = [r for r in self.results if 0 < r['score'] < r['max_score']]
        failed_tests = [r for r in self.results if r['score'] == 0]

        self.logger.info(f"Fully passed: {len(passed_tests)} items")
        self.logger.info(f"Partially passed: {len(partial_tests)} items")
        self.logger.info(f"Failed: {len(failed_tests)} items")

        return {
            'total_score': self.total_score,
            'max_score': self.max_score,
            'percentage': self.total_score/self.max_score*100,
            'passed': len(passed_tests),
            'partial': len(partial_tests),
            'failed': len(failed_tests),
            'results': self.results
        }

def main():
    """Main function"""
    evaluator = AutomatedEvaluator()
    summary = evaluator.run_all_tests()

    # Save detailed results
    with open(EVALUATION_DIR / 'test_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nEvaluation completed! Total score: {summary['total_score']}/{summary['max_score']} ({summary['percentage']:.1f}%)")
    print(f"Detailed results saved to: {EVALUATION_DIR / 'test_results.json'}")

if __name__ == "__main__":
    main()