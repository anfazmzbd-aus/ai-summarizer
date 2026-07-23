class MiddlewarePipeline:

    def __init__(self):

        self._middlewares = []

    def add(
        self,
        middleware,
    ):
        self._middlewares.append(middleware)

    def before_execution(
        self,
        runtime_context,
    ):

        for middleware in self._middlewares:
            middleware.before_execution(runtime_context)

    def after_execution(
        self,
        runtime_context,
        result,
    ):

        for middleware in reversed(self._middlewares):
            middleware.after_execution(
                runtime_context,
                result,
            )
