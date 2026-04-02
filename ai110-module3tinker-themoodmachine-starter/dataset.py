"""
Shared data for the Mood Machine lab.

This file defines:
  - POSITIVE_WORDS: starter list of positive words
  - NEGATIVE_WORDS: starter list of negative words
  - SAMPLE_POSTS: short example posts for evaluation and training
  - TRUE_LABELS: human labels for each post in SAMPLE_POSTS
"""

# ---------------------------------------------------------------------
# Starter word lists
# ---------------------------------------------------------------------

POSITIVE_WORDS = [
    "happy",
    "great",
    "good",
    "love",
    "excited",
    "awesome",
    "fun",
    "chill",
    "relaxed",
    "amazing",
    "wonderful",
    "proud",
    "beautiful",
    "fantastic",
    "joy",
    "grateful",
    "blessed",
    "fire",
    "lit",
    "dope",
    "goated",
    "slaps",
    "vibe",
    "hyped",
    "hopeful",
    "vibing",
]

NEGATIVE_WORDS = [
    "sad",
    "bad",
    "terrible",
    "awful",
    "angry",
    "upset",
    "tired",
    "stressed",
    "hate",
    "boring",
    "annoyed",
    "frustrated",
    "miserable",
    "depressed",
    "disappointing",
    "trash",
    "mid",
    "cringe",
    "sus",
    "toxic",
    "drained",
    "overwhelmed",
    "exhausted",
    "hard",
]

# Emoji sentiment signals used by the rule-based analyzer
POSITIVE_EMOJIS = ["😊", "😂", "🔥", "❤️", "💯", "🙌", "😍", "🥳", ":)", "^^"]
NEGATIVE_EMOJIS = ["😢", "😡", "💀", "😤", "🥲", ":(", "😞", "😭"]

# ---------------------------------------------------------------------
# Starter labeled dataset
# ---------------------------------------------------------------------

# Short example posts written as if they were social media updates or messages.
SAMPLE_POSTS = [
    "I love this class so much",
    "Today was a terrible day",
    "Feeling tired but kind of hopeful",
    "This is fine",
    "So excited for the weekend",
    "I am not happy about this",
    # --- New posts: slang, emojis, sarcasm, mixed emotions, ambiguity ---
    "Lowkey stressed but kind of proud of myself",
    "This song is fire 🔥🔥🔥",
    "I absolutely love getting stuck in traffic",
    "just vibing rn honestly",
    "I'm fine 🥲",
    "ngl that exam was mid at best",
    "I'm exhausted but we got the W 🙌",
    "bruh this is so boring I can't 💀",
    "Grateful for today, even though it was hard",
    "whatever I don't even care anymore",
]

# Human labels for each post above.
# Allowed labels in the starter:
#   - "positive"
#   - "negative"
#   - "neutral"
#   - "mixed"
TRUE_LABELS = [
    "positive",   # "I love this class so much"
    "negative",   # "Today was a terrible day"
    "mixed",      # "Feeling tired but kind of hopeful"
    "neutral",    # "This is fine"
    "positive",   # "So excited for the weekend"
    "negative",   # "I am not happy about this"
    # --- Labels for new posts ---
    "mixed",      # "Lowkey stressed but kind of proud of myself"
    "positive",   # "This song is fire 🔥🔥🔥"
    "negative",   # "I absolutely love getting stuck in traffic" (sarcasm)
    "positive",   # "just vibing rn honestly"
    "negative",   # "I'm fine 🥲" (sarcastic/sad emoji contradicts words)
    "negative",   # "ngl that exam was mid at best"
    "mixed",      # "I'm exhausted but we got the W 🙌"
    "negative",   # "bruh this is so boring I can't 💀"
    "mixed",      # "Grateful for today, even though it was hard"
    "negative",   # "whatever I don't even care anymore"
]

# Sanity check: posts and labels must stay aligned.
assert len(SAMPLE_POSTS) == len(TRUE_LABELS), (
    f"Mismatch: {len(SAMPLE_POSTS)} posts vs {len(TRUE_LABELS)} labels"
)
