"""
Category Search Functional Test
"""
import sys
import os
import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from locallens.core.config import Config
from locallens.core.database import DatabaseManager
from locallens.search.engine import SearchEngine

@pytest.fixture(scope="module")
def search_engine():
    """Initialize and return a search engine instance"""
    config = Config()
    db_manager = DatabaseManager(config.database_path)
    engine = SearchEngine(config, db_manager)
    # Make sure to load business data
    engine._get_businesses()
    return engine

def test_category_search_strictness(search_engine):
    “””
    Test that when searching by subcategory, results strictly match.
    “””
    # Execute category search
    results = search_engine.search_by_category(
        category=”Restaurants”,
        subcategory=”Chinese”,
        limit=20
    )

    # Assert result is not empty
    assert results is not None, “Search result should not be None”
    assert 'businesses' in results, “Search result should contain 'businesses' key”

    businesses = results['businesses']

    # Assert returned businesses exist
    assert len(businesses) > 0, “Should return at least one business”

    # Important assertion: check that each returned business contains the “Chinese” category
    for business in businesses:
        categories = business.get('categories', '')
        assert 'chinese' in categories.lower(), \
            f”Business '{business.get('name')}' (ID: {business.get('business_id')}) with categories '{categories}' does not contain 'chinese'”
