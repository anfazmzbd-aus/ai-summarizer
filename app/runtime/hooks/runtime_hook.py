from abc import ABC
from abc import abstractmethod


class RuntimeHook(ABC):

    @abstractmethod
    def before_node(
        self,
        context,
        node: str,
    ): ...

    @abstractmethod
    def after_node(
        self,
        context,
        node: str,
        result,
    ): ...

    @abstractmethod
    def before_layer(
        self,
        context,
        layer: int,
    ): ...

    @abstractmethod
    def after_layer(
        self,
        context,
        layer: int,
    ): ...
