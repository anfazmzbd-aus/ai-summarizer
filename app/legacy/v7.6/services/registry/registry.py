AGENT_REGISTRY = {}

def register_agent(
    name,
    depends_on=None,
    produces=None
):

    if depends_on is None:
        depends_on = []

    if produces is None:
        produces = []

    def decorator(func):

        AGENT_REGISTRY[name] = {
            "function": func,
            "depends_on": depends_on,
            "produces": produces
        }

        return func

    return decorator