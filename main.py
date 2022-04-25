import typing as tp
from pyray import *

from functools import partial
from entity import Player, Bullet, BulletDirection, Enemy, EnemyType, Item, AbstractEntity
from scene import Scene
from game import Game, GameState
from ref import Reference
from ui import UIManager, MovementDirection, MovingRectangle
from random import randrange


def main() -> tp.NoReturn:
    init_window(1024, 576, "Epic Cube")

    _HEART_TEXTURE = load_texture('./textures/heart.png')
    _HALF_HEART_TEXTURE = load_texture('./texture/half_heart.png')
    _PLAYER_GLOW = load_texture('./textures/glow.png')
    _LOGO = load_texture('./textures/logo.png')

    init_audio_device()

    set_target_fps(60)

    # Musics
    pandora = load_music_stream('./music/pandora.mp3')
    set_music_pitch(pandora, 1.1)
    play_music_stream(pandora)

    # Sounds
    time_up_wav = load_wave('./sounds/time_up.wav')
    time_up_snd = load_sound_from_wave(time_up_wav)

    time_pass_wav = load_wave('./sounds/time_passes.wav')
    time_pass_snd = load_sound_from_wave(time_pass_wav)

    shoot_wav = load_wave('./sounds/shoot.wav')
    shoot_snd = load_sound_from_wave(shoot_wav)

    enemy_hit_wav = load_wave('./sounds/enemy_hit.wav')
    enemy_hit_snd = load_sound_from_wave(enemy_hit_wav)

    _item_pickup_wav = load_wave('./sounds/item.wav')
    _item_pickup_snd = load_sound_from_wave(_item_pickup_wav)

    player = Player(100, 100)
    game = Game()

    moving_rectangle = MovingRectangle()
    ui = UIManager(player._hp, _HEART_TEXTURE, _HALF_HEART_TEXTURE)

    bullets: tp.List[Bullet] = []
    enemies: tp.List[Enemy] = [Enemy(200, 200, EnemyType.CIRCLE, 1), Enemy(
        700, 300, EnemyType.CIRCLE, 1), Enemy(1000, 300, EnemyType.CIRCLE, 1)]

    # From there we shall pick items to put on the map
    items: tp.List[Item] = [
        Item("Ukulele", int(1024/2) - 16, int(576/2) - 16, 'items/ukulele.png'),
        Item("Straw Hat", int(1024/2) - 16,
             int(576/2) - 16, 'items/mugiwara.png'),
        Item("Butt Plug", int(1024/2) - 16, int(576/2) - 16, 'items/plug.png'),
    ]

    current_map_item = None  # Item currently on the map

    current_map_item = items[randrange(0, len(items))]

    game.current_scene = Scene.load_random_map()

    player_taken_damage = False

    # If there are 0 seconds left, the game ends (very sad)
    seconds_left = Reference(60)
    invisibility_frames = 15
    invisibility_frames_passed = 0
    frames_passed = 0  # We use that for the funny timer, every 60 frames_passed we decrease one second from the timer

    def increase_seconds(s: int) -> tp.NoReturn:
        play_sound(time_up_snd)
        seconds_left.set(seconds_left.get() + s)

    increase_seconds_by_five = partial(increase_seconds, 5)
    increase_seconds_by_ten = partial(increase_seconds, 10)

    while not window_should_close():
        frames_passed += 1

        # if game.state == GameState.GAME:

        if player_taken_damage:

            invisibility_frames_passed += 1

            if invisibility_frames_passed == invisibility_frames:
                player_taken_damage = False
                invisibility_frames_passed = 0

        if frames_passed == 60 and game.state == GameState.GAME:
            play_sound(time_pass_snd)

            if seconds_left.get() > 0:
                seconds_left.set(seconds_left.get() - 1)

            frames_passed = 0

        update_music_stream(pandora)
        delta = get_frame_time()

        if is_key_pressed(KEY_RIGHT):
            play_sound(shoot_snd)
            bullets.append(Bullet(player.x + 16, player.y +
                           16, BulletDirection.RIGHT))

        if is_key_pressed(KEY_LEFT):
            play_sound(shoot_snd)
            bullets.append(
                Bullet(player.x + 16, player.y + 16, BulletDirection.LEFT))

        if is_key_pressed(KEY_DOWN):
            play_sound(shoot_snd)
            bullets.append(
                Bullet(player.x + 16, player.y + 16, BulletDirection.DOWN))

        if is_key_pressed(KEY_UP):
            play_sound(shoot_snd)
            bullets.append(
                Bullet(player.x + 16, player.y + 16, BulletDirection.UP))

        player.update(delta)
        moving_rectangle.update(delta)

        if len(enemies) > 0:
            for enemy in enemies:

                for bullet in bullets:
                    if bullet is not None:

                        if AbstractEntity.entities_collided(bullet, enemy):
                            play_sound(enemy_hit_snd)
                            enemy.on_collision(
                                bullet, increase_seconds_by_five, player.damage)
                            bullets[bullets.index(bullet)] = None

                if AbstractEntity.entities_collided(player, enemy):
                    if not player_taken_damage:  # We check if the player has any invisibility frames left
                        player_taken_damage = True
                        player.on_collision(enemy, None)

                enemy.update(delta, player.x, player.y)

        enemies = list(filter(lambda e: e.health > 0, enemies))

        if current_map_item is not None and AbstractEntity.entities_collided(current_map_item, player):
            play_sound(_item_pickup_snd)
            current_map_item.on_collision(player, None)

            # Make sure you cannot get the same item twice
            items = list(filter(lambda i: i != current_map_item, items))

        ui.update(player._hp, seconds_left)

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

        if current_map_item is not None:
            current_map_item.draw()

        draw_texture(_PLAYER_GLOW, player.x - 34, player.y - 34, RAYWHITE)
        player.draw()

        moving_rectangle.draw()
        ui.draw()

        if game.state == GameState.MENU:
            draw_texture(_LOGO, int(1024/2) - 170, 25, RAYWHITE)

        end_drawing()

    close_window()


if __name__ == '__main__':
    main()
