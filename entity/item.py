from .entity import AbstractEntity, _ENTITY_SIZE
from .enemy import Enemy, EnemyType
from .player import Player
from scene import Tile
from pyray import Texture2D, Image, load_texture_from_image, load_image, draw_texture_rec, Rectangle, Vector2, RAYWHITE
import typing as tp


class Item(AbstractEntity):

    name: str
    x: int
    y: int
    texture: Texture2D

    def __init__(self, name: str, init_x: int, init_y: int, text: str) -> tp.NoReturn:
        self.name = name
        self.x = init_x
        self.y = init_y
        
        image = load_image(text)
        self.texture = load_texture_from_image(image)

    def on_collision(self, other: tp.Any, callback: tp.Callable):
        if isinstance(other, Player):
            # Make the object disappear
            self.x = -100
            self.y = -100
            print("PICKED")

    def update(self, delta: float, *args) -> tp.NoReturn:
        return super().update(delta, *args)

    def draw(self) -> tp.NoReturn:
        draw_texture_rec(self.texture, Rectangle(0, 0, 32, 32), Vector2(self.x, self.y), RAYWHITE)