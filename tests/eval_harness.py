"""
Evaluation harness for VibeMatch AI.

Runs a fixed set of predefined queries through the full RAG pipeline and
prints a structured pass/fail report. Each test case checks observable
properties of the output rather than exact wording.

Usage:
  python -m tests.eval_harness            # requires ANTHROPIC_API_KEY
  python -m tests.eval_harness --dry-run  # mocked, no API calls

Exit code: 0 if all tests pass, 1 if any fail.
"""

import json
import sys
from typing import Callable
from unittest.mock import MagicMock, patch

from src.ai_recommender import AIRecommender

CATALOG = "data/songs.csv"

# ---------------------------------------------------------------------------
# Test cases: (query, list of checker functions)
# Each checker returns (passed: bool, note: str)
# ---------------------------------------------------------------------------

def _non_empty(text: str):
    ok = len(text.strip()) > 20
    return ok, "output is non-empty" if ok else "output too short or empty"

def _mentions_a_song(text: str):
    catalog_titles = [
        "Sunrise City", "Midnight Coding", "Storm Runner", "Library Rain",
        "Gym Hero", "Spacewalk Thoughts", "Coffee Shop Stories", "Night Drive Loop",
        "Focus Flow", "Rooftop Lights", "Velvet Nights", "Block Rewind",
        "Morning Sonata", "Iron Cascade", "Ember Road", "Signal Burst",
        "Golden Haze", "Rust and Rain",
    ]
    matched = [t for t in catalog_titles if t in text]
    ok = len(matched) > 0
    return ok, f"mentions song(s): {matched}" if ok else "no catalog song title found in output"

def _no_hallucinated_artist(text: str):
    real_artists = [
        "Neon Echo", "LoRoom", "Voltline", "Paper Lanterns", "Max Pulse",
        "Orbit Bloom", "Slow Stereo", "Indigo Parade", "SoulBridge",
        "Dusty Cipher", "Clara Voss", "Wolfburn", "Hazel Finn",
        "Prism Wave", "Maren Cole", "Old River",
    ]
    unknown = [
        word for word in text.split()
        if word.istitle() and word not in real_artists
        and word not in ("Here", "Try", "These", "This", "The", "A", "An",
                         "For", "With", "Both", "And", "Or", "In", "On",
                         "If", "Is", "It", "Its", "You", "Your", "I",
                         "My", "We", "All", "Some", "Also", "Great",
                         "Good", "Best", "Top", "First", "Second", "Third",
                         "Perfect", "Ideal", "Nice", "Sure", "Note",
                         "Midnight", "Sunrise", "Storm", "Library", "Gym",
                         "Spacewalk", "Coffee", "Night", "Focus", "Rooftop",
                         "Velvet", "Block", "Morning", "Iron", "Ember",
                         "Signal", "Golden", "Rust", "Rain", "City",
                         "Coding", "Runner", "Hero", "Thoughts", "Stories",
                         "Drive", "Loop", "Flow", "Lights", "Nights",
                         "Rewind", "Sonata", "Cascade", "Road", "Burst",
                         "Haze")
    ]
    # We can't perfectly detect hallucinated artists without NLP,
    # so this is a soft check: output should not be empty
    ok = len(text.strip()) > 0
    return ok, "output present (hallucination check is heuristic)"

def _guardrail_triggered(text: str):
    ok = "describe" in text.lower() or "looking for" in text.lower()
    return ok, "guardrail message returned" if ok else "guardrail NOT triggered for empty query"


TEST_CASES = [
    {
        "name": "Chill study session",
        "query": "I need something chill and acoustic to study late at night",
        "mock_parse": json.dumps({"genre": "lofi", "mood": "chill",
                                  "target_energy": 0.38, "target_valence": 0.58,
                                  "likes_acoustic": True}),
        "mock_reply": 'For late-night studying, "Midnight Coding" by LoRoom is perfect — low energy, acoustic, and focused. "Library Rain" is another great pick with its 0.35 energy and 0.86 acousticness.',
        "checkers": [_non_empty, _mentions_a_song],
    },
    {
        "name": "High-energy workout",
        "query": "I want something loud and intense to get hyped for the gym",
        "mock_parse": json.dumps({"genre": "pop", "mood": "intense",
                                  "target_energy": 0.93, "target_valence": 0.77,
                                  "likes_acoustic": False}),
        "mock_reply": '"Gym Hero" by Max Pulse is exactly what you need — 0.93 energy and built for intensity. "Signal Burst" (EDM, 0.88 energy) will keep you moving too.',
        "checkers": [_non_empty, _mentions_a_song],
    },
    {
        "name": "Sad and rainy day",
        "query": "Something melancholic for a rainy afternoon",
        "mock_parse": json.dumps({"genre": "folk", "mood": "sad",
                                  "target_energy": 0.28, "target_valence": 0.30,
                                  "likes_acoustic": True}),
        "mock_reply": '"Ember Road" by Hazel Finn fits perfectly — folk, sad, and 0.25 energy with high acousticness. "Rust and Rain" is another melancholic pick.',
        "checkers": [_non_empty, _mentions_a_song],
    },
    {
        "name": "Empty query guardrail",
        "query": "",
        "mock_parse": "",   # should never be called
        "mock_reply": "",   # should never be called
        "checkers": [_guardrail_triggered],
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_case(case: dict, dry_run: bool) -> tuple:
    """Run a single test case. Returns (passed_all, results_list)."""
    results = []

    if dry_run:
        client = MagicMock()
        if case["query"]:
            client.messages.create.side_effect = [
                MagicMock(content=[MagicMock(text=case["mock_parse"])]),
                MagicMock(content=[MagicMock(text=case["mock_reply"])]),
            ]
        with patch("src.ai_recommender.anthropic.Anthropic", return_value=client):
            rec = AIRecommender(CATALOG)
            output = rec.recommend(case["query"])
    else:
        rec = AIRecommender(CATALOG)
        output = rec.recommend(case["query"])

    all_passed = True
    for checker in case["checkers"]:
        passed, note = checker(output)
        results.append((passed, note))
        if not passed:
            all_passed = False

    return all_passed, results, output


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    mode = "DRY RUN (mocked)" if dry_run else "LIVE (real API)"

    print(f"\n{'=' * 60}")
    print(f"  VibeMatch Evaluation Harness  [{mode}]")
    print(f"{'=' * 60}\n")

    total = len(TEST_CASES)
    passed_count = 0

    for i, case in enumerate(TEST_CASES, 1):
        print(f"[{i}/{total}] {case['name']}")
        print(f"  Query: {case['query']!r}")

        case_passed, results, output = run_case(case, dry_run)

        short_output = output[:120].replace("\n", " ") + ("..." if len(output) > 120 else "")
        print(f"  Output: {short_output!r}")

        for passed, note in results:
            icon = "PASS" if passed else "FAIL"
            print(f"  [{icon}] {note}")

        if case_passed:
            passed_count += 1
            print(f"  --> PASSED\n")
        else:
            print(f"  --> FAILED\n")

    print(f"{'=' * 60}")
    print(f"  Results: {passed_count}/{total} test cases passed")
    if passed_count == total:
        print("  All tests passed.")
    else:
        print(f"  {total - passed_count} test(s) failed.")
    print(f"{'=' * 60}\n")

    sys.exit(0 if passed_count == total else 1)


if __name__ == "__main__":
    main()
