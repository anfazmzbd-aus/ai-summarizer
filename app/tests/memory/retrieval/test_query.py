from app.memory import RetrievalQuery


def test_query():

    query = RetrievalQuery(text="summary")

    assert query.limit == 5
