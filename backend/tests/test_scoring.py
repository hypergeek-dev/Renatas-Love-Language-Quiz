from app.scoring import build_result, calculate_raw_scores, classify_profile, normalize_percentages


def test_binary_answer_scoring():
    scores = calculate_raw_scores({1: "A", 2: "B"})
    assert scores["WORDS"] == 1
    assert scores["SERVICE"] == 1


def test_editing_an_answer_replaces_rather_than_adds():
    first = calculate_raw_scores({1: "A"})
    assert first["WORDS"] == 1
    edited = calculate_raw_scores({1: "B"})
    assert edited["WORDS"] == 0
    assert edited["TIME"] == 1
    assert sum(edited.values()) == 1


def test_score_normalization_totals_100():
    percentages = normalize_percentages({"WORDS": 1, "TIME": 1, "SERVICE": 1, "TOUCH": 1, "GIFTS": 1})
    assert sum(percentages.values()) == 100
    assert set(percentages.values()) == {20}


def test_tie_order_is_deterministic():
    balanced_answers = {
        1: "A",
        2: "A",
        3: "A",
        4: "A",
        5: "A",
        6: "A",
        7: "A",
        8: "A",
        9: "A",
        10: "A",
        11: "A",
        12: "A",
        13: "A",
        14: "A",
        15: "A",
        16: "A",
        17: "A",
        18: "A",
        19: "B",
        20: "A",
        21: "B",
        22: "B",
        23: "A",
        24: "B",
        25: "A",
        26: "A",
        27: "B",
        28: "B",
        29: "A",
        30: "A",
    }
    result = build_result(balanced_answers)
    assert result["percent_total"] == 100
    assert result["primary"]["key"] == "SERVICE"
    assert result["profile_shape"] == "Broad"


def test_profile_classifications():
    assert classify_profile({"WORDS": 30, "TIME": 20, "SERVICE": 18, "TOUCH": 17, "GIFTS": 15}) == "Focused"
    assert classify_profile({"WORDS": 25, "TIME": 22, "SERVICE": 20, "TOUCH": 18, "GIFTS": 16}) == "Blended"
    assert classify_profile({"WORDS": 22, "TIME": 21, "SERVICE": 20, "TOUCH": 19, "GIFTS": 18}) == "Broad"
