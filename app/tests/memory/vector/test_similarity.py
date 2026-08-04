from app.memory.vector import cosine_similarity


def test_similarity():

    score = cosine_similarity(
        [1, 0],
        [1, 0],
    )

    assert score == 1.0


def test_zero_vector():

    score = cosine_similarity(
        [0, 0],
        [1, 1],
    )

    assert score == 0.0
