"""
PerformanceTest
"""
import sys
import os
import pytest
import time

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from locallens.ui.cli_complete import CLI
from locallens.core.config import Config
from locallens.core.database import DatabaseManager
from locallens.search.engine import SearchEngine


class TestPerformance:
    """Performance Test Suite"""

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

    def test_search_response_time(self, setup_cli):
        """Test search response time should be within limits"""
        cli = setup_cli

        # Set location
        cli.current_location = (27.91, -82.71)
        cli.search_engine.set_user_context(None, cli.current_location)

        # Prepare 5 different search queries
        queries = [
            "restaurant",
            "coffee",
            "pizza",
            "italian",
            "food"
        ]

        response_times = []

        # Execute 5 searches and record response times
        for query in queries:
            start_time = time.time()

            results = cli.search_engine.search(
                query=query,
                location=cli.current_location
            )

            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)

            # Verify search success
            assert results is not None, f"Search '{query}' should return results"

            # Verify single search completes within 5 seconds
            assert response_time <= 5.0, f"Search '{query}' response time {response_time:.2f}s exceeds 5 second limit"

        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times)

        # Verify average response time is within 3 seconds
        assert avg_response_time <= 3.0, f"Average response time {avg_response_time:.2f}s exceeds 3 second limit"

        # Output performance statistics (for debugging)
        print(f"\nPerformance Statistics:")
        print(f"Individual search response times: {[f'{t:.2f}s' for t in response_times]}")
        print(f"Average response time: {avg_response_time:.2f}s")
        print(f"Maximum response time: {max(response_times):.2f}s")
        print(f"Minimum response time: {min(response_times):.2f}s")
