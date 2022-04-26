from .entity import AbstractEntity, _ENTITY_SIZE
from .bullet import BulletDirection
from pyray import draw_rectangle, RED
from enum import IntEnum
import typing as tp


class EnemyBullet(AbstractEntity):

    _SPEED = 550.0

    def __init__(self, init_x: int, init_y: int, direction: BulletDirection):
        self.x = init_x
        self.y = init_y
        self.direction = direction

    def draw(self):
        draw_rectangle(self.x, self.y, 8, 8, RED)

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