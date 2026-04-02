# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class uses:
  - Preprocessing with punctuation removal and emoji extraction
  - Positive/negative word matching with negation handling
  - Emoji sentiment signals
  - A numeric score mapped to mood labels (positive, negative, neutral, mixed)
"""

import re
from typing import List, Optional

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS, POSITIVE_EMOJIS, NEGATIVE_EMOJIS


# Words that flip the sentiment of the next token
NEGATION_WORDS = {"not", "no", "never", "don't", "dont", "isn't", "isnt",
                  "wasn't", "wasnt", "can't", "cant", "won't", "wont",
                  "wouldn't", "wouldnt", "shouldn't", "shouldnt", "hardly",
                  "barely", "neither", "nor"}

# Sarcasm amplifiers: when "absolutely/totally/really" appear before a positive
# word AND the text also contains a known negative-context word, it's likely sarcastic.
SARCASM_AMPLIFIERS = {"absolutely", "totally", "just", "really", "so", "obviously"}
NEGATIVE_CONTEXT_WORDS = {"traffic", "stuck", "waiting", "line", "hours",
                          "monday", "broken", "fail", "failed", "late",
                          "delayed", "cancelled", "canceled", "dying"}


class MoodAnalyzer:
    """
    A rule based mood classifier with negation handling, emoji signals,
    and slang awareness.
    """

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)
        self.positive_emojis = set(POSITIVE_EMOJIS)
        self.negative_emojis = set(NEGATIVE_EMOJIS)

    # -----------------------------------------------------------------
    # Preprocessing
    # -----------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens.

        Steps:
          1. Lowercase and strip whitespace
          2. Extract emojis as separate tokens
          3. Remove punctuation (except apostrophes inside words)
          4. Split on whitespace
        """
        cleaned = text.strip().lower()

        # Pull out unicode emojis and text emojis before stripping punctuation
        emojis_found = []
        for emoji in (self.positive_emojis | self.negative_emojis):
            while emoji in cleaned:
                emojis_found.append(emoji)
                cleaned = cleaned.replace(emoji, " ", 1)

        # Remove punctuation but keep apostrophes inside contractions
        cleaned = re.sub(r"[^\w\s']", " ", cleaned)
        # Collapse multiple spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        tokens = cleaned.split()
        tokens.extend(emojis_found)
        return tokens

    # -----------------------------------------------------------------
    # Scoring logic
    # -----------------------------------------------------------------

    def score_text(self, text: str) -> int:
        """
        Compute a numeric mood score for the given text.

        Enhancements implemented:
          - Negation handling: "not happy" flips the score contribution
          - Emoji signals: positive emojis add +1, negative emojis subtract -1
          - Sarcasm detection: amplifier + positive word + negative context → flip
          - Each positive word → +1, each negative word → -1
        """
        tokens = self.preprocess(text)
        score = 0
        negate = False

        # Sarcasm check: if text has an amplifier before a positive word
        # AND contains a negative-context word, flip positive contributions.
        has_negative_context = any(t in NEGATIVE_CONTEXT_WORDS for t in tokens)
        has_amplifier = any(t in SARCASM_AMPLIFIERS for t in tokens)
        sarcasm_flip = has_negative_context and has_amplifier

        for token in tokens:
            if token in self.positive_emojis:
                score += 1
                continue
            if token in self.negative_emojis:
                score -= 1
                continue

            if token in NEGATION_WORDS:
                negate = True
                continue

            if token in SARCASM_AMPLIFIERS or token in NEGATIVE_CONTEXT_WORDS:
                negate = False
                continue

            if token in self.positive_words:
                if negate:
                    score -= 1
                elif sarcasm_flip:
                    score -= 1  # sarcasm: treat positive word as negative
                else:
                    score += 1
                negate = False
            elif token in self.negative_words:
                score += 1 if negate else -1
                negate = False
            else:
                negate = False

        return score

    # -----------------------------------------------------------------
    # Label prediction
    # -----------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        """
        Convert the numeric score into a mood label.

        We also check whether the text has BOTH positive and negative
        signals — if so, it's "mixed" regardless of the net score.

        Mapping:
          has both positive and negative signals → "mixed"
          score > 0  → "positive"
          score < 0  → "negative"
          score == 0 → "neutral"
        """
        tokens = self.preprocess(text)
        score = self.score_text(text)

        # Detect mixed: count raw positive and negative signals
        has_pos = any(
            t in self.positive_words or t in self.positive_emojis for t in tokens
        )
        has_neg = any(
            t in self.negative_words or t in self.negative_emojis for t in tokens
        )

        if has_pos and has_neg:
            return "mixed"
        elif score > 0:
            return "positive"
        elif score < 0:
            return "negative"
        else:
            return "neutral"

    # -----------------------------------------------------------------
    # Explanations
    # -----------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining WHY the model chose its label.
        Shows matched positive/negative tokens, emoji hits, sarcasm detection,
        and the final score.
        """
        tokens = self.preprocess(text)
        positive_hits: List[str] = []
        negative_hits: List[str] = []
        emoji_hits: List[str] = []
        score = 0
        negate = False

        has_negative_context = any(t in NEGATIVE_CONTEXT_WORDS for t in tokens)
        has_amplifier = any(t in SARCASM_AMPLIFIERS for t in tokens)
        sarcasm_flip = has_negative_context and has_amplifier

        for token in tokens:
            if token in self.positive_emojis:
                emoji_hits.append(token)
                score += 1
                continue
            if token in self.negative_emojis:
                emoji_hits.append(token)
                score -= 1
                continue

            if token in NEGATION_WORDS:
                negate = True
                continue

            if token in SARCASM_AMPLIFIERS or token in NEGATIVE_CONTEXT_WORDS:
                negate = False
                continue

            if token in self.positive_words:
                if negate:
                    negative_hits.append(f"not-{token}")
                    score -= 1
                elif sarcasm_flip:
                    negative_hits.append(f"sarcasm-{token}")
                    score -= 1
                else:
                    positive_hits.append(token)
                    score += 1
                negate = False
            elif token in self.negative_words:
                if negate:
                    positive_hits.append(f"not-{token}")
                    score += 1
                else:
                    negative_hits.append(token)
                    score -= 1
                negate = False
            else:
                negate = False

        sarcasm_note = " [SARCASM DETECTED]" if sarcasm_flip else ""
        return (
            f"Score = {score}{sarcasm_note} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'}, "
            f"emojis: {emoji_hits or '[]'})"
        )
