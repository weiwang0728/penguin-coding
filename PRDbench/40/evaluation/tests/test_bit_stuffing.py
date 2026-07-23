import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_bit_stuffing_algorithm():
    """Test bit stuffing algorithm implementation"""
    try:
        # Try to import bit stuffing related module
        bit_stuffing_found = False
        bit_stuffing_impl = None

        # Try to import from utils.coding
        try:
            from utils.coding import BitStuffing
            bit_stuffing_impl = BitStuffing()
            bit_stuffing_found = True
        except ImportError:
            pass

        # Try to import from utils.frame
        if not bit_stuffing_found:
            try:
                from utils.frame import BitStuffing
                bit_stuffing_impl = BitStuffing()
                bit_stuffing_found = True
            except ImportError:
                pass

        # Try to import related functions from other modules
        if not bit_stuffing_found:
            try:
                from utils.coding import bit_stuff, bit_unstuff
                bit_stuffing_found = True
            except ImportError:
                pass

        # Try to import from frame module
        if not bit_stuffing_found:
            try:
                from utils.frame import stuff_bits, unstuff_bits
                bit_stuffing_found = True
            except ImportError:
                pass

        assert bit_stuffing_found, "Bit stuffing algorithm implementation not found"

        # Test bit stuffing functionality
        test_data = "11111100"  # Contains consecutive 5 '1's test data
        expected_result = "111110100"  # Expected to insert '0' after consecutive 5 '1's

        stuffing_result = None

        # Try different methods to use bit stuffing
        if bit_stuffing_impl:
            if hasattr(bit_stuffing_impl, 'stuff'):
                stuffing_result = bit_stuffing_impl.stuff(test_data)
            elif hasattr(bit_stuffing_impl, 'bit_stuff'):
                stuffing_result = bit_stuffing_impl.bit_stuff(test_data)
            elif hasattr(bit_stuffing_impl, 'insert_zeros'):
                stuffing_result = bit_stuffing_impl.insert_zeros(test_data)

        # Try function call
        if stuffing_result is None:
            try:
                stuffing_result = bit_stuff(test_data)
            except NameError:
                pass

        if stuffing_result is None:
            try:
                stuffing_result = stuff_bits(test_data)
            except NameError:
                pass

        # Verify bit stuffing result
        if stuffing_result is not None:
            assert isinstance(stuffing_result, str), "Bit stuffing result should be a string"
            assert len(stuffing_result) >= len(test_data), "Data length after stuffing should not be less than original data"

            # Check if consecutive 5 '1's are correctly processed
            if "11111" in test_data:
                # After stuffing there should not be consecutive 6 '1's
                assert "111111" not in stuffing_result, "Still contains consecutive 6 '1's after bit stuffing"

        # Check frame delimiter uniqueness protection
        frame_delimiter = "01111110"

        # Test that frame delimiter doesn't appear in data
        test_data_with_delimiter = "0111111001111110"

        if bit_stuffing_impl:
            if hasattr(bit_stuffing_impl, 'stuff'):
                result = bit_stuffing_impl.stuff(test_data_with_delimiter)
                if result:
                    # Check if there are still complete frame delimiters after stuffing (excluding actual frame boundaries)
                    delimiter_count = result.count(frame_delimiter)
                    assert delimiter_count <= 2, "Bit stuffing cannot protect frame delimiter uniqueness"

    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")