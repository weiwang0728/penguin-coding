import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_buffer_size_constants():
    """Test buffer size configuration"""
    try:
        # Try to import buffer constants from different modules
        buffer_constants = {}

        # Try to import from params module
        try:
            from utils.params import INTER_NE_BUFSIZE, IN_NE_BUFSIZE
            buffer_constants['INTER_NE_BUFSIZE'] = INTER_NE_BUFSIZE
            buffer_constants['IN_NE_BUFSIZE'] = IN_NE_BUFSIZE
        except ImportError:
            pass

        # Try to import from other possible modules
        if not buffer_constants:
            try:
                from utils.config import INTER_NE_BUFSIZE, IN_NE_BUFSIZE
                buffer_constants['INTER_NE_BUFSIZE'] = INTER_NE_BUFSIZE
                buffer_constants['IN_NE_BUFSIZE'] = IN_NE_BUFSIZE
            except ImportError:
                pass

        # Try to import from main module
        if not buffer_constants:
            try:
                import main
                if hasattr(main, 'INTER_NE_BUFSIZE'):
                    buffer_constants['INTER_NE_BUFSIZE'] = main.INTER_NE_BUFSIZE
                if hasattr(main, 'IN_NE_BUFSIZE'):
                    buffer_constants['IN_NE_BUFSIZE'] = main.IN_NE_BUFSIZE
            except ImportError:
                pass

        # Check if buffer constants are found
        found_constants = len(buffer_constants)
        assert found_constants >= 1, f"At least 1 buffer size constant should be defined, found {found_constants}"

        # Verify constant values
        for const_name, const_value in buffer_constants.items():
            assert isinstance(const_value, int), f"{const_name} should be an integer type"
            assert const_value > 0, f"{const_name} should be a positive number, got value: {const_value}"
            assert const_value <= 65536, f"{const_name} value is too large, got value: {const_value}"

        # Check if both required constants are defined
        required_constants = ['INTER_NE_BUFSIZE', 'IN_NE_BUFSIZE']
        found_required = [const for const in required_constants if const in buffer_constants]

        if len(found_required) == 2:
            # Verify that the two buffer sizes are reasonable
            inter_size = buffer_constants['INTER_NE_BUFSIZE']
            in_size = buffer_constants['IN_NE_BUFSIZE']

            assert inter_size >= 512, "Inter-network-element communication buffer should be at least 512 bytes"
            assert in_size >= 256, "Intra-network-element communication buffer should be at least 256 bytes"

    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")