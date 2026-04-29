"""
VibeMatch — Music Recommendation System

Modes:
  python -m src.main        Rule-based batch mode (6 test profiles)
  python -m src.main --ai   AI-powered interactive mode (Claude + RAG)
"""

import sys

from src.logger import setup_logging
from src.recommender import load_songs, recommend_songs

CATALOG = "data/songs.csv"

# ---------------------------------------------------------------------------
# Standard profiles
# ---------------------------------------------------------------------------

HIGH_ENERGY_POP = {
    "genre":          "pop",
    "mood":           "happy",
    "target_energy":  0.85,
    "target_valence": 0.85,
    "likes_acoustic": False,
}

CHILL_LOFI = {
    "genre":          "lofi",
    "mood":           "chill",
    "target_energy":  0.38,
    "target_valence": 0.58,
    "likes_acoustic": True,
}

DEEP_INTENSE_ROCK = {
    "genre":          "rock",
    "mood":           "intense",
    "target_energy":  0.90,
    "target_valence": 0.30,
    "likes_acoustic": False,
}

# ---------------------------------------------------------------------------
# Adversarial / edge-case profiles
# ---------------------------------------------------------------------------

# Conflicting: user says high-energy (0.9) but also wants "sad" mood.
# Sad songs in the dataset are low-energy folk tracks — scorer rewards
# genre+mood match but penalises energy distance, creating tension.
CONFLICTING_ENERGY_SAD = {
    "genre":          "folk",
    "mood":           "sad",
    "target_energy":  0.90,
    "target_valence": 0.20,
    "likes_acoustic": True,
}

# Mismatch: genre = classical but wants stadium-level energy.
# Classical songs cluster around energy 0.15–0.25.
CLASSICAL_BUT_HYPER = {
    "genre":          "classical",
    "mood":           "peaceful",
    "target_energy":  0.95,
    "target_valence": 0.75,
    "likes_acoustic": False,
}

# All-neutral: no genre/mood anchors, all continuous values at dead-centre.
ALL_NEUTRAL = {
    "genre":          "",
    "mood":           "",
    "target_energy":  0.50,
    "target_valence": 0.50,
    "likes_acoustic": None,
}

PROFILES = [
    ("High-Energy Pop",                               HIGH_ENERGY_POP),
    ("Chill Lofi",                                    CHILL_LOFI),
    ("Deep Intense Rock",                             DEEP_INTENSE_ROCK),
    ("Conflicting Energy vs Mood (adversarial)",      CONFLICTING_ENERGY_SAD),
    ("Classical but Hyper-Energy (adversarial)",      CLASSICAL_BUT_HYPER),
    ("All-Neutral / No Anchors   (adversarial)",      ALL_NEUTRAL),
]


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_recommendations(label: str, user_prefs: dict, recommendations: list) -> None:
    width = 64
    print(f"\n{'=' * width}")
    print(f"  Profile : {label}")
    print(f"  Genre   : {user_prefs.get('genre') or '(none)'}"
          f"   Mood: {user_prefs.get('mood') or '(none)'}")
    print(f"  Energy  : {user_prefs.get('target_energy', 'N/A')}"
          f"   Valence: {user_prefs.get('target_valence', 'N/A')}"
          f"   Acoustic: {user_prefs.get('likes_acoustic')}")
    print(f"{'=' * width}")

    for rank, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        print(f"\n  #{rank}  {song['title']}  —  {song['artist']}")
        print(f"       Score : {score:.2f} / 6.50")
        print(f"       Genre : {song['genre']}  |  Mood: {song['mood']}"
              f"  |  Energy: {song['energy']:.2f}")
        print(f"       Why:")
        for reason in explanation.split("; "):
            print(f"         • {reason}")
        print(f"  {'-' * (width - 2)}")

    print(f"{'=' * width}\n")


# ---------------------------------------------------------------------------
# Run modes
# ---------------------------------------------------------------------------

def run_batch_mode() -> None:
    songs = load_songs(CATALOG)
    print(f"Loaded {len(songs)} songs.\n")
    for label, prefs in PROFILES:
        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(label, prefs, recs)


def run_ai_mode() -> None:
    from src.ai_recommender import AIRecommender

    recommender = AIRecommender(CATALOG)
    print("\nVibeMatch AI — powered by Claude (RAG)")
    print("Describe what you want to listen to. Type 'quit' to exit.\n")

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not query:
            continue

        print("\nVibeMatch:", flush=True)
        response = recommender.recommend(query)
        print(response)
        print()


def main() -> None:
    setup_logging()

    if "--ai" in sys.argv:
        run_ai_mode()
    else:
        run_batch_mode()


if __name__ == "__main__":
    main()
