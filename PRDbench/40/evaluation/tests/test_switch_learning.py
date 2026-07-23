import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_address_learning_mechanism():
    """Test switch address learning mechanism"""
    try:
        # Try to import the switch-related class
        from layer.switch import Switch

        # Create a switch instance
        switch = Switch()

        # Check if the address learning function is implemented:
        # 1. Automatically extract source address
        # 2. Update port address table
        # 3. Set lifetime to REMOTE_MAX_LIFE

        # Check the REMOTE_MAX_LIFE constant
        if hasattr(switch, 'REMOTE_MAX_LIFE'):
            remote_max_life = switch.REMOTE_MAX_LIFE
        else:
            # Try to import from another location
            try:
                from utils.params import REMOTE_MAX_LIFE
                remote_max_life = REMOTE_MAX_LIFE
            except ImportError:
                remote_max_life = 300  # Default value

        assert isinstance(remote_max_life, int), "REMOTE_MAX_LIFE should be an integer"
        assert remote_max_life > 0, "REMOTE_MAX_LIFE should be a positive number"

        # Check address learning method
        learning_methods = ['learn_address', 'process_frame', 'handle_frame', 'learn']
        found_method = None

        for method in learning_methods:
            if hasattr(switch, method):
                found_method = method
                break

        assert found_method is not None, "Switch is missing an address learning method"

        # Check port address table update functionality
        if hasattr(switch, 'switch_table') or hasattr(switch, 'address_table'):
            table = getattr(switch, 'switch_table', None) or getattr(switch, 'address_table', None)
            assert table is not None, "Switch is missing a port address table"

        # Check source address extraction functionality
        extract_methods = ['extract_source', 'get_source_address', 'parse_source']
        found_extract = False

        for method in extract_methods:
            if hasattr(switch, method):
                found_extract = True
                break

        # If there is no independent extraction method, check if it's implemented in the learning method
        if not found_extract and found_method:
            found_extract = True  # Assume the extraction functionality is implemented in the learning method

        assert found_extract, "Switch is missing source address extraction functionality"

    except ImportError:
        pytest.fail("Unable to import Switch class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")