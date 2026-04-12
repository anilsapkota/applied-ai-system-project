# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

### Singleton Genre Bias

The most significant bias discovered during experimentation is what can be
called the **singleton genre trap**. Thirteen of the fifteen genres in the
catalog have exactly one song each, yet the scoring logic awards the same
genre-match bonus
regardless of how many songs that genre contains. This creates a hidden
unfairness: a user who prefers `lofi` benefits from three genre-matched
candidates in every recommendation run, while a user who prefers `hip-hop`,
`blues`, `r&b`, or `metal` benefits from only one. After that single match,
their remaining four results are filled entirely by songs from unrelated genres
— chosen only because their energy and valence happen to be numerically close.
In practice this means the system silently serves most users as if they had no
genre preference at all, while appearing to respect it. A fairer design would
either normalize the genre bonus by catalog density, or explicitly surface the
scarcity to the user rather than papering over it with continuous-signal
fallbacks.

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
- **Conflicting Energy vs Mood** — genre: folk, mood: sad, energy target: 0.90
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

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
