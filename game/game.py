from scene import Scene
from enum import IntEnum

class GameState(IntEnum):

    MENU = 0
    GAME = 1
    GAME_OVER = 2

class Game:

    current_scene: Scene

    def __init__(self):
        pass