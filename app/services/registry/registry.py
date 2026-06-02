AGENT_REGISTRY = {}

def register_agent(name):

    def decorator(func):

        AGENT_REGISTRY[name] = func

        return func

    return decorator