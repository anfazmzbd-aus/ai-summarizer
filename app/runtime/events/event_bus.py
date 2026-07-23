class EventBus:

    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback):
        self._subscribers.setdefault(event_type, []).append(callback)

    def unsubscribe(self, event_type, callback):
        self._subscribers[event_type].remove(callback)

    def publish(self, event):

        for callback in self._subscribers.get(type(event), []):
            callback(event)
