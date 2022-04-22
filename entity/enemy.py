from .entity import AbstractEntity, _ENTITY_SIZE
from pyray import draw_circle, RED
from enum import IntEnum
import typing as tp


class EnemyType(IntEnum):

    TRIANGLE = 0
    CIRCLE = 1


class Enemy(AbstractEntity):

    _type: EnemyType

    def __init__(self, init_x: int, init_y: int, en_type: EnemyType, damage: int):
        self.x = init_x
        self.y = init_x
        self._type = en_type
        self.damage = damage

        if self._type == EnemyType.CIRCLE:
            self.health = 100

    def draw(self):
        if self._type == EnemyType.CIRCLE:
            draw_circle(self.x, self.y, 16, RED)

    def update(self, delta):
        pass

    def on_collision(self, other: tp.Any, callback: tp.Callable):
        return super().on_collision(other, callback)