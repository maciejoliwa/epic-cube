from .entity import AbstractEntity, _ENTITY_SIZE
from .enemy import Enemy, EnemyType
from .enemy_bullet import EnemyBullet
from scene import Tile
from pyray import is_key_down, KEY_A, KEY_D, KEY_W, KEY_S, draw_rectangle, GREEN
import typing as tp

class Player(AbstractEntity):

    _hp: int = 6

    def __init__(self, init_x: int, init_y: int):
        self.x = init_x
        self.y = init_y
        self.damage = 5
        self.speed = 450.0

    def update(self, delta: float) -> tp.NoReturn:
        calculated_speed = int(delta * self.speed)

        # Those ifs checking coords are to make sure the player cannot leave outside the window

        if is_key_down(KEY_A):
            if self.x > 0:
                self.x -= calculated_speed
        
        if is_key_down(KEY_D):
            if self.x < 992:  # 1024 - 32 (width of window - width of player entity)
                self.x += calculated_speed

        if is_key_down(KEY_S):
            if self.y < 544:  # 576 - 32 (height of window - height of player)
                self.y += calculated_speed

        if is_key_down(KEY_W):
            if self.y > 0:
                self.y -= calculated_speed

    def draw(self) -> tp.NoReturn:
        draw_rectangle(self.x, self.y, _ENTITY_SIZE, _ENTITY_SIZE, GREEN)

    def _damage(self, damage: int) -> tp.NoReturn:
        pass

    def on_collision(self, other: tp.Any, callback: tp.Callable):
        if isinstance(other, Enemy):
            self._hp -= other.damage
        if isinstance(other, EnemyBullet):
            self._hp -= 1