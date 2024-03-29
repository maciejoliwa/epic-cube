from .entity import AbstractEntity, _ENTITY_SIZE
from .enemy import Enemy, EnemyType
from .player import Player
from scene import Tile
from pyray import Texture2D, Image, load_texture_from_image, load_image, draw_texture_rec, Rectangle, Vector2, RAYWHITE, load_wave, load_sound_from_wave, play_sound
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

            if self.name == "Butt Plug":
                pass
            
            if self.name == 'Windows':
                pass

            if self.name == 'Ukulele':
                other._hp += 4
                other.damage += 2
            
            if self.name == 'Black':
                other._hp -= 1
                other.speed += 50.0

            if self.name == 'Straw Hat':
                other._hp += 1
                other.speed += 50.0

            if self.name == 'C Programming Language':
                other._hp += 1
                other.speed += 75.0
                other.damage += 5

            if self.name == 'JavaScript The Good Parts':
                other._hp += 1
                other.speed -= 25.0
                other.damage += 1

            if self.name == 'Skirt':
                other._hp -= 5
                other.speed += 50.0

            if self.name == 'Vodka':
                other._hp -= int(other._hp/2)
                other.damage += 5
                other.speed -= 50.0


    def update(self, delta: float, *args) -> tp.NoReturn:
        return super().update(delta, *args)

    def draw(self) -> tp.NoReturn:
        draw_texture_rec(self.texture, Rectangle(0, 0, 32, 32), Vector2(self.x, self.y), RAYWHITE)