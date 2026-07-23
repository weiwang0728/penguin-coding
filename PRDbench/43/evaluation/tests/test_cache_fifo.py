#!/usr/bin/env python3
"""
Unit Test: Cache Replacement Strategy - FIFO Strategy Test
Test the Client class cache management functionality, verify that FIFO (First In First Out) strategy is correctly implemented.
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import Mock

# Add src directory to path for module import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from distributed_fs.client import Client


class TestCacheFIFO:
    """Test Client class FIFO cache strategy"""

    def setup_method(self):
        """Preparation work before each test method execution"""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_proxy = Mock()
        self.mock_proxy.system_config = {'cache_size': 5}

        self.client = Client(self.mock_proxy)
        self.client.session_id = "test_session_123"
        self.client.username = "test_user"
        self.client.client_id = "test_client"
        self.client.cache_dir = os.path.join(self.temp_dir, 'cache')
        os.makedirs(self.client.cache_dir, exist_ok=True)
        self.client.cache_size = 5
        self.client.cache_queue.clear()

    def teardown_method(self):
        """Cleanup work after each test method execution"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def assert_equal(self, actual, expected, message=""):
        """Simple assertion function"""
        if actual != expected:
            raise AssertionError(f"Assertion failed: expected {expected}, actual {actual}. {message}")
        print(f"OK Assertion passed: {message}")
    
    def test_cache_fifo_strategy(self):
        """Test FIFO cache strategy core functionality"""
        print("=" * 50)
        print("FIFO Cache Strategy Unit Test")
        print("=" * 50)

        # Configure mock proxy
        def mock_read_file(session_id, file_name):
            return f"Content of {file_name}"

        self.mock_proxy.read_file = mock_read_file

        # Test 1: Fill cache capacity
        print("Test 1: Fill cache capacity")
        for i in range(1, 6):  # file1.txt to file5.txt
            file_name = f'file{i}.txt'
            self.client.read_file(file_name)

        self.assert_equal(len(self.client.cache_queue), 5, "Cache queue size is 5")
        self.assert_equal(len(os.listdir(self.client.cache_dir)), 5, "Cache directory file count is 5")

        # Test 2: FIFO eviction
        print("Test 2: FIFO eviction mechanism")
        self.client.read_file('file6.txt')

        self.assert_equal(len(self.client.cache_queue), 5, "Queue size remains 5 after eviction")
        cached_files = os.listdir(self.client.cache_dir)
        if 'file1.txt' in cached_files:
            raise AssertionError("The earliest file file1.txt should have been evicted")
        if 'file6.txt' not in cached_files:
            raise AssertionError("New file file6.txt should be in cache")

        expected_queue = ['file2.txt', 'file3.txt', 'file4.txt', 'file5.txt', 'file6.txt']
        self.assert_equal(list(self.client.cache_queue), expected_queue, "Queue order after FIFO eviction")

        print("=" * 50)
        print("All FIFO cache strategy tests passed!")
        print("OK Cache capacity limit is 5 files")
        print("OK First In First Out (FIFO) eviction strategy")
        print("=" * 50)

        return True


def test_cache_fifo_strategy():
    """Main test function"""
    test_instance = TestCacheFIFO()
    test_instance.setup_method()

    try:
        return test_instance.test_cache_fifo_strategy()
    finally:
        test_instance.teardown_method()


if __name__ == "__main__":
    success = test_cache_fifo_strategy()
    if not success:
        exit(1)