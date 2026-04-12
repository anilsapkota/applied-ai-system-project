"""
Command line runner for the Music Recommender Simulation.

Runs six user profiles through the recommender and prints top-5 results for each.

Standard profiles:
  1. High-Energy Pop
  2. Chill Lofi
  3. Deep Intense Rock

Adversarial / edge-case profiles (stress the scoring logic):
  4. Conflicting Energy vs Mood  — energy: 0.9 but mood: sad
  5. Genre vs Energy mismatch   — genre: classical, target_energy: 0.95
  6. All-Middle / Neutral        — every value at 0.5, no genre/mood
"""

from recommender import load_songs, recommend_songs


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

# Conflicting: user says high-energy (0.9) but also wants a "sad" mood.
# Sad songs in the dataset are low-energy folk tracks — the scorer will
# reward genre+mood match but penalise energy distance, creating tension.
CONFLICTING_ENERGY_SAD = {
    "genre":          "folk",
    "mood":           "sad",
    "target_energy":  0.90,    # conflicts: sad folk tracks have energy ~0.25
    "target_valence": 0.20,
    "likes_acoustic": True,    # conflicts with high-energy EDM-style signal
}

# Mismatch: genre = classical but wants stadium-level energy.
# Classical songs score +2 for genre but lose heavily on energy proximity
# (classical tracks cluster around energy 0.15–0.25).
CLASSICAL_BUT_HYPER = {
    "genre":          "classical",
    "mood":           "peaceful",
    # conflicts: classical songs cluster around energy 0.15–0.25
    "target_energy":  0.95,
    "target_valence": 0.75,
    "likes_acoustic": False,   # conflicts: classical is almost always acoustic
}

# All-neutral: no genre/mood anchors, all continuous values at dead-centre.
# Every song is equally penalised by energy/valence distance; the scorer
# should fall back to pure proximity arithmetic with no identity bonus.
ALL_NEUTRAL = {
    "genre":          "",      # no genre preference — never matches anything
    "mood":           "",      # no mood preference
    "target_energy":  0.50,
    "target_valence": 0.50,
    "likes_acoustic": None,    # no acoustic preference — skip that signal
}

# ---------------------------------------------------------------------------

PROFILES = [
    ("High-Energy Pop",           HIGH_ENERGY_POP),
    ("Chill Lofi",                CHILL_LOFI),
    ("Deep Intense Rock",         DEEP_INTENSE_ROCK),
    ("Conflicting Energy vs Mood (adversarial)", CONFLICTING_ENERGY_SAD),
    ("Classical but Hyper-Energy (adversarial)", CLASSICAL_BUT_HYPER),
    ("All-Neutral / No Anchors   (adversarial)", ALL_NEUTRAL),
]


def print_recommendations(
    label: str, user_prefs: dict, recommendations: list
) -> None:
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
        print(f"       Score : {score:.2f} / 6.00")
        print(f"       Genre : {song['genre']}  |  Mood: {song['mood']}"
              f"  |  Energy: {song['energy']:.2f}")
        print(f"       Why:")
        for reason in explanation.split("; "):
            print(f"         • {reason}")
        print(f"  {'-' * (width - 2)}")

    print(f"{'=' * width}\n")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    for label, prefs in PROFILES:
        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(label, prefs, recs)


if __name__ == "__main__":
    main()
