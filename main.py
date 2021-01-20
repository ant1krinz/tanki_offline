import math
import os
import random
import sqlite3
import sys
import time
import pygame
import pygame_gui

clock = pygame.time.Clock()
pygame.init()
size = WIDTH, HEIGHT = 1050, 700
screen = pygame.display.set_mode(size)

start_new_game = False

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
skulls_group = pygame.sprite.Group()
bushes_group = pygame.sprite.Group()
borders_group = pygame.sprite.Group()
borders_snow_group = pygame.sprite.Group()
shot_group = pygame.sprite.Group()
shot_group_player = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_group2 = pygame.sprite.Group()
train_group = pygame.sprite.Group()
cars_group = pygame.sprite.Group()
stone_group = pygame.sprite.Group()
sand_trains = pygame.sprite.Group()
kaktus_group = pygame.sprite.Group()
spawn_group = pygame.sprite.Group()

FPS = 31

SCORE = 0

ENEMIES_LEFT = 13

PLAYER_NAME = ''

LVL = 1

smaller_font = pygame.font.SysFont("Century Gothic", 24)
font = pygame.font.SysFont("Century Gothic", 30)
font_for_fps = pygame.font.SysFont('Century Gothic', 40)


def show_info():
    player_name = show_player_name()
    fps = update_fps()
    level_num = show_lvl()
    score_text = statistics()[0]
    score_amount = statistics()[1]
    lives = show_lives()
    res = show_hp()
    if res:
        hp1 = res[0]
        hp2 = res[1]
    left = show_enemies_left()

    screen.blit(fps, (925 - fps.get_width() // 2, 20))
    screen.blit(player_name, (925 - player_name.get_width() // 2, 80))
    screen.blit(level_num, (925 - level_num.get_width() // 2, 120))
    screen.blit(score_text, (925 - 1.5 * score_text.get_width() // 2, 160))
    screen.blit(score_amount, (925 - score_text.get_width() // 2 + 65, 160))
    screen.blit(lives, (925 - lives.get_width() // 2, 200))

    if player.health == 100:
        screen.blit(hp1, (925 - hp1.get_width() // 2 - hp2.get_width() // 2, 240))
        screen.blit(hp2, (925 - hp1.get_width() // 2 + hp2.get_width() * 2.5, 240))
    elif player.health == 50:
        screen.blit(hp1, (925 - hp1.get_width() // 2 - hp2.get_width() // 2, 240))
        screen.blit(hp2, (925 - hp1.get_width() // 2 + hp2.get_width() * 4.1, 240))

    screen.blit(left, (925 - left.get_width() // 2, 280))


def show_lives():
    lives_text = font.render(f'Жизни: {player.lives}', 1, pygame.Color("white"))
    return lives_text


def show_hp():
    hp_text1 = font.render(f'Здоровье: ', 1, pygame.Color("white"))
    hp_text2_red = font.render(f'{player.health}', 1, pygame.Color("#F55A46"))
    hp_text2_green = font.render(f'{player.health}', 1, pygame.Color("#2CE66D"))

    if player.health == 100:
        return (hp_text1, hp_text2_green)

    if player.health == 50:
        return (hp_text1, hp_text2_red)


def show_lvl():
    global LVL
    lvl_text = font.render(f'Уровень: {LVL}', 1, pygame.Color("white"))
    return lvl_text


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font_for_fps.render(f'FPS: {fps}', 1, pygame.Color("white"))
    return fps_text


def statistics():
    score1 = font.render(f'Очки: ', 1, pygame.Color("white"))
    score2 = font.render(f'{SCORE}', 1, pygame.Color("#FBEE73"))
    return (score1, score2)


def show_enemies_left():
    left = smaller_font.render(f'Врагов осталось: {ENEMIES_LEFT}', 1, pygame.Color("white"))
    return left


def show_player_name():
    name = smaller_font.render(PLAYER_NAME, 1, pygame.Color("#6EE2E6"))
    return name


def auto_spawn():
    global ENEMIES_LEFT
    necessary = 1300 * LVL - SCORE
    if ENEMIES_LEFT <= 5:
        if necessary > ENEMIES_LEFT * 100:
            Enemy()
            ENEMIES_LEFT += 1


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def respawn():
    player.health = 100
    delta_x = spawn_position[0] * tile_width - player.rect.x
    delta_y = spawn_position[1] * tile_width - player.rect.y
    player.rect = player.rect.move(delta_x, delta_y)


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    pygame.display.set_caption('Tanki Offline')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()


def level():
    global PLAYER_NAME, LVL
    db = sqlite3.connect("data/database.db")
    cur = db.cursor()
    result = cur.execute("""UPDATE players_and_levels SET level = ? WHERE name = ?""",
                         (LVL, PLAYER_NAME)).fetchall()
    db.commit()
    db.close()
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 50)
    text = font.render(f"УРОВЕНЬ {LVL}", True, (255, 255, 255))
    text_x = WIDTH // 2 - text.get_width() // 2
    text_y = HEIGHT // 2 - text.get_height()
    font2 = pygame.font.Font(None, 40)
    second_text = font2.render("НАЖМИТЕ ЛЮБУЮ КНОПКУ ЧТОБЫ НАЧАТЬ", True, (255, 255, 255))
    text_x2 = WIDTH // 4 - text.get_width() // 4
    text_y2 = HEIGHT // 1.8 - text.get_height() // 10
    screen.blit(text, (text_x, text_y))
    screen.blit(second_text, (text_x2, text_y2))
    playing = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def death_screen():
    global WIDTH, HEIGHT
    fon = pygame.transform.scale(load_image('death_screen.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    pygame.display.set_caption('Tanki Offline')

    font = pygame.font.Font(None, 57)
    text = font.render("ВЫ ПРОИГРАЛИ", True, pygame.Color('white'))
    text_x = WIDTH // 2 - text.get_width() // 2
    text_y = HEIGHT // 2 - text.get_height() // 2 * 14
    text_w = text.get_width()
    text_h = text.get_height()

    manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'data/theme.json')

    restart_play = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 105, HEIGHT // 2 - 30 * 6), (210, 70)),
        text='Начать заново',
        manager=manager
    )

    exit_game = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 105, HEIGHT // 2 - 30 * 3), (210, 70)),
        text='Выйти из игры',
        manager=manager
    )

    while True:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == exit_game:
                        exit_dialog = pygame_gui.windows.UIConfirmationDialog(
                            rect=pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 - 130), (300, 260)),
                            manager=manager,
                            window_title='Подтверждение',
                            action_long_desc='Вы уверены, что хотите выйти?',
                            action_short_name='Ok',
                            blocking=True
                        )
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == restart_play:
                        restart_game()
                        return

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    terminate()

            manager.process_events(event)

        manager.update(time_delta)
        screen.blit(fon, (0, 0))
        pygame.draw.rect(screen, pygame.Color('#251b11'), (text_x - 10, text_y - 10,
                                                           text_w + 20, text_h + 20))
        screen.blit(text, (text_x, text_y))
        manager.draw_ui(screen)
        pygame.display.update()


def nickname_window(new):
    global WIDTH, HEIGHT, PLAYER_NAME, SCORE, LVL, start_new_game
    fon = pygame.transform.scale(load_image('tanki_online.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    pygame.display.set_caption('Tanki Offline')

    manager = pygame_gui.UIManager((WIDTH, HEIGHT))

    text1 = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT // 2 - 30 * 6.7), (200, 40)),
        text='Введите имя', manager=manager)

    entry_name = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((WIDTH // 2 - 102, HEIGHT // 2 - 30 * 5.5), (205, 60)),
        manager=manager
    )

    play = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT // 2 - 30 * 4), (200, 40)),
        text='В бой!',
        manager=manager
    )

    back = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT // 2 - 30 * 2.5), (200, 40)),
        text='Назад',
        manager=manager
    )

    while True:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play:
                        db = sqlite3.connect('data/database.db')
                        cur = db.cursor()
                        if entry_name.text:
                            if len(entry_name.text) <= 10:
                                if new:
                                    res1 = cur.execute("""SELECT level FROM players_and_levels WHERE name = ?""",
                                                       (entry_name.text,)).fetchall()
                                    if not res1:
                                        result = cur.execute(
                                            """INSERT INTO players_and_levels(name,level) VALUES (?,?)""",
                                            (entry_name.text, 1)).fetchall()
                                        PLAYER_NAME = entry_name.text
                                        db.commit()
                                        db.close()
                                        start_new_game = True
                                        return
                                    else:
                                        message = pygame_gui.windows.UIMessageWindow(
                                            rect=pygame.Rect((WIDTH // 2 - 130, HEIGHT // 2 - 160), (260, 160)),
                                            html_message='Введённое имя уже существует!',
                                            window_title='Сообщение',
                                            manager=manager,
                                        )
                                        continue

                                else:
                                    result = cur.execute("""SELECT level FROM players_and_levels WHERE name = ?""",
                                                         (entry_name.text,)).fetchall()
                                    if result:
                                        SCORE = 1300 * (result[0][0] - 1)
                                        if result[0][0] == 1:
                                            LVL = result[0][0]
                                            start_new_game = True
                                        else:
                                            LVL = result[0][0] - 1
                                        PLAYER_NAME = entry_name.text
                                        db.commit()
                                        db.close()
                                        return
                                    else:
                                        message = pygame_gui.windows.UIMessageWindow(
                                            rect=pygame.Rect((WIDTH // 2 - 130, HEIGHT // 2 - 160), (260, 160)),
                                            html_message='Введённое имя не существует!',
                                            window_title='Сообщение',
                                            manager=manager,
                                        )
                                        continue

                            else:
                                message = pygame_gui.windows.UIMessageWindow(
                                    rect=pygame.Rect((WIDTH // 2 - 130, HEIGHT // 2 - 166), (260, 166)),
                                    html_message='Длина имени не может превышать 10 символов!',
                                    window_title='Сообщение',
                                    manager=manager,
                                )
                        else:
                            message = pygame_gui.windows.UIMessageWindow(
                                rect=pygame.Rect((WIDTH // 2 - 130, HEIGHT // 2 - 160), (260, 160)),
                                html_message='Вы не ввели имя!',
                                window_title='Сообщение',
                                manager=manager,
                            )

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == back:
                        main_menu()
                        return

            manager.process_events(event)

        screen.blit(fon, (0, 0))
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()


def main_menu():
    global WIDTH, HEIGHT
    fon = pygame.transform.scale(load_image('tanki_online.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    pygame.display.set_caption('Tanki Offline')

    manager = pygame_gui.UIManager((WIDTH, HEIGHT))

    start_play = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT // 2 - 30 * 6), (200, 60)),
        text='Начать игру',
        manager=manager
    )

    continue_play = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT // 2 - 30 * 3), (200, 60)),
        text='Продолжить игру',
        manager=manager
    )

    settings = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT // 2), (200, 60)),
        text='Настройки',
        manager=manager
    )

    exit_game = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT // 2 - 30 * -3), (200, 60)),
        text='Выйти из игры',
        manager=manager
    )

    while True:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_play:
                        nickname_window(True)
                        return

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == continue_play:
                        nickname_window(False)
                        return

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == settings:
                        pass

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == exit_game:
                        exit_dialog = pygame_gui.windows.UIConfirmationDialog(
                            rect=pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 - 130), (300, 260)),
                            manager=manager,
                            window_title='Подтверждение',
                            action_long_desc='Вы уверены, что хотите выйти?',
                            action_short_name='Ok',
                            blocking=True
                        )

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    terminate()

            manager.process_events(event)

        screen.blit(fon, (0, 0))

        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()


main_menu()


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('beton.png'),
    'bush': load_image('leaves.png'),
    'skull': load_image('skull.png'),
    'border': pygame.transform.scale(load_image('border.png'), (50, 50)),
    'relsi': pygame.transform.rotate(load_image('relsi.png'), 90),
    'train': pygame.transform.rotate(load_image('train.png'), 90),
    'car': pygame.transform.rotate(load_image('blue_car.png'), 90),
    'broke_relsi': pygame.transform.rotate(load_image('broken_relsi.png'), 90),
    'stone': load_image('kamni.png'),
    'sandy_train_main': pygame.transform.rotate(load_image('sand_train.png'), 90),
    'kaktus': load_image('cactus.png'),
    'spawn': load_image('flag.png')

}
low_broke_box_image = load_image('low_broke_box.png')
medium_broke_box_image = load_image('medium_broke_box.png')
hard_broke_box_image = load_image('hard_broke_box.png')

low_broke_train_image = pygame.transform.rotate(load_image('low_broke_train.png'), 90)
medium_broke_train_image = pygame.transform.rotate(load_image('medium_broke_train.png'), 90)
hard_broke_train_image = pygame.transform.rotate(load_image('hard_broke_train.png'), 90)

low_broke_car_image = pygame.transform.rotate(load_image('low_broke_car.png'), 90)
medium_broke_car_image = pygame.transform.rotate(load_image('medium_broke_car.png'), 90)
hard_broke_car_image = pygame.transform.rotate(load_image('hard_broke_car.png'), 90)

player_image = load_image('main_tank2.png')
shot_image = load_image('ammo3.png')

enemy_image = load_image('enemy_tank1.png')
low_broke_tank_image = load_image('low_broke_tank.png')
medium_broke_tank_image = load_image('medium_broke_tank.png')

low_broke_sand_train_image = pygame.transform.rotate(load_image('low_broke_sand_train.png'), 90)
medium_broke_sand_train_image = pygame.transform.rotate(load_image('medium_broke_sand_train.png'), 90)
hard_broke_sand_train_image = pygame.transform.rotate(load_image('hard_broke_sand_train.png'), 90)

broke_main_tank = load_image('broke_tank.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        if tile_type == 'wall':
            walls_group.add(self)
        if tile_type == 'bush':
            bushes_group.add(self)
        if tile_type == 'border':
            borders_group.add(self)
        if tile_type == 'train':
            train_group.add(self)
        if tile_type == 'car':
            cars_group.add(self)
        if tile_type == 'skull':
            skulls_group.add(self)
            self.distinction = 'w'
        if tile_type == 'stone':
            stone_group.add(self)
        if tile_type == 'sandy_train_main':
            sand_trains.add(self)
        if tile_type == 'kaktus':
            kaktus_group.add(self)
        if tile_type == 'spawn':
            spawn_group.add(self)
        self.health = 100
        self.type = tile_type


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.distinction = "w"
        self.health = 100
        self.lives = 2

    def change_position(self):
        move = (0, 0)

        if pygame.key.get_pressed()[pygame.K_w]:
            move = (0, -tile_width / 10)
            if self.distinction == "w":
                pass
            elif self.distinction == "s":
                self.image = pygame.transform.rotate(self.image, 180)
            elif self.distinction == "a":
                self.image = pygame.transform.rotate(self.image, 270)
            elif self.distinction == "d":
                self.image = pygame.transform.rotate(self.image, 90)
            self.distinction = "w"

        elif pygame.key.get_pressed()[pygame.K_s]:
            move = (0, tile_width / 10)
            if self.distinction == "w":
                self.image = pygame.transform.rotate(self.image, 180)
            elif self.distinction == "s":
                pass
            elif self.distinction == "a":
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.distinction == "d":
                self.image = pygame.transform.rotate(self.image, 270)
            self.distinction = "s"

        if pygame.key.get_pressed()[pygame.K_d]:
            move = (tile_width / 10, 0)
            if self.distinction == "w":
                self.image = pygame.transform.rotate(self.image, 270)
            elif self.distinction == "s":
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.distinction == "a":
                self.image = pygame.transform.rotate(self.image, 180)
            elif self.distinction == "d":
                pass
            self.distinction = "d"

        if pygame.key.get_pressed()[pygame.K_a]:
            move = (-tile_width / 10, 0)
            if self.distinction == "w":
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.distinction == "s":
                self.image = pygame.transform.rotate(self.image, 270)
            elif self.distinction == "a":
                pass
            elif self.distinction == "d":
                self.image = pygame.transform.rotate(self.image, 180)
            self.distinction = "a"

        self.rect = self.rect.move(move)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, kaktus_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, sand_trains):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, borders_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, borders_snow_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, enemy_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, train_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, cars_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, skulls_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, stone_group):
            self.rect = self.rect.move(-move[0], -move[1])


player = None

spawn_position = 0, 0


def load_snow_images():
    global low_broke_box_image, medium_broke_box_image, hard_broke_box_image, tile_images, low_broke_train_image, medium_broke_train_image, hard_broke_train_image
    low_broke_box_image = load_image('low_broke_box_snow.png')
    medium_broke_box_image = load_image('medium_broke_box_snow.png')
    hard_broke_box_image = load_image('hard_broke_box_snow.png')
    low_broke_train_image = pygame.transform.rotate(load_image('low_broke_snow_train.png'), 90)
    medium_broke_train_image = pygame.transform.rotate(load_image('medium_broke_snow_train.png'), 90)
    hard_broke_train_image = pygame.transform.rotate(load_image('hard_broke_snow_train.png'), 90)
    tile_images['empty'] = load_image('snow.png')
    tile_images['border'] = pygame.transform.scale(load_image('snow_border.png'), (50, 50))
    tile_images['wall'] = load_image('snow_box.png')
    tile_images['relsi'] = pygame.transform.rotate(load_image('snow_relsi.png'), 90)
    tile_images['broke_relsi'] = pygame.transform.rotate(load_image('broken_snow_relsi.png'), 90)
    tile_images['train'] = pygame.transform.rotate(load_image('snow_train.png'), 90)
    tile_images['car'] = pygame.transform.rotate(load_image('snow_car.png'), 90)
    tile_images['spawn'] = load_image('snow_flag.png')


def load_sand_images():
    global low_broke_box_image, medium_broke_box_image, hard_broke_box_image, tile_images, low_broke_train_image, \
        medium_broke_train_image, hard_broke_train_image, low_broke_car_image, \
        medium_broke_car_image, hard_broke_car_image
    low_broke_box_image = load_image('low_broke_box_sand.png')
    medium_broke_box_image = load_image('medium_broke_box_sand.png')
    hard_broke_box_image = load_image('hard_broke_box_sand.png')
    low_broke_train_image = pygame.transform.rotate(load_image('low_broke_sand_train_2part.png'), 90)
    medium_broke_train_image = pygame.transform.rotate(load_image('medium_broke_sand_train_2part.png'), 90)
    hard_broke_train_image = pygame.transform.rotate(load_image('hard_broke_sand_train_2part.png'), 90)
    low_broke_car_image = pygame.transform.rotate(load_image('low_broke_sand_car.png'), 90)
    medium_broke_car_image = pygame.transform.rotate(load_image('medium_broke_sand_car.png'), 90)
    hard_broke_car_image = pygame.transform.rotate(load_image('hard_broke_sand_car.png'), 90)
    tile_images['empty'] = pygame.transform.scale(load_image('sand.png'), (50, 50))
    tile_images['border'] = pygame.transform.scale(load_image('sand_border.png'), (50, 50))
    tile_images['wall'] = load_image('box.png')
    tile_images['relsi'] = pygame.transform.rotate(load_image('sand_relsi.png'), 90)
    tile_images['broke_relsi'] = pygame.transform.rotate(load_image('broken_sand_relsi.png'), 90)
    tile_images['train'] = pygame.transform.rotate(load_image('sand_train_2part.png'), 90)
    tile_images['car'] = pygame.transform.rotate(load_image('sand_car.png'), 90)
    tile_images['spawn'] = load_image('sand_flag.png')


def generate_level(level):
    global spawn_position
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == ',':
                Tile('bush', x, y)
            elif level[y][x] == '%':
                Tile('border', x, y)
            elif level[y][x] == '@':
                Tile('spawn', x, y)
                new_player = Player(x, y)
                spawn_position = x, y
            elif level[y][x] == '!':
                Tile('relsi', x, y)
            elif level[y][x] == '2':
                Tile('stone', x, y)
            elif level[y][x] == '*':
                Tile('train', x, y)
            elif level[y][x] == '$':
                Tile('car', x, y)
            elif level[y][x] == '&':
                Tile('skull', x, y)
            elif level[y][x] == '8':
                Tile('sandy_train_main', x, y)
            elif level[y][x] == '9':
                Tile('kaktus', x, y)
    return new_player, x, y


class Shot(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, parent):
        super().__init__(shot_group, all_sprites)
        self.image = pygame.transform.scale(shot_image, (20, 20))
        self.rect = self.image.get_rect().move(pos_x + 15, pos_y + 15)
        self.parent = parent

        if self.parent == player:
            shot_group_player.add(self)

        if self.parent.distinction == "w":
            self.vy = -10
            self.vx = 0

        elif self.parent.distinction == "a":
            self.vy = 0
            self.vx = -10

        elif self.parent.distinction == "d":
            self.vy = 0
            self.vx = 10

        elif self.parent.distinction == "s":
            self.vy = 10
            self.vx = 0

    def update(self):
        global SCORE, ENEMIES_LEFT
        self.rect = self.rect.move(self.vx, self.vy)

        if pygame.sprite.spritecollide(self, borders_group, False):
            all_sprites.remove(self)
            shot_group.remove(self)
            if self in shot_group_player:
                shot_group_player.remove(self)

        if self.parent == player:
            for sprite in pygame.sprite.spritecollide(self, enemy_group, False):
                all_sprites.remove(self)
                shot_group.remove(self)
                sprite.health -= 20
                if sprite.health == 0:
                    enemy_group.remove(sprite)
                    all_sprites.remove(sprite)
                    enemy_group2.remove(sprite)
                    SCORE += 100
                    ENEMIES_LEFT -= 1
                else:
                    change_enemy_image(sprite)
                if self in shot_group_player:
                    shot_group_player.remove(self)

        elif self.parent in enemy_group:
            enemy_group2.remove(self.parent)
            for sprite in pygame.sprite.spritecollide(self, enemy_group2, False):
                all_sprites.remove(self)
                shot_group.remove(self)
                sprite.health -= 20
                if sprite.health == 0:
                    enemy_group.remove(sprite)
                    enemy_group2.remove(sprite)
                    all_sprites.remove(sprite)
                    ENEMIES_LEFT -= 1
                else:
                    change_enemy_image(sprite)

            if pygame.sprite.spritecollideany(self, player_group):
                player.health -= 50
                if player.health == 0:
                    player.lives -= 1
                    if player.lives == 0:
                        death_screen()
                    if player.lives == 1:
                        respawn()
                shot_group.remove(self)
                all_sprites.remove(self)
            enemy_group2.add(self.parent)

        for car in pygame.sprite.spritecollide(self, cars_group, False):
            car.health -= 25

            if car.health == 75:
                car.image = low_broke_car_image

            if car.health == 50:
                car.image = medium_broke_car_image

            if car.health == 25:
                car.image = hard_broke_car_image

            if car.health == 0:
                x = car.rect.x / tile_width
                y = car.rect.y / tile_width
                Tile('empty', x, y)
                cars_group.remove(car)
                all_sprites.remove(car)

            all_sprites.remove(self)
            shot_group.remove(self)
            if self in shot_group_player:
                shot_group_player.remove(self)

        for wall in pygame.sprite.spritecollide(self, walls_group, False):
            wall.health -= 25

            if wall.health == 75:
                wall.image = low_broke_box_image

            if wall.health == 50:
                wall.image = medium_broke_box_image

            if wall.health == 25:
                wall.image = hard_broke_box_image

            if wall.health == 0:
                x = wall.rect.x / tile_width
                y = wall.rect.y / tile_width
                Tile('empty', x, y)
                walls_group.remove(wall)
                all_sprites.remove(wall)

            all_sprites.remove(self)
            shot_group.remove(self)
            if self in shot_group_player:
                shot_group_player.remove(self)

        for strain in pygame.sprite.spritecollide(self, sand_trains, False):
            strain.health -= 25

            if strain.health == 75:
                strain.image = low_broke_sand_train_image

            if strain.health == 50:
                strain.image = medium_broke_sand_train_image

            if strain.health == 25:
                strain.image = hard_broke_sand_train_image

            if strain.health == 0:
                x = strain.rect.x / tile_width
                y = strain.rect.y / tile_width
                Tile('broke_relsi', x, y)
                sand_trains.remove(strain)
                all_sprites.remove(strain)

            all_sprites.remove(self)
            shot_group.remove(self)
            if self in shot_group_player:
                shot_group_player.remove(self)

        for train in pygame.sprite.spritecollide(self, train_group, False):
            train.health -= 25
            if train.health == 75:
                train.image = low_broke_train_image

            if train.health == 50:
                train.image = medium_broke_train_image

            if train.health == 25:
                train.image = hard_broke_train_image

            if train.health == 0:
                x = train.rect.x / tile_width
                y = train.rect.y / tile_width
                Tile('broke_relsi', x, y)
                train_group.remove(train)
                all_sprites.remove(train)

            all_sprites.remove(self)
            shot_group.remove(self)
            if self in shot_group_player:
                shot_group_player.remove(self)

        for skull in pygame.sprite.spritecollide(self, skulls_group, False):
            skull.health -= 25
            if skull.health == 0:
                x = skull.rect.x / tile_width
                y = skull.rect.y / tile_width
                Tile('empty', x, y)
                skulls_group.remove(skull)
                all_sprites.remove(skull)
                distinctions = ["w", "a", "s", "d"]

                for i in range(1, 4):
                    Shot(skull.rect.x, skull.rect.y, skull)
                    skull.distinction = distinctions[i]
                Shot(skull.rect.x, skull.rect.y, skull)

                skull.distinction = 'w'

                for i in range(1, 4):
                    Shot(skull.rect.x, skull.rect.y, skull)
                    skull.distinction = distinctions[i]
                Shot(skull.rect.x, skull.rect.y, skull)

            all_sprites.remove(self)
            shot_group.remove(self)
            if self in shot_group_player:
                shot_group_player.remove(self)

        if pygame.sprite.spritecollideany(self, stone_group):
            all_sprites.remove(self)
            shot_group.remove(self)
            if self in shot_group_player:
                shot_group_player.remove(self)

        if pygame.sprite.spritecollideany(self, kaktus_group):
            all_sprites.remove(self)
            shot_group.remove(self)
            if self in shot_group_player:
                shot_group_player.remove(self)


def level():
    global PLAYER_NAME, LVL
    db = sqlite3.connect("data/database.db")
    cur = db.cursor()
    result = cur.execute("""UPDATE players_and_levels SET level = ? WHERE name = ?""",
                         (LVL, PLAYER_NAME)).fetchall()
    db.commit()
    db.close()
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 50)
    text = font.render(f"УРОВЕНЬ {LVL}", True, (255, 255, 255))
    text_x = WIDTH // 2 - text.get_width() // 2
    text_y = HEIGHT // 2 - text.get_height()
    font2 = pygame.font.Font(None, 40)
    second_text = font2.render("НАЖМИТЕ ЛЮБУЮ КНОПКУ ЧТОБЫ НАЧАТЬ", True, (255, 255, 255))
    text_x2 = WIDTH // 4 - text.get_width() // 4
    text_y2 = HEIGHT // 1.8 - text.get_height() // 10
    screen.blit(text, (text_x, text_y))
    screen.blit(second_text, (text_x2, text_y2))
    playing = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def restart_game():
    global SCORE, LVL, player, level_x, level_y, ENEMIES_LEFT
    clear_groups()
    if LVL == 1:
        SCORE = 0
    else:
        SCORE = (LVL - 1) * 1300
    ENEMIES_LEFT = 13
    player, level_x, level_y = generate_level(load_level("level{}.txt".format(LVL)))
    for _ in range(13):
        Enemy()
    level()


def update_level():
    global SCORE, LVL, player, level_x, level_y, ENEMIES_LEFT
    if SCORE / LVL == 1300:
        clear_groups()
        ENEMIES_LEFT = 13
        LVL += 1
        if LVL == 3:
            load_snow_images()
        if LVL == 5:
            load_sand_images()
        player, level_x, level_y = generate_level(load_level("level{}.txt".format(LVL)))
        for _ in range(13):
            Enemy()
        level()


def clear_groups():
    all_sprites.empty()
    shot_group.empty()
    shot_group_player.empty()
    walls_group.empty()
    sand_trains.empty()
    kaktus_group.empty()
    player_group.empty()
    borders_group.empty()
    borders_snow_group.empty()
    stone_group.empty()
    tiles_group.empty()
    enemy_group.empty()
    enemy_group2.empty()
    bushes_group.empty()
    train_group.empty()
    skulls_group.empty()
    cars_group.empty()


def bot_spawn(new_bot):
    x = random.randint(1, 14)
    y = random.randint(1, 8)
    new_bot.rect.x = tile_width * x
    new_bot.rect.y = tile_width * y
    while pygame.sprite.spritecollideany(new_bot, walls_group) \
            or pygame.sprite.spritecollideany(new_bot, borders_group) \
            or pygame.sprite.spritecollideany(new_bot, borders_snow_group) \
            or pygame.sprite.spritecollideany(new_bot, sand_trains) \
            or pygame.sprite.spritecollideany(new_bot, kaktus_group) \
            or pygame.sprite.spritecollideany(new_bot, stone_group) \
            or pygame.sprite.spritecollideany(new_bot, player_group) \
            or pygame.sprite.spritecollideany(new_bot, enemy_group) \
            or pygame.sprite.spritecollideany(new_bot, train_group) \
            or pygame.sprite.spritecollideany(new_bot, skulls_group) \
            or pygame.sprite.spritecollideany(new_bot, cars_group):
        x = random.randint(1, 14)
        y = random.randint(1, 8)
        new_bot.rect.x = tile_width * x
        new_bot.rect.y = tile_width * y


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.image = enemy_image
        self.distinction = 's'
        bot_spawn(self)
        self.health = 60
        self.follow = False
        enemy_group.add(self)
        enemy_group2.add(self)

    def update(self):
        distance = math.sqrt((player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2)
        if not self.follow:
            if self.distinction == 's':
                enemy_group2.remove(self)
                delta = (0, tile_width / 15)
                self.rect = self.rect.move(delta)
                if pygame.sprite.spritecollide(self, borders_group, False) or \
                        pygame.sprite.spritecollideany(self, borders_snow_group) or \
                        pygame.sprite.spritecollideany(self, stone_group) or \
                        pygame.sprite.spritecollideany(self, walls_group) or \
                        pygame.sprite.spritecollideany(self, kaktus_group) or \
                        pygame.sprite.spritecollideany(self, sand_trains) or \
                        pygame.sprite.spritecollideany(self, enemy_group2) or \
                        pygame.sprite.spritecollideany(self, player_group) or \
                        pygame.sprite.spritecollideany(self, train_group) or \
                        pygame.sprite.spritecollideany(self, skulls_group) or \
                        pygame.sprite.spritecollideany(self, cars_group) or \
                        pygame.sprite.spritecollideany(self, spawn_group):
                    self.rect = self.rect.move(-delta[0], -delta[1])
                    if self.distinction == "w":
                        self.image = pygame.transform.rotate(self.image, 90)
                    elif self.distinction == "s":
                        self.image = pygame.transform.rotate(self.image, 270)
                    elif self.distinction == "a":
                        pass
                    elif self.distinction == "d":
                        self.image = pygame.transform.rotate(self.image, 180)
                    self.distinction = "a"
                    res1 = random.randint(1, 2)
                    if res1 == 2:
                        res2 = random.randint(1, 2)
                        if res2 == 1:
                            self.image = pygame.transform.rotate(self.image, 270)
                            self.distinction = 'w'
                        elif res2 == 2:
                            self.image = pygame.transform.rotate(self.image, 180)
                            self.distinction = 'd'
                enemy_group2.add(self)
            elif self.distinction == 'a':
                delta = (-tile_width / 15, 0)
                enemy_group2.remove(self)
                self.rect = self.rect.move(delta)
                if pygame.sprite.spritecollideany(self, borders_group) or \
                        pygame.sprite.spritecollideany(self, borders_snow_group) or \
                        pygame.sprite.spritecollideany(self, stone_group) or \
                        pygame.sprite.spritecollideany(self, walls_group) or \
                        pygame.sprite.spritecollideany(self, kaktus_group) or \
                        pygame.sprite.spritecollideany(self, sand_trains) or \
                        pygame.sprite.spritecollideany(self, enemy_group2) or \
                        pygame.sprite.spritecollideany(self, player_group) or \
                        pygame.sprite.spritecollideany(self, train_group) or \
                        pygame.sprite.spritecollideany(self, skulls_group) or \
                        pygame.sprite.spritecollideany(self, cars_group) or \
                        pygame.sprite.spritecollideany(self, spawn_group):
                    self.rect = self.rect.move(-delta[0], -delta[1])
                    if self.distinction == "w":
                        self.image = pygame.transform.rotate(self.image, 270)
                    elif self.distinction == "s":
                        self.image = pygame.transform.rotate(self.image, 90)
                    elif self.distinction == "a":
                        self.image = pygame.transform.rotate(self.image, 180)
                    elif self.distinction == "d":
                        pass
                    self.distinction = "d"
                    res1 = random.randint(1, 2)
                    if res1 == 2:
                        res2 = random.randint(1, 2)
                        if res2 == 1:
                            self.image = pygame.transform.rotate(self.image, 90)
                            self.distinction = 'w'
                        elif res2 == 2:
                            self.image = pygame.transform.rotate(self.image, 270)
                            self.distinction = 's'
                enemy_group2.add(self)

            elif self.distinction == 'w':
                delta = (0, -tile_width / 15)
                enemy_group2.remove(self)
                self.rect = self.rect.move(delta)
                if pygame.sprite.spritecollideany(self, borders_group) or \
                        pygame.sprite.spritecollideany(self, borders_snow_group) or \
                        pygame.sprite.spritecollideany(self, stone_group) or \
                        pygame.sprite.spritecollideany(self, walls_group) or \
                        pygame.sprite.spritecollideany(self, kaktus_group) or \
                        pygame.sprite.spritecollideany(self, sand_trains) or \
                        pygame.sprite.spritecollideany(self, enemy_group2) or \
                        pygame.sprite.spritecollideany(self, player_group) or \
                        pygame.sprite.spritecollideany(self, train_group) or \
                        pygame.sprite.spritecollideany(self, skulls_group) or \
                        pygame.sprite.spritecollideany(self, cars_group) or \
                        pygame.sprite.spritecollideany(self, spawn_group):
                    self.rect = self.rect.move(-delta[0], -delta[1])
                    if self.distinction == "w":
                        self.image = pygame.transform.rotate(self.image, 180)
                    elif self.distinction == "s":
                        pass
                    elif self.distinction == "a":
                        self.image = pygame.transform.rotate(self.image, 90)
                    elif self.distinction == "d":
                        self.image = pygame.transform.rotate(self.image, 270)
                    self.distinction = "s"
                    res1 = random.randint(1, 2)
                    if res1 == 2:
                        res2 = random.randint(1, 2)
                        if res2 == 1:
                            self.image = pygame.transform.rotate(self.image, 90)
                            self.distinction = 'd'
                        elif res2 == 2:
                            self.image = pygame.transform.rotate(self.image, 270)
                            self.distinction = 'a'
                enemy_group2.add(self)

            elif self.distinction == 'd':
                delta = (tile_width / 15, 0)
                self.rect = self.rect.move(delta)
                enemy_group2.remove(self)
                if pygame.sprite.spritecollideany(self, borders_group) or \
                        pygame.sprite.spritecollideany(self, borders_snow_group) or \
                        pygame.sprite.spritecollideany(self, stone_group) or \
                        pygame.sprite.spritecollideany(self, walls_group) or \
                        pygame.sprite.spritecollideany(self, kaktus_group) or \
                        pygame.sprite.spritecollideany(self, sand_trains) or \
                        pygame.sprite.spritecollideany(self, enemy_group2) or \
                        pygame.sprite.spritecollideany(self, player_group) or \
                        pygame.sprite.spritecollideany(self, train_group) or \
                        pygame.sprite.spritecollideany(self, skulls_group) or \
                        pygame.sprite.spritecollideany(self, cars_group) or \
                        pygame.sprite.spritecollideany(self, spawn_group):
                    self.rect = self.rect.move(-delta[0], -delta[1])
                    if self.distinction == "w":
                        pass
                    elif self.distinction == "s":
                        self.image = pygame.transform.rotate(self.image, 180)
                    elif self.distinction == "a":
                        self.image = pygame.transform.rotate(self.image, 270)
                    elif self.distinction == "d":
                        self.image = pygame.transform.rotate(self.image, 90)
                    self.distinction = "w"
                    res1 = random.randint(1, 2)
                    if res1 == 2:
                        res2 = random.randint(1, 2)
                        if res2 == 1:
                            self.image = pygame.transform.rotate(self.image, 90)
                            self.distinction = 'a'
                        elif res2 == 2:
                            self.image = pygame.transform.rotate(self.image, 180)
                            self.distinction = 's'
                enemy_group2.add(self)
            res3 = random.randint(1, 80)
            if res3 == 1:
                Shot(self.rect.x, self.rect.y, self)


def change_enemy_image(enemy):
    hp = enemy.health
    dist = enemy.distinction
    if hp == 40:
        if dist == 'w':
            enemy.image = pygame.transform.rotate(low_broke_tank_image, 180)
        elif dist == 's':
            enemy.image = low_broke_tank_image
        elif dist == 'a':
            enemy.image = pygame.transform.rotate(low_broke_tank_image, 270)
        elif dist == 'd':
            enemy.image = pygame.transform.rotate(low_broke_tank_image, 90)

    elif hp == 20:
        if dist == 'w':
            enemy.image = pygame.transform.rotate(medium_broke_tank_image, 180)
        elif dist == 's':
            enemy.image = medium_broke_tank_image
        elif dist == 'a':
            enemy.image = pygame.transform.rotate(medium_broke_tank_image, 270)
        elif dist == 'd':
            enemy.image = pygame.transform.rotate(medium_broke_tank_image, 90)


if start_new_game:
    player, level_x, level_y = generate_level(load_level("level1.txt"))
    for _ in range(13):
        Enemy()
    level()

pygame.display.set_caption('Tanki Offline')

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if len(shot_group_player) < 1:
                shot = Shot(player.rect.x, player.rect.y, player)

    update_level()
    start_time = time.time()
    player.change_position()
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    show_info()
    player_group.draw(screen)
    shot_group.draw(screen)
    shot_group.update()
    walls_group.update()
    kaktus_group.update()
    sand_trains.update()
    train_group.update()
    skulls_group.update()
    enemy_group.draw(screen)
    enemy_group.update()
    pygame.display.flip()
    auto_spawn()
    clock.tick(FPS)
