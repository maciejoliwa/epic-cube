import typing as tp
from pyray import *

from entity import Player, Bullet, BulletDirection, Enemy, EnemyType, Item, AbstractEntity
from scene import Scene
from game import Game, GameState
from ui import UIManager, MovementDirection, MovingRectangle

def main() -> tp.NoReturn:
    init_window(1024, 576, "Epic Cube")

    init_audio_device()

    set_target_fps(60)
    
    # Musics
    pandora = load_music_stream('./music/pandora.mp3')
    play_music_stream(pandora)

    # Sounds
    shoot_wav = load_wave('./sounds/shoot.wav')
    shoot_snd = load_sound_from_wave(shoot_wav)

    enemy_hit_wav = load_wave('./sounds/enemy_hit.wav')
    enemy_hit_snd = load_sound_from_wave(enemy_hit_wav)

    _item_pickup_wav = load_wave('./sounds/item.wav')
    _item_pickup_snd = load_sound_from_wave(_item_pickup_wav)

    player = Player(100, 100)
    game = Game()

    moving_rectangle = MovingRectangle()
    ui = UIManager(player._hp)

    bullets: tp.List[Bullet] = []
    enemies: tp.List[Enemy] = [Enemy(200, 200, EnemyType.CIRCLE, 1)]

    test_item = Item("A Rock", 400, 300, 'items/item1.png')

    game.current_scene = Scene.load_random_map()
    

    while not window_should_close():
        update_music_stream(pandora)
        delta = get_frame_time()

        if is_key_pressed(KEY_M):
            game.current_scene = Scene.load_random_map()

        if is_key_pressed(KEY_RIGHT):
            play_sound(shoot_snd)
            bullets.append(Bullet(player.x + 16, player.y + 16, BulletDirection.RIGHT))

        if is_key_pressed(KEY_LEFT):
            play_sound(shoot_snd)
            bullets.append(Bullet(player.x + 16, player.y + 16, BulletDirection.LEFT))

        if is_key_pressed(KEY_DOWN):
            play_sound(shoot_snd)            
            bullets.append(Bullet(player.x + 16, player.y + 16, BulletDirection.DOWN))

        if is_key_pressed(KEY_UP):
            play_sound(shoot_snd)
            bullets.append(Bullet(player.x + 16, player.y + 16, BulletDirection.UP))

        player.update(delta)
        moving_rectangle.update(delta)

        if len(enemies) > 0:
            for enemy in enemies:

                for bullet in bullets:
                    if bullet is not None:

                        if AbstractEntity.entities_collided(bullet, enemy):
                            enemy.on_collision(bullet, None, player.damage)
                            bullets[bullets.index(bullet)] = None

                if AbstractEntity.entities_collided(player, enemy):
                    player.on_collision(enemy, None)

                enemy.update(delta)

        enemies = list(filter(lambda e: e.health > 0, enemies))
        
        if AbstractEntity.entities_collided(test_item, player):
            play_sound(_item_pickup_snd)
            test_item.on_collision(player, None)
                    
        ui.update(player._hp)

        for tile in game.current_scene.tiles:

            if AbstractEntity.entities_collided(player, tile):
                if len(enemies) == 0:  # Make sure there are no enemies left in the current room
                    if tile.name == 'teleport_up':
                        moving_rectangle.move(MovementDirection.TO_BOTTOM)
                        player.y = 540
                        game.current_scene = Scene.load_random_map()

                    elif tile.name == 'teleport_right':
                        moving_rectangle.move(MovementDirection.TO_LEFT)
                        player.x = 32
                        game.current_scene = Scene.load_random_map()

                    elif tile.name == 'teleport_left':
                        moving_rectangle.move(MovementDirection.TO_RIGHT)
                        player.x = 960
                        game.current_scene = Scene.load_random_map()

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