class HookManager:

    def __init__(self):

        self._hooks = []

    def register(
        self,
        hook,
    ):

        self._hooks.append(hook)

    def before_node(
        self,
        context,
        node,
    ):

        for hook in self._hooks:
            hook.before_node(
                context,
                node,
            )

    def after_node(
        self,
        context,
        node,
        result,
    ):

        for hook in self._hooks:
            hook.after_node(
                context,
                node,
                result,
            )

    def before_layer(
        self,
        context,
        layer,
    ):

        for hook in self._hooks:
            hook.before_layer(
                context,
                layer,
            )

    def after_layer(
        self,
        context,
        layer,
    ):

        for hook in self._hooks:
            hook.after_layer(
                context,
                layer,
            )
