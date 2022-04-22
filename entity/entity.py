from abc import ABC, abstractmethod
import typing as tp


_ENTITY_SIZE = 32

class AbstractEntity(ABC):

    def __init__(self, init_x: int, init_y: int) -> tp.NoReturn:
        self.x = init_x
        self.y = init_y

    @abstractmethod
    def update(self, delta: float, *args) -> tp.NoReturn:
        pass

    @abstractmethod
    def draw(self) -> tp.NoReturn:
        pass

    @abstractmethod
    def on_collision(self, other: tp.Any, callback: tp.Callable):
        pass
