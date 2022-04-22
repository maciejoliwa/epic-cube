import typing as tp
from scene import Scene
from entity import Item
from enum import IntEnum

class GameState(IntEnum):

    MENU = 0
    GAME = 1
    GAME_OVER = 2

class Game:

    current_scene: Scene
    score: int = 0
    collected_items: tp.List[Item] = []
    state: GameState = GameState.MENU

    def __init__(self):
        pass