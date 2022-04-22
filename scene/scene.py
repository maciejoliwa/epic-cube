import typing as tp
from pathlib import Path
from random import randrange
from .tile import Tile, get_tile_by_character

class Scene:

    fname: str
    tiles: tp.List[Tile]
    is_item_room = False

    def __init__(self, fname: str, is_item_room: bool = False) -> tp.NoReturn:
        self.fname = fname
        self.tiles = self._read_map_file()
        self.is_item_room = is_item_room

    @staticmethod
    def load_random_map() -> 'Scene':
        maps_directory = Path('maps/')
        maps = list(maps_directory.iterdir())
        random_map = maps[randrange(0, len(maps))]

        return Scene(random_map.absolute())

    def _read_map_file(self) -> tp.List[Tile]:
        results = []

        with open(self.fname, 'r') as MAP_FILE:
            contents = MAP_FILE.read()
            singular_characters = list(contents)

            length = len(singular_characters)
            
            x: int = 0
            y: int = 0

            for i in range(length):

                if singular_characters[i] == '\n':
                    x = 0
                    y += 32
                else:
                    results.append(get_tile_by_character(x, y, singular_characters[i]))
                    x += 32

        return results

    def render(self) -> tp.NoReturn:
        for tile in self.tiles:
            tile.draw()