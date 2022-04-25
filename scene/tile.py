from dataclasses import dataclass
from pyray import Color, DARKBLUE, BLUE, PINK, YELLOW, BLACK, WHITE, RED, draw_rectangle


@dataclass
class Tile:

    name: str
    x: int
    y: int
    color: Color

    def draw(self):
        draw_rectangle(self.x, self.y, 32, 32, self.color)


def get_tile_by_character(x: int, y: int, char: str) -> Tile:
    TILES = {
        'X': Tile('floor', x, y, DARKBLUE),
        'O': Tile('wall', x, y, BLUE),
        'T': Tile('floor_t', x, y, WHITE),
        '^': Tile('teleport_up', x, y, YELLOW),
        '>': Tile('teleport_right', x, y, YELLOW),
        '<': Tile('teleport_left', x, y, YELLOW),
        '-': Tile('damage', x, y, RED),
        'E': Tile('spawner', x, y, PINK)
    }

    return TILES[char]