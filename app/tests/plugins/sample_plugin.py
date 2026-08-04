from app.plugins import (
    Plugin,
    PluginMetadata,
)


class SamplePlugin(Plugin):

    @property
    def metadata(self):

        return PluginMetadata(
            "sample",
            "1.0",
        )

    def initialize(self, context):
        pass

    def shutdown(self):
        pass


PLUGIN_CLASS = SamplePlugin
