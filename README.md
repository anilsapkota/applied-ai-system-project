# Music Recommender Simulation — VibeMatch 1.0

A rule-based music recommender built as a hands-on simulation of how
content-based filtering works. Given a user's stated taste preferences, the
system scores every song in an 18-track catalog and returns the top five
matches with plain-language explanations.

Built for CodePath AI Engineering (Module 3) as a classroom exploration of
recommender system design, bias, and evaluation.

---

## How the System Works

This is **content-based filtering**: it reads what a user says they want and
finds songs whose attributes are closest to that description. There is no
listening history, no learning over time, and no comparison to other users.

Each song is scored on five signals and the scores are summed. The top five
results are returned.

### Scoring Formula

| Signal | Rule | Points |
|---|---|---|
| Genre match | Exact string match on genre | +1.0 |
| Mood match | Exact string match on mood | +1.0 |
| Energy proximity | `3.0 × (1 − abs(energy − target))` | 0.0 → +3.0 |
| Valence proximity | `1.0 × (1 − abs(valence − target))` | 0.0 → +1.0 |
| Acoustic alignment | Match → +0.5; mismatch → −0.5 | −0.5 → +0.5 |

**Maximum possible score: 6.5**

> Note: these are the weights after a weight-shift experiment (see below).
> The original weights had genre at +2.0 and energy at 1.5×. Doubling energy
> and halving genre produced more honest results for adversarial profiles.

### Song Attributes Used

| Feature | Type | What it captures |
|---|---|---|
| `genre` | string | Musical category (pop, lofi, rock, metal, etc.) |
| `mood` | string | Emotional label (happy, chill, intense, sad, etc.) |
| `energy` | float 0–1 | Calm vs. driving intensity |
| `valence` | float 0–1 | Sunny vs. melancholic emotional color |
| `acousticness` | float 0–1 | Organic/acoustic vs. electronic production |
| `tempo_bpm` | float | Pace in beats per minute (loaded but not scored) |
| `danceability` | float 0–1 | Rhythmic quality (loaded but not scored) |

---

## Project Structure

```
├── data/
│   └── songs.csv           18-song catalog with all attributes
├── src/
│   ├── main.py        Runs all six profiles, prints results
│   └── recommender.py      load_songs, score_song, recommend_songs
├── tests/
│   └── test_recommender.py Unit tests for scoring logic
├── model_card.md      Full model card (bias, evaluation, reflection)
└── reflection.md           Profile-pair comparisons in plain language
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac / Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run all six profiles:

   ```bash
   python -m src.main
   ```

### Running Tests

```bash
pytest
```

---

## User Profiles Tested

Six profiles were run through the recommender. Three are realistic listener
types; three are adversarial profiles designed to expose weaknesses.

### Standard Profiles

**High-Energy Pop**
```python
{"genre": "pop", "mood": "happy", "target_energy": 0.85,
 "target_valence": 0.85, "likes_acoustic": False}
```
Top result: *Sunrise City* (pop/happy) — 6.40 / 6.50. Tight, confident
results. All five signals aligned.

**Chill Lofi**
```python
{"genre": "lofi", "mood": "chill", "target_energy": 0.38,
 "target_valence": 0.58, "likes_acoustic": True}
```
Top result: *Library Rain* (lofi/chill) — 6.39 / 6.50. The lofi cluster
in the dataset (3 songs) gives this profile the most variety of any genre.

**Deep Intense Rock**
```python
{"genre": "rock", "mood": "intense", "target_energy": 0.90,
 "target_valence": 0.30, "likes_acoustic": False}
```
Top result: *Storm Runner* (rock/intense) — 6.29 / 6.50. #1 is correct,
but #2 (Gym Hero, pop/intense) ranks above #3 (Iron Cascade, metal) — see
Limitations below.

### Adversarial Profiles

**Conflicting Energy vs Mood** — `genre: folk`, `mood: sad`,
`energy target: 0.90`. Folk and sad songs are the quietest in the catalog
(energy ~0.25). The scorer can't detect the contradiction and produces a
scattered playlist: folk at #1 from the identity bonus, metal and rock
filling the remaining slots from the energy signal.

**Classical but Hyper-Energy** — `genre: classical`, `mood: peaceful`,
`energy target: 0.95`. Classical tracks have energy ~0.18. Under the old
weights, Morning Sonata (classical) still won because the genre bonus
dominated. After the weight experiment, Morning Sonata disappeared from the
top 5 entirely — replaced by pop and EDM.

**All-Neutral** — no genre, no mood, `energy: 0.50`, `valence: 0.50`.
Without identity signals, the system caps at 3.70 / 6.50 and clusters
around mid-tempo songs. The "best" result with no information is simply the
most mathematically average song in the catalog.

---

## Experiments

### Weight Shift: Energy ×2, Genre ÷2

Original weights: genre +2.0, energy 1.5×.
Experiment weights: genre +1.0, energy 3.0×.

**What changed:**

- The *Classical but Hyper-Energy* profile flipped completely. Morning
  Sonata won under the original weights (genre bonus dominated); it
  disappeared from the top 5 after the change (energy pulled results toward
  pop and EDM). This showed the original system was essentially ignoring
  energy for well-matched genre profiles.
- The *Conflicting Energy vs Mood* profile became more honest. The gap
  between #1 and #2 shrank from 2.84 points to 1.17, making the
  contradiction visible in the scores instead of hiding it.
- Standard profiles (Pop, Lofi, Rock) kept the same ranking order. Their
  signals were consistent enough that changing weights didn't change who won.

**Verdict:** The new weights are better for incoherent and adversarial
profiles. They don't fix the core structural problem (genre proximity
blindness) for well-formed profiles.

---

## Limitations and Bias

### The Singleton Genre Trap (most significant)

13 of 15 genres have exactly one song. The system gives the same genre-match
bonus (+1.0) regardless of catalog depth. A lofi user gets three genre-matched
candidates per run; a hip-hop or metal user gets one, then the remaining four
slots fill with unrelated genres chosen by energy proximity alone. Most users
are silently served as if they had no genre preference.

### Genre and Mood Labels Are Binary

Rock and metal get no partial credit for being adjacent genres. "Aggressive"
and "intense" are treated as complete strangers. This caused *Iron Cascade*
(metal/aggressive) to rank below *Gym Hero* (pop/intense) for a rock/intense
listener — Gym Hero matched the mood label; Iron Cascade did not.

### Acoustic Dead-Zone (acousticness 0.30–0.60)

The acoustic signal only fires at the extremes (< 0.30 or > 0.60). Three
songs — Rooftop Lights (indie pop, 0.35), Velvet Nights (r&b, 0.32), Golden
Haze (soul, 0.58) — receive no acoustic signal at all, regardless of user
preference.

### No Contradiction Detection

If a user's preferences conflict (e.g., folk + sad + energy 0.90), the system
runs all signals simultaneously and produces a confused playlist. It never
warns the user that their inputs are incompatible.

---

## Reflection

Building VibeMatch made one thing immediately clear: a recommendation system is
only as smart as the structure of its data. The profiles that produced good
results (Chill Lofi, High-Energy Pop) felt intelligent not because the
algorithm was clever, but because those genres happen to cluster naturally in
the feature space — lofi songs really are low-energy and acoustic; pop songs
really are high valence and electronic. When the data structure mirrors the
real world, a weighted sum can look like insight. The adversarial profiles
broke that illusion the moment the inputs stopped aligning with how the data
was organized.

The more surprising lesson was about labels. The biggest ranking failure in
the whole project — Iron Cascade (metal) losing to Gym Hero (pop) for a rock
listener — had nothing to do with weights or math. It happened because a mood
tag said "aggressive" instead of "intense." One word. Real recommender systems
at scale deal with this constantly: categories that look precise on paper
collapse when the labels aren't consistent. No amount of weight tuning fixes a
labeling problem.

---

## Further Reading

- [model_card.md](model_card.md) — Full model card covering algorithm
  summary, data description, strengths, biases, evaluation, intended use,
  ideas for improvement, and personal reflection
- [reflection.md](reflection.md) — Plain-language comparison of all six
  profile pairs: what changed between outputs and why it makes sense
