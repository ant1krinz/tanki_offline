import pygame
import sys
import os
import random
import time

clock = pygame.time.Clock()
pygame.init()
size = WIDTH, HEIGHT = 1050, 700
screen = pygame.display.set_mode(size)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
bushes_group = pygame.sprite.Group()
borders_group = pygame.sprite.Group()
shot_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_group2 = pygame.sprite.Group()
train_group = pygame.sprite.Group()
cars_group = pygame.sprite.Group()

FPS = 30

SCORE = 0

LVL = 1

font = pygame.font.SysFont("Arial", 30)


def show_lvl():
    global LVL
    lvl_text = font.render(f'Уровень {LVL}', 1, pygame.Color("white"))
    return lvl_text


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(f'FPS: {fps}', 1, pygame.Color("white"))
    return fps_text


def statistics():
    stata = font.render(f'Очки: {SCORE}', 1, pygame.Color("white"))
    return stata


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


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
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

def menu():
    screen.fill((255, 255, 255))
    fon = pygame.transform.scale(load_image('putin.jpg'), (WIDTH - 400, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    texts = ["В бой!", "Настройки", "Выход"]
    width = 5
    for i in range(3):
        text = font.render(texts[i], 1, (255, 255, 255))
        text_h = text.get_height()
        text_w = text.get_width()
        text_x = WIDTH // 1.2 - text.get_width() // 1.4
        text_y = (HEIGHT // 5) * i + text_h // 2 + HEIGHT // 5
        pygame.draw.rect(screen, (255, 0, 0), (text_x - 10 - width // 2, text_y - 10,
                                               text_w + 20 - width // 2, text_h + 20), 0)
        pygame.draw.rect(screen, (0, 0, 0), (text_x - 10 - width // 2, text_y - 10,
                                               text_w + 20 - width // 2, text_h + 20), width)
        screen.blit(text, (text_x, text_y))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


menu()


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
    'border': pygame.transform.scale(load_image('border.png'), (50, 50)),
    'relsi': pygame.transform.rotate(load_image('relsi.png'), 90),
    'train': pygame.transform.rotate(load_image('train.png'), 90),
    'car': pygame.transform.rotate(load_image('blue_car.png'), 90),
    'broke_relsi': pygame.transform.rotate(load_image('broken_relsi.png'), 90)
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
        self.health = 100
        self.type = tile_type


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.distinction = "w"

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
        if pygame.sprite.spritecollideany(self, borders_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, enemy_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, train_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, cars_group):
            self.rect = self.rect.move(-move[0], -move[1])


player = None


def generate_level(level):
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
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '!':
                Tile('relsi', x, y)
            elif level[y][x] == '*':
                Tile('train', x, y)
            elif level[y][x] == '$':
                Tile('car', x, y)
    return new_player, x, y


class Shot(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, parent):
        super().__init__(shot_group, all_sprites)
        self.image = pygame.transform.scale(shot_image, (20, 20))
        self.rect = self.image.get_rect().move(pos_x + 15, pos_y + 15)
        self.parent = parent

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

    def update(self, *args):
        global SCORE
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollide(self, walls_group, False):
            all_sprites.remove(self)
            shot_group.remove(self)

        if pygame.sprite.spritecollide(self, borders_group, False):
            all_sprites.remove(self)
            shot_group.remove(self)

        if self.parent == player:
            for sprite in pygame.sprite.spritecollide(self, enemy_group, False):
                all_sprites.remove(self)
                shot_group.remove(self)
                sprite.health -= 20
                if sprite.health == 0:
                    enemy_group.remove(sprite)
                    all_sprites.remove(sprite)
                    SCORE += 100
        else:
            enemy_group2.remove(self.parent)
            for sprite in pygame.sprite.spritecollide(self, enemy_group2, False):
                all_sprites.remove(self)
                shot_group.remove(self)
                sprite.health -= 20
                if sprite.health == 0:
                    enemy_group.remove(sprite)
                    all_sprites.remove(sprite)
                    SCORE += 100
            enemy_group2.add(self.parent)

        if pygame.sprite.spritecollideany(self, cars_group):
            pygame.sprite.spritecollideany(self, cars_group).health -= 25

            if pygame.sprite.spritecollideany(self, cars_group).health == 75:
                pygame.sprite.spritecollideany(self, cars_group).image = low_broke_car_image

            if pygame.sprite.spritecollideany(self, cars_group).health == 50:
                pygame.sprite.spritecollideany(self, cars_group).image = medium_broke_car_image

            if pygame.sprite.spritecollideany(self, cars_group).health == 25:
                pygame.sprite.spritecollideany(self, cars_group).image = hard_broke_car_image

            if pygame.sprite.spritecollideany(self, cars_group).health == 0:
                pygame.sprite.spritecollideany(self, cars_group).image = tile_images['empty']
                cars_group.remove(pygame.sprite.spritecollideany(self, cars_group))
            all_sprites.remove(self)
            shot_group.remove(self)

        if pygame.sprite.spritecollideany(self, walls_group):
            pygame.sprite.spritecollideany(self, walls_group).health -= 25

            if pygame.sprite.spritecollideany(self, walls_group).health == 75:
                pygame.sprite.spritecollideany(self, walls_group).image = low_broke_box_image

            if pygame.sprite.spritecollideany(self, walls_group).health == 50:
                pygame.sprite.spritecollideany(self, walls_group).image = medium_broke_box_image

            if pygame.sprite.spritecollideany(self, walls_group).health == 25:
                pygame.sprite.spritecollideany(self, walls_group).image = hard_broke_box_image

            if pygame.sprite.spritecollideany(self, walls_group).health == 0:
                pygame.sprite.spritecollideany(self, walls_group).image = tile_images['empty']
                walls_group.remove(pygame.sprite.spritecollideany(self, walls_group))

        if pygame.sprite.spritecollideany(self, train_group):
            pygame.sprite.spritecollideany(self, train_group).health -= 25

            if pygame.sprite.spritecollideany(self, train_group).health == 75:
                pygame.sprite.spritecollideany(self, train_group).image = low_broke_train_image

            if pygame.sprite.spritecollideany(self, train_group).health == 50:
                pygame.sprite.spritecollideany(self, train_group).image = medium_broke_train_image

            if pygame.sprite.spritecollideany(self, train_group).health == 25:
                pygame.sprite.spritecollideany(self, train_group).image = hard_broke_train_image

            if pygame.sprite.spritecollideany(self, train_group).health == 0:
                pygame.sprite.spritecollideany(self, train_group).image = tile_images['broke_relsi']
                train_group.remove(pygame.sprite.spritecollideany(self, train_group))
            all_sprites.remove(self)
            shot_group.remove(self)
def level():
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
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)
level()

def update_level():
    global SCORE, LVL, player, level_x, level_y
    if SCORE == 1000 and LVL == 1:
        all_sprites.empty()
        shot_group.empty()
        walls_group.empty()
        player_group.empty()
        borders_group.empty()
        tiles_group.empty()
        enemy_group.empty()
        bushes_group.empty()
        train_group.empty()
        cars_group.empty()
        player, level_x, level_y = generate_level(load_level("level2.txt"))
        for _ in range(10):
            Enemy()
        LVL = 2
        
level()


def bot_spawn(new_bot):
    x = random.randint(1, 14)
    y = random.randint(1, 8)
    new_bot.rect.x = tile_width * x
    new_bot.rect.y = tile_width * y
    if enemy_group:
        while pygame.sprite.spritecollideany(new_bot, walls_group) \
                or pygame.sprite.spritecollideany(new_bot, borders_group) \
                or pygame.sprite.spritecollideany(new_bot, player_group) \
                or pygame.sprite.spritecollideany(new_bot, enemy_group) \
                or pygame.sprite.spritecollideany(new_bot, train_group) \
                or pygame.sprite.spritecollideany(new_bot, cars_group):
            x = random.randint(8, 10)
            y = random.randint(2, 3)
            new_bot.rect.x = tile_width * x
            new_bot.rect.y = tile_width * y
    return x, y


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.image = enemy_image
        self.distinction = 's'
        bot_spawn(self)
        self.health = 60
        enemy_group.add(self)
        enemy_group2.add(self)

    def update(self):
        if self.distinction == 's':
            enemy_group2.remove(self)
            delta = (0, tile_width / 15)
            self.rect = self.rect.move(delta)
            if pygame.sprite.spritecollide(self, borders_group, False) or \
                    pygame.sprite.spritecollideany(self, walls_group) or \
                    pygame.sprite.spritecollideany(self, enemy_group2) or \
                    pygame.sprite.spritecollideany(self, player_group) or \
                    pygame.sprite.spritecollideany(self, train_group) or \
                    pygame.sprite.spritecollideany(self, cars_group):
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
                    pygame.sprite.spritecollideany(self, walls_group) or \
                    pygame.sprite.spritecollideany(self, enemy_group2) or \
                    pygame.sprite.spritecollideany(self, player_group) or \
                    pygame.sprite.spritecollideany(self, train_group) or \
                    pygame.sprite.spritecollideany(self, cars_group):
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
                    pygame.sprite.spritecollideany(self, walls_group) or \
                    pygame.sprite.spritecollideany(self, enemy_group2) or \
                    pygame.sprite.spritecollideany(self, player_group) or \
                    pygame.sprite.spritecollideany(self, train_group) or \
                    pygame.sprite.spritecollideany(self, cars_group):
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
                    pygame.sprite.spritecollideany(self, walls_group) or \
                    pygame.sprite.spritecollideany(self, enemy_group2) or \
                    pygame.sprite.spritecollideany(self, player_group) or \
                    pygame.sprite.spritecollideany(self, train_group) or \
                    pygame.sprite.spritecollideany(self, cars_group):
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
        res3 = random.randint(1, 100)
        if res3 == 1:
            Shot(self.rect.x, self.rect.y, self)

player, level_x, level_y = generate_level(load_level("level1.txt"))

for _ in range(10):
    Enemy()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if len(shot_group) < 3:
              shot = Shot(player.rect.x, player.rect.y, player)

    update_level()
    start_time = time.time()
    player.change_position()
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    player_group.draw(screen)
    shot_group.draw(screen)
    screen.blit(update_fps(), (880, 20))
    screen.blit(show_lvl(), (880, 60))
    screen.blit(statistics(), (880, 100))
    shot_group.update()
    walls_group.update()
    train_group.update()
    enemy_group.draw(screen)
    enemy_group.update()
    pygame.display.flip()
    clock.tick(FPS)