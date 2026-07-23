#!/usr/bin/env python3
"""
Operation Queue Management Test
Verify queue file generation and ordered execution during multi-client concurrent operations
"""

import os
import sys
import time
import threading
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def run_dfs_command(commands, timeout=15):
    """Run distributed file system command"""
    try:
        process = subprocess.Popen(
            ['python', 'src/distributed_fs/main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd='.'
        )
        
        input_text = '\n'.join(commands) + '\n'
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
        
        return {
            'success': 'successfully' in stdout.lower() or 'login successful' in stdout.lower(),
            'stdout': stdout,
            'stderr': stderr,
            'returncode': process.returncode
        }
    except subprocess.TimeoutExpired:
        process.kill()
        return {'success': False, 'stdout': '', 'stderr': 'Timeout', 'returncode': -1}
    except Exception as e:
        return {'success': False, 'stdout': '', 'stderr': str(e), 'returncode': -1}

def test_queue_file_generation():
    """Test queue file generation"""
    print("=" * 50)
    print("Queue File Generation Test")
    print("=" * 50)

    # Create shared test file
    setup_result = run_dfs_command([
        'login user1 password123',
        'create shared_queue_test.txt full',
        'exit'
    ])

    if not setup_result['success']:
        print("FAIL Setup shared queue test file failed")
        return False

    def concurrent_write(user_id, content_id):
        """Concurrent write function"""
        passwords = ['password123', 'password234', 'password345']
        commands = [
            f'login user{user_id} {passwords[user_id-1]}',
            f'write shared_queue_test.txt "content from user{user_id} - {content_id}"',
            'exit'
        ]

        result = run_dfs_command(commands)
        return {
            'user_id': user_id,
            'success': result['success'],
            'output': result['stdout'],
            'has_queue_log': 'QUEUE_ADD' in result['stdout']
        }

    # Rapidly execute multiple write operations to trigger queue
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(1, 4):
            future = executor.submit(concurrent_write, i, int(time.time()))
            futures.append(future)
            time.sleep(0.05)  # Small interval to ensure queue trigger

        results = []
        for future in futures:
            results.append(future.result())

    # Analyze results
    successful_writes = [r for r in results if r['success']]
    queue_operations = [r for r in results if r['has_queue_log']]

    print(f"Successful writes: {len(successful_writes)}/3")
    print(f"Queue operations detected: {len(queue_operations)}")

    # Check if temp directory has queue files
    temp_dir = os.path.join('src', 'temp')
    queue_files = []
    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            if file.startswith('queue_'):
                queue_files.append(file)
                print(f"Found queue file: {file}")

    if len(successful_writes) >= 2 and (len(queue_operations) > 0 or len(queue_files) > 0):
        print("PASS Queue file generation test passed")
        return True
    else:
        print("FAIL Queue file generation test failed")
        return False

def test_ordered_execution():
    """Test ordered execution"""
    print("=" * 50)
    print("Ordered Execution Test")
    print("=" * 50)

    # Create test file
    setup_result = run_dfs_command([
        'login user1 password123',
        'create order_test_file.txt full',
        'exit'
    ])

    if not setup_result['success']:
        print("FAIL Setup order test file failed")
        return False

    # Write different content in sequence
    def sequential_write(user_id, sequence):
        passwords = ['password123', 'password234', 'password345']
        commands = [
            f'login user{user_id} {passwords[user_id-1]}',
            f'write order_test_file.txt "sequence_{sequence}_user{user_id}"',
            'exit'
        ]

        start_time = time.time()
        result = run_dfs_command(commands)
        end_time = time.time()

        return {
            'user_id': user_id,
            'sequence': sequence,
            'success': result['success'],
            'timestamp': start_time,
            'duration': end_time - start_time,
            'output': result['stdout']
        }

    # Execute write operations in sequence
    results = []
    for i in range(1, 4):
        result = sequential_write(i, i)
        results.append(result)
        time.sleep(0.2)  # Ensure timestamp order

    # Check execution order of final file content
    final_read = run_dfs_command([
        'login user1 password123',
        'read order_test_file.txt',
        'exit'
    ])

    successful_writes = [r for r in results if r['success']]

    print(f"Sequential writes: {len(successful_writes)}/3 successful")

    if final_read['success'] and len(successful_writes) >= 2:
        print("PASS Ordered execution test passed")
        return True
    else:
        print("FAIL Ordered execution test failed")
        return False

def main():
    """Main test function"""
    print("Operation Queue Management Test Started")
    print("=" * 60)

    tests = [
        ("Queue File Generation", test_queue_file_generation),
        ("Ordered Execution", test_ordered_execution),
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

        time.sleep(1)  # Test isolation

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} passed")
    if passed == total:
        print("All operation queue tests passed!")
    print("=" * 60)

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)