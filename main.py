import pygame as pg
import functions as func
from random import randint
import socket
import os

os.environ['SDL_VIDEO_WINDOW_POS'] = '450, 35'

# инициализация окна, шрифта, счётчика времени
pg.init()
size = WIDTH, HEIGHT = 300, 400
FPS = 60
fonts_lose = [pg.font.Font(None, 40), pg.font.Font(None, 35), pg.font.Font(None, 35), pg.font.Font(None, 35),
              pg.font.Font(None, 30)]
fonts_start = [pg.font.Font(None, 30), pg.font.Font(None, 20), pg.font.Font(None, 20), pg.font.Font(None, 20)]
clock = pg.time.Clock()
screen = pg.display.set_mode(size)
pg.display.set_caption('Doodle Jump')
player_img = [pg.transform.scale(func.load_image('doodler.png'), (90, 70)),
              pg.transform.scale(func.load_image('doodler_jump.png'), (90, 70))]
all_sprites = pg.sprite.Group()
all_tiles = pg.sprite.Group()
all_players = pg.sprite.Group()
max_score = 0
myhost = socket.gethostname()
with open("data/score.csv") as f:
    massive = f.readlines()
    for line in massive:
        name, score = line.split(';')
        if name == myhost:
            max_score = max(max_score, int(score))
running = True
lose_f = False
same_score_f = False


# инициализация класса игрока
class Player(pg.sprite.Sprite):
    # инициализация иконки игрока, его размеров и положения
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        # подгоняем картинку под размер игрока
        self.image = player_img[0]
        # выставляем размеры и позицию игрока
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        # задаём высоту прыжка
        self.jump_height = 20
        # горизонтальная скорость
        self.x_speed = 7
        # изменение высоты
        self.temp_y = 0
        # гравитацию
        self.gravity = 0.4
        # сторону движения
        self.side = 0
        # состояние прыжка
        self.jump = False
        #
        self.transformed = False


    # функция обновления положения игрока
    def update(self, side):
        # если игрок касается платформы, то прыгаем, изменяя временную высоту
        platform_collided = pg.sprite.spritecollideany(self, all_tiles)
        if platform_collided \
                and pg.sprite.collide_mask(self, platform_collided) \
                and 1 <= (self.get_y() + self.rect.height) - platform_collided.rect.y <= 15 \
                and not self.jump:
            # изменяем временную высоту
            self.temp_y = -10
            self.jump = True
            self.frame = 1
        # изменяем высоту
        self.rect.y += self.temp_y
        # изменяем времменую высоту, прибавляя гравитацию
        self.temp_y += self.gravity
        # если временная высоту больше нуля, то игрок не в прыжке
        if self.temp_y >= 0:
            self.jump = False
        # определяем сторону движения
        if side is not None:
            self.side = side
        # по стороне движения двигаем персонажа
        self.rect.x += self.x_speed * self.side
        if self.side == -1:
            if self.jump:
                self.image = pg.transform.flip(pg.transform.scale(player_img[1], (90, 70)), True, False)
            else:
                self.image = pg.transform.flip(pg.transform.scale(player_img[0], (90, 70)), True, False)
            self.transformed = True
        elif self.side == 1:
            if self.jump:
                self.image = player_img[1]
            else:
                self.image = player_img[0]
            self.transformed = False
        else:
            if self.transformed:
                if self.jump:
                    self.image = pg.transform.flip(pg.transform.scale(player_img[1], (90, 70)), True, False)
                else:
                    self.image = pg.transform.flip(pg.transform.scale(player_img[0], (90, 70)), True, False)
            else:
                if self.jump:
                    self.image = player_img[1]
                else:
                    self.image = player_img[0]


    def get_y(self):
        return self.rect.y

    def get_x(self):
        return self.rect.x

    def set_x(self, x):
        self.rect.x = x

    def set_y(self, y):
        self.rect.y = y


# инициализация класса платформы
class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, moveable = 0, breakable = 0, groups=[all_tiles, all_sprites]):
        super().__init__(groups)
        self.image = pg.Surface((60, 10))
        pg.draw.rect(self.image, 'black', (0, 0, 60, 10))
        self.rect = pg.Rect(x, y, 60, 10)
        if moveable == 0:
            self.moveable = True if randint(0, 10) == 1 else False
        else:
            self.moveable = False
        if breakable == 0:
            self.breakable = True if randint(0, 20) == 1 else False
        else:
            self.breakable = False
        if self. moveable:
            self.x_speed = -1 if randint(0, 10) in (1, 2, 3, 4, 5) else 1
            self.borders = (self.rect.x - 200 if self.rect.x - 200 >= 60 else 60,
                            self.rect.x + 200 if self.rect.x + 200 <= HEIGHT - 60 else HEIGHT - 60)
        if self.breakable:
            pg.draw.rect(self.image, 'red', (0, 0, 60, 10))

    def update(self):
        #
        if self.moveable:
            self.rect.x += self.x_speed
            #
            if self.rect.x <= self.borders[0]:
                self.x_speed = 1
            elif self.rect.x >= self.borders[1]:
                self.x_speed = -1
        if self.breakable:
            if pg.sprite.spritecollideany(self, all_players):
                self.kill()


def generate_platforms():
    Platform(175, 580, moveable=1, breakable=1)
    for i in range(20):
        Platform(randint(0, WIDTH - 40), 580 - (50 * (i + 1)))


def kill_platforms():
    for tile in all_tiles:
        tile.kill()


def kill_player():
    for pl in all_players:
        pl.kill()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.max_y = -1
        self.dy = 0
        self.score = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target, lose_f):
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
        if self.dy < 0:
            self.dy = 0
        elif lose_f:
            self.dy = -10000
        else:
            self.score += self.dy

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score


def draw_grid(blocksize=50):
    blockSize = blocksize
    for x in range(0, WIDTH, blockSize):
        for y in range(0, HEIGHT, blockSize):
            rect = pg.Rect(x, y, blockSize, blockSize)
            pg.draw.rect(screen, 'black', rect, 1)


camera = Camera()
player = Player(170, 300, all_sprites, all_players)
running_start_screen = True
while running_start_screen:
    tick = clock.tick(FPS)
    Platform(175, 380, moveable=1, breakable=1)

    screen.fill('white')
    draw_grid()
    camera.update(player, lose_f)

    for sprite in all_sprites:
        camera.apply(sprite)

    all_players.update(None)
    all_players.draw(screen)
    all_tiles.draw(screen)

    texts = ['Doodle Jump', 'Нажмите любую клавишу для старта', f'Ваш лучший рекорд:{max_score}']
    text_coord = 10
    font = 0
    for line in texts:
        string_rendered = fonts_start[font].render(line, True, 'red')
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        font += 1
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            running_start_screen = False
        if event.type == pg.QUIT:
            running_start_screen = False
            # заканчиваем программу
            func.terminate()

    pg.display.flip()

kill_player()
kill_platforms()
WIDTH, HEIGHT = 550, 700
size = WIDTH, HEIGHT
pg.display.set_mode(size)
player = Player(170, 500, all_sprites, all_players)
camera = Camera()
generate_platforms()
# игровой цикл
while running:
    # единица времени
    tick = clock.tick(FPS)

    # сторона прыжка (лево или право)
    side = None
    # последняя платформа
    last_tile = None
    # заполняем экран белым и отрисовываем все спрайты
    screen.fill('white')
    draw_grid()
    if not lose_f:
        all_sprites.draw(screen)

    # обновляем положение камеры
    camera.update(player, lose_f)
    # пробегаемя по платформам и решаем, убивать конкретную платформу или создать новую

    for tile in all_tiles:
        if tile.rect.y >= HEIGHT:
            tile.kill()
        last_tile = tile
    if last_tile.rect.y > 50:
        x, y = randint(0, WIDTH - 60), -randint(0, 5)
        Platform(x, y)
        if all_tiles.sprites()[-1].breakable:
            x1 = randint(0, WIDTH - 60)
            while x < x1 < x + 60 or x - 60 < x1 < x:
                x1 = randint(0, WIDTH - 60)
            Platform(x1, y, moveable=all_tiles.sprites()[-1].moveable, breakable=1,
                     groups=all_tiles.sprites()[-1].groups())

    # передвигаем все спрайты относительно игрока при помощи камеры
    for sprite in all_sprites:
        camera.apply(sprite)

    max_score = max(max_score, camera.get_score())
    text = str(camera.get_score())
    score_rendered = fonts_lose[-1].render(text, True, 'blue')
    screen.blit(score_rendered, (5, 5))

    # пробегаемся по событиям
    for event in pg.event.get():
        # если выход, то завершаем цикл и записываем рекорд
        if event.type == pg.QUIT:
            # останавливаем цикл
            runnning = False
            with open('data/score.csv') as f:
                name, score = f.readlines()[-1].split(';')
                if name == myhost and int(score) == max_score:
                    same_score_f = True
            if not same_score_f:
                with open('data/score.csv', 'a') as f:
                    f.write(f'{myhost};{max_score}\n')
                # заканчиваем программу
            func.terminate()
        # если кнопка нажата, то выбираем сторону движения
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_d, pg.K_RIGHT):
                side = 1
            elif event.key in (pg.K_a, pg.K_LEFT):
                side = -1
            if lose_f:
                camera.set_score(0)
                kill_platforms()
                lose_f = False
                player.set_y(500)
                player.set_x(170)
                player.temp_y = 0
                generate_platforms()
        # если кнопка отжата, то приравниваем сторону к нулю
        if event.type == pg.KEYUP:
            if event.key in (pg.K_d, pg.K_RIGHT):
                side = 0
            elif event.key in (pg.K_a, pg.K_LEFT):
                side = 0

    # передвигаем игрока в сторону и передвигаем платформы
    player.update(side)
    all_tiles.update()

    if player.get_x() > WIDTH - 45:
        player.set_x(-45)

    elif player.get_x() < -45:
        player.set_x(WIDTH - 45)

    if player.get_y() - player.rect.height > HEIGHT:
        texts = ['Вы проиграли!', 'Нажмите любую клавишу для перезапуска', f'Ваш рекорд:{camera.get_score()}',
                 f'Лучший рекорд:{max_score}']
        text_coord = 220
        font = 0
        for line in texts:
            string_rendered = fonts_lose[font].render(line, True, 'red')
            intro_rect = string_rendered.get_rect()
            text_coord += 30
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
            font += 1
        lose_f = True

    # обновляем кадh
    pg.display.flip()
