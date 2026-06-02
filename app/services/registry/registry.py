AGENT_REGISTRY = {}

def register_agent(
    name,
    depends_on=None
):

    if depends_on is None:
        depends_on = []

    def decorator(func):

        AGENT_REGISTRY[name] = {
            "function": func,
            "depends_on": depends_on
        }

        return func

    return decorator