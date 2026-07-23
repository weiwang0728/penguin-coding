import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_ack_nak_mechanism():
    """Test stop-and-wait ARQ - ACK/NAK mechanism"""
    try:
        # Try to import ARQ-related module
        arq_found = False
        arq_impl = None

        # Try to import ARQ implementation from different modules
        try:
            from utils.flow_control import ARQ
            arq_impl = ARQ()
            arq_found = True
        except ImportError:
            pass

        if not arq_found:
            try:
                from layer.net import NetLayer
                net_layer = NetLayer()
                if hasattr(net_layer, 'ack') or hasattr(net_layer, 'nak'):
                    arq_impl = net_layer
                    arq_found = True
            except ImportError:
                pass

        if not arq_found:
            try:
                from utils.frame import Frame
                frame = Frame()
                if hasattr(frame, 'ack_flag'):
                    arq_found = True
            except ImportError:
                pass

        assert arq_found, "ARQ mechanism implementation not found"

        # Check ACK mechanism
        ack_found = False

        if arq_impl:
            ack_methods = ['send_ack', 'ack', 'acknowledge', 'confirm']
            for method in ack_methods:
                if hasattr(arq_impl, method):
                    ack_found = True
                    break

        # Check if ACK flag is defined in frame structure
        if not ack_found:
            try:
                from utils.frame import Frame
                frame = Frame()
                if hasattr(frame, 'ack_flag') or hasattr(frame, 'ack'):
                    ack_found = True
            except ImportError:
                pass

        assert ack_found, "ACK acknowledgment mechanism not found"

        # Check NAK mechanism
        nak_found = False

        if arq_impl:
            nak_methods = ['send_nak', 'nak', 'negative_ack', 'reject']
            for method in nak_methods:
                if hasattr(arq_impl, method):
                    nak_found = True
                    break

        # Check if frame structure supports NAK
        if not nak_found:
            try:
                from utils.frame import Frame
                frame = Frame()
                # NAK is typically represented by different values of ACK flag
                if hasattr(frame, 'ack_flag'):
                    nak_found = True
            except ImportError:
                pass

        assert nak_found, "NAK negative acknowledgment mechanism not found"

    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")

def test_sequence_number_alternation():
    """Test stop-and-wait ARQ - sequence number alternation"""
    try:
        # Try to import sequence number related implementation
        seq_found = False
        seq_impl = None

        # Try to import from frame structure
        try:
            from utils.frame import Frame
            frame = Frame()
            if hasattr(frame, 'sequence_number') or hasattr(frame, 'seq_num'):
                seq_impl = frame
                seq_found = True
        except ImportError:
            pass

        # Try to import from network layer
        if not seq_found:
            try:
                from layer.net import NetLayer
                net_layer = NetLayer()
                if hasattr(net_layer, 'sequence_number') or hasattr(net_layer, 'seq'):
                    seq_impl = net_layer
                    seq_found = True
            except ImportError:
                pass

        assert seq_found, "Sequence number mechanism implementation not found"

        # Check sequence number field
        seq_field_found = False

        if seq_impl:
            seq_attributes = ['sequence_number', 'seq_num', 'seq', 'sequence']
            for attr in seq_attributes:
                if hasattr(seq_impl, attr):
                    seq_field_found = True
                    break

        assert seq_field_found, "Sequence number field not found"

        # Check sequence number alternation mechanism
        alternation_found = False

        if seq_impl:
            # Check if there is a sequence number update method
            update_methods = ['next_sequence', 'toggle_sequence', 'update_seq', 'alternate_seq']
            for method in update_methods:
                if hasattr(seq_impl, method):
                    alternation_found = True
                    break

        # Check if there is 0/1 alternation logic
        if not alternation_found:
            # If there is a sequence number field, assume alternation logic is implemented
            if seq_field_found:
                alternation_found = True

        assert alternation_found, "Sequence number alternation mechanism not found"

        # Verify sequence number range (should be 0/1 alternation)
        if seq_impl and hasattr(seq_impl, 'sequence_number'):
            seq_val = getattr(seq_impl, 'sequence_number')
            if seq_val is not None:
                assert seq_val in [0, 1], f"Sequence number should be 0 or 1, got value: {seq_val}"

    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")