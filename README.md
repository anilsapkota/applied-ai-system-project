# VibeMatch 2.0 — AI-Powered Music Recommender with RAG

> **CodePath Applied AI Systems — Final Project**

---

## Original Project (Modules 1–3)

**VibeMatch 1.0** was a rule-based music recommendation simulation built for CodePath AI Engineering Modules 1–3. It scored an 18-song catalog against hard-coded user taste profiles (genre, mood, energy, valence, acousticness) using a weighted formula and returned the top five matches with plain-language explanations. The system had no AI component — it was a pure Python weighted-sum scorer designed to explore how content-based filtering works and where it breaks down. Three adversarial profiles (conflicting energy vs mood, genre vs energy mismatch, all-neutral inputs) exposed key weaknesses: binary genre labels, singleton genre catalogs, and no contradiction detection.

---

## What VibeMatch 2.0 Does

VibeMatch 2.0 upgrades the rule-based simulation into a working AI system. Users describe what they want to listen to in plain English — "something chill and acoustic for studying" — and the system responds with a personalized recommendation backed by real audio feature data.

The core AI feature is **Retrieval-Augmented Generation (RAG)**:
1. Claude reads the natural-language query and extracts structured music preferences (genre, mood, energy, etc.)
2. The original rule-based scorer retrieves the best-matching songs from the catalog using those preferences
3. Claude reads the retrieved songs alongside the original query and generates a personalized, conversational recommendation

The system also includes structured logging, input guardrails, graceful error handling, and a full reliability test suite — including a standalone evaluation harness.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                     User Input                      │
│        "chill lofi for late night studying"         │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│              STEP 1 — Preference Extraction         │
│   Claude (Haiku) parses natural language → JSON     │
│   {genre: "lofi", energy: 0.38, acoustic: true ...} │
│   Guardrail: empty query returns safe message here  │
└──────────────────────────┬──────────────────────────┘
                           │  structured preferences
                           ▼
┌─────────────────────────────────────────────────────┐
│              STEP 2 — Retrieval (RAG)               │
│   Rule-based scorer reads data/songs.csv            │
│   Scores all 18 songs on 5 signals                  │
│   Returns top 10 ranked candidates + scores         │
└──────────────────────────┬──────────────────────────┘
                           │  retrieved song context
                           ▼
┌─────────────────────────────────────────────────────┐
│              STEP 3 — Augmented Generation          │
│   Claude (Haiku) receives:                          │
│     • original user query                           │
│     • ranked song list with audio feature data      │
│   Generates conversational recommendation           │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│                    Output                           │
│   Natural-language recommendation with explanations │
└─────────────────────────────────────────────────────┘

Supporting systems (run throughout):
  • src/logger.py        → logs every step to logs/vibematch_YYYYMMDD.log
  • tests/               → pytest unit tests + eval_harness.py for reliability
```

---

## Project Structure

```
├── data/
│   └── songs.csv                 18-song catalog with audio features
├── src/
│   ├── main.py                   Entry point (batch mode + --ai interactive mode)
│   ├── recommender.py            Rule-based scorer — also the RAG retrieval layer
│   ├── ai_recommender.py         Claude RAG pipeline (NEW)
│   └── logger.py                 Structured logging setup (NEW)
├── tests/
│   ├── test_recommender.py       Unit tests for scoring logic
│   ├── test_ai_recommender.py    Reliability tests for AI layer (NEW)
│   └── eval_harness.py           Evaluation harness — predefined inputs, pass/fail report (NEW)
├── logs/                         Auto-created; daily log files written here
├── .env.example                  API key template (NEW)
├── model_card.md                 Model card with bias analysis (from v1)
├── reflection.md                 Profile comparison analysis (from v1)
└── requirements.txt              Python dependencies
```

---

## Setup Instructions

**1. Clone the repo and create a virtual environment:**

```bash
git clone https://github.com/anilsapkota/applied-ai-system-project
cd applied-ai-system-project
python -m venv .venv
source .venv/bin/activate      # Mac / Linux
.venv\Scripts\activate         # Windows
```

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Set your Anthropic API key:**

```bash
cp .env.example .env
# Open .env and paste your key from https://console.anthropic.com/
```

Or set it directly in your shell:

```bash
export ANTHROPIC_API_KEY=your_key_here   # Mac/Linux
set ANTHROPIC_API_KEY=your_key_here      # Windows CMD
```

**4. Run the original rule-based batch mode (no API key needed):**

```bash
python -m src.main
```

**5. Run the AI-powered interactive mode:**

```bash
python -m src.main --ai
```

**6. Run the test suite:**

```bash
pytest
```

**7. Run the evaluation harness (dry run — no API key needed):**

```bash
python -m tests.eval_harness --dry-run
```

**8. Run the evaluation harness against the live API:**

```bash
python -m tests.eval_harness
```

---

## Sample Interactions

### Interaction 1 — Late-night study session

```
You: I need something chill and acoustic to study late at night

VibeMatch:
For late-night studying, I'd start with "Midnight Coding" by LoRoom —
it's a lofi track with energy 0.42 and high acousticness (0.71), designed
for exactly this kind of focused, low-stimulation listening. "Library Rain"
by Paper Lanterns is even calmer (energy 0.35, acousticness 0.86) and has
a slightly more ambient feel if you want something that fades into the
background. "Focus Flow" by LoRoom rounds out the set — it's labeled
"focused" rather than "chill" but shares the same low-energy, acoustic
signature.

All three sit well under 0.45 energy and above 0.70 acousticness, which
matches exactly what you described.
```

### Interaction 2 — Pre-workout pump-up

```
You: Something loud and high energy to get hyped for the gym

VibeMatch:
For maximum gym energy, "Gym Hero" by Max Pulse is the obvious pick —
0.93 energy, 132 BPM, and labeled "intense." "Signal Burst" by Prism Wave
(EDM, 0.88 energy, 140 BPM) is close behind and adds an uplifting feel if
you want something that feels triumphant rather than just heavy. "Iron
Cascade" by Wolfburn (metal, 0.97 energy) is the most extreme option —
168 BPM and aggressive — if you want something that hits harder.

I'd suggest starting with Gym Hero, then Signal Burst, and saving Iron
Cascade for the final set.
```

### Interaction 3 — Empty query guardrail

```
You: (blank input)

VibeMatch:
Please describe what kind of music you're looking for.
```

### Interaction 4 — Conflicting preferences (honest response)

```
You: I want sad acoustic folk music but also super high energy

VibeMatch:
I want to be honest: your request has a built-in conflict. The folk and
sad songs in this catalog (like "Ember Road" by Hazel Finn, energy 0.25)
are all low-energy and acoustic — that's the nature of the genre. High
energy (0.8+) points toward metal, EDM, and pop, which are the opposite
of folk and sad.

The retrieval system's top results reflect this tension: it found "Ember
Road" as the best folk/sad match, but the energy signal pulled in "Iron
Cascade" and "Signal Burst" to fill the remaining slots. That playlist
would feel incoherent.

My recommendation: pick one signal. If you want mood and texture, go with
Ember Road and Rust and Rain. If you want energy, go with Gym Hero or
Signal Burst. I can't find a song that's genuinely folk, sad, and high
energy — because that combination doesn't really exist in this catalog
(or in most music).
```

---

## Design Decisions and Trade-offs

**Why RAG and not a standalone LLM call?**
A plain LLM call would hallucinate song titles and artists. By grounding the generation step in retrieved catalog data, the AI can only recommend songs that actually exist. The retrieval layer also provides structured audio features (energy, valence, acousticness) that the language model alone cannot reason about.

**Why keep the rule-based scorer as the retrieval layer?**
The existing weighted-sum scorer already encodes useful domain knowledge (energy proximity matters more than genre for adversarial profiles). Rather than replacing it, RAG uses it as a fast, deterministic retrieval step. This also means batch mode (no API key) still works.

**Why two Claude calls instead of one?**
Splitting preference extraction and recommendation generation into two calls keeps each prompt focused. A single call that tried to do both would be harder to debug, harder to test, and would mix structured-output logic (JSON) with conversational logic (natural language). The cost is one extra API call per query.

**Why claude-haiku-4-5-20251001?**
Speed and cost. Haiku is fast enough for interactive use and produces reliable JSON for the preference parsing step. For longer, more nuanced recommendations, the model can be swapped to Sonnet by changing the `model` parameter in `AIRecommender`.

**Trade-off: 18-song catalog**
The catalog is intentionally small for classroom purposes. The singleton genre problem (13 of 15 genres have exactly one song) limits recommendation diversity. A production system would need a much larger catalog or an external music API.

---

## Testing Summary

**Unit tests (`pytest`):**

| Test | What it checks | Result |
|---|---|---|
| `test_recommend_returns_non_empty_string` | Normal query returns text | Pass |
| `test_empty_query_returns_guardrail_without_api_call` | Empty input hits guardrail before API | Pass |
| `test_malformed_json_from_claude_falls_back_gracefully` | Bad JSON from Claude doesn't crash | Pass |
| `test_parse_preferences_returns_required_keys` | Extracted prefs have all 5 required keys | Pass |
| `test_similar_queries_retrieve_overlapping_candidates` | Identical prefs → identical retrieval | Pass |
| `test_recommend_returns_songs_sorted_by_score` | Rule-based scorer ranks correctly | Pass |
| `test_explain_recommendation_returns_non_empty_string` | Explanation is a non-empty string | Pass |

All 7 tests pass. All AI tests are fully mocked — no API key required for `pytest`.

**Evaluation harness (`tests/eval_harness.py --dry-run`):**

4 predefined scenarios checked for: non-empty output, mention of a real catalog song, guardrail activation. All 4 pass in dry-run mode.

**What worked:**
- The preference parsing step was robust across a wide range of phrasings
- The RAG grounding reliably prevented hallucinated song titles
- The guardrail (empty query check) worked consistently before any API call

**What didn't:**
- The 18-song catalog is too small to handle exotic genre requests — a user asking for blues gets one result then energy-matched pop
- The preference parser occasionally mapped unusual moods to the wrong genre (e.g., "nostalgic" → "jazz" instead of "hip-hop") because the mapping guide is heuristic

---

## Reflection and Ethics

**Limitations and biases:**
- The catalog has 18 songs. Genres with one entry (hip-hop, metal, blues, jazz, etc.) are systematically underserved — users with those tastes see one genre match and then energy-proximity fills the rest.
- The preference parsing prompt uses heuristic mappings that reflect common Western music vocabulary. Users with different cultural references may get worse extractions.
- The scoring formula was tuned for this specific catalog. Its weights do not generalize.

**Could this be misused?**
The system recommends music, so direct harm potential is low. However, a more general RAG system built on this architecture could be misused if the retrieval corpus contained harmful content. Mitigation: the generation prompt (`_RECOMMEND_SYSTEM`) restricts Claude to songs in the retrieved list and does not allow it to invent content.

**What surprised me during testing:**
The most surprising finding was how well the guardrail worked compared to the retrieval quality. A blank query was handled correctly every time. But when the catalog had a semantic gap — a user asked for "nostalgic hip-hop" and the one hip-hop song was labeled "nostalgic" — the system performed well despite the small catalog. The label matching, not the AI, was responsible.

**Collaboration with AI during this project:**

*Helpful suggestion:* When designing the two-step Claude architecture (parse then generate), the AI suggested splitting the prompts so the parsing step returns only JSON and the generation step uses only natural language. This turned out to be the right call — it made testing much easier because the two responsibilities could be mocked and verified independently.

*Flawed suggestion:* In an early draft, the AI suggested using `temperature=0` for the preference parsing step to make it deterministic. This was incorrect advice — the Anthropic API does not expose a `temperature` parameter on `messages.create` the same way OpenAI does, and setting it caused an API error. The fix was to remove the parameter and rely on the system prompt's structured output instruction instead.

---

## Stretch Features Implemented

| Feature | Implementation | Location |
|---|---|---|
| **RAG Enhancement** | Two-stage RAG: preference extraction decouples query understanding from retrieval, improving accuracy for ambiguous queries | `src/ai_recommender.py` |
| **Test Harness** | `eval_harness.py` runs 4 predefined scenarios, checks pass/fail for output validity, catalog grounding, and guardrail behavior | `tests/eval_harness.py` |

---

## Loom Video Walkthrough

> _Add your Loom link here before submission._

---

## Portfolio Reflection

This project taught me that the hardest part of an AI system is not the AI itself — it's the interface between structured data and language. The retrieval layer (rule-based scorer) worked reliably and predictably. The generation layer (Claude) was flexible and natural. The failure points were always in the middle: how well the preference extraction step translated a vague human phrase into a structured query the scorer could use. That translation layer — the seam between unstructured language and structured logic — is where real AI engineering lives. A future employer looking at this project should see: I understand that AI systems are not just prompts, they are retrieval + grounding + generation working together, and each layer needs to be independently testable.

---

## Further Reading

- [model_card.md](model_card.md) — Algorithm summary, data description, biases, and evaluation (from v1)
- [reflection.md](reflection.md) — Plain-language comparison of all six test profiles (from v1)
