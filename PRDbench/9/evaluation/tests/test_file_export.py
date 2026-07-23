#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Export Function Tests
"""

import pytest
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.export_service import export_service
from services.trip_service import trip_service
from models.trip import TripPlan, TripStatus

class TestFileExport:
    """File Export Test Class"""
    
    def setup_method(self):
        """Test preparation"""
        # Create test trip
        self.test_trip = trip_service.create_new_trip("Test Export Trip")
        trip_service.add_trip_segment("Beijing", "Shanghai", 24.0)
        trip_service.add_trip_segment("Shanghai", "Guangzhou", 12.0)
    
    def test_file_save_verification(self):
        """Test file save verification"""
        # Export Markdown file
        try:
            filepath = export_service.export_to_markdown(
                trip_service.current_trip,
                "test_export"
            )

            # Verify file exists
            assert os.path.exists(filepath), f"Exported file does not exist: {filepath}"

            # Verify file size (adjust to more reasonable expected value)
            file_size = os.path.getsize(filepath)
            assert file_size > 500, f"File size too small: {file_size} bytes"

            # Verify file readability
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0, "File content is empty"
                assert "Trip Report" in content or "Test Export Trip" in content, "File content is incorrect"

            # Clean up test file
            if os.path.exists(filepath):
                os.remove(filepath)

        except Exception as e:
            pytest.fail(f"File export test failed: {e}")
    
    def test_markdown_export_content(self):
        """Test Markdown export content"""
        try:
            filepath = export_service.export_to_markdown(
                trip_service.current_trip,
                "content_test"
            )

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Verify necessary content
            assert "# " in content, "Missing Markdown title"
            assert "Beijing" in content, "Missing departure city information"
            assert "Shanghai" in content, "Missing destination city information"
            assert "Guangzhou" in content, "Missing second segment destination information"

            # Clean up test file
            if os.path.exists(filepath):
                os.remove(filepath)

        except Exception as e:
            pytest.fail(f"Markdown content test failed: {e}")
    
    def test_export_directory_creation(self):
        """Test export directory creation"""
        # Test export to non-existent directory
        test_dir = "test_exports"
        full_test_dir = os.path.join("exports", test_dir)
        if os.path.exists(full_test_dir):
            import shutil
            shutil.rmtree(full_test_dir)

        try:
            filepath = export_service.export_to_markdown(
                trip_service.current_trip,
                f"{test_dir}/test_file"
            )

            # Verify both directory and file are created
            assert os.path.exists(full_test_dir), "Export directory not created"
            assert os.path.exists(filepath), "Export file not created"

            # Clean up test directory
            if os.path.exists(full_test_dir):
                import shutil
                shutil.rmtree(full_test_dir)

        except Exception as e:
            pytest.fail(f"Directory creation test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])