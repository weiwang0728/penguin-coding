"""Tests for context compaction logic."""

from src.compact import needs_compaction, COMPACT_THRESHOLD, MAX_CONTEXT_TOKENS


class TestNeedsCompaction:
    def test_returns_true_when_no_api_data(self):
        assert needs_compaction(last_input_tokens=0, pending_delta=0) is True

    def test_returns_true_when_approaching_threshold(self):
        threshold = int(MAX_CONTEXT_TOKENS * COMPACT_THRESHOLD)
        assert needs_compaction(last_input_tokens=threshold + 1, pending_delta=0) is True

    def test_returns_false_when_well_below_threshold(self):
        assert needs_compaction(last_input_tokens=1000, pending_delta=500) is False

    def test_pending_delta_pushes_over_threshold(self):
        threshold = int(MAX_CONTEXT_TOKENS * COMPACT_THRESHOLD)
        # Just under threshold with last_input_tokens alone
        assert needs_compaction(last_input_tokens=threshold - 100, pending_delta=0) is False
        # But over with pending_delta
        assert needs_compaction(last_input_tokens=threshold - 100, pending_delta=200) is True

    def test_exact_threshold_boundary(self):
        threshold = int(MAX_CONTEXT_TOKENS * COMPACT_THRESHOLD)
        # At exactly the threshold, should not trigger (uses >)
        assert needs_compaction(last_input_tokens=threshold, pending_delta=0) is False

    def test_custom_max_tokens(self):
        # Small max_tokens for testing
        assert needs_compaction(last_input_tokens=81, pending_delta=0, max_tokens=100) is True
        assert needs_compaction(last_input_tokens=79, pending_delta=0, max_tokens=100) is False
