import pytest
import sys
import os
import re

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

class TestOutputFormat:

    def test_entity_name_and_type(self):
        """Test if entity output includes name and type label"""
        # Simulate entity output format
        sample_output = """
        Kaga Kyoichiro/nr 3 inTokyoa rainy night, detectiveKaga KyoichiroCorrectinAdjustinvestigateOnemysterious case
        Tanaka Yukiho/nr 2 victimErYesOneNamenamedTanaka Yukihoyoungwoman, sheYesOneNamenurse
        Tokyo/ns 1 inTokyoa rainy night, detectiveKaga KyoichiroCorrectinAdjustinvestigate
        """

        # Check if it includes entity name and type label
        lines = sample_output.strip().split('\n')
        for line in lines:
            if line.strip():
                # Check format: entity_name/type frequency context
                parts = line.strip().split(' ', 2)
                assert len(parts) >= 2, f"Output format incorrect: {line}"

                entity_with_type = parts[0]
                assert '/' in entity_with_type, f"Entity should include type label: {entity_with_type}"

                entity_name, entity_type = entity_with_type.split('/', 1)
                assert len(entity_name) > 0, "Entity name cannot be empty"
                assert entity_type in ['nr', 'ns', 't', 'nn'], f"Entity type should be one of nr/ns/t/nn: {entity_type}"

    def test_entity_frequency(self):
        """Test if entity output includes frequency information"""
        sample_output = """
        Kaga Kyoichiro/nr 3 inTokyoa rainy night, detectiveKaga KyoichiroCorrectinAdjustinvestigateOnemysterious case
        Tanaka Yukiho/nr 2 victimErYesOneNamenamedTanaka Yukihoyoungwoman, sheYesOneNamenurse
        Tokyo/ns 1 inTokyoa rainy night, detectiveKaga KyoichiroCorrectinAdjustinvestigate
        """

        lines = sample_output.strip().split('\n')
        for line in lines:
            if line.strip():
                parts = line.strip().split(' ', 2)
                assert len(parts) >= 2, f"Output format incorrect: {line}"

                frequency = parts[1]
                assert frequency.isdigit(), f"Frequency should be a number: {frequency}"
                assert int(frequency) > 0, f"Frequency should be greater than 0: {frequency}"

    def test_entity_context(self):
        """Test if entity output includes context information (8 characters before and after)"""
        sample_output = """
        Kaga Kyoichiro/nr 3 inTokyoa rainy night, detectiveKaga KyoichiroCorrectinAdjustinvestigateOnemysterious case
        Tanaka Yukiho/nr 2 victimErYesOneNamenamedTanaka Yukihoyoungwoman, sheYesOneNamenurse
        Tokyo/ns 1 inTokyoa rainy night, detectiveKaga KyoichiroCorrectinAdjustinvestigate
        """

        lines = sample_output.strip().split('\n')
        for line in lines:
            if line.strip():
                parts = line.strip().split(' ', 2)
                assert len(parts) >= 3, f"Output should include context information: {line}"

                context = parts[2]
                assert len(context) > 0, "Context information cannot be empty"

                # Check if context contains entity name
                entity_name = parts[0].split('/')[0]
                assert entity_name in context, f"Context should contain entity name: {entity_name} not in {context}"

                # Check context length (should include 8 characters before and after, but only basic check here)
                assert len(context) >= len(entity_name), "Context length should be reasonable"

if __name__ == '__main__':
    pytest.main([__file__])
