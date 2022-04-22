from .entity import AbstractEntity, _ENTITY_SIZE
from pyray import draw_rectangle, YELLOW
from enum import IntEnum
import typing as tp


class BulletDirection(IntEnum):

    UP = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3


class Bullet(AbstractEntity):

    _SPEED = 550.0

    def __init__(self, init_x: int, init_y: int, direction: BulletDirection):
        self.x = init_x
        self.y = init_y
        self.direction = direction

    def draw(self):
        draw_rectangle(self.x, self.y, 8, 8, YELLOW)

    def update(self, delta: float):
        calc = int(self._SPEED * delta)

        if self.direction == BulletDirection.UP:
            self.y -= calc

        if self.direction == BulletDirection.DOWN:
            self.y += calc
        
        if self.direction == BulletDirection.LEFT:
            self.x -= calc
        
        if self.direction == BulletDirection.RIGHT:
            self.x += calc

    def on_collision(self, other: tp.Any, callback: tp.Callable):
        return super().on_collision(other, callback)