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

    # Taste profile: upbeat pop listener who wants happy, high-energy tracks
    user_prefs = {
        "genre":          "pop",     # hard identity signal; strongest weight
        "mood":           "happy",   # contextual target; feel-good listening
        "target_energy":  0.80,      # wants lively but not exhausting energy
        "target_valence": 0.82,      # prefers bright, sunny emotional tone
        "likes_acoustic": False,     # produced/electronic sound preferred
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 60
    print(f"\n{'=' * width}")
    print(f"  Top {len(recommendations)} Recommendations")
    print(f"  Profile: {user_prefs['genre']} / {user_prefs['mood']}")
    print(f"{'=' * width}")

    for rank, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        print(f"\n  #{rank}  {song['title']}  —  by {song['artist']}")
        print(f"       Score: {score:.2f} / 6.00")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}"
              f"  |  Energy: {song['energy']:.2f}")
        print(f"       Why:")
        for reason in explanation.split("; "):
            print(f"         • {reason}")
        print(f"  {'-' * (width - 2)}")

    print(f"{'=' * width}\n")


if __name__ == "__main__":
    main()
