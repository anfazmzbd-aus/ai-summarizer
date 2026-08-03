from app.policy import SecurityConfig


def test_defaults():

    config = SecurityConfig()

    assert config.allowed_agent_types == set()
    assert config.allowed_origins == set()
    assert config.require_authenticated is False
    assert config.require_tenant_id is False
