"""
Reliability tests for the AI recommender.

All tests mock the Anthropic client — no real API calls are made.
This lets the test suite run in CI without an API key.

Tests cover:
  1. Normal query returns a non-empty recommendation string
  2. Empty query hits the guardrail before any API call
  3. Malformed JSON from Claude falls back gracefully (no crash)
  4. Preference parsing returns the expected dict structure
  5. Similar queries retrieve overlapping candidate songs (consistency)
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.ai_recommender import AIRecommender

CATALOG = "data/songs.csv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_client(parse_text: str, recommend_text: str) -> MagicMock:
    """Return a mock anthropic.Anthropic() whose messages.create cycles through two responses."""
    client = MagicMock()
    client.messages.create.side_effect = [
        MagicMock(content=[MagicMock(text=parse_text)]),
        MagicMock(content=[MagicMock(text=recommend_text)]),
    ]
    return client


_LOFI_PREFS = json.dumps({
    "genre": "lofi",
    "mood": "chill",
    "target_energy": 0.40,
    "target_valence": 0.58,
    "likes_acoustic": True,
})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@patch("src.ai_recommender.anthropic.Anthropic")
def test_recommend_returns_non_empty_string(MockAnthropic):
    MockAnthropic.return_value = _mock_client(
        _LOFI_PREFS,
        "Try Midnight Coding and Library Rain — both are perfect for studying.",
    )
    rec = AIRecommender(CATALOG)
    result = rec.recommend("chill lofi for studying")

    assert isinstance(result, str)
    assert len(result.strip()) > 0


@patch("src.ai_recommender.anthropic.Anthropic")
def test_empty_query_returns_guardrail_without_api_call(MockAnthropic):
    client = MagicMock()
    MockAnthropic.return_value = client

    rec = AIRecommender(CATALOG)
    result = rec.recommend("   ")

    # Guardrail message must mention what to do
    assert "describe" in result.lower() or "looking for" in result.lower()
    # No API call should have been made
    client.messages.create.assert_not_called()


@patch("src.ai_recommender.anthropic.Anthropic")
def test_malformed_json_from_claude_falls_back_gracefully(MockAnthropic):
    MockAnthropic.return_value = _mock_client(
        "not valid json { broken",
        "Here are some songs you might like.",
    )
    rec = AIRecommender(CATALOG)
    # Should not raise; fallback prefs trigger a valid retrieval + generation
    result = rec.recommend("something good")

    assert isinstance(result, str)
    assert len(result.strip()) > 0


@patch("src.ai_recommender.anthropic.Anthropic")
def test_parse_preferences_returns_required_keys(MockAnthropic):
    client = MagicMock()
    client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=_LOFI_PREFS)]
    )
    MockAnthropic.return_value = client

    rec = AIRecommender(CATALOG)
    prefs = rec._parse_preferences("chill music for late night")

    for key in ("genre", "mood", "target_energy", "target_valence", "likes_acoustic"):
        assert key in prefs, f"Missing key: {key}"

    assert 0.0 <= prefs["target_energy"] <= 1.0
    assert 0.0 <= prefs["target_valence"] <= 1.0


@patch("src.ai_recommender.anthropic.Anthropic")
def test_similar_queries_retrieve_overlapping_candidates(MockAnthropic):
    """
    Consistency check: two queries that parse to the same preferences
    must retrieve the same songs from the rule-based scorer.
    """
    client = MagicMock()
    client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=_LOFI_PREFS)]
    )
    MockAnthropic.return_value = client

    rec = AIRecommender(CATALOG)
    prefs_a = rec._parse_preferences("chill beats for studying")
    prefs_b = rec._parse_preferences("lofi music to relax")

    from src.recommender import recommend_songs
    songs_a = {s["title"] for s, _, _ in recommend_songs(prefs_a, rec.songs, k=5)}
    songs_b = {s["title"] for s, _, _ in recommend_songs(prefs_b, rec.songs, k=5)}

    # Identical parsed prefs must yield identical retrieval results
    assert songs_a == songs_b
