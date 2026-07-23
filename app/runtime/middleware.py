from abc import ABC
from abc import abstractmethod


class RuntimeMiddleware(ABC):

    @abstractmethod
    def before_execution(
        self,
        runtime_context,
    ): ...

    @abstractmethod
    def after_execution(
        self,
        runtime_context,
        result,
    ): ...
