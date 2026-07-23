#!/usr/bin/env python3
"""
Performance test script - Test report generation performance with large data volume
"""

import subprocess
import time
import os
import sys

def test_performance():
    """Test performance requirements"""
    print("🚀 Starting performance test...")
    print("=" * 50)

    # Test command
    command = [
        "python", "-m", "src.main",
        "report", "generate-full",
        "--data-path", "evaluation/large_data.csv",
        "--format", "markdown",
        "--output-path", "evaluation/performance_report.md"
    ]

    print(f"Executing command: {' '.join(command)}")
    print("⏱️  Starting timer...")

    # Record start time
    start_time = time.time()

    try:
        # Execute command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # Record end time
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        print("=" * 50)

        # Check execution result
        if result.returncode == 0:
            print("✅ Command execution successful!")
            print("\n📋 Standard output:")
            print(result.stdout)

            # Check if output file exists
            if os.path.exists("evaluation/performance_report.md"):
                file_size = os.path.getsize("evaluation/performance_report.md")
                print(f"📄 Generated report file size: {file_size} bytes")

                # Read first few lines to verify content
                with open("evaluation/performance_report.md", 'r', encoding='utf-8') as f:
                    first_lines = [f.readline().strip() for _ in range(3)]
                    print("📝 First 3 lines of report file:")
                    for i, line in enumerate(first_lines, 1):
                        print(f"   {i}. {line}")
            else:
                print("❌ Output file not generated!")
                return False

            # Performance evaluation
            print("\n🎯 Performance evaluation:")
            if execution_time < 30:
                print(f"✅ Performance test passed! Execution time {execution_time:.2f}s < 30s")
                return True
            else:
                print(f"⚠️  Performance warning: Execution time {execution_time:.2f}s >= 30s")
                return False

        else:
            print("❌ Command execution failed!")
            print(f"Return code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False

    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"❌ Execution exception: {e}")
        print(f"Execution time: {execution_time:.2f} seconds")
        return False

if __name__ == "__main__":
    success = test_performance()
    sys.exit(0 if success else 1)