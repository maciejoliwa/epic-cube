import typing as tp
from pyray import *

from entity import Player, Bullet, BulletDirection, Enemy, EnemyType, Item
from scene import Scene
from game import Game
from ui import UIManager, MovementDirection, MovingRectangle

def main() -> tp.NoReturn:
    init_window(1024, 576, "Epic Cube")
    
    player = Player(100, 100)
    game = Game()

    moving_rectangle = MovingRectangle()
    ui = UIManager(player._hp)

    bullets: tp.List[Bullet] = []
    enemies: tp.List[Enemy] = [Enemy(200, 200, EnemyType.CIRCLE, 1)]

    test_item = Item("Dead Sea Scrolls", 400, 300, 'items/item1.png')

    game.current_scene = Scene.load_random_map()
    
    set_target_fps(60)

    while not window_should_close():
        delta = get_frame_time()

        if is_key_pressed(KEY_L):
            moving_rectangle.move(MovementDirection.TO_RIGHT)
            game.current_scene = Scene.load_random_map()
        
        if is_key_pressed(KEY_J):
            moving_rectangle.move(MovementDirection.TO_LEFT)
            game.current_scene = Scene.load_random_map()

        if is_key_pressed(KEY_I):
            moving_rectangle.move(MovementDirection.TO_TOP)
            game.current_scene = Scene.load_random_map()

        if is_key_pressed(KEY_K):
            moving_rectangle.move(MovementDirection.TO_BOTTOM)
            game.current_scene = Scene.load_random_map()
        
        if is_key_pressed(KEY_RIGHT):
            bullets.append(Bullet(player.x, player.y, BulletDirection.RIGHT))

        if is_key_pressed(KEY_LEFT):
            bullets.append(Bullet(player.x, player.y, BulletDirection.LEFT))

        if is_key_pressed(KEY_DOWN):
            bullets.append(Bullet(player.x, player.y, BulletDirection.DOWN))

        if is_key_pressed(KEY_UP):
            bullets.append(Bullet(player.x, player.y, BulletDirection.UP))

        player.update(delta)
        moving_rectangle.update(delta)

        if len(enemies) > 0:
            for enemy in enemies:

                if check_collision_recs(
                    Rectangle(player.x, player.y, 32, 32),
                    Rectangle(enemy.x, enemy.y, 32, 32)
                ):
                    player.on_collision(enemy, None)

                enemy.update(delta)
        
        if check_collision_recs(
                    Rectangle(player.x, player.y, 32, 32),
                    Rectangle(test_item.x, test_item.y, 32, 32)
                ):
                    test_item.on_collision(player, None)
                    
        ui.update(player._hp)

        if len(bullets) > 0:
            for bullet in bullets:

                if bullet is not None:

                    if bullet.x > 1032:
                        bullets[bullets.index(bullet)] = None

                    if bullet.x < -8:
                        bullets[bullets.index(bullet)] = None

                    if bullet.y > 584:
                        bullets[bullets.index(bullet)] = None
                        
                    if bullet.y < -8:
                        bullets[bullets.index(bullet)] = None

                    bullet.update(delta)

        begin_drawing()
        clear_background(WHITE)

        game.current_scene.render()
        
        if len(enemies) > 0:
            for enemy in enemies:
                enemy.draw()

        if len(bullets) > 0:
            for bullet in bullets:
                if bullet is not None:
                    bullet.draw()

        test_item.draw()
        player.draw()

        moving_rectangle.draw()
        ui.draw()
        end_drawing()
    close_window()


if __name__ == '__main__':
    main()