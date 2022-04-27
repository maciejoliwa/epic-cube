from .entity import AbstractEntity, _ENTITY_SIZE
from .enemy import Enemy, EnemyType
from .player import Player
from scene import Tile
from pyray import Texture2D, Image, load_texture_from_image, load_image, draw_texture_rec, Rectangle, Vector2, RAYWHITE, load_wave, load_sound_from_wave, play_sound
import typing as tp


class HeartDrop(AbstractEntity):

    x: int
    y: int
    texture: Texture2D

    def __init__(self, init_x: int, init_y: int, texture: Texture2D) -> tp.NoReturn:
        self.x = init_x
        self.y = init_y
        self.texture = texture

    def on_collision(self, other: tp.Any, callback: tp.Callable):
        if isinstance(other, Player):
           other._hp += 1

    def update(self, delta: float, *args) -> tp.NoReturn:
        return super().update(delta, *args)

    def draw(self) -> tp.NoReturn:
        draw_texture_rec(self.texture, Rectangle(0, 0, 8, 8), Vector2(self.x, self.y), RAYWHITE)