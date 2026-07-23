from abc import ABC
from abc import abstractmethod


class CheckpointBackend(ABC):

    @abstractmethod
    def save(
        self,
        checkpoint,
    ): ...

    @abstractmethod
    def load(
        self,
        execution_id,
    ): ...

    @abstractmethod
    def delete(
        self,
        execution_id,
    ): ...

    @abstractmethod
    def exists(
        self,
        execution_id,
    ): ...
