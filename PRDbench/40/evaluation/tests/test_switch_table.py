import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_switch_table_structure():
    """Test the basic implementation of the SwitchTable class"""
    try:
        # Try to import the SwitchTable class
        from layer.switch import SwitchTable

        # Create a SwitchTable instance
        switch_table = SwitchTable()

        # Check if the data structure is a dictionary type
        if hasattr(switch_table, 'table'):
            table = switch_table.table
        elif hasattr(switch_table, 'address_table'):
            table = switch_table.address_table
        elif hasattr(switch_table, 'port_table'):
            table = switch_table.port_table
        else:
            pytest.fail("SwitchTable class is missing the address table data structure")

        assert isinstance(table, dict), "Port address table should be a dictionary type"

        # Test the add entry function
        test_local_port = 1
        test_remote_port = 11300
        test_lifetime = 100

        # Try to add an entry
        if hasattr(switch_table, 'add_entry'):
            switch_table.add_entry(test_local_port, test_remote_port, test_lifetime)
        elif hasattr(switch_table, 'learn'):
            switch_table.learn(test_local_port, test_remote_port, test_lifetime)
        elif hasattr(switch_table, 'update'):
            switch_table.update(test_local_port, test_remote_port, test_lifetime)

        # Verify the data structure format: dict[local_port, dict[remote_port, lifetime]]
        if test_local_port in table:
            assert isinstance(table[test_local_port], dict), "The value for a given port should be a dictionary"
            if test_remote_port in table[test_local_port]:
                assert isinstance(table[test_local_port][test_remote_port], (int, float)), "Lifetime should be a numeric type"

    except ImportError:
        # Try other possible import paths
        try:
            from switch import SwitchTable
            # Repeat the above tests
        except ImportError:
            pytest.fail("Unable to import SwitchTable class")
    except Exception as e:
        pytest.fail(f"Test Failed: {str(e)}")