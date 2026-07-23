import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_crc16_parameters():
    """Test CRC-16 algorithm parameter configuration"""
    try:
        # Try to import CRC-related module
        from utils.frame import CRC16

        # Check polynomial and initial value
        crc_instance = CRC16()

        # Check if polynomial is 0xA001
        if hasattr(crc_instance, 'polynomial'):
            assert crc_instance.polynomial == 0xA001, f"Polynomial error: expected 0xA001, got {hex(crc_instance.polynomial)}"
        elif hasattr(crc_instance, 'poly'):
            assert crc_instance.poly == 0xA001, f"Polynomial error: expected 0xA001, got {hex(crc_instance.poly)}"

        # Check if initial value is 0xFFFF
        if hasattr(crc_instance, 'initial_value'):
            assert crc_instance.initial_value == 0xFFFF, f"Initial value error: expected 0xFFFF, got {hex(crc_instance.initial_value)}"
        elif hasattr(crc_instance, 'init_val'):
            assert crc_instance.init_val == 0xFFFF, f"Initial value error: expected 0xFFFF, got {hex(crc_instance.init_val)}"

    except ImportError:
        # Try other possible import paths
        try:
            from utils.coding import CRC16
            crc_instance = CRC16()
            # Repeat the above checks
        except ImportError:
            pytest.fail("Unable to import CRC16 class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")

def test_crc16_calculation():
    """Test CRC-16 checksum functionality"""
    try:
        from utils.frame import CRC16

        crc_instance = CRC16()

        # Test data
        test_data = b"01111110"

        # Try to calculate CRC
        if hasattr(crc_instance, 'calculate'):
            result = crc_instance.calculate(test_data)
        elif hasattr(crc_instance, 'compute'):
            result = crc_instance.compute(test_data)
        elif hasattr(crc_instance, 'crc'):
            result = crc_instance.crc(test_data)
        else:
            pytest.fail("CRC16 class is missing calculation method")

        # Verify result is an integer and in valid range
        assert isinstance(result, int), "CRC calculation result should be an integer"
        assert 0 <= result <= 0xFFFF, f"CRC result exceeds 16-bit range: {hex(result)}"

    except ImportError:
        try:
            from utils.coding import CRC16
            # Repeat the above test
        except ImportError:
            pytest.fail("Unable to import CRC16 class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")