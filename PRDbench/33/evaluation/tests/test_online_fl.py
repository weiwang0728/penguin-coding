#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test online federated learning functions
"""

import pytest
import subprocess
import time
import os
import sys
import socket
import threading

# Add project root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_client_connection_display():
    """Test client connection count display"""

    # Start main program process
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # Send input to start online federated learning
        input_data = "2\n8080\n9000\n3\n6\n"
        stdout, stderr = process.communicate(input=input_data, timeout=15)

        # Verify if client connection information is displayed
        output = stdout + stderr
        connection_patterns = [
            "Client 1 connected",
            "Client 2 connected",
            "Client 3 connected",
            "connected"
        ]

        has_connection_display = any(pattern in output for pattern in connection_patterns)
        assert has_connection_display, f"Should display client connection information, actual output: {output}"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("Program did not complete within expected time")
    except Exception as e:
        process.kill()
        pytest.fail(f"Error occurred during test: {e}")

def test_client_ready_status():
    """Test client ready status display"""

    # Start main program process
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # Send input to start online federated learning
        input_data = "2\n8080\n9000\n5\n6\n"
        stdout, stderr = process.communicate(input=input_data, timeout=15)

        # Verify if client ready status information is displayed
        output = stdout + stderr
        ready_patterns = [
            "1/5 clients ready",
            "2/5 clients ready",
            "3/5 clients ready",
            "4/5 clients ready",
            "5/5 clients ready",
            "clients ready"
        ]

        has_ready_display = any(pattern in output for pattern in ready_patterns)
        assert has_ready_display, f"Should display client ready status information, actual output: {output}"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("Program did not complete within expected time")
    except Exception as e:
        process.kill()
        pytest.fail(f"Error occurred during test: {e}")

def test_port_configuration():
    """Test port configuration function"""

    # Start main program process
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # Test different port configurations
        input_data = "2\n8080\n9000\n2\n6\n"
        stdout, stderr = process.communicate(input=input_data, timeout=10)

        # Verify if port configuration is accepted
        output = stdout + stderr
        port_patterns = [
            "8080",
            "9000",
            "receive port",
            "send port"
        ]

        has_port_config = any(pattern in output.lower() for pattern in [p.lower() for p in port_patterns])
        assert has_port_config, f"Should display port configuration information, actual output: {output}"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("Program did not complete within expected time")
    except Exception as e:
        process.kill()
        pytest.fail(f"Error occurred during test: {e}")

def test_invalid_port_handling():
    """Test invalid port handling"""

    # Start main program process
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # Send invalid port number
        input_data = "2\n99999\n8080\n9000\n2\n6\n"  # Invalid port number
        stdout, stderr = process.communicate(input=input_data, timeout=10)

        # Verify if error information is displayed
        output = stdout + stderr
        assert "error" in output.lower(), "Should display port error information"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("Program did not complete within expected time")
    except Exception as e:
        process.kill()
        pytest.fail(f"Error occurred during test: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
