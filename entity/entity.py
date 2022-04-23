from abc import ABC, abstractmethod
import typing as tp
from pyray import check_collision_recs, Rectangle

_ENTITY_SIZE = 32

class AbstractEntity(ABC):

    def __init__(self, init_x: int, init_y: int) -> tp.NoReturn:
        self.x = init_x
        self.y = init_y

    @staticmethod
    def entities_collided(e1: 'AbstractEntity', e2: 'AbstractEntity') -> bool:
        return check_collision_recs(
            Rectangle(e1.x, e1.y, _ENTITY_SIZE, _ENTITY_SIZE),
            Rectangle(e2.x, e2.y, _ENTITY_SIZE, _ENTITY_SIZE),
        )

    @abstractmethod
    def update(self, delta: float, *args) -> tp.NoReturn:
        pass

    @abstractmethod
    def draw(self) -> tp.NoReturn:
        pass

    @abstractmethod
    def on_collision(self, other: tp.Any, callback: tp.Callable):
        pass
