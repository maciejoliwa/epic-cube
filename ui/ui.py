from dataclasses import dataclass
from pyray import draw_text, WHITE, BLACK

@dataclass
class UIManager:

    player_hp: int

    def update(self, player_hp: int):
        self.player_hp = player_hp

    def draw(self):
        draw_text(f"HP: {self.player_hp}/6", 25, 25, 32, BLACK)