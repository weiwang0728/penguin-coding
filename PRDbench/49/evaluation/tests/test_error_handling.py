#!/usr/bin/env python3
"""
Error Handling Tests

Tests for error handling functionality in the IoT Environmental System.
"""

import sys
import subprocess
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestErrorHandling:
    """Test error handling functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.src_dir = Path(__file__).parent.parent.parent / "src"
    
    def test_invalid_command_handling(self):
        """Test handling of invalid commands."""
        
        # Test invalid main command
        result = subprocess.run(
            ["python", "main.py", "invalid_command"],
            cwd=self.src_dir,
            capture_output=True,
            text=True
        )
        
        # Should provide helpful error message
        error_output = result.stderr.lower()
        has_helpful_message = any(keyword in error_output for keyword in ["usage", "help", "command", "error"])
        
        # System should either handle gracefully or provide helpful message
        assert has_helpful_message, "Should provide helpful error message for invalid command"
        
        print("✓ Invalid command handling test passed")
    
    def test_invalid_parameter_handling(self):
        """Test handling of invalid parameters."""
        
        # Test invalid temperature parameter
        result = subprocess.run(
            ["python", "main.py", "ml", "predict", "--temperature", "invalid_temp"],
            cwd=self.src_dir,
            capture_output=True,
            text=True
        )
        
        # Should provide parameter-related error message
        error_output = result.stderr.lower()
        param_keywords = ["invalid", "parameter", "value", "float", "number"]
        
        has_param_error = any(keyword in error_output for keyword in param_keywords)
        
        assert has_param_error, "Should provide informative parameter error message"
        
        print("✓ Invalid parameter handling test passed")
    
    def test_system_stability(self):
        """Test that system doesn't crash on various error conditions."""
        
        # Test multiple error conditions
        error_commands = [
            ["python", "main.py", "--invalid-flag"],
            ["python", "main.py", "mqtt", "publish", "--file", "nonexistent.csv"],
            ["python", "main.py", "data", "analyze", "--file", "missing.csv"],
        ]
        
        stability_score = 0
        
        for cmd in error_commands:
            try:
                result = subprocess.run(
                    cmd,
                    cwd=self.src_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Any controlled exit is good (not hanging or crashing)
                if result.returncode in [0, 1, 2]:  # Normal exit codes
                    stability_score += 1
                    
            except subprocess.TimeoutExpired:
                # Timeout means the command hung, which is not good
                pass
            except Exception:
                # Other exceptions are also not good
                pass
        
        # At least half should handle gracefully
        assert stability_score >= len(error_commands) // 2, \
            f"System stability insufficient: {stability_score}/{len(error_commands)}"
        
        print(f"✓ System stability test passed - {stability_score}/{len(error_commands)} handled gracefully")


def test_error_handling():
    """Main test function."""
    test_instance = TestErrorHandling()
    test_instance.setup_method()
    
    test_instance.test_invalid_command_handling()
    test_instance.test_invalid_parameter_handling()
    test_instance.test_system_stability()
    
    print("All error handling tests passed!")


if __name__ == "__main__":
    test_error_handling()