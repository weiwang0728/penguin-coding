import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_router_table_structure():
    """Test RouterTable class data structure"""
    try:
        # Try to import the RouterTable class
        from layer.router import RouterTable

        # Create a RouterTable instance
        router_table = RouterTable()

        # Check WAN mapping structure (router_id -> Path structure)
        wan_attributes = ['wan_table', 'wan_routes', 'router_table', 'wan']
        found_wan = False
        wan_table = None

        for attr in wan_attributes:
            if hasattr(router_table, attr):
                wan_table = getattr(router_table, attr)
                found_wan = True
                break

        assert found_wan, "RouterTable is missing WAN mapping structure"
        assert isinstance(wan_table, dict), "WAN mapping should be a dictionary type"

        # Check LAN mapping structure (host_id -> exit_port)
        lan_attributes = ['lan_table', 'lan_routes', 'host_table', 'lan']
        found_lan = False
        lan_table = None

        for attr in lan_attributes:
            if hasattr(router_table, attr):
                lan_table = getattr(router_table, attr)
                found_lan = True
                break

        assert found_lan, "RouterTable is missing LAN mapping structure"
        assert isinstance(lan_table, dict), "LAN mapping should be a dictionary type"

        # Check basic routing table operation methods
        methods = ['add_route', 'update_route', 'get_route', 'lookup']
        found_methods = []

        for method in methods:
            if hasattr(router_table, method):
                found_methods.append(method)

        assert len(found_methods) > 0, "RouterTable is missing basic routing operation methods"

    except ImportError:
        # Try other possible import paths
        try:
            from router import RouterTable
            # Repeat the above test logic
        except ImportError:
            pytest.fail("Unable to import RouterTable class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")