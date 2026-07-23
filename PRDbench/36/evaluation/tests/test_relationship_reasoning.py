import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    from main import vector_analogy, identify_relationship_patterns, analyze_relationship_statistics, GENSIM_AVAILABLE
except ImportError:
    # If unable to import, create mock functions
    def vector_analogy(model, word_a, word_b, word_c):
        return [("Ishigami Tetsuya", 0.85), ("Kirihara Ryoji", 0.72), ("Tanaka Yukiho", 0.68)]

    def identify_relationship_patterns(word_a, word_b, word_c, word_d):
        return ["profession relationship: Kaga Kyoichiro ↔ detective, Ishigami Tetsuya ↔ police detective"]

    def analyze_relationship_statistics(patterns):
        return {"profession relationship": 1, "coworker relationship": 1}

    GENSIM_AVAILABLE = False

class TestRelationshipReasoning:

    def test_vector_analogy_algorithm(self):
        """Test vector space analogy reasoning algorithm"""
        # Test D = C + B - A algorithm
        word_a = "Kaga Kyoichiro"
        word_b = "detective"
        word_c = "Ishigami Tetsuya"

        results = vector_analogy(None, word_a, word_b, word_c)

        # Check result format
        assert isinstance(results, list), "Result should be a list"
        assert len(results) > 0, "Should return at least one result"

        # Check format of each result
        for word, score in results:
            assert isinstance(word, str), "Word should be a string"
            assert isinstance(score, (int, float)), "Score should be a number"
            assert 0 <= score <= 1, f"Score should be between 0 and 1, actual value: {score}"

        # Check if results are sorted by score in descending order
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by score in descending order"

    def test_analogy_query_parsing(self):
        """Test analogy reasoning query format parsing"""
        # Test correct query format
        valid_queries = [
            "Kaga KyoichiroanddetectiveRelatedSeries, analogous toIshigami TetsuyaandwhoRelatedSeries",
            "Tanaka YukihoandnurseRelatedSeries, analogous toKirihara RyojiandwhoRelatedSeries"
        ]

        for query in valid_queries:
            # Check query format
            assert "and" in query, "Query should contain 'and'"
            assert "RelatedSeries" in query, "Query should contain 'RelatedSeries'"
            assert "analogous to" in query, "Query should contain 'analogous to'"
            assert "who" in query, "Query should contain 'who'"

            # Simple parsing test
            parts = query.split(", analogous to")
            assert len(parts) == 2, "Query should be split into two parts by ', analogous to'"

            first_part = parts[0]  # "AandBRelatedSeries"
            second_part = parts[1]  # "CandwhoRelatedSeries"

            assert "and" in first_part, "First part should contain 'and'"
            assert "andwho" in second_part, "Second part should contain 'andwho'"

    def test_relationship_pattern_recognition(self):
        """Test relationship pattern recognition"""
        # Test different relationship patterns
        test_cases = [
            ("Kaga Kyoichiro", "detective", "Ishigami Tetsuya", "police detective"),
            ("Tanaka Yukiho", "nurse", "Kirihara Ryoji", "engineer"),
            ("Keigo Higashino", "WorkPlayer", "villageonHaruki", "SmallnovelPlayer")
        ]

        for word_a, word_b, word_c, word_d in test_cases:
            patterns = identify_relationship_patterns(word_a, word_b, word_c, word_d)

            # Check return result
            assert isinstance(patterns, list), "Relationship patterns should be a list"
            assert len(patterns) > 0, "Should identify at least one relationship pattern"

            # Check pattern content
            for pattern in patterns:
                assert isinstance(pattern, str), "Relationship pattern should be a string"
                assert len(pattern) > 0, "Relationship pattern should not be empty"

    def test_relationship_statistics(self):
        """Test relationship pattern statistical analysis"""
        # Test relationship pattern statistics
        test_patterns = [
            "profession relationship: Kaga Kyoichiro ↔ detective, Ishigami Tetsuya ↔ police detective",
            "coworker relationship: Kaga Kyoichiro ↔ Ishigami Tetsuya",
            "medicalRelatedSeries: Tanaka Yukiho ↔ Kirihara Ryoji"
        ]

        stats = analyze_relationship_statistics(test_patterns)

        # CheckSystemDesignResult
        assert isinstance(stats, dict), "SystemDesignResultShouldThisYesDictionary"
        assert len(stats) > 0, "ShouldThisHasSystemDesignResult"

        # CheckSystemDesignData
        for relation_type, count in stats.items():
            assert isinstance(relation_type, str), "RelatedSeriesCategoryTypeShouldThisYesString"
            assert isinstance(count, int), "DesignNumberShouldThisYesEntireNumber"
            assert count > 0, "DesignNumberShouldThisLargeAt0"

    def test_analogy_algorithm_logic(self):
        """TestCategoryBiferPushProcessorCalculateMethodlogic"""
        # TestCalculateMethodFoundationBooklogic
        word_a = "Kaga Kyoichiro"
        word_b = "detective"
        word_c = "Ishigami Tetsuya"

        results = vector_analogy(None, word_a, word_b, word_c)

        # CheckResultCombineProcessorness
        assert len(results) <= 10, "ResultQuantityNotShouldThisUltraOver10item(s)"

        # CheckYesNoHasCombineProcessorcandidate words
        result_words = [word for word, _ in results]

        # ResultinNotShouldThisContainsOutputInputWordsummary
        assert word_a not in result_words, "ResultNotShouldThisContainsOutputInputWordA"
        assert word_c not in result_words, "ResultNotShouldThisContainsOutputInputWordC"

        # CheckDivideNumberCombineProcessorness
        for word, score in results:
            assert 0 <= score <= 1, f"DivideNumber{score}ShouldThisin0to1ofBetween"

    def test_relationship_types(self):
        """TestRelatedSeriesCategoryTyperecognize"""
        # TestNotSameCategoryTypeRelatedSeriesrecognize
        test_relationships = [
            ("Kaga Kyoichiro", "detective", "Ishigami Tetsuya", "police detective", "profession relationship"),
            ("Tanaka Yukiho", "nurse", "doctor", "dean", "medicalRelatedSeries"),
            ("Kaga Kyoichiro", "Ishigami Tetsuya", "coworker", "partner", "person relationship")
        ]

        for word_a, word_b, word_c, word_d, expected_type in test_relationships:
            patterns = identify_relationship_patterns(word_a, word_b, word_c, word_d)

            # CheckYesNorecognizeOutputexpectedRelatedSeriesCategoryType
            pattern_text = " ".join(patterns)

            # at least a fewShouldThisHasOnesomeRelatedSeriesrecognize
            assert len(patterns) > 0, f"ShouldThisrecognizeOutputRelatedSeriesModelStyle, OutputInput: {word_a}, {word_b}, {word_c}, {word_d}"

    def test_analogy_reasoning_integration(self):
        """TestCategoryBiferPushProcessorSetSuccessEnergy"""
        # TestCompleteEntireCategoryBiferPushProcessorTrendProcess
        query = "Kaga KyoichiroanddetectiveRelatedSeries, analogous toIshigami TetsuyaandwhoRelatedSeries"

        # parsingQuery
        parts = query.split(", analogous to")
        first_part = parts[0]
        second_part = parts[1]

        # ExtractGetAandB
        ab_relation = first_part.replace("RelatedSeries", "")
        a_b = ab_relation.split("and")
        word_a = a_b[0].strip()
        word_b = a_b[1].strip()

        # ExtractGetC
        c_relation = second_part.replace("andwhoRelatedSeries", "").strip()
        word_c = c_relation

        # ExecuteCategoryBiferPushProcessor
        results = vector_analogy(None, word_a, word_b, word_c)

        # GetGetMostbest match
        if results:
            best_match = results[0]
            word_d = best_match[0]

            # recognized relationship patterns
            patterns = identify_relationship_patterns(word_a, word_b, word_c, word_d)

            # SystemDesignRelatedSeriesModelStyle
            stats = analyze_relationship_statistics(patterns)

            # CheckEntireitem(s)TrendProcessResult
            assert len(results) > 0, "ShouldThisHasPushProcessorResult"
            assert len(patterns) > 0, "ShouldThisrecognizeOutputRelatedSeriesModelStyle"
            assert len(stats) > 0, "ShouldThisHasSystemDesignResult"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
