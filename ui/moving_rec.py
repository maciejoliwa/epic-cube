from enum import IntEnum
from pyray import draw_rectangle, BLACK, RED
import typing as tp

class MovementDirection(IntEnum):

    TO_LEFT = 0
    TO_TOP = 1
    TO_RIGHT = 2
    TO_BOTTOM = 3


# A rectangle that creates a transition between rooms
class MovingRectangle:
    
    x = -1024
    y = 0
    width = 1024
    height = 576
    speed = 5000.0
    current_direction: MovementDirection = None

    def update(self, delta: float) -> tp.NoReturn:
        if self.current_direction != None:
            if self.current_direction == MovementDirection.TO_RIGHT:
                if self.x <= 1024:
                    self.x += int(self.speed * delta)

            if self.current_direction == MovementDirection.TO_LEFT:
                if self.x > -1024:
                    self.x -= int(self.speed * delta)

            if self.current_direction == MovementDirection.TO_TOP:
                if self.y > -576:
                    self.y -= int(self.speed * delta)

            if self.current_direction == MovementDirection.TO_BOTTOM:
                if self.y < 576:
                    self.y += int(self.speed * delta)

    def move(self, movement_direction: MovementDirection) -> tp.NoReturn:
        self.current_direction = movement_direction

        if self.current_direction == MovementDirection.TO_RIGHT:
            self.x = -1024
            self.y = 0
        
        if self.current_direction == MovementDirection.TO_LEFT:
            self.x = 1024
            self.y = 0

        if self.current_direction == MovementDirection.TO_TOP:
            self.x = 0
            self.y = 576

        if self.current_direction == MovementDirection.TO_BOTTOM:
            self.x = 0
            self.y = -576

    def draw(self) -> tp.NoReturn:
        draw_rectangle(self.x, self.y, self.width, self.height, BLACK)