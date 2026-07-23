#!/usr/bin/env python3
"""
User persona generation test script
Test [2.2.5 User Persona Generation] functionality
"""

import subprocess
import json
import os
import sys
from pathlib import Path

def test_persona_generation():
    """Test user persona generation functionality"""
    print("🧪 Starting user persona generation functionality test...")

    # 1. Execute user persona generation command
    cmd = [
        "python", "-m", "src.main", "persona", "generate",
        "--from-cluster-results", "evaluation/reports/cluster/results.json",
        "--output-dir", "evaluation/reports/personas"
    ]

    print(f"📋 Executing command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            print(f"❌ Command execution failed, exit code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False

        print("✅ Command execution successful")
        print(f"Output: {result.stdout}")

        # 2. Check if expected output files exist
        expected_files = [
            "evaluation/reports/personas/cluster_0.json",
            "evaluation/reports/personas/cluster_1.json",
            "evaluation/reports/personas/cluster_2.json"
        ]

        for file_path in expected_files:
            if not os.path.exists(file_path):
                print(f"❌ Expected output file does not exist: {file_path}")
                return False
            print(f"✅ File exists: {file_path}")

        # 3. Validate file content structure
        for file_path in expected_files:
            if not validate_persona_file_structure(file_path):
                return False

        print("🎉 All tests passed! User persona generation functionality works correctly.")
        return True

    except Exception as e:
        print(f"❌ Exception occurred during test: {e}")
        return False

def validate_persona_file_structure(file_path):
    """Validate user persona file structure"""
    print(f"🔍 Validating file structure: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check required fields
        required_fields = [
            'cluster_id',
            'cluster_name',
            'sample_count',
            'demographics',
            'motivations',
            'consumption_patterns',
            'venue_preferences',
            'persona_summary'
        ]

        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return False

        # Check demographics subfields
        demographics_fields = ['gender_distribution', 'age_group_distribution']
        for field in demographics_fields:
            if field not in data['demographics']:
                print(f"❌ Missing field in demographics: {field}")
                return False

        # Check motivations subfields
        motivations_fields = ['price_sensitivity', 'satisfaction_level', 'amenities_importance']
        for field in motivations_fields:
            if field not in data['motivations']:
                print(f"❌ Missing field in motivations: {field}")
                return False

        # Check consumption_patterns subfields
        consumption_fields = ['frequency_distribution', 'dominant_frequency', 'spending_behavior']
        for field in consumption_fields:
            if field not in data['consumption_patterns']:
                print(f"❌ Missing field in consumption_patterns: {field}")
                return False

        # Check venue_preferences subfields
        venue_fields = ['preferred_venue_distribution', 'dominant_preference', 'preference_description']
        for field in venue_fields:
            if field not in data['venue_preferences']:
                print(f"❌ Missing field in venue_preferences: {field}")
                return False

        print(f"✅ File structure validation passed: {file_path}")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON format error: {e}")
        return False
    except Exception as e:
        print(f"❌ File validation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_persona_generation()
    sys.exit(0 if success else 1)