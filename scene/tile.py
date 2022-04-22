from dataclasses import dataclass
from pyray import Color, DARKBLUE, BLUE, YELLOW, draw_rectangle


@dataclass
class Tile:

    x: int
    y: int
    color: Color

    def draw(self):
        draw_rectangle(self.x, self.y, 32, 32, self.color)


def get_tile_by_character(x: int, y: int, char: str) -> Tile:
    TILES = {
        'X': Tile(x, y, DARKBLUE),
        'O': Tile(x, y, BLUE),
        'T': Tile(x, y, YELLOW)
    }

    return TILES[char]