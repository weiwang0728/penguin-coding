#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Test: Code Structure Layered Architecture Verification

Test Goal: Verify whether project code is designed with clear layered architecture: functional layer/service layer/CLI layer
"""

import os
import py test
from pathlib import Path


class TestCodeStructure:
 """Code structure test class"""

 def test_layered_architecture(self):
 """Test layered architecture design"""
 project_root = Path(__file__).parent.parent.parent / "src"

 # Verify main layered directories exist
 assert (project_root / "credit_assessment").exists(), "Main module directory does not exist"

 # Verify functional layer directories
 functional_dirs = [
 "data", # Data processing layer
 "algorithms", # Algorithm layer
 "evaluation", # Evaluation layer
 "utils" # Utility layer
 ]

 for dir_name in functional_dirs:
 dir_path = project_root / "credit_assessment" / dir_name
 assert dir_path.exists(), f"Functional layer directory {dir_name} does not exist"
 assert (dir_path / "__init__.py").exists(), f"Functional layer directory {dir_name} missing __init__.py"

 # Verify service layer directories (business logic)
 service_dirs = ["algorithms", "data", "evaluation"]
 for dir_name in service_dirs:
 dir_path = project_root / "credit_assessment" / dir_name
 # Check if business logic files exist
 py_files = list(dir_path.glob("*.py"))
 assert len(py_files) >= 2, f"Service layer directory {dir_name} should contain at least 2 Python files (including __init__.py)"

 # Verify CLI layer directory
 cli_dir = project_root / "credit_assessment" / "cli"
 assert cli_dir.exists(), "CLI layer directory does not exist"
 assert (cli_dir / "__init__.py").exists(), "CLI layer directory missing __init__.py"
 assert (cli_dir / "main_cli.py").exists(), "CLI layer missing main CLI file"

 # Verify directory separation clarity
 # Data processing functionality should be in data directory
 data_files = list((project_root / "credit_assessment" / "data").glob("*.py"))
 data_related_files = [f for f in data_files if "data" in f.name.lower() or "preprocess" in f.name.lower()]
 assert len(data_related_files) >= 1, "Data layer missing data processing related files"

 # Algorithm functionality should be in algorithms directory
 alg_files = list((project_root / "credit_assessment" / "algorithms").glob("*.py"))
 alg_related_files = [f for f in alg_files if "algorithm" in f.name.lower() or "regression" in f.name.lower() or "network" in f.name.lower()]
 assert len(alg_related_files) >= 1, "Algorithm layer missing algorithm related files"

 # CLI functionality should be in cli directory
 cli_files = list((project_root / "credit_assessment" / "cli").glob("*.py"))
 cli_related_files = [f for f in cli_files if "cli" in f.name.lower() or "menu" in f.name.lower()]
 assert len(cli_related_files) >= 1, "CLI layer missing command line related files"


if __name__ == "__main__":
 # Allow direct execution of this test file
 py test.main([__file__])
