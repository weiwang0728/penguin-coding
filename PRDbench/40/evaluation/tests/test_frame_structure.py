import sys
import os
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_frame_fields_completeness():
    """Test frame structure field completeness"""
    try:
        # Try to import the frame-related module
        from utils.frame import Frame

        # Check if frame structure contains required fields
        required_fields = [
            'frame_delimiter',  # Frame delimiter (8 bits)
            'source_port',      # Source port (16 bits)
            'session_state',    # Session state (2 bits)
            'ack_flag',         # Acknowledgment flag (1 bit)
            'sequence_number',  # Sequence number (1 bit)
            'data_segment',     # Data segment (32 bits)
            'dest_port',        # Destination port (16 bits)
            'crc_checksum'      # CRC checksum (16 bits)
        ]

        # Check if Frame class has these fields
        frame_instance = Frame()
        missing_fields = []

        for field in required_fields:
            if not hasattr(frame_instance, field):
                missing_fields.append(field)

        assert len(missing_fields) == 0, f"Missing fields: {missing_fields}"

        # Check bit size configuration
        bit_sizes = {
            'frame_delimiter': 8,
            'source_port': 16,
            'session_state': 2,
            'ack_flag': 1,
            'sequence_number': 1,
            'data_segment': 32,
            'dest_port': 16,
            'crc_checksum': 16
        }

        for field, expected_bits in bit_sizes.items():
            if hasattr(frame_instance, f"{field}_bits"):
                actual_bits = getattr(frame_instance, f"{field}_bits")
                assert actual_bits == expected_bits, f"{field} bit count error: expected {expected_bits}, got {actual_bits}"

    except ImportError as e:
        pytest.fail("Unable to import Frame class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")

    print("Frame structure field completeness test passed")

if __name__ == "__main__":
    try:
        test_frame_fields_completeness()
        print("All tests passed")
    except Exception as e:
        print(f"Test execution failed: {str(e)}")
        exit(1)