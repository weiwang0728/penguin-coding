"""
Personalization Functional Test
"""
import sys
import os
import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from locallens.ui.cli_complete import CLI
from locallens.core.config import Config
from locallens.core.database import DatabaseManager
from locallens.search.engine import SearchEngine


class TestPersonalization:
    """Personalization Test Suite"""

    @pytest.fixture
    def setup_cli(self):
        """Set up test environment"""
        cli = CLI()

        # Initialize configuration and database connection
        config = Config()
        db_manager = DatabaseManager(config.database_path)
        search_engine = SearchEngine(config, db_manager)

        # Set CLI components
        cli.config = config
        cli.db_manager = db_manager
        cli.search_engine = search_engine

        return cli

    def test_personalized_ranking(self, setup_cli):
        """Test personalized ranking"""
        cli = setup_cli
        # Set location
        location = (27.91, -82.71)
        # User 1 search
        cli.current_user_id = "HFECrzYDpgbS5EmTBtj2zQ"
        cli.current_location = location
        cli.search_engine.set_user_context("HFECrzYDpgbS5EmTBtj2zQ", location)
        results1 = cli.search_engine.search(
            query="restaurant",
            location=location,
            user_id="HFECrzYDpgbS5EmTBtj2zQ"
        )
        # User 2 search
        cli.current_user_id = "Xwnf20FKuikiHcSpcEbpKQ"
        cli.search_engine.set_user_context("Xwnf20FKuikiHcSpcEbpKQ", location)
        results2 = cli.search_engine.search(
            query="restaurant",
            location=location,
            user_id="Xwnf20FKuikiHcSpcEbpKQ"
        )
        # Verify both results exist
        assert results1 is not None and 'businesses' in results1
        assert results2 is not None and 'businesses' in results2
        businesses1 = results1['businesses']
        businesses2 = results2['businesses']
        # Ensure both users have enough results
        if len(businesses1) >= 5 and len(businesses2) >= 5:
            # Compare top 5 result business IDs
            top5_ids_HFECrzYDpgbS5EmTBtj2zQ = [b.get('business_id') for b in businesses1[:5]]
            top5_ids_Xwnf20FKuikiHcSpcEbpKQ = [b.get('business_id') for b in businesses2[:5]]
            # Calculate ranking differences
            different_positions = 0
            for i in range(5):
                if i < len(top5_ids_HFECrzYDpgbS5EmTBtj2zQ) and i < len(top5_ids_Xwnf20FKuikiHcSpcEbpKQ):
                    if top5_ids_HFECrzYDpgbS5EmTBtj2zQ[i] != top5_ids_Xwnf20FKuikiHcSpcEbpKQ[i]:
                        different_positions += 1
            # Should have some ranking differences (relaxed requirements, as sample data may be limited)
            assert different_positions >= 1, f"Top 5 search results for two users should have ranking differences, actual differences: {different_positions}"
        # Should have at least some results
        assert len(businesses1) > 0 and len(businesses2) > 0, "Both users should have search results"
