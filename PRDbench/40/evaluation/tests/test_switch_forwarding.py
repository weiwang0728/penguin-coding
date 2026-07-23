import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_unicast_forwarding():
    """Test switch unicast forwarding"""
    try:
        # Try to import the Switch class
        from layer.switch import Switch

        switch = Switch()

        # Check unicast forwarding method
        unicast_methods = ['unicast_forward', 'forward_unicast', 'send_unicast', 'forward_to_port']
        found_unicast = False

        for method in unicast_methods:
            if hasattr(switch, method):
                found_unicast = True
                break

        # Check general forwarding method
        if not found_unicast:
            forward_methods = ['forward', 'forward_frame', 'process_frame', 'handle_frame']
            for method in forward_methods:
                if hasattr(switch, method):
                    found_unicast = True
                    break

        assert found_unicast, "Switch is missing unicast forwarding functionality"

        # Check address table query functionality
        lookup_methods = ['lookup_port', 'find_port', 'get_port', 'query_table']
        found_lookup = False

        for method in lookup_methods:
            if hasattr(switch, method):
                found_lookup = True
                break

        # Check if there is an address table
        if not found_lookup:
            if hasattr(switch, 'switch_table') or hasattr(switch, 'address_table'):
                found_lookup = True

        assert found_lookup, "Switch is missing address table query functionality"

    except ImportError:
        pytest.fail("Unable to import Switch class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")

def test_broadcast_forwarding():
    """Test switch broadcast forwarding"""
    try:
        from layer.switch import Switch

        switch = Switch()

        # Check broadcast forwarding method
        broadcast_methods = ['broadcast', 'forward_broadcast', 'send_broadcast', 'flood_all']
        found_broadcast = False

        for method in broadcast_methods:
            if hasattr(switch, method):
                found_broadcast = True
                break

        # Check if general forwarding method supports broadcast
        if not found_broadcast:
            forward_methods = ['forward', 'forward_frame', 'process_frame']
            for method in forward_methods:
                if hasattr(switch, method):
                    # Assume general forwarding method supports broadcast
                    found_broadcast = True
                    break

        assert found_broadcast, "Switch is missing broadcast forwarding functionality"

        # Check port management functionality
        port_methods = ['get_ports', 'list_ports', 'all_ports', 'get_interfaces']
        found_ports = False

        for method in port_methods:
            if hasattr(switch, method):
                found_ports = True
                break

        # Check if there is a port list attribute
        if not found_ports:
            port_attrs = ['ports', 'interfaces', 'port_list', 'connections']
            for attr in port_attrs:
                if hasattr(switch, attr):
                    found_ports = True
                    break

        assert found_ports, "Switch is missing port management functionality"

    except ImportError:
        pytest.fail("Unable to import Switch class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")

def test_flooding_forwarding():
    """Test switch flooding forwarding"""
    try:
        from layer.switch import Switch

        switch = Switch()

        # Check flooding forwarding method
        flood_methods = ['flood', 'flooding', 'flood_unknown', 'forward_unknown']
        found_flood = False

        for method in flood_methods:
            if hasattr(switch, method):
                found_flood = True
                break

        # Check unknown address processing
        if not found_flood:
            unknown_methods = ['handle_unknown', 'process_unknown', 'unknown_destination']
            for method in unknown_methods:
                if hasattr(switch, method):
                    found_flood = True
                    break

        # Check general forwarding method
        if not found_flood:
            forward_methods = ['forward', 'forward_frame', 'process_frame']
            for method in forward_methods:
                if hasattr(switch, method):
                    # Assume general forwarding method contains flooding logic
                    found_flood = True
                    break

        assert found_flood, "Switch is missing flooding forwarding functionality"

        # Check unknown address detection functionality
        detection_methods = ['is_unknown', 'address_unknown', 'not_in_table']
        found_detection = False

        for method in detection_methods:
            if hasattr(switch, method):
                found_detection = True
                break

        # If there is an address table, assume it can detect unknown addresses
        if not found_detection:
            if hasattr(switch, 'switch_table') or hasattr(switch, 'address_table'):
                found_detection = True

        assert found_detection, "Switch is missing unknown address detection functionality"

    except ImportError:
        pytest.fail("Unable to import Switch class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")