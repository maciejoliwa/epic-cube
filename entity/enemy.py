from re import I
from .entity import AbstractEntity, _ENTITY_SIZE
from .bullet import Bullet
from pyray import draw_circle, RED, PURPLE, YELLOW, draw_triangle, Vector2
from enum import IntEnum
import typing as tp


class EnemyType(IntEnum):

    TRIANGLE = 0
    CIRCLE = 1
    ESCAPING_TRIANGLE = 2
    TRIANGLE_BOSS = 3


class Enemy(AbstractEntity):

    _CIRCLE_SPEED = 200.0
    _TRIANGLE_SPEED = 100.0
    _TRIANGLE_BOSS_SPEED = 0.0

    _type: EnemyType

    def __init__(self, init_x: int, init_y: int, en_type: EnemyType, damage: int):
        self.x = init_x
        self.y = init_y
        self._type = en_type
        self.damage = damage

        if self._type == EnemyType.CIRCLE:
            self.health = 20
            self.speed = self._CIRCLE_SPEED

        if self._type == EnemyType.TRIANGLE:
            self.health = 40
            self.speed = self._TRIANGLE_SPEED

        if self._type == EnemyType.ESCAPING_TRIANGLE:
            self.health = 15
            self.speed = 280.0

        if self._type == EnemyType.TRIANGLE_BOSS:
            self.health = 200
            self.speed = self._TRIANGLE_BOSS_SPEED

    def draw(self):
        if self.health > 0:
            if self._type == EnemyType.CIRCLE:
                draw_circle(self.x, self.y, 16, RED)
            if self._type == EnemyType.TRIANGLE:
                draw_triangle(Vector2(self.x, self.y), Vector2(self.x - 16, self.y + 32), Vector2(self.x + 16, self.y + 32), PURPLE)
            if self._type == EnemyType.ESCAPING_TRIANGLE:
                draw_triangle(Vector2(self.x, self.y), Vector2(self.x - 16, self.y + 32), Vector2(self.x + 16, self.y + 32), YELLOW)
            if self._type == EnemyType.TRIANGLE_BOSS:
                draw_triangle(Vector2(self.x, self.y), Vector2(self.x - 96, self.y + 144), Vector2(self.x + 96, self.y + 144), RED)

    def update(self, delta, *args):
        player_x = args[0]
        player_y = args[1]
        enemies = args[2]
    
        # Cirlces will follow the player
        if self._type == EnemyType.CIRCLE or self._type == EnemyType.TRIANGLE:
            if self.x > player_x + 16:
                self.x -= int(self.speed * delta)
            if self.x < player_x + 16:
                self.x += int(self.speed * delta)
            if self.y > player_y + 16:
                self.y -= int(self.speed * delta)
            if self.y < player_y + 16:
                self.y += int(self.speed * delta)

        if self._type == EnemyType.ESCAPING_TRIANGLE:
            if self.x > player_x + 16 and self.x + 32 < 1024:
                self.x += int(self.speed * delta)
            if self.x < player_x + 16 and self.x - 32 > 0:
                self.x -= int(self.speed * delta)
            if self.y > player_y + 16 and self.y + 32 < 576:
                self.y += int(self.speed * delta)
            if self.y < player_y + 16 and self.y - 32 > 0:
                self.y -= int(self.speed * delta)

        if self.health <= 0:
            self.x = -500
            self.y = -500

    def on_collision(self, other: tp.Any, callback: tp.Callable, *args):
        player_damage = args[0]

        if isinstance(other, Bullet):
            self.health -= player_damage

            if callback is not None and self.health <= 0:
                callback()
