from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Scoring recipe (max ~6.0):
      +2.0  genre match (exact)
      +1.0  mood match (exact)
      +0.0–1.5  energy proximity: 1.5 × (1 − |song.energy − target_energy|)
      +0.0–1.0  valence proximity: 1.0 × (1 − |song.valence − target_valence|)
      ±0.5  acoustic alignment

    Returns:
      (score, reasons) — reasons is a list of human-readable strings
    """
    score = 0.0
    reasons = []

    # Genre match — strongest identity signal
    if song["genre"] == user_prefs.get("genre", ""):
        score += 2.0
        reasons.append(f"genre match (+2.0)")

    # Mood match — contextual fit
    if song["mood"] == user_prefs.get("mood", ""):
        score += 1.0
        reasons.append(f"mood match (+1.0)")

    # Energy proximity — continuous signal, weighted 1.5
    target_energy = user_prefs.get("target_energy")
    if target_energy is not None:
        energy_score = 1.5 * (1 - abs(song["energy"] - target_energy))
        score += energy_score
        reasons.append(f"energy proximity ({energy_score:+.2f})")

    # Valence proximity — emotional color, weighted 1.0
    target_valence = user_prefs.get("target_valence")
    if target_valence is not None:
        valence_score = 1.0 * (1 - abs(song["valence"] - target_valence))
        score += valence_score
        reasons.append(f"valence proximity ({valence_score:+.2f})")

    # Acoustic alignment — tiebreaker (±0.5)
    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        acousticness = song["acousticness"]
        if likes_acoustic and acousticness > 0.60:
            score += 0.5
            reasons.append("acoustic preference match (+0.5)")
        elif not likes_acoustic and acousticness < 0.30:
            score += 0.5
            reasons.append("electronic production match (+0.5)")
        elif likes_acoustic and acousticness < 0.30:
            score -= 0.5
            reasons.append("production mismatch — too electronic (-0.5)")
        elif not likes_acoustic and acousticness > 0.70:
            score -= 0.5
            reasons.append("production mismatch — too acoustic (-0.5)")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    return []
