from app.questions import DIMENSIONS, validate_question_bank


def test_question_bank_validation():
    validation = validate_question_bank()
    assert validation["valid"], validation["errors"]
    assert validation["question_count"] == 30


def test_pair_balance_matrix():
    matrix = validate_question_bank()["pair_matrix"]
    for row in DIMENSIONS:
        for column in DIMENSIONS:
            if row == column:
                assert matrix[row][column] == "-"
            else:
                assert matrix[row][column] == 3
