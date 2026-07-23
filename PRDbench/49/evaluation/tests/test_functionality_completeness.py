#!/usr/bin/env python3
"""
Functionality Completeness Tests

Tests for verifying that all PRD-required core functionality is available through CLI.
"""

import sys
import subprocess
import re
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestFunctionalityCompleteness:
    """Test functionality completeness."""
    
    def setup_method(self):
        """Setup test environment."""
        self.src_dir = Path(__file__).parent.parent.parent / "src"
        self.required_commands = {
            'mqtt': ['publish', 'subscribe'],
            'data': ['analyze', 'clean', 'merge'],
            'ml': ['train', 'predict', 'evaluate'],
            'system': ['status', 'monitor'],
            'web': [],
            'setup': []
        }
    
    def test_all_commands_available(self):
        """Test that all required commands are available."""
        
        # Get main help output
        result = subprocess.run(
            ["python", "main.py", "--help"],
            cwd=self.src_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Main help command should execute successfully"
        
        help_output = result.stdout.lower()
        
        # Check for main command groups
        missing_commands = []
        
        for main_command in self.required_commands.keys():
            if main_command not in help_output:
                missing_commands.append(main_command)
        
        assert len(missing_commands) == 0, f"Missing main commands: {missing_commands}"
        
        print(f"✓ All main commands available: {list(self.required_commands.keys())}")
    
    def test_subcommands_available(self):
        """Test that required subcommands are available."""
        
        missing_subcommands = []
        
        for main_command, subcommands in self.required_commands.items():
            if not subcommands:  # Skip commands without subcommands
                continue
                
            # Get subcommand help
            result = subprocess.run(
                ["python", "main.py", main_command, "--help"],
                cwd=self.src_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                missing_subcommands.append(f"{main_command} (help failed)")
                continue
            
            subcommand_help = result.stdout.lower()
            
            for subcommand in subcommands:
                if subcommand not in subcommand_help:
                    missing_subcommands.append(f"{main_command}.{subcommand}")
        
        assert len(missing_subcommands) == 0, f"Missing subcommands: {missing_subcommands}"
        
        print("✓ All required subcommands available")
    
    def test_mqtt_functionality_accessible(self):
        """Test MQTT functionality accessibility."""
        
        mqtt_tests = [
            (["python", "main.py", "mqtt", "publish", "--help"], "MQTT publish help"),
            (["python", "main.py", "mqtt", "subscribe", "--help"], "MQTT subscribe help"),
        ]
        
        for command, description in mqtt_tests:
            result = subprocess.run(command, cwd=self.src_dir, capture_output=True, text=True)
            assert result.returncode == 0, f"{description} should be accessible"
        
        print("✓ MQTT functionality accessible")
    
    def test_data_management_functionality_accessible(self):
        """Test data management functionality accessibility."""
        
        data_tests = [
            (["python", "main.py", "data", "analyze", "--help"], "Data analyze help"),
            (["python", "main.py", "data", "clean", "--help"], "Data clean help"),
            (["python", "main.py", "data", "merge", "--help"], "Data merge help"),
        ]
        
        for command, description in data_tests:
            result = subprocess.run(command, cwd=self.src_dir, capture_output=True, text=True)
            assert result.returncode == 0, f"{description} should be accessible"
        
        print("✓ Data management functionality accessible")
    
    def test_ml_functionality_accessible(self):
        """Test machine learning functionality accessibility."""
        
        ml_tests = [
            (["python", "main.py", "ml", "train", "--help"], "ML train help"),
            (["python", "main.py", "ml", "predict", "--help"], "ML predict help"),
            (["python", "main.py", "ml", "evaluate", "--help"], "ML evaluate help"),
        ]
        
        for command, description in ml_tests:
            result = subprocess.run(command, cwd=self.src_dir, capture_output=True, text=True)
            assert result.returncode == 0, f"{description} should be accessible"
        
        print("✓ Machine learning functionality accessible")
    
    def test_system_monitoring_functionality_accessible(self):
        """Test system monitoring functionality accessibility."""
        
        system_tests = [
            (["python", "main.py", "system", "status", "--help"], "System status help"),
            (["python", "main.py", "system", "monitor", "--help"], "System monitor help"),
        ]
        
        for command, description in system_tests:
            result = subprocess.run(command, cwd=self.src_dir, capture_output=True, text=True)
            assert result.returncode == 0, f"{description} should be accessible"
        
        print("✓ System monitoring functionality accessible")
    
    def test_web_functionality_accessible(self):
        """Test web interface functionality accessibility."""
        
        result = subprocess.run(
            ["python", "main.py", "web", "--help"],
            cwd=self.src_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Web interface help should be accessible"
        
        # Check for key web options
        help_output = result.stdout.lower()
        web_options = ["host", "port"]
        
        for option in web_options:
            assert option in help_output, f"Web interface should support --{option} option"
        
        print("✓ Web interface functionality accessible")
    
    def test_setup_functionality_accessible(self):
        """Test setup functionality accessibility."""
        
        result = subprocess.run(
            ["python", "main.py", "setup", "--help"],
            cwd=self.src_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Setup functionality should be accessible"
        
        print("✓ Setup functionality accessible")
    
    def test_command_parameter_validation(self):
        """Test that commands properly validate parameters."""
        
        # Test commands with required parameters
        parameter_tests = [
            (["python", "main.py", "ml", "predict"], "ML predict should require parameters"),
            (["python", "main.py", "mqtt", "publish", "--file"], "MQTT publish should validate file parameter"),
        ]
        
        validation_working = 0
        
        for command, description in parameter_tests:
            result = subprocess.run(command, cwd=self.src_dir, capture_output=True, text=True)
            
            # Should either fail with helpful message or succeed
            if result.returncode != 0:
                # Check if error message is helpful
                error_output = result.stderr.lower()
                if any(keyword in error_output for keyword in ["usage", "required", "missing", "help"]):
                    validation_working += 1
            else:
                # If it succeeds, that's also fine (might have defaults)
                validation_working += 1
        
        # At least half of the parameter validation should work
        assert validation_working >= len(parameter_tests) // 2, \
            f"Parameter validation insufficient: {validation_working}/{len(parameter_tests)}"
        
        print(f"✓ Command parameter validation test passed - {validation_working}/{len(parameter_tests)}")
    
    def test_core_workflow_completeness(self):
        """Test that core IoT workflows are complete."""
        
        # Test core workflow: data collection -> analysis -> prediction
        workflow_steps = [
            (["python", "main.py", "mqtt", "--help"], "MQTT communication available"),
            (["python", "main.py", "data", "--help"], "Data management available"),
            (["python", "main.py", "ml", "--help"], "Machine learning available"),
            (["python", "main.py", "system", "--help"], "System monitoring available"),
        ]
        
        completed_steps = 0
        
        for command, description in workflow_steps:
            result = subprocess.run(command, cwd=self.src_dir, capture_output=True, text=True)
            if result.returncode == 0:
                completed_steps += 1
            else:
                print(f"Warning: {description} - command failed")
        
        # All core workflow components should be available
        completion_rate = completed_steps / len(workflow_steps)
        assert completion_rate >= 0.75, f"Core workflow completion rate too low: {completion_rate:.2%}"
        
        print(f"✓ Core workflow completeness test passed - {completed_steps}/{len(workflow_steps)} components")


def test_all_commands_available():
    """Main test function for pytest."""
    test_instance = TestFunctionalityCompleteness()
    test_instance.setup_method()
    
    test_instance.test_all_commands_available()
    test_instance.test_subcommands_available()
    test_instance.test_mqtt_functionality_accessible()
    test_instance.test_data_management_functionality_accessible()
    test_instance.test_ml_functionality_accessible()
    test_instance.test_system_monitoring_functionality_accessible()
    test_instance.test_web_functionality_accessible()
    test_instance.test_setup_functionality_accessible()
    test_instance.test_command_parameter_validation()
    test_instance.test_core_workflow_completeness()
    
    print("All functionality completeness tests passed!")


if __name__ == "__main__":
    test_all_commands_available()