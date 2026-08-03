from app.policy import SecurityContext


def test_defaults():

    context = SecurityContext()

    assert context.authenticated is True
    assert context.tenant_id is None
    assert context.origin is None
