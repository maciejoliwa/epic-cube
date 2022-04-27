from copy import deepcopy, copy
from multiprocessing.sharedctypes import Value
import typing as tp
from pyray import *

from functools import partial
from entity import Player, Bullet, BulletDirection, Enemy, EnemyType, Item, AbstractEntity, EnemyBullet
from scene import Scene
from game import Game, GameState
from ref import Reference
from ui import UIManager, MovementDirection, MovingRectangle
from random import randrange, randint



def main() -> tp.NoReturn:
    init_window(1024, 576, "Epic Cube")

    _HEART_TEXTURE = load_texture('./textures/heart.png')
    _HALF_HEART_TEXTURE = load_texture('./texture/half_heart.png')
    _PLAYER_GLOW = load_texture('./textures/glow.png')
    _LOGO = load_texture('./textures/logo.png')
    _VIGNETTE = load_texture('./textures/vignette.png')
    _EXPLOSION = load_texture('./textures/boom.png')

    class Explosion:

        texture_x = 0  # add 128
        texture_y = 0  # add 128 every 4 frames
        frame = 0
        frames_to_next_frame = 4
        frames_passed = 0

        def __init__(self, init_x, init_y) -> None:
            self.x = init_x
            self.y = init_y

        def update(self):
            if self.frame == 10:
                self.x = -500
                self.y = -500
                return

            self.frames_passed += 1
            if self.frames_passed == self.frames_to_next_frame:
                self.texture_x += 128
                if self.frame == 4 or self.frame == 8:
                    self.texture_y += 128
                    self.texture_x = 0
                
                self.frames_passed = 0
                self.frame += 1

        def draw(self):
            draw_texture_rec(_EXPLOSION, Rectangle(self.texture_x, self.texture_y, 128, 128), Vector2(self.x, self.y), RAYWHITE)


    init_audio_device()

    set_target_fps(60)

    # Musics
    pandora = load_music_stream('./music/p1.mp3')
    play_music_stream(pandora)
    set_music_pitch(pandora, 0.9)

    # Sounds
    boom_wav = load_wave('./sounds/boom.wav')
    boom_snd = load_sound_from_wave(boom_wav)

    time_up_wav = load_wave('./sounds/time_up.wav')
    time_up_snd = load_sound_from_wave(time_up_wav)

    enemy_shoot_wav = load_wave('./sounds/enemy_shoot.wav')
    enemy_shoot_snd = load_sound_from_wave(enemy_shoot_wav)

    time_pass_wav = load_wave('./sounds/time_passes.wav')
    time_pass_snd = load_sound_from_wave(time_pass_wav)

    shoot_wav = load_wave('./sounds/shoot.wav')
    shoot_snd = load_sound_from_wave(shoot_wav)

    enemy_hit_wav = load_wave('./sounds/enemy_hit.wav')
    enemy_hit_snd = load_sound_from_wave(enemy_hit_wav)

    player_hurt_wav = load_wave('./sounds/player_hurt.wav')
    player_hurt_snd = load_sound_from_wave(player_hurt_wav)

    lose_wav = load_wave('./sounds/lose.wav')
    lose_snd = load_sound_from_wave(lose_wav)

    _item_pickup_wav = load_wave('./sounds/item.wav')
    _item_pickup_snd = load_sound_from_wave(_item_pickup_wav)

    player = Player(100, 100)
    game = Game()

    moving_rectangle = MovingRectangle()
    ui = UIManager(player._hp, _HEART_TEXTURE, _HALF_HEART_TEXTURE)

    bullets: tp.List[Bullet] = []
    enemy_bullets: tp.List[EnemyBullet] = []
    enemies: tp.List[Enemy] = []
    explosions: tp.List[Explosion] = []

    ALL_GAME_ITEMS = [Item("Ukulele", int(1024/2) - 16, int(576/2) - 16, 'items/ukulele.png'),
        Item("Straw Hat", int(1024/2) - 16,
             int(576/2) - 16, 'items/mugiwara.png'),
        Item("Butt Plug", int(1024/2) - 16, int(576/2) - 16, 'items/plug.png'),
        Item("Black", int(1024/2) - 16, int(576/2) - 16, 'items/black.png'),]

    # From there we shall pick items to put on the map
    items: tp.List[Item] = [copy(i) for i in ALL_GAME_ITEMS]

    current_map_item = Reference(None)  # Item currently on the map

    def randomize_enemy_type() -> EnemyType:
        r_number = randint(1, 20)

        if r_number > 1 and r_number < 10:
            return EnemyType.CIRCLE
        else:
            return EnemyType.TRIANGLE
    
    def get_random_item():
        r_number = randint(0, 50)
        if r_number > 0 and r_number < 10:
            try:
                current_map_item.set(items[randrange(0, len(items))])
            except ValueError:
                current_map_item.set(copy(Item("Black", int(1024/2) - 16, int(576/2) - 16, 'items/black.png')))

    game.current_scene = Scene.load_random_map()

    player_taken_damage = False

    # If there are 0 seconds left, the game ends (very sad)
    seconds_left = Reference(60)
    invisibility_frames = 15
    flash_frames = 5
    flash_frames_passed = 5
    invisibility_frames_passed = 0
    frames_passed = 0  # We use that for the funny timer, every 60 frames_passed we decrease one second from the timer

    enemies_to_spawn = Reference(5)
    all_enemies_spawned = Reference(False)

    def player_has_item(item_name: str) -> bool:
        filtered_collected_items = list(filter(lambda i: i.name == item_name, game.collected_items))
        return (len(filtered_collected_items) >= 1)

    def spawn_enemies():
        r_number = randint(1, 5) * len(list(filter(lambda t: t.name == 'spawner' ,game.current_scene.tiles)))
        all_enemies_spawned.set(False)
        enemies_to_spawn.set(r_number)

    def increase_seconds(s: int) -> tp.NoReturn:
        play_sound(time_up_snd)
        seconds_left.set(seconds_left.get() + s)

    increase_seconds_by_five = partial(increase_seconds, 5)
    increase_seconds_by_ten = partial(increase_seconds, 10)

    LOSE_SOUND_PLAYED_ONCE = False

    while not window_should_close():
        if player._hp <= 0:
            if not LOSE_SOUND_PLAYED_ONCE:
                play_sound(lose_snd)
                LOSE_SOUND_PLAYED_ONCE = True
            game.state = GameState.GAME_OVER

        frames_passed += 1

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
            if player_has_item('Butt Plug'):
                bullets.append(Bullet(player.x + 16, player.y, BulletDirection.RIGHT))
                bullets.append(Bullet(player.x + 16, player.y +
                           32, BulletDirection.RIGHT))
            bullets.append(Bullet(player.x + 16, player.y +
                           16, BulletDirection.RIGHT))

        if is_key_pressed(KEY_LEFT):
            play_sound(shoot_snd)
            if player_has_item('Butt Plug'):
                bullets.append(Bullet(player.x + 16, player.y, BulletDirection.LEFT))
                bullets.append(Bullet(player.x + 16, player.y +
                           32, BulletDirection.LEFT))
            bullets.append(
                Bullet(player.x + 16, player.y + 16, BulletDirection.LEFT))
                
        if is_key_pressed(KEY_DOWN):
            play_sound(shoot_snd)
            if player_has_item('Butt Plug'):
                bullets.append(Bullet(player.x, player.y, BulletDirection.DOWN))
                bullets.append(Bullet(player.x + 32, player.y, BulletDirection.DOWN))
            bullets.append(
                Bullet(player.x + 16, player.y + 16, BulletDirection.DOWN))

        if is_key_pressed(KEY_UP):
            play_sound(shoot_snd)
            if player_has_item('Butt Plug'):
                bullets.append(Bullet(player.x, player.y, BulletDirection.UP))
                bullets.append(Bullet(player.x + 32, player.y, BulletDirection.UP))
            bullets.append(
                Bullet(player.x + 16, player.y + 16, BulletDirection.UP))

        player.update(delta)
        moving_rectangle.update(delta)

        if game.state == GameState.GAME:
            if len(explosions) > 0:
                for explosion in explosions:
                    if explosion is not None:
                        explosion.update()

                        if explosion.frame == 10:  # Animation has finished
                            explosions[explosions.index(explosion)] = None

            if len(enemies) > 0:
                for enemy in enemies:

                    if enemy._type == EnemyType.TRIANGLE:
                        if frames_passed == 59:
                            # Triangles fire bullets in three directions (up, left and right)
                            play_sound(enemy_shoot_snd)
                            enemy_bullets.append(EnemyBullet(enemy.x + 16, enemy.y + 16, BulletDirection.RIGHT))                        
                            enemy_bullets.append(EnemyBullet(enemy.x + 16, enemy.y + 16, BulletDirection.LEFT))                        
                            enemy_bullets.append(EnemyBullet(enemy.x + 16, enemy.y + 16, BulletDirection.UP))

                    for bullet in bullets:
                        if bullet is not None:

                            if AbstractEntity.entities_collided(bullet, enemy):
                                play_sound(enemy_hit_snd)
                                enemy.on_collision(
                                    bullet, increase_seconds_by_five, player.damage)
                                bullets[bullets.index(bullet)] = None

                                if enemy.health <= 0:
                                    play_sound(boom_snd)
                                    explosions.append(Explosion(enemy.x - 64, enemy.y - 64))

                    if AbstractEntity.entities_collided(player, enemy):
                        if not player_taken_damage:  # We check if the player has any invisibility frames left
                            player_taken_damage = True
                            flash_frames_passed = 0
                            play_sound(player_hurt_snd)
                            player.on_collision(enemy, None)

                    enemy.update(delta, player.x, player.y, enemies)

            enemies = list(filter(lambda e: e.health > 0, enemies))

        if current_map_item.get() is not None and AbstractEntity.entities_collided(current_map_item.get(), player):
            play_sound(_item_pickup_snd)
            current_map_item.get().on_collision(player, increase_seconds_by_ten)
            game.collected_items.append(current_map_item.get())

            # Make sure you cannot get the same item twice
            items = list(filter(lambda i: i != current_map_item.get(), items))

        ui.update(player._hp, seconds_left)

        for tile in game.current_scene.tiles:

            if tile.name == 'spawner':
                if not all_enemies_spawned.get():
                    if frames_passed == 59:
                        enemies_to_spawn.set(enemies_to_spawn.get() - 1)
                        enemies.append(Enemy(tile.x, tile.y, randomize_enemy_type(), 1))

                        if enemies_to_spawn.get() == 0:
                            all_enemies_spawned.set(True)

            if AbstractEntity.entities_collided(player, tile):
                if tile.name == 'damage':
                    if not player_taken_damage:
                        player_taken_damage = True
                        play_sound(player_hurt_snd)
                        player._hp -= 1
                        flash_frames_passed = 0

                if len(enemies) == 0:  # Make sure there are no enemies left in the current room
                    if tile.name == 'teleport_up':
                        get_random_item()
                        moving_rectangle.move(MovementDirection.TO_BOTTOM)
                        player.y = 540
                        game.current_scene = Scene.load_random_map()
                        spawn_enemies()
                        bullets = []
                        enemy_bullets = []

                    elif tile.name == 'teleport_right':
                        get_random_item()
                        moving_rectangle.move(MovementDirection.TO_LEFT)
                        player.x = 32
                        game.current_scene = Scene.load_random_map()
                        spawn_enemies()
                        bullets = []
                        enemy_bullets = []

                    elif tile.name == 'teleport_left':
                        get_random_item()
                        moving_rectangle.move(MovementDirection.TO_RIGHT)
                        player.x = 960
                        game.current_scene = Scene.load_random_map()
                        spawn_enemies()
                        bullets = []
                        enemy_bullets = []

        if len(enemy_bullets) > 0:
            for bullet in enemy_bullets:

                if bullet is not None:

                    # Remove bullets out of bounds
                    if bullet.x > 1032:
                        enemy_bullets[enemy_bullets.index(bullet)] = None

                    if bullet.x < -8:
                        enemy_bullets[enemy_bullets.index(bullet)] = None

                    if bullet.y > 584:
                        enemy_bullets[enemy_bullets.index(bullet)] = None

                    if bullet.y < -8:
                        enemy_bullets[enemy_bullets.index(bullet)] = None

                    bullet.update(delta)

                    if AbstractEntity.entities_collided(player, bullet):

                        if not player_taken_damage:  # We check if the player has any invisibility frames left
                            player_taken_damage = True
                            play_sound(player_hurt_snd)
                            player.on_collision(bullet, None)
                            flash_frames_passed = 0
                            if bullet in enemy_bullets:
                                enemy_bullets[enemy_bullets.index(bullet)] = None

        if len(bullets) > 0:
            for bullet in bullets:

                if bullet is not None:

                    # Remove bullets out of bounds
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

        if len(enemy_bullets) > 0:
            for bullet in enemy_bullets:
                if bullet is not None:
                    bullet.draw()

        if len(explosions) > 0:
            for explosion in explosions:
                if explosion is not None:
                    explosion.draw()

        if current_map_item.get() is not None:
            current_map_item.get().draw()

        if game.state == GameState.GAME:
            draw_texture(_PLAYER_GLOW, player.x - 34, player.y - 34, RAYWHITE)
            player.draw()

        moving_rectangle.draw()

        draw_texture(_VIGNETTE, 0, 0, RAYWHITE)

        if flash_frames_passed <= flash_frames:
            draw_rectangle(0, 0, 1024, 576, Color(255, 0, 0, 100))
            flash_frames_passed+=1
        ui.draw()

        if game.state == GameState.GAME_OVER:
            game_over_text_length = measure_text("GAME OVER", 32)
            replay_text_length = measure_text("Press 'r' to try again!", 16) 
            draw_text("GAME OVER", int(1024/2) - int(game_over_text_length/2), int(576/2), 32, RAYWHITE)
            draw_text("Press 'r' to try again!", int(1024/2) - int(replay_text_length/2), int(576/2) + 50, 16, RAYWHITE)

            enemies = []

            if is_key_pressed(KEY_R):
                # Reset the game
                game.current_scene = Scene.load_random_map()
                game.state = GameState.GAME
                seconds_left.set(60)
                frames_passed = 0
                player._hp = 6
                items = []
                game.collected_items = []
                items = ALL_GAME_ITEMS.copy()
                LOSE_SOUND_PLAYED_ONCE = False

        if game.state == GameState.MENU:
            draw_texture(_LOGO, int(1024/2) - 170, 25, RAYWHITE)

        end_drawing()

    close_window()


if __name__ == '__main__':
    main()
