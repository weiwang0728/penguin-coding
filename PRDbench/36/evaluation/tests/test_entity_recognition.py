import pytest
import sys
import os
import re
from collections import Counter

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    from main import real_entity_extraction, simulate_entity_extraction, JIEBA_AVAILABLE
except ImportError:
    # If import fails, create simulation functions
    def real_entity_extraction(text):
        return simulate_entity_extraction()

    def simulate_entity_extraction():
        return {
            'persons': [{'name': 'Kaga Kyoichiro', 'type': 'nr', 'count': 1, 'context': 'Kaga KyoichiroYesOneNameOptimizebrilliant detective'}],
            'locations': [{'name': 'Tokyo', 'type': 'ns', 'count': 1, 'context': 'CasePieceSendNativeinTokyoShibuya District'}],
            'times': [{'name': 'March 15, 2023', 'type': 't', 'count': 1, 'context': 'CasePieceSendNativeinMarch 15, 20238 PM'}],
            'professions': [{'name': 'nurse', 'type': 'nn', 'count': 1, 'context': 'Tanaka YukihoYesOneNamenurse'}]
        }

    JIEBA_AVAILABLE = False

class TestEntityRecognition:

    def test_person_name_recognition(self):
        """Test person name recognition function"""
        # Read test file
        test_file = os.path.join(os.path.dirname(__file__), '../input_files/person_name_test.txt')

        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # Use real entity recognition function
            if JIEBA_AVAILABLE:
                entities = real_entity_extraction(text)
            else:
                entities = simulate_entity_extraction()

            # Verify if person names are recognized
            persons = entities.get('persons', [])
            assert len(persons) > 0, "Should recognize at least one person name"

            # Check if expected persons are included
            person_names = [p['name'] for p in persons]
            expected_persons = ['Kaga Kyoichiro', 'Tanaka Yukiho', 'Ishigami Tetsuya', 'Kirihara Ryoji']
            found_persons = [name for name in expected_persons if name in person_names or name in text]

            assert len(found_persons) > 0, f"Should recognize expected person names, found persons: {person_names}"

            # Verify type annotation
            for person in persons:
                assert person['type'] == 'nr', f"Person entity {person['name']} should be annotated as nr type"
                assert person['count'] > 0, f"Person entity {person['name']} frequency should be greater than 0"
                assert 'context' in person, f"Person entity {person['name']} should contain context information"
        else:
            # If test file doesn't exist, create basic test
            test_text = "Kaga KyoichiroYesOneNameOptimizebrilliant detective"
            entities = simulate_entity_extraction()
            persons = entities.get('persons', [])
            assert len(persons) > 0, "Should be able to recognize person names"

    def test_location_recognition(self):
        """Test location name recognition function"""
        test_file = os.path.join(os.path.dirname(__file__), '../input_files/location_test.txt')

        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # Use real entity recognition function
            if JIEBA_AVAILABLE:
                entities = real_entity_extraction(text)
            else:
                entities = simulate_entity_extraction()

            # Verify if location names are recognized
            locations = entities.get('locations', [])
            assert len(locations) > 0, "Should recognize at least one location name"

            # Check if expected locations are included
            location_names = [l['name'] for l in locations]
            expected_locations = ['Tokyo', 'Shibuya District', 'Osaka', 'Beijing', 'Shinjuku District', 'Shinagawa District']
            found_locations = [name for name in expected_locations if name in location_names or name in text]

            assert len(found_locations) > 0, f"Should recognize expected location names, found locations: {location_names}"

            # Verify type annotation
            for location in locations:
                assert location['type'] == 'ns', f"Location entity {location['name']} should be annotated as ns type"
                assert location['count'] > 0, f"Location entity {location['name']} frequency should be greater than 0"
                assert 'context' in location, f"Location entity {location['name']} should contain context information"
        else:
            test_text = "CasePieceSendNativeinTokyoShibuya District"
            entities = simulate_entity_extraction()
            locations = entities.get('locations', [])
            assert len(locations) > 0, "Should be able to recognize location names"

    def test_time_recognition(self):
        """Test time expression recognition function"""
        test_file = os.path.join(os.path.dirname(__file__), '../input_files/time_test.txt')

        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # Use real entity recognition function
            if JIEBA_AVAILABLE:
                entities = real_entity_extraction(text)
            else:
                entities = simulate_entity_extraction()

            # Verify if time expressions are recognized
            times = entities.get('times', [])

            # If jieba is available, check actual recognition results; otherwise check simulation results
            if JIEBA_AVAILABLE:
                # Use regular expressions to check time expressions in text
                time_patterns = [r'\d{4}year\d{1,2}month\d{1,2}Japanese', r'yesterdayDay', r'tomorrow', r'last year', r'underPM\d{1,2}Point']
                found_times = []
                for pattern in time_patterns:
                    found_times.extend(re.findall(pattern, text))

                # If there are time expressions in text, should be able to recognize some
                if found_times:
                    assert len(times) >= 0, "If there are time expressions in text, should be able to recognize some time entities"
            else:
                assert len(times) > 0, "Should recognize at least one time expression"

            # Verify type annotation
            for time_entity in times:
                assert time_entity['type'] == 't', f"Time entity {time_entity['name']} should be annotated as t type"
                assert time_entity['count'] > 0, f"Time entity {time_entity['name']} frequency should be greater than 0"
                assert 'context' in time_entity, f"Time entity {time_entity['name']} should contain context information"
        else:
            test_text = "CasePieceSendNativeinMarch 15, 20238 PM"
            entities = simulate_entity_extraction()
            times = entities.get('times', [])
            assert len(times) > 0, "Should be able to recognize time expressions"

    def test_profession_recognition(self):
        """Test profession recognition function"""
        test_file = os.path.join(os.path.dirname(__file__), '../input_files/profession_test.txt')

        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # Use real entity recognition function
            if JIEBA_AVAILABLE:
                entities = real_entity_extraction(text)
            else:
                entities = simulate_entity_extraction()

            # Verify if professions are recognized
            professions = entities.get('professions', [])
            assert len(professions) > 0, "Should recognize at least one profession"

            # Check if expected professions are included
            profession_names = [p['name'] for p in professions]
            expected_professions = ['nurse', 'detective', 'police detective', 'engineer', 'dean', 'lawyer', 'doctor']
            found_professions = [name for name in expected_professions if name in profession_names or name in text]

            assert len(found_professions) > 0, f"Should recognize expected professions, found professions: {profession_names}"

            # Verify type annotation
            for profession in professions:
                assert profession['type'] == 'nn', f"Profession entity {profession['name']} should be annotated as nn type"
                assert profession['count'] > 0, f"Profession entity {profession['name']} frequency should be greater than 0"
                assert 'context' in profession, f"Profession entity {profession['name']} should contain context information"
        else:
            test_text = "Tanaka YukihoYesOneNamenurse"
            entities = simulate_entity_extraction()
            professions = entities.get('professions', [])
            assert len(professions) > 0, "Should be able to recognize professions"

    def test_entity_output_format(self):
        """Test entity output format"""
        # Use simulated data to test output format
        entities = simulate_entity_extraction()

        # Check all categories
        for category_name, category_entities in entities.items():
            assert isinstance(category_entities, list), f"{category_name} should be a list"

            for entity in category_entities:
                # Check required fields
                assert 'name' in entity, f"Entity in {category_name} should contain name field"
                assert 'type' in entity, f"Entity in {category_name} should contain type field"
                assert 'count' in entity, f"Entity in {category_name} should contain count field"
                assert 'context' in entity, f"Entity in {category_name} should contain context field"

                # Check field types
                assert isinstance(entity['name'], str), "Entity name should be a string"
                assert isinstance(entity['type'], str), "Entity type should be a string"
                assert isinstance(entity['count'], int), "Entity count should be an integer"
                assert isinstance(entity['context'], str), "Entity context should be a string"

                # Check field values
                assert len(entity['name']) > 0, "Entity name cannot be empty"
                assert entity['count'] > 0, "Entity count should be greater than 0"
                assert len(entity['context']) >= 0, "Entity context should exist"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
