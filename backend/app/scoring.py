from __future__ import annotations

from typing import Literal

from .questions import DIMENSIONS, Dimension, QUESTION_BANK, get_question

AnswerKey = Literal["A", "B"]

DISPLAY_NAMES: dict[Dimension, str] = {
    "WORDS": "Words of Affirmation",
    "TIME": "Quality Time",
    "SERVICE": "Acts of Service",
    "TOUCH": "Physical Affection",
    "GIFTS": "Thoughtful Gifts",
}

INTERPRETATIONS: dict[Dimension, dict[str, str]] = {
    "WORDS": {
        "high": "You seem to notice love strongly when care is spoken with tenderness and specificity. Thoughtful words may stay with you because they make affection feel seen, named, and remembered.",
        "medium": "Words matter to you, especially when they feel personal rather than automatic, though they appear to be one part of a wider pattern of feeling loved.",
        "low": "You may appreciate kind words without experiencing them as your strongest emotional signal of affection.",
    },
    "TIME": {
        "high": "You may especially notice care when someone gives you their unhurried attention. Shared presence, lingering conversations, and protected time together seem to carry real emotional weight.",
        "medium": "Time together matters to you, although it may matter most when paired with other signs of attentiveness and care.",
        "low": "You may enjoy shared time without needing it to be the main way affection is shown.",
    },
    "SERVICE": {
        "high": "You seem to notice love strongly when care becomes action. Someone remembering what weighs on you and quietly making life easier may speak louder than a grand declaration.",
        "medium": "Practical help matters to you, although it appears to be one of several ways you recognize care.",
        "low": "You may appreciate practical help without experiencing it as one of your strongest emotional signals of affection.",
    },
    "TOUCH": {
        "high": "You seem to respond strongly to closeness that does not need many words. A hand held at the right moment or a long embrace may make love feel immediate and real.",
        "medium": "Physical closeness appears meaningful to you, especially in moments where it carries comfort, reassurance, or quiet intimacy.",
        "low": "You may value affectionate touch, but your results suggest other forms of care may register more strongly for you.",
    },
    "GIFTS": {
        "high": "You may especially notice care when thoughtfulness becomes something tangible. A small keepsake or remembered detail can feel like proof that someone carried you in their mind.",
        "medium": "Thoughtful gifts matter to you when they are personal and memory-rich, though they seem to share space with other ways of recognizing love.",
        "low": "You may enjoy meaningful surprises without relying on gifts as a primary emotional signal.",
    },
}


def calculate_raw_scores(answers: dict[int, AnswerKey]) -> dict[Dimension, float]:
    scores = {dimension: 0.0 for dimension in DIMENSIONS}
    for question_id, selected in answers.items():
        question = get_question(question_id)
        a_dimension = question["choices"]["A"]["dimension"]
        b_dimension = question["choices"]["B"]["dimension"]
        if selected == "A" and a_dimension:
            scores[a_dimension] += 1.0
        elif selected == "B" and b_dimension:
            scores[b_dimension] += 1.0
    return scores


def normalize_percentages(scores: dict[Dimension, float]) -> dict[Dimension, int]:
    total = sum(scores.values())
    if total == 0:
        return {dimension: 0 for dimension in DIMENSIONS}
    exact = {dimension: (score / total) * 100 for dimension, score in scores.items()}
    floors = {dimension: int(value) for dimension, value in exact.items()}
    remainder = 100 - sum(floors.values())
    ranked_remainders = sorted(
        DIMENSIONS,
        key=lambda dimension: (exact[dimension] - floors[dimension], scores[dimension], -DIMENSIONS.index(dimension)),
        reverse=True,
    )
    percentages = floors.copy()
    for dimension in ranked_remainders[:remainder]:
        percentages[dimension] += 1
    return percentages


def classify_profile(percentages: dict[Dimension, int]) -> str:
    ordered = sorted(percentages.values(), reverse=True)
    top_gap = ordered[0] - ordered[1]
    spread = ordered[0] - ordered[-1]
    # Broad: no dimension is more than 8 percentage points above another.
    # Blended: the top two dimensions are within 4 points and the profile is not broad.
    # Focused: the leading dimension is at least 10 points above second place.
    if spread <= 8:
        return "Broad"
    if top_gap <= 4:
        return "Blended"
    if top_gap >= 10:
        return "Focused"
    return "Blended"


def band_for(percent: int) -> str:
    if percent >= 24:
        return "high"
    if percent >= 16:
        return "medium"
    return "low"


def build_result(answers: dict[int, AnswerKey]) -> dict:
    raw_scores = calculate_raw_scores(answers)
    percentages = normalize_percentages(raw_scores)
    ordered = sorted(DIMENSIONS, key=lambda dimension: (-percentages[dimension], DIMENSIONS.index(dimension)))
    primary, secondary = ordered[0], ordered[1]
    profile_shape = classify_profile(percentages)
    close = percentages[primary] - percentages[secondary] <= 4
    if close:
        summary = (
            f"Your results suggest that {DISPLAY_NAMES[primary]} and {DISPLAY_NAMES[secondary]} "
            "are almost equally important to you."
        )
    else:
        summary = (
            f"This suggests you may especially notice care through {DISPLAY_NAMES[primary]}, "
            f"with {DISPLAY_NAMES[secondary]} close behind."
        )
    dimensions = [
        {
            "key": dimension,
            "name": DISPLAY_NAMES[dimension],
            "score": raw_scores[dimension],
            "percentage": percentages[dimension],
            "interpretation": INTERPRETATIONS[dimension][band_for(percentages[dimension])],
        }
        for dimension in ordered
    ]
    return {
        "completed": len(answers) == len(QUESTION_BANK),
        "primary": {"key": primary, "name": DISPLAY_NAMES[primary], "percentage": percentages[primary]},
        "secondary": {"key": secondary, "name": DISPLAY_NAMES[secondary], "percentage": percentages[secondary]},
        "profile_shape": profile_shape,
        "summary": summary,
        "dimensions": dimensions,
        "percent_total": sum(percentages.values()),
    }
