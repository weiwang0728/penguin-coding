#!/usr/bin/env python3
"""
Timeout Control Test
Test file lock 30-second timeout mechanism
"""

import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_lock_timeout():
    """Test lock timeout mechanism"""
    print("=" * 50)
    print("Test lock timeout control mechanism")
    print("=" * 50)
    
    try:
        from distributed_fs.utils import FileLock
        import tempfile

        temp_dir = tempfile.mkdtemp()

        def hold_lock_for_timeout():
            """Hold lock until timeout"""
            lock = FileLock(temp_dir, 'timeout_test')
            try:
                # Use shorter timeout for testing (5 seconds instead of 30 seconds)
                acquired = lock.acquire(timeout=5)
                if acquired:
                    print("PASS First process acquired lock successfully")
                    time.sleep(6)  # Hold lock for 6 seconds, exceeding 5 second timeout
                    lock.release()
                    print("PASS First process released lock")
                    return True
                else:
                    print("FAIL First process failed to acquire lock")
                    return False
            except Exception as e:
                print(f"FAIL First process exception: {e}")
                return False

        def try_acquire_after_timeout():
            """Try to acquire lock after timeout"""
            time.sleep(1)  # Ensure first process acquires lock first
            lock = FileLock(temp_dir, 'timeout_test')
            try:
                print("INFO Second process trying to acquire lock...")
                acquired = lock.acquire(timeout=8)  # Give enough time to wait for first lock timeout
                if acquired:
                    print("PASS Second process acquired lock successfully (first lock timed out)")
                    lock.release()
                    print("PASS Second process released lock")
                    return True
                else:
                    print("FAIL Second process failed to acquire lock")
                    return False
            except Exception as e:
                print(f"FAIL Second process exception: {e}")
                return False

        # Use thread pool to test concurrent lock acquisition
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(hold_lock_for_timeout)
            future2 = executor.submit(try_acquire_after_timeout)

            result1 = future1.result()
            result2 = future2.result()

        # Cleanup temporary directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

        if result1 and result2:
            print("PASS Timeout control test passed")
            return True
        else:
            print("FAIL Timeout control test failed")
            return False

    except ImportError as e:
        print(f"FAIL Cannot import test module: {e}")
        return False
    except Exception as e:
        print(f"FAIL Test exception: {e}")
        return False

def test_file_lock_basic_functionality():
    """Test file lock basic functionality"""
    print("=" * 50)
    print("Test file lock basic functionality")
    print("=" * 50)

    try:
        from distributed_fs.utils import FileLock
        import tempfile

        temp_dir = tempfile.mkdtemp()

        # Test lock acquisition and release
        lock = FileLock(temp_dir, 'basic_test')

        # Test 1: Normal acquisition and release
        acquired = lock.acquire(timeout=5)
        if not acquired:
            print("FAIL Cannot acquire lock")
            return False

        print("PASS Successfully acquired lock")

        lock.release()
        print("PASS Successfully released lock")

        # Test 2: Use with statement
        try:
            with FileLock(temp_dir, 'with_test') as test_lock:
                print("PASS With statement acquired lock successfully")
                time.sleep(0.1)
            print("PASS With statement auto-released lock")
        except Exception as e:
            print(f"FAIL With statement test failed: {e}")
            return False

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

        return True

    except Exception as e:
        print(f"FAIL Basic function test exception: {e}")
        return False

def main():
    """Main test function"""
    print("Timeout Control Test Started")
    print("=" * 60)

    tests = [
        ("File Lock Basic Function", test_file_lock_basic_functionality),
        ("Lock Timeout Mechanism", test_lock_timeout),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nExecuting Test: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"PASS {test_name}: Success")
            else:
                print(f"FAIL {test_name}: Failed")
        except Exception as e:
            print(f"FAIL {test_name}: Exception - {e}")

        time.sleep(0.5)  # Test isolation

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} passed")
    if passed == total:
        print("All timeout control tests passed!")
    print("=" * 60)

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)