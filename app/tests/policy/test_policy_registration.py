from app.policy import PolicyRegistration


def test_default_priority():

    registration = PolicyRegistration(policy=None)

    assert registration.priority == 100
