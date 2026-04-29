"""
RAG-powered music recommender using Claude.

Pipeline:
  1. Claude parses a natural-language query into structured preferences (JSON)
  2. Rule-based scorer retrieves the best-matching songs from the catalog
  3. Claude generates a personalized recommendation using those songs as context
"""

import json
import logging
from typing import Dict, List, Tuple

import anthropic

from src.recommender import load_songs, recommend_songs

logger = logging.getLogger(__name__)

# --- Prompts -----------------------------------------------------------------

_PARSE_SYSTEM = """\
You extract music preferences from natural-language queries.
Return ONLY valid JSON — no explanation, no markdown, no extra text — with these exact keys:
{
  "genre":          "<string, or empty string if unclear>",
  "mood":           "<string, or empty string if unclear>",
  "target_energy":  <float 0.0–1.0>,
  "target_valence": <float 0.0–1.0>,
  "likes_acoustic": <true | false | null>
}

Mapping guide:
  chill / relaxed / calm / study    → energy 0.30–0.40, likes_acoustic true
  upbeat / energetic / hype / pump  → energy 0.80–0.95
  sad / melancholic / dark          → valence 0.20–0.35
  happy / joyful / uplifting        → valence 0.75–0.90
  acoustic / unplugged / coffeeshop → likes_acoustic true
  electronic / EDM / synth / bass   → likes_acoustic false
  no preference / unsure            → empty string or null
"""

_RECOMMEND_SYSTEM = """\
You are VibeMatch, a warm and knowledgeable music recommendation assistant.

A retrieval system has already found the best-matching songs from the catalog
using audio-feature scoring. Your job:

1. Read the user's original request and the retrieved song list.
2. Select the 3–5 songs that best fit the request.
3. For each pick, give 1–2 sentences explaining why it fits.
4. If the retrieved songs don't quite match the request, say so honestly.

Keep your tone conversational. Do not invent songs that are not in the list.
"""


class AIRecommender:
    """
    RAG-powered recommender.
    Retrieval: rule-based scorer in recommender.py
    Generation: Claude (claude-haiku-4-5-20251001 by default for speed/cost)
    """

    def __init__(
        self,
        catalog_path: str,
        model: str = "claude-haiku-4-5-20251001",
    ) -> None:
        self.client = anthropic.Anthropic()
        self.songs = load_songs(catalog_path)
        self.model = model
        logger.info("AIRecommender ready — %d songs, model=%s", len(self.songs), model)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_preferences(self, user_query: str) -> Dict:
        """Step 1: ask Claude to turn natural language into a preference dict."""
        logger.debug("Parsing query: %r", user_query)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            system=_PARSE_SYSTEM,
            messages=[{"role": "user", "content": user_query}],
        )
        raw = response.content[0].text.strip()
        logger.debug("Raw preference JSON: %s", raw)
        try:
            prefs = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning("Preference JSON parse failed (%s) — using neutral fallback", exc)
            prefs = {
                "genre": "",
                "mood": "",
                "target_energy": 0.5,
                "target_valence": 0.5,
                "likes_acoustic": None,
            }
        return prefs

    def _format_candidates(self, candidates: List[Tuple]) -> str:
        """Format retrieved songs into a readable context block for Claude."""
        lines = []
        for rank, (song, score, why) in enumerate(candidates, 1):
            lines.append(
                f'{rank}. "{song["title"]}" by {song["artist"]}'
                f' | Genre: {song["genre"]} | Mood: {song["mood"]}'
                f' | Energy: {song["energy"]:.2f} | Score: {score:.2f}\n'
                f'   Signals: {why}'
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recommend(self, user_query: str, k: int = 5) -> str:
        """
        Full RAG pipeline: parse query → retrieve songs → generate response.

        Returns a natural-language recommendation string.
        Returns a safe guardrail message for empty queries.
        """
        if not user_query.strip():
            logger.warning("Empty query — returning guardrail message")
            return "Please describe what kind of music you're looking for."

        # Step 1 — parse natural language into structured preferences
        prefs = self._parse_preferences(user_query)
        logger.info("Extracted preferences: %s", prefs)

        # Step 2 — retrieve candidates using rule-based scorer (retrieval step)
        retrieve_k = min(k * 2, len(self.songs))
        candidates = recommend_songs(prefs, self.songs, k=retrieve_k)
        logger.info("Retrieved %d candidate songs for RAG context", len(candidates))

        # Step 3 — build augmented prompt (retrieved context + original query)
        context = self._format_candidates(candidates)
        augmented = (
            f"User request: {user_query}\n\n"
            f"Retrieved songs (ranked by audio-feature match):\n{context}"
        )

        # Step 4 — generate recommendation with Claude
        logger.debug("Sending augmented prompt to Claude")
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=_RECOMMEND_SYSTEM,
            messages=[{"role": "user", "content": augmented}],
        )
        result = response.content[0].text.strip()
        logger.info("Recommendation generated (%d chars)", len(result))
        return result
