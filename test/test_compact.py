"""Tests for context compaction logic."""

from src.compact import needs_compaction, L2_SUMMARIZE_THRESHOLD, MAX_CONTEXT_TOKENS


class TestNeedsCompaction:
    def test_no_api_data_uses_local_estimate(self):
        # No API baseline: small local estimate -> no compaction at startup
        assert needs_compaction(last_input_tokens=0, pending_delta=0) is False
        threshold = int(MAX_CONTEXT_TOKENS * L2_SUMMARIZE_THRESHOLD)
        # Local estimate (fresh session passes the full estimate) over threshold -> compact
        assert needs_compaction(last_input_tokens=0, pending_delta=threshold + 1) is True
        assert needs_compaction(last_input_tokens=0, pending_delta=threshold - 1) is False

    def test_returns_true_when_approaching_threshold(self):
        threshold = int(MAX_CONTEXT_TOKENS * L2_SUMMARIZE_THRESHOLD)
        assert needs_compaction(last_input_tokens=threshold + 1, pending_delta=0) is True

    def test_returns_false_when_well_below_threshold(self):
        assert needs_compaction(last_input_tokens=1000, pending_delta=500) is False

    def test_pending_delta_pushes_over_threshold(self):
        threshold = int(MAX_CONTEXT_TOKENS * L2_SUMMARIZE_THRESHOLD)
        # Just under threshold with last_input_tokens alone
        assert needs_compaction(last_input_tokens=threshold - 100, pending_delta=0) is False
        # But over with pending_delta
        assert needs_compaction(last_input_tokens=threshold - 100, pending_delta=200) is True

    def test_exact_threshold_boundary(self):
        threshold = int(MAX_CONTEXT_TOKENS * L2_SUMMARIZE_THRESHOLD)
        # At exactly the threshold, should not trigger (uses >)
        assert needs_compaction(last_input_tokens=threshold, pending_delta=0) is False

    def test_custom_max_tokens(self):
        # Small max_tokens for testing (default threshold 0.7)
        assert needs_compaction(last_input_tokens=71, pending_delta=0, max_tokens=100) is True
        assert needs_compaction(last_input_tokens=69, pending_delta=0, max_tokens=100) is False

    def test_tiered_thresholds(self):
        from src.compact import L3_COLLAPSE_THRESHOLD

        l2_threshold = int(MAX_CONTEXT_TOKENS * L2_SUMMARIZE_THRESHOLD)
        l3_threshold = int(MAX_CONTEXT_TOKENS * L3_COLLAPSE_THRESHOLD)
        # Between L2 and L3: L2 triggers, L3 does not
        assert needs_compaction(last_input_tokens=l2_threshold + 1, pending_delta=0) is True
        assert needs_compaction(
            last_input_tokens=l2_threshold + 1, pending_delta=0,
            threshold=L3_COLLAPSE_THRESHOLD,
        ) is False
        # Above L3: both trigger
        assert needs_compaction(
            last_input_tokens=l3_threshold + 1, pending_delta=0,
            threshold=L3_COLLAPSE_THRESHOLD,
        ) is True
