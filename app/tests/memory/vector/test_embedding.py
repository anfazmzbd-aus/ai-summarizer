from app.memory.vector import EmbeddingProvider


class TestEmbedding(EmbeddingProvider):

    def embed(self, text):

        return [1.0]


def test_embedding():

    provider = TestEmbedding()

    assert provider.embed("hello") == [1.0]
