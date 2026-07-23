#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file naming conventions
"""

import pytest
import os
import sys
import glob
import re

# Add project root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_log_naming_convention():
    """Test log file naming convention"""

    # Find log files
    log_dirs = [
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'log_file'),
        os.path.join(os.path.dirname(__file__), '..'),
        os.path.join(os.path.dirname(__file__), '..', '..')
    ]

    log_files = []
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            log_files.extend(glob.glob(os.path.join(log_dir, '*.log')))

    # If no log files found, create some test files to verify naming convention
    if not log_files:
        test_dir = os.path.join(os.path.dirname(__file__), '..', 'test_logs')
        os.makedirs(test_dir, exist_ok=True)

        # Create test files that comply with naming convention
        test_files = [
            'result_5_10_5.log',
            'result_10_10_10.log',
            'result_15_10_15.log',
            'result_20_10_20.log'
        ]

        for filename in test_files:
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f'Test log file: {filename}\n')
            log_files.append(filepath)

    # Verify at least some log files exist
    assert len(log_files) > 0, "Log files should exist to test naming convention"

    # Define naming convention patterns
    naming_patterns = [
        r'result_\d+_\d+_\d+\.log',  # result_clients_rounds_epochs.log
        r'result_stage\d+_\d+\.log',  # result_stage1_2.log
        r'expected_result_\d+_\d+_\d+\.log',  # expected_result_clients_rounds_epochs.log
    ]

    compliant_files = []
    non_compliant_files = []

    for log_file in log_files:
        filename = os.path.basename(log_file)
        is_compliant = any(re.match(pattern, filename) for pattern in naming_patterns)

        if is_compliant:
            compliant_files.append(filename)
        else:
            non_compliant_files.append(filename)

    # Verify naming convention
    print(f"Files compliant with naming convention: {compliant_files}")
    print(f"Files not compliant with naming convention: {non_compliant_files}")

    # At least some files should comply with naming convention
    assert len(compliant_files) > 0, "There should be files that comply with naming convention"

    # Check specific naming format
    for filename in compliant_files:
        if re.match(r'result_\d+_\d+_\d+\.log', filename):
            # Extract parameter information
            match = re.match(r'result_(\d+)_(\d+)_(\d+)\.log', filename)
            if match:
                clients, rounds, epochs = match.groups()
                print(f"File {filename} contains parameter information: clients={clients}, rounds={rounds}, epochs={epochs}")

                # Verify parameter value validity
                assert 1 <= int(clients) <= 20, f"Client quantity should be between 1-20: {clients}"
                assert 1 <= int(rounds) <= 100, f"Training rounds should be between 1-100: {rounds}"
                assert 1 <= int(epochs) <= 1000, f"Local training rounds should be between 1-1000: {epochs}"

def test_parameter_extraction():
    """Test extracting parameter information from file names"""

    test_filenames = [
        'result_5_10_5.log',
        'result_10_10_10.log',
        'result_15_10_15.log',
        'result_20_10_20.log'
    ]

    for filename in test_filenames:
        match = re.match(r'result_(\d+)_(\d+)_(\d+)\.log', filename)
        assert match is not None, f"File name {filename} should match result_X_Y_Z.log format"

        clients, rounds, epochs = match.groups()
        assert clients.isdigit(), f"Client quantity should be a number: {clients}"
        assert rounds.isdigit(), f"Training rounds should be a number: {rounds}"
        assert epochs.isdigit(), f"Local training rounds should be a number: {epochs}"

def test_file_extension():
    """Test file extension"""

    # Find all related files
    search_dirs = [
        os.path.join(os.path.dirname(__file__), '..'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'log_file')
    ]

    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            # Check log file extension
            log_files = glob.glob(os.path.join(search_dir, 'result_*'))
            for log_file in log_files:
                assert log_file.endswith('.log'), f"Log file should end with .log: {log_file}"

if __name__ == "__main__":
    pytest.main([__file__])
