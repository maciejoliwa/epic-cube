from .entity import AbstractEntity, _ENTITY_SIZE
from .enemy import Enemy, EnemyType
from scene import Tile
from pyray import is_key_down, KEY_A, KEY_D, KEY_W, KEY_S, draw_rectangle, GREEN
import typing as tp

class Player(AbstractEntity):

    _hp: int = 6

    def __init__(self, init_x: int, init_y: int):
        self.x = init_x
        self.y = init_y
        self.speed = 250.0

    def update(self, delta: float) -> tp.NoReturn:
        calculated_speed = int(delta * self.speed)

        if is_key_down(KEY_A):
            self.x -= calculated_speed
        
        if is_key_down(KEY_D):
            self.x += calculated_speed

        if is_key_down(KEY_S):
            self.y += calculated_speed

        if is_key_down(KEY_W):
            self.y -= calculated_speed

    def draw(self) -> tp.NoReturn:
        draw_rectangle(self.x, self.y, _ENTITY_SIZE, _ENTITY_SIZE, GREEN)

    def _damage(self, damage: int) -> tp.NoReturn:
        pass

    def on_collision(self, other: tp.Any, callback: tp.Callable):
        if isinstance(other, Enemy):
            self._hp -= other.damage