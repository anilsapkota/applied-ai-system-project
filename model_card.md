# Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeMatch 1.0**

A rule-based music recommender that matches songs to a listener's stated taste
using a weighted scoring formula. Built as a classroom simulation of how
real-world recommender systems think about user preferences.

---

## 2. Goal / Task

VibeMatch tries to answer one question: given what a user tells us they like,
which five songs in the catalog are the best fit for them right now?

It is not trying to predict what a user will click on or learn from their
history. It takes a snapshot of stated preferences — genre, mood, energy
level, and whether they like acoustic or electronic sounds — and scores every
song
against those preferences. The top five scores become the recommendations.

This is designed for classroom exploration, not for real users. It is a
hands-on way to understand how scoring formulas, data gaps, and weight choices
shape what a recommender suggests.

---

## 3. Algorithm Summary

Think of it like a job interview scorecard. Each song gets graded on five
criteria, and the scores add up to a total.

**Genre match:** If the song's genre matches what the user asked for, it earns
one point. This is all-or-nothing — "rock" and "metal" are treated as
completely different, even though most listeners know they're neighbors.

**Mood match:** Same idea. If the song's mood label matches the user's target
mood, it earns another point. Again, "intense" and "aggressive" are treated as
strangers.

**Energy proximity:** The system compares the song's energy level (a number
from 0 to 1) to the user's target energy. The closer they are, the better the
score — worth up to three points. This is the heaviest signal in the current
setup after a weight experiment that doubled it from its original value of 1.5.

**Valence proximity:** Valence measures how positive or upbeat a song sounds.
The system rewards songs that are emotionally close to what the user wants,
worth up to one point.

**Acoustic preference:** If the user likes acoustic sounds and the song is very
acoustic, it earns a half-point bonus. If there is a mismatch (user wants
acoustic but the song is fully electronic, or vice versa), it loses a
half-point. Songs in the middle range of acousticness get no signal at all.

The song with the highest total score wins, and the top five are returned. The
maximum possible score is 6.5.

---

## 4. Data

The catalog contains **18 songs** stored in a CSV file. Each song has the
following attributes: title, artist, genre, mood, energy (0–1), tempo in BPM,
valence (0–1), danceability (0–1), and acousticness (0–1).

**Genres represented:** lofi, pop, rock, metal, classical, folk, jazz,
blues, soul, r&b, hip-hop, edm, synthwave, ambient, indie pop (15 total).

**Moods represented:** chill, happy, intense, focused, relaxed, moody,
romantic, nostalgic, peaceful, aggressive, sad, uplifting, dreamy,
melancholic (14 total).

No data was added or removed from the starter dataset.

**Key limits:** Lofi is the only genre with three songs; pop has two. Every
other genre has exactly one. This means the catalog is extremely sparse — a
real streaming service might have millions of songs per genre. The small size
makes patterns and biases much easier to see, which is useful for learning, but
it also means the recommender runs out of relevant options very quickly for
most listener types.

---

## 5. Strengths

The system works best when a user's stated preferences align with a
well-stocked corner of the catalog.

**Lofi listeners** get accurate, consistent results. All three lofi tracks
cluster together in low energy and high acousticness, so the continuous signals
(energy, valence, acoustic) reinforce the genre match rather than working
against it. The top results feel genuinely cohesive.

**Pop listeners** also see reasonable results. Sunrise City scores near-perfect
because it matches genre, mood, energy, and valence simultaneously. The second
result (Gym Hero) is a reasonable stretch — same genre, higher energy —
which is how a real "more like this" feature might behave.

**The scoring explanation is honest.** Every recommendation comes with a
breakdown of exactly which signals fired and by how much. Unlike a black-box
neural network, this system can always tell you why it picked a song. That
transparency is a genuine strength for debugging and learning.

**Coherent profiles score confidently.** When a user's genre, mood, and energy
all point in the same direction, the scores cluster near the maximum and the
gap between good and bad matches is large. The system is decisive when it has
clear
information.

---

## 6. Limitations and Bias

### Singleton Genre Bias

The most significant bias discovered during experimentation is what can be
called the **singleton genre trap**. Thirteen of the fifteen genres in the
catalog have exactly one song each, yet the scoring logic awards the same
genre-match bonus regardless of how many songs that genre contains. This
creates a hidden unfairness: a user who prefers `lofi` benefits from three
genre-matched
candidates in every recommendation run, while a user who prefers `hip-hop`,
`blues`, `r&b`, or `metal` benefits from only one. After that single match,
their remaining four results are filled entirely by songs from unrelated genres
— chosen only because their energy and valence happen to be numerically
close.
In practice this means the system silently serves most users as if they had no
genre preference at all, while appearing to respect it. A fairer design would
either normalize the genre bonus by catalog density, or explicitly surface the
scarcity to the user rather than papering over it with continuous-signal
fallbacks.

### Genre and Mood Labels Are Binary

The system treats every genre as equally distant from every other. Rock and
metal get no credit for being neighbors; classical and jazz share no partial
credit for both being acoustic and melodic. The same is true for moods:
"aggressive" and "intense" are treated as completely different even though a
listener who wants one would often accept the other. This caused Iron Cascade
(metal/aggressive) to rank below Gym Hero (pop/intense) for a rock/intense
listener — a result that feels wrong to any human ear.

### The Acoustic Dead-Zone

The acoustic signal only fires at the extremes. Songs with acousticness between
0.30 and 0.60 receive no bonus or penalty regardless of a user's stated
preference. Three songs — Rooftop Lights (indie pop), Velvet Nights (r&b),
and Golden Haze (soul) — all sit in this dead-zone and are effectively
invisible to the acoustic preference signal.

### No Concept of Contradiction Detection

If a user provides contradictory preferences (e.g., genre: folk, mood: sad, but
energy: 0.90), the system does not flag the conflict. It just runs both signals
simultaneously and produces a confused playlist — folk/sad at the top from
the identity bonus, then metal and EDM filling the remaining slots from the
energy
signal. A real recommender should either warn the user or find a principled way
to resolve the contradiction.

---

## 7. Evaluation

Six user profiles were tested across two runs — one with the original weights
and one after an experiment that doubled the energy weight and halved the genre
weight. Three profiles represented real listener types; three were adversarial
profiles built to expose weaknesses in the scoring logic.

**Profiles tested:**

- **High-Energy Pop** — genre: pop, mood: happy, energy target: 0.85
- **Chill Lofi** — genre: lofi, mood: chill, energy target: 0.38
- **Deep Intense Rock** — genre: rock, mood: intense, energy target: 0.90
- **Conflicting Energy vs Mood** — genre: folk, mood: sad,
  energy target: 0.90
- **Classical but Hyper-Energy** — genre: classical, mood: peaceful,
  energy target: 0.95
- **All-Neutral** — no genre or mood, all values at 0.50

**What we looked for:** whether the top-5 results matched what a real listener
with that taste would actually enjoy, and whether the scoring reasons made
intuitive sense.

**What surprised us:**

The most surprising result came from the *Deep Intense Rock* profile. Metal
(Iron Cascade) ranked below pop (Gym Hero) even though metal is obviously
closer to rock than pop is. The reason was that Gym Hero carries the label
"intense" — matching the mood preference — while Iron Cascade is labeled
"aggressive," which the system treats as a complete mismatch. A single word
difference in a mood tag changed the ranking more than the actual genre of the
music.

The *Classical but Hyper-Energy* profile revealed a clean tipping point: under
the original weights, Morning Sonata (classical) won because the genre and mood
bonus overrode the energy mismatch. After doubling the energy weight, Morning
Sonata disappeared from the top 5 entirely and was replaced by pop and EDM
songs. This showed that the original system was essentially ignoring energy for
well-matched genre/mood profiles — and that the two weight choices produce
qualitatively different recommenders, not just slightly different rankings.

The *All-Neutral* profile confirmed that without genre or mood anchors, the
system caps out at 3.70 / 6.50 — less than 57% of the maximum possible score.
Every result was a mid-tempo song, not because those are the best songs, but
because they are closest to 0.50 energy. The system has no concept of
diversity, so it reliably clusters around the mathematical center of the
dataset.

---

## 8. Intended Use and Non-Intended Use

**This system is intended for:**

- Classroom exercises about how recommender systems work
- Experimenting with scoring weights and seeing how they change output
- Learning to spot bias and filter bubbles in simple rule-based systems
- Prototyping a preference-matching idea before building something larger

**This system should NOT be used for:**

- Real music recommendations to real users — the 18-song catalog is far too
  small to be useful, and the genre/mood label system is too coarse
- Any context where fairness across listener types matters — the singleton
  genre bias systematically disadvantages most users
- Drawing conclusions about what music a person "should" like — the system
  has no listening history, no feedback loop, and no understanding of context
  (time
  of day, activity, social setting)
- Production deployment of any kind without substantial redesign

---

## 9. Ideas for Improvement

**1. Add genre adjacency (partial credit for related genres)**

Instead of a binary genre match, build a small lookup table that defines which
genres are neighbors. Rock and metal would share partial credit; lofi and
ambient would too. This would fix the Iron Cascade / Gym Hero ranking problem
and make recommendations feel musically coherent for a much wider range of
listeners.

**2. Inject diversity into the top-5**

Right now the top 5 can contain songs that are nearly identical to each other
(e.g., three lofi tracks that differ by only 0.05 energy). A diversity step
after scoring — penalizing a song if it is too similar to one already
selected
— would produce playlists that feel varied and exploratory rather than
repetitive.

**3. Detect and surface contradictory preferences**

Before scoring, check whether the user's inputs make sense together. If genre
and energy target conflict (e.g., classical + energy 0.95), tell the user
rather than silently producing a broken playlist. Even a simple message like
"note: classical songs in this catalog have very low energy — results may not
match your energy target" would make the system feel honest and trustworthy.

---

## 9. Personal Reflection

**Biggest learning moment**

The single most clarifying moment was watching Iron Cascade (metal) rank below
Gym Hero (pop) for a user who explicitly asked for deep rock. I expected the
system to fail in complex ways — subtle biases in the numbers, edge cases in
the math. Instead it failed for the simplest possible reason: a mood label said
"aggressive" instead of "intense," and that one word cost a metal song its
rightful spot. It made the point more directly than any lecture could: a
recommendation system is only as smart as the data it's given. If the labels
are coarse, the output will be coarse — regardless of how carefully you tune
the weights.

**How AI tools helped, and when I had to double-check them**

Using AI assistance to apply the weight-shift experiment (doubling energy,
halving genre) was fast and accurate for the mechanical parts — changing the
number, updating the display string, recalculating the max score. The math
verification came back correct and saved time I would have spent re-reading the
formula by hand.

Where I had to stay alert was in interpreting the results. The AI could tell
me which lines changed and confirm the arithmetic was valid. It could not tell
me whether the new weights made the recommender *better* — that required
actually listening to the logic, comparing the two ranked lists, and forming a
judgment about whether Iron Cascade should rank above Gym Hero. That judgment
is irreducibly human. The tools were most useful as a fast pair of hands; the
thinking still had to happen on my side.

**What surprised me about simple algorithms "feeling" like recommendations**

I expected a five-signal weighted sum to feel mechanical and obviously fake.
What surprised me was how quickly the Chill Lofi and High-Energy Pop profiles
produced results that felt genuinely right — Sunrise City for the pop
listener,
Library Rain for the lofi listener, with coherent explanations attached. For a
moment it felt like the system understood music.

Then I ran the adversarial profiles and the illusion broke cleanly. The
"Classical but Hyper-Energy" profile exposed that the system had no
understanding at all — it was just adding numbers. What made the normal
profiles feel smart was not intelligence but coincidence: the features in the
dataset happened to cluster in ways that match real-world intuitions about
those genres. Lofi songs are genuinely low-energy and acoustic; pop songs are
genuinely high valence and electronic. When the data structure mirrors the
real world, a simple sum can look like insight. When it doesn't — classical
with high energy — the
seams show immediately.

**What I would try next**

The gap I most want to close is genre proximity. Right now "rock" and "metal"
are as far apart as "rock" and "ambient," which is obviously wrong. A small
adjacency map — rock is near metal, metal is near rock, lofi is near ambient
—
would fix the Iron Cascade problem without redesigning anything else. It is the
smallest change with the largest likely impact on recommendation quality.

After that, I would add a catalog-size awareness layer: before returning
results, check how many songs matched on genre and tell the user. "We found
your genre (folk) in 1 of 18 songs — results may not reflect your full taste"
is the kind of honest signal that builds trust instead of hiding a known
weakness. Real recommendation systems often suppress that information; I think
surfacing it would make this one more useful as a learning tool.

