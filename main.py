from copy import deepcopy, copy
import typing as tp
from pyray import *

from functools import partial

from raylib import FLAG_MSAA_4X_HINT
from entity import Player, Bullet, BulletDirection, Enemy, EnemyType, Item, AbstractEntity, EnemyBullet
from entity.heartdrop import HeartDrop
from scene import Scene, Tile
from game import Game, GameState
from ref import Reference
from ui import UIManager, MovementDirection, MovingRectangle
from random import randrange, randint



def main() -> tp.NoReturn:
    set_config_flags(FLAG_MSAA_4X_HINT)

    init_window(1024, 576, "Epic Cube")

    _HEART_TEXTURE = load_texture('./textures/heart.png')
    _HALF_HEART_TEXTURE = load_texture('./texture/half_heart.png')
    _PLAYER_GLOW = load_texture('./textures/glow.png')
    _LOGO = load_texture('./textures/logo.png')
    _VIGNETTE = load_texture('./textures/vignette.png')
    _EXPLOSION = load_texture('./textures/boom.png')
    _HEART_DROP_TEXTURE = load_texture('./textures/heart-drop.png')
    _CIRLCE_GLOW_TEXTURE = load_texture('./textures/circle-glow.png')
    _FOX_EARS = load_texture('./textures/fox-ears.png')
    _WINDOWS_UPDATE = load_texture('./textures/update.png')
    _SPACE_TEXTURE = load_texture('./textures/space.png')

    class FlashingText:
        
        text: str = ''
        frames_showing = 180
        frames_passed = 0
        showing = False

        def show(self):
            text_length = measure_text(self.text, 32)
            if self.showing:
                self.frames_passed += 1
                if self.frames_passed < self.frames_showing:
                    draw_text(self.text, int(1024/2) - int(text_length/2), 45, 32, WHITE)
                else:
                    self.frames_passed = 0
                    self.showing = False
                    
        def update_text(self, text: str):
            self.text = text

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

    class WindowsItemEffect:
        """
        A class that manages effects of picking up the windows item

        Effects:
            - Randomly, player's speed will be dropped to 0, making it impossible to move
            - A big ass windows update screen will be drawn on the top layer of the screen, covering the current room
            - It will be displayed for at most few seconds, it has to be annoying 
        """

        currently_displaying: bool = False
        seconds: int = 0
        frames = -1
        frames_to_pass = 0

        def draw(self) -> tp.NoReturn:
            if self.currently_displaying:
                draw_texture(_WINDOWS_UPDATE, 0, 0, RAYWHITE)

        def update(self) -> tp.NoReturn:
            if self.frames == self.frames_to_pass and self.currently_displaying:
                self.currently_displaying = False
                self.seconds = 0
                self.frames = -1

            if self.currently_displaying:
                self.frames += 1
    
            if not player_has_item('Windows'):  # We don't do anything if the player does not have the item
                return

            if not self.currently_displaying:
                r_number = randint(0, 10000)  # We get a random number between 0 and 100

                if r_number > 0 and r_number < 10: # If the random number is higher than 0 but lesser than 20, we display the windows update screen
                    self.seconds = randint(1, 3)  # Number of seconds the screen will be displayed for
                    self.currently_displaying = True
                    self.frames_to_pass = self.seconds * 60

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

    heart_pickup_wav = load_wave('./sounds/heartpickup.wav')
    heart_pickup_snd = load_sound_from_wave(heart_pickup_wav)

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
    hearts: tp.List[HeartDrop] = []

    ALL_GAME_ITEMS = [
        Item("Ukulele", int(1024/2) - 16, int(576/2) - 16, 'items/ukulele.png'),
        Item("Straw Hat", int(1024/2) - 16,int(576/2) - 16, 'items/mugiwara.png'),
        Item("Butt Plug", int(1024/2) - 16, int(576/2) - 16, 'items/plug.png'),
        Item("Black", int(1024/2) - 16, int(576/2) - 16, 'items/black.png'),
        Item("Fox's Tail", int(1024/2) - 16, int(576/2) - 16, 'items/fox-tail.png'),
        Item("Fox's Head", int(1024/2) - 16, int(576/2) - 16, 'items/fox-head.png'),
        Item("Fox's Leg", int(1024/2) - 16, int(576/2) - 16, 'items/fox-leg.png'),
        Item("C Programming Language", int(1024/2) - 16, int(576/2) - 16, 'items/c.png'),
        Item("JavaScript The Good Parts", int(1024/2) - 16, int(576/2) - 16, 'items/js.png'),
        Item("Skirt", int(1024/2) - 16, int(576/2) - 16, 'items/skirt.png'),
        Item("Vodka", int(1024/2) - 16, int(576/2) - 16, 'items/vodka.png'),
        Item("Windows", int(1024/2) - 16, int(576/2) - 16, 'items/windows.png'),  # by Patrycja
        ]

    # From there we shall pick items to put on the map
    # We perform a copying on each element to not remove items from the original array by the reference
    items: tp.List[Item] = [copy(i) for i in ALL_GAME_ITEMS]

    current_map_item = Reference(None)  # Item currently visible on the map

    windows_item = WindowsItemEffect()

    def randomize_enemy_type() -> EnemyType:
        r_number = randint(1, 30)

        if game.rooms_finished > 20 and game.rooms_finished <= 40:
            if r_number > 1 and r_number < 5:
                return EnemyType.CIRCLE
            if r_number > 5 and r_number < 10:
                return EnemyType.FOUR_DIRECTIONS_CIRCLE
            elif r_number > 10 and r_number < 15:
                return EnemyType.ESCAPING_TRIANGLE
            else:
                return EnemyType.TRIANGLE
        
        if r_number > 1 and r_number < 10:
            return EnemyType.CIRCLE
        elif r_number > 10 and r_number < 15:
            return EnemyType.ESCAPING_TRIANGLE
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

    invisibility_frames = 15
    flash_frames = 5
    flash_frames_passed = 5
    invisibility_frames_passed = 0
    frames_passed = 0  # We use that for the funny timer

    enemies_to_spawn = Reference(5)
    all_enemies_spawned = Reference(False)

    def player_has_item(item_name: str) -> bool:
        filtered_collected_items = list(filter(lambda i: i.name == item_name, game.collected_items))
        return (len(filtered_collected_items) >= 1)

    def spawn_enemies():
        r_number = randint(1, 3) * len(list(filter(lambda t: t.name == 'spawner' ,game.current_scene.tiles)))
        all_enemies_spawned.set(False)
        enemies_to_spawn.set(r_number)

    LOSE_SOUND_PLAYED_ONCE = False
    TEXT_SHOWING_OBJECT = FlashingText()

    def update_room_tiles(tile: Tile) -> Tile:
        if tile.name == 'floor':
            if game.rooms_finished > 20 and game.rooms_finished < 40:
                return Tile('floor_past_20', tile.x, tile.y, Color(100, 50, 50, 255))
            if game.rooms_finished > 40 and game.rooms_finished < 60:
                return Tile('floor_past_20', tile.x, tile.y, Color(112, 9, 53, 255))
            if game.rooms_finished > 60 and game.rooms_finished < 80:
                return Tile('floor_past_20', tile.x, tile.y, Color(195, 66, 36, 255))
            if game.rooms_finished > 80 and game.rooms_finished < 100:
                return Tile('floor_past_20', tile.x, tile.y, Color(0, 0, 0, 0))
        if tile.name == 'wall':
            if game.rooms_finished > 20 and game.rooms_finished < 40:
                return Tile('wall_past_20', tile.x, tile.y, Color(70, 40, 40, 255))
            if game.rooms_finished > 40 and game.rooms_finished < 60:  # Credits to Jula, very cool colours
                return Tile('floor_past_20', tile.x, tile.y, Color(80, 2, 23, 255))
            if game.rooms_finished > 60 and game.rooms_finished < 80:
                return Tile('floor_past_20', tile.x, tile.y, Color(150, 30, 20, 255))
            if game.rooms_finished > 80 and game.rooms_finished < 100:
                return Tile('floor_past_20', tile.x, tile.y, Color(0, 0, 0, 0))
        else:
                return tile

        return tile

    def update_scene():
        game.current_scene.tiles = list(map(update_room_tiles, game.current_scene.tiles))

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

        if frames_passed == 60:
            frames_passed = 0

        update_music_stream(pandora)
        delta = get_frame_time()

        windows_item.update()

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
                Bullet(player.x + 16, player.y, BulletDirection.DOWN))

        if is_key_pressed(KEY_UP):
            play_sound(shoot_snd)
            if player_has_item('Butt Plug'):
                bullets.append(Bullet(player.x, player.y, BulletDirection.UP))
                bullets.append(Bullet(player.x + 32, player.y, BulletDirection.UP))
            bullets.append(
                Bullet(player.x + 16, player.y, BulletDirection.UP))

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
                            enemy_bullets.append(EnemyBullet(enemy.x + 16, enemy.y + 4, BulletDirection.RIGHT))                        
                            enemy_bullets.append(EnemyBullet(enemy.x + 16, enemy.y + 4, BulletDirection.LEFT))                        
                            enemy_bullets.append(EnemyBullet(enemy.x, enemy.y + 8, BulletDirection.UP))

                    if enemy._type == EnemyType.ESCAPING_TRIANGLE:
                        if frames_passed == 20:
                            # Triangles fire bullets in three directions (up, left and right)
                            play_sound(enemy_shoot_snd)

                            if player.x < enemy.x:
                                enemy_bullets.append(EnemyBullet(enemy.x + 16, enemy.y + 4, BulletDirection.LEFT))                        
                            
                            if player.y < enemy.y:
                                enemy_bullets.append(EnemyBullet(enemy.x, enemy.y + 8, BulletDirection.UP))

                            if player.y > enemy.y:
                                enemy_bullets.append(EnemyBullet(enemy.x + 16, enemy.y + 4, BulletDirection.DOWN))

                            if player.x > enemy.x:
                                enemy_bullets.append(EnemyBullet(enemy.x + 16, enemy.y + 4, BulletDirection.RIGHT))                       

                    for bullet in bullets:
                        if bullet is not None:

                            if AbstractEntity.entities_collided(bullet, enemy, 16, 16):
                                play_sound(enemy_hit_snd)
                                enemy.on_collision(
                                    bullet, None, player.damage)
                                bullets[bullets.index(bullet)] = None

                                if enemy.health <= 0:
                                    play_sound(boom_snd)
                                    explosions.append(Explosion(enemy.x - 64, enemy.y - 64))
                                    # Spawn heart if rng hits right

                                    r_number = randint(1, 20)
                                    if r_number > 15:
                                        hearts.append(HeartDrop(enemy.x, enemy.y, _HEART_DROP_TEXTURE))

                    if AbstractEntity.entities_collided(player, enemy, 32, 32):
                        if not player_taken_damage:  # We check if the player has any invisibility frames left
                            player_taken_damage = True
                            flash_frames_passed = 0
                            play_sound(player_hurt_snd)
                            player.on_collision(enemy, None)

                    enemy.update(delta, player.x, player.y, enemies)

            enemies = list(filter(lambda e: e.health > 0, enemies))

        if current_map_item.get() is not None and AbstractEntity.entities_collided(current_map_item.get(), player, 32, 32):
            play_sound(_item_pickup_snd)
            current_map_item.get().on_collision(player, None)
            game.collected_items.append(current_map_item.get())

            if current_map_item.get().name == 'Butt Plug':
                TEXT_SHOWING_OBJECT.update_text('Triple Shot!')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == 'Straw Hat':
                TEXT_SHOWING_OBJECT.update_text('Speed Up + Health Up!')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == 'Black':
                TEXT_SHOWING_OBJECT.update_text('Speed Up + Health Down!')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == 'Ukulele':
                TEXT_SHOWING_OBJECT.update_text('Health Up + Damage Up!')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == 'C Programming Language':
                TEXT_SHOWING_OBJECT.update_text('Health Up + Speed Up + Damage Up!')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == 'JavaScript The Good Parts':
                TEXT_SHOWING_OBJECT.update_text('Small Health Up + Speed Down + Small Damage Up!')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == 'Skirt':
                TEXT_SHOWING_OBJECT.update_text('Health up + Speed up!')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == 'Vodka':
                TEXT_SHOWING_OBJECT.update_text('Health Down + Speed Down + Damage Up!')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == "Fox's Head":
                TEXT_SHOWING_OBJECT.update_text('Fox\'s Head...???')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == "Fox's Leg":
                TEXT_SHOWING_OBJECT.update_text('Fox\'s Leg...???')
                TEXT_SHOWING_OBJECT.showing = True
            
            if current_map_item.get().name == "Fox's Tail":
                TEXT_SHOWING_OBJECT.update_text('Fox\'s Tail...???')
                TEXT_SHOWING_OBJECT.showing = True

            if current_map_item.get().name == "Windows":
                TEXT_SHOWING_OBJECT.update_text('Random Freezes...')
                TEXT_SHOWING_OBJECT.showing = True

            # Make sure you cannot get the same item twice
            items = list(filter(lambda i: i != current_map_item.get(), items))

        ui.update(player._hp, game.rooms_finished, player.damage, player.speed)

        for tile in game.current_scene.tiles:

            if tile.name == 'spawner':
                if not all_enemies_spawned.get():
                    if frames_passed == 59:
                        enemies_to_spawn.set(enemies_to_spawn.get() - 1)
                        enemies.append(Enemy(tile.x, tile.y, randomize_enemy_type(), 1))

                        if enemies_to_spawn.get() == 0:
                            all_enemies_spawned.set(True)

            if AbstractEntity.entities_collided(player, tile, 32, 32):
                if tile.name == 'damage':
                    if not player_taken_damage:
                        player_taken_damage = True
                        play_sound(player_hurt_snd)
                        player._hp -= 1
                        flash_frames_passed = 0

                if len(enemies) == 0:  # Make sure there are no enemies left in the current room
                    if tile.name == 'teleport_up':
                        if game.rooms_finished == 20:
                            enemies.append(Enemy(int(1024/2), int(572/2), EnemyType.TRIANGLE_BOSS, 5))
                        
                        get_random_item()
                        moving_rectangle.move(MovementDirection.TO_BOTTOM)
                        player.y = 540
                        game.current_scene = Scene.load_random_map()
                        hearts = []
                        spawn_enemies()
                        bullets = []
                        current_map_item.set(None)
                        enemy_bullets = []
                        game.rooms_finished += 1
                        update_scene()

                    elif tile.name == 'teleport_right':
                        if game.rooms_finished == 20:
                            enemies.append(Enemy(int(1024/2), int(572/2), EnemyType.TRIANGLE_BOSS, 5))
                        
                        get_random_item()
                        moving_rectangle.move(MovementDirection.TO_LEFT)
                        player.x = 32
                        game.current_scene = Scene.load_random_map()
                        spawn_enemies()
                        bullets = []
                        enemy_bullets = []
                        current_map_item.set(None)
                        hearts = []
                        game.rooms_finished += 1
                        update_scene()


                    elif tile.name == 'teleport_left':
                        if game.rooms_finished == 20:
                            enemies.append(Enemy(int(1024/2), int(572/2), EnemyType.TRIANGLE_BOSS, 5))

                        current_map_item.set(None)                        
                        get_random_item()
                        moving_rectangle.move(MovementDirection.TO_RIGHT)
                        player.x = 960
                        game.current_scene = Scene.load_random_map()
                        spawn_enemies()
                        bullets = []
                        hearts = []
                        enemy_bullets = []
                        game.rooms_finished += 1
                        update_scene()

        if len(hearts) > 0:
            for heart in hearts:
                if heart is not None:

                    if AbstractEntity.entities_collided(heart, player, 8, 8):
                        heart.on_collision(player, None)
                        hearts[hearts.index(heart)] = None
                        play_sound(heart_pickup_snd)

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

                    if AbstractEntity.entities_collided(bullet, player, 8, 8):

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

        draw_texture(_SPACE_TEXTURE, 0, 0, RAYWHITE)
        game.current_scene.render()

        if len(enemies) > 0:
            for enemy in enemies:
                if enemy._type == EnemyType.CIRCLE:
                    draw_texture(_CIRLCE_GLOW_TEXTURE, enemy.x - 31, enemy.y - 33, RAYWHITE)
                enemy.draw()
            
        if len(hearts) > 0:
            for heart in hearts:
                if heart is not None:
                    heart.draw()

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

            if player_has_item("Fox's Leg") and player_has_item("Fox's Head") and player_has_item("Fox's Tail"):  # Add fox ears to the player if the player has collected all fox's items
                draw_rectangle(player.x, player.y, 32, 32, Color(255, 46, 0, 255))
                draw_texture(_FOX_EARS, player.x, player.y - 9, RAYWHITE)

        moving_rectangle.draw()

        draw_texture(_VIGNETTE, 0, 0, RAYWHITE)

        if flash_frames_passed <= flash_frames:
            draw_rectangle(0, 0, 1024, 576, Color(255, 0, 0, 100))
            flash_frames_passed+=1
        ui.draw()
        TEXT_SHOWING_OBJECT.show()
        
        windows_item.draw()

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
                frames_passed = 0
                player.reset_stats()
                items = []
                game.collected_items = []
                items = ALL_GAME_ITEMS.copy()
                hearts = []
                LOSE_SOUND_PLAYED_ONCE = False
                game.rooms_finished = 0

        if game.state == GameState.MENU:
            draw_texture(_LOGO, int(1024/2) - 170, 25, RAYWHITE)

        end_drawing()

    close_window()


if __name__ == '__main__':
    main()
