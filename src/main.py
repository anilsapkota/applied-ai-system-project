"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Taste profile: high-energy listener who prefers dark, driving rock
    user_prefs = {
        "genre":          "rock",    # hard identity signal; strongest weight
        "mood":           "intense", # contextual target; workout/focus
        "target_energy":  0.88,     # wants high intensity; penalizes low-energy songs
        "target_valence": 0.45,     # prefers darker/edgier feel over sunny pop
        "likes_acoustic": False,    # electronic/distorted production preferred
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
