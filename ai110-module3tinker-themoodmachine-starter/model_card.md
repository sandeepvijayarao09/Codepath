# Model Card: Mood Machine

This model card documents **two** versions of the Mood Machine sentiment classifier:

1. A **rule-based model** implemented in `mood_analyzer.py`
2. A **machine learning model** implemented in `ml_experiments.py` using scikit-learn

Both models were explored and compared during this lab.

## 1. Model Overview

**Model type:**
Both a hand-coded rule-based classifier and a logistic regression ML classifier were built and compared.

**Intended purpose:**
Classify short social-media-style text posts into one of four mood labels: **positive**, **negative**, **neutral**, or **mixed**.

**How it works (brief):**
- *Rule-based:* The analyzer preprocesses text (lowercasing, punctuation removal, emoji extraction), then scores each token: +1 for positive words, -1 for negative words. It handles negation ("not happy" flips the score), detects basic sarcasm (amplifier + positive word + negative context), and treats emojis as sentiment signals. The net score is mapped to a label, with a special check for mixed signals.
- *ML model:* Text is converted to bag-of-words features using `CountVectorizer`, then a `LogisticRegression` model is trained on the labeled posts. It learns word-label associations from the data rather than hand-crafted rules.

## 2. Data

**Dataset description:**
The dataset contains **16 posts** in `SAMPLE_POSTS`, each with a corresponding label in `TRUE_LABELS`. The original starter had 6 posts; 10 were added covering slang, emojis, sarcasm, mixed emotions, and ambiguous/apathetic tone.

**Labeling process:**
Labels were assigned by reading each post and deciding the dominant emotional tone. Posts with both positive and negative signals (e.g., "I'm exhausted but we got the W") were labeled "mixed." Sarcastic posts (e.g., "I absolutely love getting stuck in traffic") were labeled by their *intended* meaning (negative), not their surface words.

Hard-to-label examples:
- "I'm fine 🥲" — the words say neutral/positive, but the emoji signals sadness. Labeled negative based on the emoji subtext.
- "whatever I don't even care anymore" — apathy/resignation. Labeled negative, though some might call it neutral.
- "Grateful for today, even though it was hard" — genuinely mixed; gratitude and difficulty coexist.

**Important characteristics of your dataset:**
- Contains Gen-Z slang ("vibing," "mid," "bruh," "ngl," "fire")
- Includes Unicode emojis (🔥, 🥲, 🙌, 💀) as sentiment carriers
- One explicitly sarcastic post
- Four posts labeled "mixed" with competing signals
- Posts range from 3 to 9 words in length

**Possible issues with the dataset:**
- Very small (16 examples) — not representative of real language diversity
- Skewed toward negative labels (7 negative, 4 mixed, 3 positive, 2 neutral)
- All posts are in English, written in a casual American internet style
- No posts with code-switching, non-English words, or formal tone
- One labeler (me) — no inter-annotator agreement measurement

## 3. How the Rule-Based Model Works

**Scoring rules:**
- Each token matching `POSITIVE_WORDS` adds +1; each matching `NEGATIVE_WORDS` subtracts -1
- **Negation handling:** Words like "not," "never," "don't" flip the next sentiment word's contribution (e.g., "not happy" → -1 instead of +1)
- **Emoji signals:** Positive emojis (😊, 🔥, ❤️, 🙌, etc.) add +1; negative emojis (😢, 💀, 🥲, etc.) subtract -1
- **Sarcasm detection:** If the text contains both a sarcasm amplifier ("absolutely," "totally," "so") AND a negative-context word ("traffic," "stuck," "waiting"), positive words are flipped to negative
- **Label thresholds:** If both positive and negative signals exist → "mixed." Otherwise: score > 0 → "positive," score < 0 → "negative," score == 0 → "neutral"

**Strengths of this approach:**
- Fully transparent: every prediction can be explained by showing which words matched and how the score was computed
- Fast and deterministic — no training required
- Negation handling correctly classifies "I am not happy about this" as negative
- The sarcasm heuristic catches the "love getting stuck in traffic" pattern
- Emoji-aware: "I'm fine 🥲" is correctly classified as negative due to the sad emoji

**Weaknesses of this approach:**
- Fails on text with no vocabulary matches: "whatever I don't even care anymore" gets neutral (no keywords hit)
- Sarcasm detection is fragile — only works when specific amplifier + context word pairs are present
- Cannot learn from data; every new pattern requires manual rule additions
- Word lists must be maintained by hand, and missing words cause silent failures

## 4. How the ML Model Works

**Features used:**
Bag-of-words representation using `CountVectorizer` — each unique word in the training set becomes a feature dimension, and the value is the word count in each post.

**Training data:**
The model was trained on all 16 posts in `SAMPLE_POSTS` with labels from `TRUE_LABELS`.

**Training behavior:**
With the expanded 16-post dataset, the model achieved 0.94 training accuracy. Adding the 10 new posts (beyond the original 6) improved its ability to handle slang and emojis since it learned associations like "vibing" → positive and "mid" → negative directly from labeled examples.

**Strengths and weaknesses:**
- *Strengths:* Learns patterns automatically — correctly classified the sarcasm case and the apathy case ("whatever I don't even care anymore" → negative) without explicit rules. Adapts when you add more labeled data.
- *Weaknesses:* Misclassified "This is fine" as negative instead of neutral — likely because "fine" co-occurred with negative-leaning training examples or the model had too few neutral examples to learn from. With only 16 training examples, it is heavily overfitting to the training set and would likely fail on unseen text.

## 5. Evaluation

**How you evaluated the model:**
Both models were evaluated on the same 16 labeled posts from `dataset.py`. Accuracy was computed as (correct predictions) / (total posts).

| Model | Accuracy |
|-------|----------|
| Rule-based | 0.94 (15/16 correct) |
| ML (LogisticRegression) | 0.94 (15/16 correct) |

**Examples of correct predictions:**

| Post | Predicted | True | Why correct |
|------|-----------|------|-------------|
| "I am not happy about this" | negative | negative | Negation handling flipped "happy" from +1 to -1 |
| "I'm exhausted but we got the W 🙌" | mixed | mixed | Detected both negative word ("exhausted") and positive emoji (🙌) |
| "I absolutely love getting stuck in traffic" | negative | negative | Sarcasm detection: amplifier "absolutely" + context word "traffic" flipped "love" |

**Examples of incorrect predictions:**

| Post | Predicted | True | Why wrong |
|------|-----------|------|-----------|
| "whatever I don't even care anymore" | neutral (rule-based) | negative | No sentiment keywords matched — "care" and "whatever" aren't in word lists, and the apathetic tone has no signal for the rule engine |
| "This is fine" | negative (ML) | neutral | ML model likely associated "fine" with negative contexts in training data, or lacked enough neutral examples to learn the pattern |

The two models fail in **different places**: the rule-based model struggles with vocabulary gaps, while the ML model struggles with data scarcity for underrepresented labels.

## 6. Limitations

- **Tiny dataset:** 16 examples is far too few for generalization. Both models are essentially memorizing patterns rather than understanding language.
- **No sarcasm generalization:** The rule-based sarcasm detector only catches one specific pattern (amplifier + positive word + negative context word). Most real sarcasm would slip through.
- **Vocabulary dependency:** The rule-based model is blind to any word not in its lists. New slang, misspellings, or non-English words produce zero signal.
- **No understanding of context or tone:** Neither model understands sentence structure, rhetorical questions, or implied meaning.
- **Single-language, single-dialect:** All training data is casual American English internet speak. The model would likely misinterpret formal English, AAVE, British English, or posts with code-switching.
- **Label ambiguity:** Several posts could reasonably have multiple labels. "I'm fine 🥲" could be neutral, negative, or mixed depending on interpretation.

## 7. Ethical Considerations

- **Misclassifying distress:** If deployed in a mental health or crisis context, labeling a genuinely distressed message as "neutral" or "positive" could delay intervention. The model's inability to detect apathy or resignation is particularly dangerous here.
- **Cultural and linguistic bias:** The word lists and training data reflect one person's casual English. Communities that use different slang, dialects, or communication styles (e.g., understatement, indirectness) would be systematically misclassified.
- **Privacy:** Analyzing personal messages raises consent and surveillance concerns, especially if users don't know their text is being scored.
- **Emoji interpretation varies:** 💀 means "dying laughing" in some contexts and genuine distress in others. The model treats it as uniformly negative.
- **Reinforcing assumptions:** Labeling ambiguous text with a single mood flattens the complexity of human emotion and could be used to make unjustified inferences about people.

## 8. Ideas for Improvement

- **More labeled data:** Expand to 100+ posts with multiple annotators to reduce bias and improve generalization.
- **Use TF-IDF** instead of raw counts in the ML model to reduce the influence of common words.
- **Bigram/trigram features** for the ML model to capture phrases like "not happy" or "stuck in traffic" as single features.
- **Better preprocessing:** Handle repeated characters ("soooo" → "so"), spelling normalization, and contractions.
- **Separate test set:** Evaluate on held-out data instead of training data to measure real generalization.
- **Contextual embeddings:** Use a pre-trained language model (e.g., a small transformer) that understands word meaning in context rather than treating each word independently.
- **Multi-annotator labels:** Have 3+ people label each post and use majority vote or soft labels to handle ambiguity.
- **Confidence scores:** Instead of hard labels, output probability distributions over labels so downstream systems can handle uncertainty.
