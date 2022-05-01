from dataclasses import dataclass
from pyray import draw_text, WHITE, BLACK, measure_text, draw_texture, Texture, RAYWHITE


@dataclass
class UIManager:

    player_hp: int
    heart: Texture
    half_heart: Texture
    rooms: int = 0

    def update(self, player_hp: int, rooms: int, player_dmg: int, player_speed: int):
        self.player_hp = player_hp
        self.rooms = rooms
        self.player_damage = player_dmg
        self.player_speed = player_speed

    def draw(self):
        x = 10
        y = 10

        for i in range(self.player_hp):
            draw_texture(self.heart, x, y, RAYWHITE)
            if i == 10 or i == 21:
                x = 10
                y += 20
            else:
                x += 30
            
        draw_text(f"Rooms Cleared: {self.rooms}", 800, 35, 24, WHITE)
        draw_text(f"Damage: {self.player_damage}", 900, 65, 16, WHITE)
        draw_text(f"Speed: {self.player_speed}", 900, 95, 16, WHITE)
