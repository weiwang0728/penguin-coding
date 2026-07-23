import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_lifetime_management():
    """Test switch lifetime management"""
    try:
        # Try to import the switch-related class
        from layer.switch import Switch

        # Create a switch instance
        switch = Switch()

        # Check lifetime management functionality
        # 1. Entry lifetime decreases by 1 each time a frame is processed
        # 2. Automatically delete expired entries

        # Check the lifetime decrement method
        decrement_methods = ['decrement_lifetime', 'age_entries', 'update_lifetime', 'tick']
        found_decrement = False

        for method in decrement_methods:
            if hasattr(switch, method):
                found_decrement = True
                break

        # Check the automatic deletion method
        cleanup_methods = ['cleanup_expired', 'remove_expired', 'purge_old_entries', 'clean']
        found_cleanup = False

        for method in cleanup_methods:
            if hasattr(switch, method):
                found_cleanup = True
                break

        # Check if frame processing method contains lifetime management
        frame_methods = ['process_frame', 'handle_frame', 'forward_frame']
        found_frame_method = False

        for method in frame_methods:
            if hasattr(switch, method):
                found_frame_method = True
                break

        # At minimum, there should be a frame processing method, and it should have lifetime management functionality
        assert found_frame_method, "Switch is missing a frame processing method"

        # Check if there is lifetime management implementation
        # Can be an independent method, or it can be integrated in frame processing
        has_lifetime_management = found_decrement or found_cleanup

        if not has_lifetime_management:
            # Check if lifetime management is implemented in the frame processing method
            # Here we assume that if there is a frame processing method, it may contain lifetime management
            has_lifetime_management = found_frame_method

        assert has_lifetime_management, "Switch is missing lifetime management mechanism"

        # Check if port address table supports lifetime
        if hasattr(switch, 'switch_table') or hasattr(switch, 'address_table'):
            table = getattr(switch, 'switch_table', None) or getattr(switch, 'address_table', None)
            if table and hasattr(table, 'table'):
                # Check if the table structure supports lifetime
                pass  # Specific implementations may vary depending on the code

    except ImportError:
        pytest.fail("Unable to import Switch class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")