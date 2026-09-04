from __future__ import annotations

from collections import Counter
from itertools import combinations
from difflib import SequenceMatcher
from typing import Literal, TypedDict

Dimension = Literal["WORDS", "TIME", "SERVICE", "TOUCH", "GIFTS"]
AnswerKey = Literal["A", "B"]

DIMENSIONS: tuple[Dimension, ...] = ("WORDS", "TIME", "SERVICE", "TOUCH", "GIFTS")


class Choice(TypedDict):
    text: str
    dimension: Dimension | None


class Question(TypedDict):
    id: int
    scene: str
    prompt: str
    choices: dict[str, Choice]


QUESTION_BANK: list[Question] = [
    {"id": 1, "scene": "It's late at night. Rain taps softly against the window, and the two of you are curled up together after a long week. You've been talking about things you normally keep hidden.", "prompt": "What would stay with you more when the night is over?", "choices": {"A": {"text": "They look at you quietly and tell you exactly what they love about the person you are, including things you never realized they noticed.", "dimension": "WORDS"}, "B": {"text": "The conversation keeps going until far too late because neither of you wants to leave this little world you've created together.", "dimension": "TIME"}}},
    {"id": 2, "scene": "You come home exhausted. You haven't complained, but your partner can tell you're running on empty.", "prompt": "Which moment would touch you more?", "choices": {"A": {"text": "They pull you close for a second and say, \"You've carried enough today. I see how hard you're trying.\"", "dimension": "WORDS"}, "B": {"text": "You notice they've already taken care of the annoying little things you were dreading so that you can finally relax.", "dimension": "SERVICE"}}},
    {"id": 3, "scene": "You're standing together somewhere beautiful just as the sun is going down. For a moment neither of you says anything.", "prompt": "What would make the moment feel more intimate?", "choices": {"A": {"text": "They turn toward you and quietly say something vulnerable, something they've wanted you to know for a long time.", "dimension": "WORDS"}, "B": {"text": "Their hand finds yours without a word, and they gently pull you closer against them.", "dimension": "TOUCH"}}},
    {"id": 4, "scene": "You meet after being apart for several days. They've clearly been thinking about you.", "prompt": "Which would reach you more deeply?", "choices": {"A": {"text": "Before anything else, they tell you how much they missed you and exactly what they missed about having you around.", "dimension": "WORDS"}, "B": {"text": "They hand you something small they found while you were apart because it instantly made them think of you.", "dimension": "GIFTS"}}},
    {"id": 5, "scene": "It's a quiet Sunday morning. There are no plans, no appointments, and nowhere either of you has to be.", "prompt": "Which version of the morning feels more loving?", "choices": {"A": {"text": "They make coffee, deal with breakfast, and quietly take care of everything while you stay warm and comfortable.", "dimension": "SERVICE"}, "B": {"text": "Phones disappear, time stops mattering, and the two of you spend the whole morning talking, laughing, and doing absolutely nothing important.", "dimension": "TIME"}}},
    {"id": 6, "scene": "You're walking home together after dinner. The streets are almost empty and the evening feels strangely peaceful.", "prompt": "What would make you feel closer?", "choices": {"A": {"text": "They slow down because neither of you wants the walk to end, and the two of you keep wandering with nowhere particular to go.", "dimension": "TIME"}, "B": {"text": "They slip their hand into yours and keep it there the whole way home.", "dimension": "TOUCH"}}},
    {"id": 7, "scene": "Your partner tells you they have a surprise planned for the evening.", "prompt": "Which surprise would feel more romantic?", "choices": {"A": {"text": "They've arranged an evening built entirely around being together, with no interruptions and nowhere else to be.", "dimension": "TIME"}, "B": {"text": "They give you something they remembered you mentioning months ago, something you had completely forgotten about.", "dimension": "GIFTS"}}},
    {"id": 8, "scene": "You've had one of those days where everything seemed to go wrong. You finally sit down beside your partner and let your shoulders drop.", "prompt": "Which response would make you feel most cared for?", "choices": {"A": {"text": "They quietly start fixing one of the problems that has been stressing you, without making a big thing out of it.", "dimension": "SERVICE"}, "B": {"text": "They pull you into them and hold you for a long time before asking you to explain anything.", "dimension": "TOUCH"}}},
    {"id": 9, "scene": "You're preparing for something important the next morning and beginning to feel overwhelmed.", "prompt": "Which gesture would feel more loving?", "choices": {"A": {"text": "Your partner quietly prepares everything they can for you so tomorrow will be easier.", "dimension": "SERVICE"}, "B": {"text": "They leave a small surprise beside your things for you to discover in the morning, chosen specifically to make you smile.", "dimension": "GIFTS"}}},
    {"id": 10, "scene": "You're sitting together on the sofa after a lovely evening when your partner says, \"Wait, I have something for you.\"", "prompt": "Which moment feels more intimate?", "choices": {"A": {"text": "Before showing you anything, they move close, wrap their arms around you and stay there for a while.", "dimension": "TOUCH"}, "B": {"text": "They give you a tiny keepsake connected to something the two of you experienced together.", "dimension": "GIFTS"}}},
    {"id": 11, "scene": "You're lying beside each other in the dark, neither of you quite ready to sleep.", "prompt": "Which would make you feel more deeply connected?", "choices": {"A": {"text": "You end up talking for another hour about dreams, memories, strange ideas, and things nobody else really knows about you.", "dimension": "TIME"}, "B": {"text": "Just before falling asleep, they tell you how much having you in their life means to them.", "dimension": "WORDS"}}},
    {"id": 12, "scene": "You're nervous about something important and trying not to show it.", "prompt": "Which would mean more?", "choices": {"A": {"text": "Your partner notices and quietly starts taking care of practical details so you have less to worry about.", "dimension": "SERVICE"}, "B": {"text": "They look you straight in the eyes and remind you why they believe in you.", "dimension": "WORDS"}}},
    {"id": 13, "scene": "You meet your partner after a difficult day. You haven't told them what happened yet.", "prompt": "What would make you feel safest with them?", "choices": {"A": {"text": "They hold your face gently, kiss your forehead, and pull you close before asking what's wrong.", "dimension": "TOUCH"}, "B": {"text": "They tell you softly, \"Whatever happened today, you don't have to earn anything from me. I'm just happy you're here.\"", "dimension": "WORDS"}}},
    {"id": 14, "scene": "It's an ordinary day, not an anniversary or birthday. Nothing special is supposed to happen.", "prompt": "Which unexpected gesture would feel more romantic?", "choices": {"A": {"text": "You find a little note from them telling you something they appreciate about you that they don't say often enough.", "dimension": "WORDS"}, "B": {"text": "They come home with a tiny thing they saw somewhere because it reminded them of an inside joke between you.", "dimension": "GIFTS"}}},
    {"id": 15, "scene": "You've both been busy for days and barely had a real moment together.", "prompt": "Which would restore the connection more?", "choices": {"A": {"text": "Your partner clears the evening completely and says, \"Tonight I just want you.\"", "dimension": "TIME"}, "B": {"text": "Before the evening starts, they take care of several things hanging over both of you so there is finally space to relax.", "dimension": "SERVICE"}}},
    {"id": 16, "scene": "You're watching a film together on a cold evening.", "prompt": "Which detail would make the evening feel warmer?", "choices": {"A": {"text": "The film almost stops mattering because you end up talking, laughing, and sharing stories through half of it.", "dimension": "TIME"}, "B": {"text": "They pull a blanket over both of you, tuck themselves against you, and absent-mindedly stroke your hand.", "dimension": "TOUCH"}}},
    {"id": 17, "scene": "You return to a place where the two of you once had a meaningful moment together.", "prompt": "Which would affect you more?", "choices": {"A": {"text": "Your partner suggests staying there for a while, just the two of you, remembering what happened and talking about everything that has changed since.", "dimension": "TIME"}, "B": {"text": "They reveal that they kept something small from that original day and have brought it back with them.", "dimension": "GIFTS"}}},
    {"id": 18, "scene": "You wake during the night feeling restless and unable to settle.", "prompt": "Which response would make you feel more loved?", "choices": {"A": {"text": "Your partner half-wakes, pulls you closer against them, and keeps an arm around you until you relax.", "dimension": "TOUCH"}, "B": {"text": "They get up with you, bring you water, adjust whatever is bothering you, and make sure you're comfortable before going back to bed.", "dimension": "SERVICE"}}},
    {"id": 19, "scene": "You casually mention something you've been struggling with, not expecting your partner to do anything about it.", "prompt": "A few days later, which discovery would move you more?", "choices": {"A": {"text": "They quietly found a way to solve part of the problem for you.", "dimension": "SERVICE"}, "B": {"text": "They found something small connected to what you told them and brought it home because they remembered.", "dimension": "GIFTS"}}},
    {"id": 20, "scene": "It's your anniversary, but you've agreed not to make a huge production out of it.", "prompt": "Which simple moment would feel more romantic?", "choices": {"A": {"text": "They give you something small but deeply personal that represents part of your story together.", "dimension": "GIFTS"}, "B": {"text": "They sit close, hold your hands, and kiss you slowly like neither of you needs to be anywhere else.", "dimension": "TOUCH"}}},
    {"id": 21, "scene": "You've achieved something you worked very hard for. Later that evening, it's just the two of you.", "prompt": "What would make the success feel even more meaningful?", "choices": {"A": {"text": "Your partner wants to spend the whole evening celebrating with you, listening to every detail and sharing your excitement.", "dimension": "TIME"}, "B": {"text": "They tell you how proud they are of you and describe the qualities they saw in you while you were fighting to get there.", "dimension": "WORDS"}}},
    {"id": 22, "scene": "You're both tired, and you admit that lately you've felt like you aren't doing enough.", "prompt": "Which response would land more deeply?", "choices": {"A": {"text": "They remind you of everything they see you doing and tell you that you don't have to prove your worth to them.", "dimension": "WORDS"}, "B": {"text": "The next day, without making an announcement about it, they take several responsibilities off your shoulders.", "dimension": "SERVICE"}}},
    {"id": 23, "scene": "You're reunited after being apart longer than usual.", "prompt": "Which first moment would overwhelm you more?", "choices": {"A": {"text": "Before either of you says much, they wrap both arms around you and hold you as though they have no intention of letting go.", "dimension": "TOUCH"}, "B": {"text": "While looking at you, they quietly say, \"I missed you. Not just having someone around. You.\"", "dimension": "WORDS"}}},
    {"id": 24, "scene": "One morning you discover your partner has been thinking about something you said weeks earlier.", "prompt": "Which discovery feels more intimate?", "choices": {"A": {"text": "They wrote you a message about it, explaining what your words made them realize and what they value about you.", "dimension": "WORDS"}, "B": {"text": "They found something connected to that conversation and saved it specifically for the right moment to give to you.", "dimension": "GIFTS"}}},
    {"id": 25, "scene": "You're going through a stressful period and have been mentally somewhere else for days.", "prompt": "Which would make you feel most loved?", "choices": {"A": {"text": "Your partner quietly handles some of the everyday things you've been forgetting so you don't have to keep everything in your head.", "dimension": "SERVICE"}, "B": {"text": "They insist on stealing you away for a few hours, somewhere you can forget responsibilities and simply be together.", "dimension": "TIME"}}},
    {"id": 26, "scene": "You're sitting somewhere beautiful together: maybe by the sea, on a balcony, or under a clear night sky.", "prompt": "What would make the memory feel especially romantic later?", "choices": {"A": {"text": "They move close enough that your shoulders touch, take your hand, and quietly stay connected to you while you watch.", "dimension": "TOUCH"}, "B": {"text": "Neither of you checks the time. You talk until the surroundings almost disappear and it feels like only the two of you exist.", "dimension": "TIME"}}},
    {"id": 27, "scene": "Your partner has planned a date without telling you much about it.", "prompt": "Which kind of thoughtfulness would affect you more?", "choices": {"A": {"text": "They've chosen a place and an evening based entirely around things they know you enjoy doing together.", "dimension": "TIME"}, "B": {"text": "Somewhere during the date, they surprise you with a small object that connects to a memory only the two of you would understand.", "dimension": "GIFTS"}}},
    {"id": 28, "scene": "You're sick in bed and feeling miserable.", "prompt": "Which kind of care would make you feel more loved?", "choices": {"A": {"text": "Your partner keeps checking what you need, brings you food and medicine, fixes the room, and makes sure you don't have to get up.", "dimension": "SERVICE"}, "B": {"text": "They climb carefully into bed beside you, stroke your hair, and stay close even though you're hardly good company.", "dimension": "TOUCH"}}},
    {"id": 29, "scene": "You've mentioned in passing that something from your childhood always makes you happy.", "prompt": "Weeks later, which surprise would affect you more?", "choices": {"A": {"text": "Your partner finds a way to recreate or obtain a small version of it for you because they remembered.", "dimension": "GIFTS"}, "B": {"text": "They quietly arrange something that lets you experience that happiness again without you having to organize anything yourself.", "dimension": "SERVICE"}}},
    {"id": 30, "scene": "You're about to say goodbye after a particularly good day together.", "prompt": "Which ending would stay in your mind longer?", "choices": {"A": {"text": "Just before you leave, they press a small keepsake from the day into your hand and say, \"So you have something from today.\"", "dimension": "GIFTS"}, "B": {"text": "They pull you back for one last long embrace, holding you for several seconds longer than necessary.", "dimension": "TOUCH"}}},
]


def public_question(question: Question) -> dict:
    return {
        "id": question["id"],
        "scene": question["scene"],
        "prompt": question["prompt"],
        "choices": {key: question["choices"][key]["text"] for key in ("A", "B")},
    }


def get_question(question_id: int) -> Question:
    for question in QUESTION_BANK:
        if question["id"] == question_id:
            return question
    raise KeyError(question_id)


def pair_key(left: Dimension, right: Dimension) -> tuple[Dimension, Dimension]:
    order = {dimension: index for index, dimension in enumerate(DIMENSIONS)}
    return tuple(sorted((left, right), key=lambda value: order[value]))  # type: ignore[return-value]


def pair_matrix() -> dict[Dimension, dict[Dimension, int | str]]:
    matrix: dict[Dimension, dict[Dimension, int | str]] = {
        row: {column: "-" if row == column else 0 for column in DIMENSIONS} for row in DIMENSIONS
    }
    for question in QUESTION_BANK:
        a = question["choices"]["A"]["dimension"]
        b = question["choices"]["B"]["dimension"]
        if a and b:
            matrix[a][b] = int(matrix[a][b]) + 1
            matrix[b][a] = int(matrix[b][a]) + 1
    return matrix


def validate_question_bank() -> dict:
    errors: list[str] = []
    ids = [question["id"] for question in QUESTION_BANK]
    if len(QUESTION_BANK) != 30:
        errors.append("Question bank must contain exactly 30 questions.")
    if len(ids) != len(set(ids)):
        errors.append("Question IDs must be unique.")

    pair_counts: Counter[tuple[Dimension, Dimension]] = Counter()
    dimension_counts: Counter[Dimension] = Counter()
    position_counts: Counter[Dimension] = Counter()
    texts: list[str] = []

    for question in QUESTION_BANK:
        choices = question.get("choices", {})
        a = choices.get("A", {}).get("dimension")
        b = choices.get("B", {}).get("dimension")
        if not question["scene"].strip() and not question["prompt"].strip():
            errors.append(f"Question {question['id']} needs scene or prompt text.")
        if not choices.get("A", {}).get("text", "").strip() or not choices.get("B", {}).get("text", "").strip():
            errors.append(f"Question {question['id']} needs nonempty A and B choices.")
        if a not in DIMENSIONS or b not in DIMENSIONS:
            errors.append(f"Question {question['id']} has invalid dimensions.")
            continue
        if a == b:
            errors.append(f"Question {question['id']} compares a dimension against itself.")
        pair_counts[pair_key(a, b)] += 1
        dimension_counts[a] += 1
        dimension_counts[b] += 1
        position_counts[a] += 1
        texts.extend([question["scene"], question["prompt"], choices["A"]["text"], choices["B"]["text"]])

    for expected_pair in combinations(DIMENSIONS, 2):
        if pair_counts[pair_key(*expected_pair)] != 3:
            errors.append(f"Pair {expected_pair[0]}-{expected_pair[1]} must appear exactly 3 times.")

    expected_dimension_total = len(QUESTION_BANK) * 2 // len(DIMENSIONS)
    for dimension in DIMENSIONS:
        if dimension_counts[dimension] != expected_dimension_total:
            errors.append(f"{dimension} appears {dimension_counts[dimension]} times, expected {expected_dimension_total}.")
        if not 3 <= position_counts[dimension] <= 9:
            errors.append(f"{dimension} appears in A position {position_counts[dimension]} times; expected reasonable balance.")

    normalized_texts = [text.strip().lower() for text in texts if text.strip()]
    if len(normalized_texts) != len(set(normalized_texts)):
        errors.append("Question or answer text contains exact duplicates.")
    for index, text in enumerate(normalized_texts):
        for other in normalized_texts[index + 1 :]:
            if len(text) > 60 and SequenceMatcher(None, text, other).ratio() > 0.92:
                errors.append("Question or answer text contains near-identical wording.")
                break

    return {
        "valid": not errors,
        "errors": errors,
        "question_count": len(QUESTION_BANK),
        "pair_matrix": pair_matrix(),
        "dimension_counts": dict(dimension_counts),
        "a_position_counts": dict(position_counts),
    }
