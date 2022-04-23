from dataclasses import dataclass
from pyray import draw_text, WHITE, BLACK, measure_text

@dataclass
class UIManager:

    player_hp: int
    seconds_left: int = 60

    def update(self, player_hp: int, seconds_left: int):
        self.player_hp = player_hp
        self.seconds_left = seconds_left

    def draw(self):
        s_left_length = measure_text(f"Seconds Left: {self.seconds_left}", 32)

        draw_text(f"HP: {self.player_hp}/6", 25, 25, 32, BLACK)
        draw_text(f"Seconds Left: {self.seconds_left}", int(1024/2) - int(s_left_length/2), 25, 32, BLACK)