from dataclasses import dataclass
from pyray import draw_text, WHITE, BLACK, measure_text, draw_texture, Texture, RAYWHITE


@dataclass
class UIManager:

    player_hp: int
    heart: Texture
    half_heart: Texture
    rooms: int = 0

    def update(self, player_hp: int, rooms: int):
        self.player_hp = player_hp
        self.rooms = rooms

    def draw(self):
        x = 25
        y = 25

        for i in range(self.player_hp):
            draw_texture(self.heart, x, y, RAYWHITE)
            if i == 10 or i == 21:
                x = 25
                y += 20
            else:
                x += 20
            
        draw_text(f"Rooms Cleared: {self.rooms}", 800, 35, 24, BLACK)