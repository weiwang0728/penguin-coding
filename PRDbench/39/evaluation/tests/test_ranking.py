"""
Ranking Weight and Multi-Feature Matching Functional Test
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
    engine.ranking_engine.set_database_manager(db_manager)
    engine._get_businesses()
    return engine

def test_exact_name_ranking(search_engine):
    """
    Test exact match business name search should rank this business at the top (Issue 4.1a)
    """
    # This business exists in the dataset
    search_query = "Jersey Mike's Subs"
    results = search_engine.search(query=search_query, limit=1)

    assert results and results['businesses'], f"Search '{search_query}' did not return any results"

    top_result = results['businesses'][0]

    assert top_result.get('name') == search_query, \
        f"Search '{search_query}' should return exact match business as top result, but returned '{top_result.get('name')}'"

def test_category_ranking_relevance(search_engine):
    """
    Test category-related keyword search result relevance (Issue 4.1b)
    """
    search_query = "Pizza"
    results = search_engine.search(query=search_query, limit=10)

    assert results and results['businesses'], f"Search '{search_query}' did not return any results"

    businesses = results['businesses']

    match_count = 0
    for business in businesses:
        name = business.get('name', '').lower()
        categories = business.get('categories', '').lower()
        if 'pizza' in name or 'pizza' in categories:
            match_count += 1

    # Assertion: top 10 results should have at least 8 relevant matches
    assert match_count >= 8, \
        f"Search '{search_query}' should have at least 8 relevant results in top 10, but only found {match_count}"

def test_address_ranking_relevance(search_engine):
    """
    Test address-related keyword search result relevance (Issue 4.1c)
    """
    # This address exists in the dataset
    search_query = "McMullen Booth Rd"
    results = search_engine.search(query=search_query, limit=5)

    assert results and results['businesses'], f"Search '{search_query}' did not return any results"

    businesses = results['businesses']

    for business in businesses:
        address = business.get('address', '')
        assert search_query.lower() in address.lower(), \
            f"Search '{search_query}' returned result '{business.get('name')}' with address '{address}' that does not contain the search keyword"
