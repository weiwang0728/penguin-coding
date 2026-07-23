#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test interrupt handling functions
"""

import pytest
import signal
import subprocess
import time
import os
import sys

# Add project root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_ctrl_c_interrupt():
    """Test Ctrl+C interrupt support"""
    # Start main program process
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,  # No buffering
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # Read initial output until main menu appears
        output_buffer = ""
        start_time = time.time()
        while "Please select function (1-6):" not in output_buffer and time.time() - start_time < 10:
            try:
                char = process.stdout.read(1)
                if char:
                    output_buffer += char
                else:
                    time.sleep(0.1)
            except:
                time.sleep(0.1)

        if "Please select function (1-6):" not in output_buffer:
            pytest.fail("Program did not display main menu")

        # Send input to start offline federated learning
        process.stdin.write("1\n")
        process.stdin.flush()

        # Wait for parameter configuration prompt
        while "Please enter client quantity" not in output_buffer and time.time() - start_time < 15:
            try:
                char = process.stdout.read(1)
                if char:
                    output_buffer += char
                else:
                    time.sleep(0.1)
            except:
                time.sleep(0.1)

        # Send parameters
        process.stdin.write("5\n10\n5\n0.01\n")
        process.stdin.flush()

        # Wait for training to start
        while "Start training" not in output_buffer and time.time() - start_time < 20:
            try:
                char = process.stdout.read(1)
                if char:
                    output_buffer += char
                else:
                    time.sleep(0.1)
            except:
                time.sleep(0.1)

        # Wait a moment for training to start
        time.sleep(1)

        # Send SIGINT signal (equivalent to Ctrl+C)
        process.send_signal(signal.SIGINT)

        # Wait for program response
        try:
            stdout, stderr = process.communicate(timeout=5)
            full_output = output_buffer + stdout + stderr
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            full_output = output_buffer + stdout + stderr

        # Verify program exits gracefully
        interrupt_keywords = ["interrupt", "interrupted by user", "KeyboardInterrupt", "interrupt signal detected", "graceful exit"]
        has_interrupt_message = any(keyword in full_output.lower() for keyword in interrupt_keywords)

        # Verify program can exit and display interrupt information
        assert process.returncode is not None, "Program should have exited"
        assert has_interrupt_message, f"Should display interrupt information, actual output: {full_output}"

        # Print output for debugging
        print(f"Program output: {full_output}")
        print(f"Return code: {process.returncode}")
        print(f"Found interrupt information: {has_interrupt_message}")

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("Program did not respond to interrupt signal within expected time")
    except Exception as e:
        process.kill()
        pytest.fail(f"Error occurred during test: {e}")

def test_graceful_shutdown():
    """Test graceful shutdown function"""
    # Start main program process
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,  # No buffering
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # Read initial output until main menu appears
        output_buffer = ""
        start_time = time.time()
        while "Please select function (1-6):" not in output_buffer and time.time() - start_time < 10:
            try:
                char = process.stdout.read(1)
                if char:
                    output_buffer += char
                else:
                    time.sleep(0.1)
            except:
                time.sleep(0.1)

        if "Please select function (1-6):" not in output_buffer:
            pytest.fail("Program did not display main menu")

        # Send exit command
        process.stdin.write("6\n")
        process.stdin.flush()

        # Wait for program to exit
        stdout, stderr = process.communicate(timeout=5)
        full_output = output_buffer + stdout + stderr

        # Verify program exits normally
        assert process.returncode == 0, "Program should exit normally"
        assert "goodbye" in full_output.lower() or "bye" in full_output.lower(), "Should display exit information"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("Program did not exit normally within expected time")
    except Exception as e:
        process.kill()
        pytest.fail(f"Error occurred during test: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
