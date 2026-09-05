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
    {"id": 1, "scene": "You finally have an evening alone after a week where you've barely connected. There are only twenty minutes before you both have to sleep.", "prompt": "Which would leave you feeling closer?", "choices": {"A": {"text": "They use those minutes to tell you what they've missed about you and why having you in their life matters.", "dimension": "WORDS"}, "B": {"text": "They put everything away, curl up beside you, and spend those twenty minutes completely present with you, even if very little is said.", "dimension": "TIME"}}},
    {"id": 2, "scene": "You've had a brutal day and come home visibly exhausted. Your partner has enough energy to do just one thing before bed.", "prompt": "Which would mean more?", "choices": {"A": {"text": "Sit beside you and tell you, sincerely and specifically, that they see how much you're carrying and admire how you've handled it.", "dimension": "WORDS"}, "B": {"text": "Quietly take care of the thing you were dreading most so you wake up tomorrow with one less burden.", "dimension": "SERVICE"}}},
    {"id": 3, "scene": "You're about to leave each other for several days. There's time for one last moment.", "prompt": "Which would stay with you more?", "choices": {"A": {"text": "They look at you and tell you exactly what they're going to miss most about you.", "dimension": "WORDS"}, "B": {"text": "They pull you into a long embrace and stay there until you absolutely have to go.", "dimension": "TOUCH"}}},
    {"id": 4, "scene": "You're apart and having a difficult evening.", "prompt": "Which arriving unexpectedly would affect you more?", "choices": {"A": {"text": "A message from them saying something deeply personal about why they love having you in their life.", "dimension": "WORDS"}, "B": {"text": "A small package containing something they chose because of a private memory the two of you share.", "dimension": "GIFTS"}}},
    {"id": 5, "scene": "It's Sunday morning. You've both had an exhausting week. There are chores everywhere, but there's also finally a little time together.", "prompt": "Which would feel more loving?", "choices": {"A": {"text": "They get up and quietly take care of the mess so you don't have to.", "dimension": "SERVICE"}, "B": {"text": "They leave the chores where they are, make coffee, and spend the morning completely with you.", "dimension": "TIME"}}},
    {"id": 6, "scene": "You're sitting beside each other after an emotional conversation.", "prompt": "Which ending would make you feel closer?", "choices": {"A": {"text": "You keep talking for another hour until you feel like they truly understand what was happening inside you.", "dimension": "TIME"}, "B": {"text": "The conversation ends, and they simply hold you against them quietly for a long time.", "dimension": "TOUCH"}}},
    {"id": 7, "scene": "Your partner wants to surprise you for your birthday but can only choose one.", "prompt": "Which surprise would mean more to you?", "choices": {"A": {"text": "They plan a whole day around things the two of you can experience together.", "dimension": "TIME"}, "B": {"text": "They give you one deeply thoughtful thing that shows they remembered something important you once told them.", "dimension": "GIFTS"}}},
    {"id": 8, "scene": "You've just received bad news and feel completely drained.", "prompt": "Which response would reach you first?", "choices": {"A": {"text": "Your partner immediately takes over the practical things you suddenly don't have the energy to deal with.", "dimension": "SERVICE"}, "B": {"text": "They sit down, pull you into their arms, and simply hold you while you absorb what happened.", "dimension": "TOUCH"}}},
    {"id": 9, "scene": "You casually mentioned something months ago that would make your life easier.", "prompt": "Which discovery would affect you more?", "choices": {"A": {"text": "Your partner has quietly solved the problem for you without waiting to be asked.", "dimension": "SERVICE"}, "B": {"text": "They found the exact little thing you mentioned and bought it because they remembered.", "dimension": "GIFTS"}}},
    {"id": 10, "scene": "After a beautiful date, you're standing outside saying goodbye.", "prompt": "Which would linger more strongly the next morning?", "choices": {"A": {"text": "The way they pulled you back for one last slow, affectionate embrace.", "dimension": "TOUCH"}, "B": {"text": "Finding the little keepsake they slipped into your pocket to remember the evening by.", "dimension": "GIFTS"}}},
    {"id": 11, "scene": "You're lying together late at night, and you've just admitted something you're insecure about.", "prompt": "Which response would mean more?", "choices": {"A": {"text": "They stay awake with you and let you talk through every messy part of it without rushing you.", "dimension": "TIME"}, "B": {"text": "They tell you clearly what they see in you that makes them love and respect you despite that insecurity.", "dimension": "WORDS"}}},
    {"id": 12, "scene": "Tomorrow you have something important that you're nervous about.", "prompt": "Which would strengthen you more tonight?", "choices": {"A": {"text": "Discovering they have prepared everything they reasonably can so tomorrow is easier.", "dimension": "SERVICE"}, "B": {"text": "Hearing them tell you exactly why they believe you can handle what's coming.", "dimension": "WORDS"}}},
    {"id": 13, "scene": "You're upset after an argument with someone else and having trouble calming down. Your partner notices.", "prompt": "Which would help you feel most loved?", "choices": {"A": {"text": "They come close, stroke your face, and hold you until your body finally starts relaxing.", "dimension": "TOUCH"}, "B": {"text": "They sit across from you and tell you the things they know you need to hear when you begin doubting yourself.", "dimension": "WORDS"}}},
    {"id": 14, "scene": "Nothing special is happening. It's just an ordinary Tuesday.", "prompt": "Which surprise would make you smile longer?", "choices": {"A": {"text": "Finding a handwritten note somewhere unexpected telling you something they genuinely appreciate about you.", "dimension": "WORDS"}, "B": {"text": "Finding a tiny gift related to an inside joke you thought they had forgotten.", "dimension": "GIFTS"}}},
    {"id": 15, "scene": "You've barely seen each other all week, and tonight is your only free evening. The apartment is a disaster.", "prompt": "What would feel more loving?", "choices": {"A": {"text": "They say, \"Forget it for tonight,\" order food, turn off the phones, and make the evening entirely about being together.", "dimension": "TIME"}, "B": {"text": "They tell you to sit down, put some music on, and deal with everything so you can finally breathe.", "dimension": "SERVICE"}}},
    {"id": 16, "scene": "You're together somewhere beautiful just before sunset. You have fifteen quiet minutes before you have to leave.", "prompt": "Which would make the memory more intimate?", "choices": {"A": {"text": "You spend those minutes talking about what this relationship has begun to mean to each of you.", "dimension": "TIME"}, "B": {"text": "You sit pressed against one another, holding hands and watching the sunset without needing to talk.", "dimension": "TOUCH"}}},
    {"id": 17, "scene": "You return to the place where you first realized there might be something between you.", "prompt": "Which gesture would move you more?", "choices": {"A": {"text": "They suggest staying for a while and reliving the memory together, talking about what each of you was secretly thinking then.", "dimension": "TIME"}, "B": {"text": "They reveal that they kept something small from that day and have saved it all this time.", "dimension": "GIFTS"}}},
    {"id": 18, "scene": "You wake up sick during the night. Your partner is exhausted too.", "prompt": "Which would make you feel more cared for?", "choices": {"A": {"text": "They pull you against them and stay awake enough to comfort you until you settle.", "dimension": "TOUCH"}, "B": {"text": "They get up, find medicine and water, adjust the room, and make sure everything you might need is beside the bed.", "dimension": "SERVICE"}}},
    {"id": 19, "scene": "You've been struggling with a problem but haven't asked your partner for help.", "prompt": "A few days later, which would mean more?", "choices": {"A": {"text": "They say, \"I looked into that thing you were struggling with,\" and have already done something useful about it.", "dimension": "SERVICE"}, "B": {"text": "They give you something small they found while thinking about what you told them.", "dimension": "GIFTS"}}},
    {"id": 20, "scene": "It's your anniversary, but money is tight, so neither gesture can be extravagant.", "prompt": "Which feels more romantic?", "choices": {"A": {"text": "They give you a tiny object with a personal story behind why they chose it for you.", "dimension": "GIFTS"}, "B": {"text": "You spend a long quiet moment wrapped around one another, kissing and holding each other without rushing anywhere.", "dimension": "TOUCH"}}},
    {"id": 21, "scene": "Something you've worked toward for months has finally gone well.", "prompt": "Which reaction from your partner would mean more?", "choices": {"A": {"text": "They want to hear the entire story and spend the evening celebrating it with you because they know how much it mattered.", "dimension": "TIME"}, "B": {"text": "They tell you how proud they are and specifically name the qualities they watched you show while getting there.", "dimension": "WORDS"}}},
    {"id": 22, "scene": "You admit that lately you feel like you're failing at keeping everything together.", "prompt": "Which response would stay with you longer?", "choices": {"A": {"text": "They tell you that your worth to them has nothing to do with how much you manage to accomplish.", "dimension": "WORDS"}, "B": {"text": "The next morning you discover they have quietly removed several things from your workload.", "dimension": "SERVICE"}}},
    {"id": 23, "scene": "You haven't seen each other for longer than usual.", "prompt": "At the moment you finally reunite, which would hit you harder emotionally?", "choices": {"A": {"text": "Being pulled immediately into an embrace where neither of you lets go for a long time.", "dimension": "TOUCH"}, "B": {"text": "Hearing them look at you and say, \"I didn't just miss having someone around. I missed you.\"", "dimension": "WORDS"}}},
    {"id": 24, "scene": "You once told your partner about something from your childhood that still means a lot to you. Months later, they haven't forgotten.", "prompt": "Which would touch you more?", "choices": {"A": {"text": "They bring it up in a letter explaining why that story helped them understand you better.", "dimension": "WORDS"}, "B": {"text": "They find something connected to that childhood memory and give it to you because they remembered.", "dimension": "GIFTS"}}},
    {"id": 25, "scene": "You are in the middle of a stressful period and haven't really felt like yourself. Your partner unexpectedly has an afternoon free.", "prompt": "Which gesture would feel more loving?", "choices": {"A": {"text": "They use the time to handle several things you've been falling behind on so life feels manageable again.", "dimension": "SERVICE"}, "B": {"text": "They take you somewhere quiet and say, \"Everything else can wait. I want some time with you.\"", "dimension": "TIME"}}},
    {"id": 26, "scene": "You're sitting together under a clear night sky. Something about the evening has made you both a little emotional.", "prompt": "Which would create the stronger feeling of connection?", "choices": {"A": {"text": "Their hand stays intertwined with yours and you lean against each other in silence.", "dimension": "TOUCH"}, "B": {"text": "You start talking and eventually realize an hour has passed because neither of you wanted the conversation to end.", "dimension": "TIME"}}},
    {"id": 27, "scene": "Your partner has one limited budget for a surprise.", "prompt": "Which would you secretly hope they chose?", "choices": {"A": {"text": "Spend it on an experience the two of you can share together.", "dimension": "TIME"}, "B": {"text": "Spend it on one meaningful object chosen specifically for you.", "dimension": "GIFTS"}}},
    {"id": 28, "scene": "You've reached the point of exhaustion where even small things feel difficult.", "prompt": "Which response makes you feel more loved?", "choices": {"A": {"text": "\"Come here.\" They pull you close, stroke your hair, and let you collapse against them.", "dimension": "TOUCH"}, "B": {"text": "\"Go rest.\" They take over the things that still need doing and refuse to let you worry about them.", "dimension": "SERVICE"}}},
    {"id": 29, "scene": "You mention something sentimental from your childhood that you haven't experienced in years.", "prompt": "Which surprise would mean more?", "choices": {"A": {"text": "Your partner tracks down a small physical reminder of it and gives it to you.", "dimension": "GIFTS"}, "B": {"text": "Your partner figures out how to recreate the experience itself for you and handles all the arrangements.", "dimension": "SERVICE"}}},
    {"id": 30, "scene": "A wonderful weekend together is ending and you won't see each other for a while.", "prompt": "Which goodbye would stay with you more?", "choices": {"A": {"text": "They give you something small from the weekend and say, \"Keep this until I see you again.\"", "dimension": "GIFTS"}, "B": {"text": "They hold you tightly at the door, kiss you goodbye, and linger until neither of you can reasonably postpone leaving anymore.", "dimension": "TOUCH"}}},
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
