"""
Personalized Recommendation Functional Test
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
    # Ensure db_manager is set to ranking_engine
    engine.ranking_engine.set_database_manager(db_manager)
    return engine

def test_recommendation_relevance(search_engine):
    """
    Test if recommendations for logged-in users are reasonable.
    """
    # Use a user with sufficient review history for testing
    user_id = "HFECrzYDpgbS5EmTBtj2zQ"

    # 1. Get user profile and category preferences
    user_profile = search_engine.ranking_engine._get_user_profile(user_id)
    assert user_profile is not None, f"Unable to load user '{user_id}' profile"

    category_prefs = user_profile.get('category_preferences', {})

    # 2. Get recommendation results
    recommendations = search_engine.get_recommendations(
        user_id=user_id,
        limit=10
    )

    # 3. Assert recommendation results are not empty
    assert recommendations is not None, "Recommendation result should not be None"
    assert 'businesses' in recommendations, "Recommendation result should contain 'businesses' key"

    recommended_businesses = recommendations['businesses']
    assert len(recommended_businesses) > 0, "Should return at least one recommended business"

    # 4. Verify recommendation result quality
    if category_prefs:
        # If user has category preferences, verify recommendation relevance
        preferred_categories = set(category_prefs.keys())

        # At least some recommendations should match user preferences
        matching_count = 0
        for business in recommended_businesses:
            business_categories_str = business.get('categories', '').lower()
            business_categories = {cat.strip() for cat in business_categories_str.split(',')}

            # Check if business categories and user preferred categories have intersection
            if not preferred_categories.isdisjoint(business_categories):
                matching_count += 1

        match_ratio = matching_count / len(recommended_businesses)
        print(f"User {user_id} has {len(category_prefs)} category preferences")
        print(f"Recommendation match rate: {match_ratio:.2f} ({matching_count}/{len(recommended_businesses)})")

        # If user has category preferences, at least 30% of recommendations should match
        assert match_ratio >= 0.3, f"Recommendation relevance too low: {matching_count}/{len(recommended_businesses)} = {match_ratio:.2f}"
    else:
        # If user has no category preferences, verify recommendations based on quality
        print(f"User {user_id} has no category preferences, verifying recommendation quality")

        # Verify recommendation business quality (ratings should be reasonable)
        total_stars = sum(b.get('stars', 0) for b in recommended_businesses)
        avg_stars = total_stars / len(recommended_businesses)
        assert avg_stars >= 2.0, f"Recommended business average rating too low: {avg_stars:.2f}"

        print(f"Recommended business average rating: {avg_stars:.2f}")

    # 5. Verify recommendation results have recommendation scores
    for business in recommended_businesses:
        assert 'recommendation_score' in business, f"Business '{business.get('name')}' is missing recommendation score"
        assert business['recommendation_score'] > 0, f"Business '{business.get('name')}' recommendation score should be greater than 0"
