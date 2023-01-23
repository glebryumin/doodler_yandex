import pygame as pg
import functions as func
from random import randint

# инициализация окна, шрифта, счётчика времени
pg.init()
size = WIDTH, HEIGHT = 400, 500
FPS = 60
fonts = [pg.font.Font(None, 30), pg.font.Font(None, 25), pg.font.Font(None, 20)]
clock = pg.time.Clock()
screen = pg.display.set_mode(size)
pg.display.set_caption('Doodle Jump')
player_img = func.load_image('doodler.png')
all_sprites = pg.sprite.Group()
all_tiles = pg.sprite.Group()
running = True
lose_f = False


# инициализация класса игрока
class Player(pg.sprite.Sprite):
    # инициализация иконки игрока, его размеров и положения
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        # подгоняем картинку под размер игрока
        self.image = pg.transform.scale(player_img, (90, 70))
        # выставляем размеры и позицию игрока
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.width -= 20
        # задаём высоту прыжка
        self.jump_height = 20
        # горизонтальная скорость
        self.x_speed = 5
        # изменение высоты
        self.temp_y = 0
        # гравитацию
        self.gravity = 0.4
        # сторону движения
        self.side = None
        # состояние прыжка
        self.jump = False

    # функция обновления положения игрока
    def update(self, side):
        # если игрок касается платформы, то прыгаем, изменяя временную высоту
        if pg.sprite.spritecollideany(self, all_tiles) and not self.jump:
            # изменяем временную высоту
            self.temp_y = -10
            self.jump = True
        # изменяем высоту
        self.rect.y += self.temp_y
        # изменяем времменую высоту, прибавляя гравитацию
        self.temp_y += self.gravity
        # если временная высоту больше нуля, то игрок не в прыжке
        if self.temp_y >= 0:
            self.jump = False
        # определяем сторону движения
        self.side = side if side is not None else self.side
        # по стороне движения двигаем персонажа
        if side == 0:
            self.rect.x += 0
        elif self.side == 'left':
            self.rect.x -= self.x_speed
            self.image = pg.transform.flip(pg.transform.scale(player_img, (90, 70)), True, False)
        elif self.side == 'right':
            self.rect.x += self.x_speed
            self.image = pg.transform.scale(player_img, (90, 70))


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
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = pg.Surface((60, 10))
        pg.draw.rect(self.image, 'black', (0, 0, 60, 10))
        self.rect = pg.Rect(x, y, 60, 10)
        self.moveable = True if randint(0, 10) == 1 else False
        self.x_speed = 0.2
        self.borders = (self.rect.x - 100 if self.rect.x - 100 > 60 else 60,
                        self.rect.x + 100 if self.rect.x + 100 < HEIGHT - 60 else HEIGHT - 60)

    def update(self):
        if self.moveable:
            self.rect.x += self.x_speed
            if self.rect.x <= self.borders[0] + 60:
                self.x_speed = -0.2
            elif self.rect.x >= self.borders[1]:
                self.x_speed = 0.2


def generate_platforms():
    Platform(175, 480, all_tiles, all_sprites)
    for i in range(10):
        Platform(randint(0, WIDTH - 40), 480 - (100 * (i + 1)), all_tiles, all_sprites)


def kill_platforms():
    for tile in all_tiles:
        tile.kill()


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
    def update(self, target):
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
        if self.dy < 0:
            self.dy = 0
        self.score += self.dy

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score


player = Player(170, 400, all_sprites)
generate_platforms()
camera = Camera()
# игровой цикл
while running:
    # единица времени
    tick = clock.tick(FPS)
    # сторона прыжка (лево или право)
    side = None

    last_tile = None
    # заполняем экран белым и отрисовываем все спрайты
    screen.fill('white')
    all_sprites.draw(screen)
    # обновляем положение камеры
    camera.update(player)
    # пробегаемя по платформам и решаем, убивать конкретную платформу или создать новую

    for tile in all_tiles:
        if tile.rect.y >= HEIGHT:
            tile.kill()
        last_tile = tile
    if last_tile.rect.y > 50:
        Platform(randint(0, WIDTH - 60), -randint(10, 50), all_tiles, all_sprites)

    # передвигаем все спрайты относительно игрока при помощи камеры
    for sprite in all_sprites:
        camera.apply(sprite)

    text = str(camera.get_score())
    score_rendered = fonts[-1].render(text, True, 'black')
    screen.blit(score_rendered, (5, 5))

    # пробегаемся по событиям
    for event in pg.event.get():
        # если выход, то завершаем цикл
        if event.type == pg.QUIT:
            runnning = False
            # заканчиваем программу
            func.terminate()
        # если кнопка нажата, то выбираем сторону движения
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_d, pg.K_RIGHT):
                side = 'right'
            elif event.key in (pg.K_a, pg.K_LEFT):
                side = 'left'
            if lose_f:
                camera.set_score(0)
                kill_platforms()
                lose_f = False
                player.set_y(480)
                player.set_x(170)
                generate_platforms()
        # если кнопка отжата, то приравниваем сторону к нулю
        if event.type == pg.KEYUP:
            if event.key in (pg.K_d, pg.K_RIGHT):
                side = 0
            elif event.key in (pg.K_a, pg.K_LEFT):
                side = 0

    # передвигаем игрока в сторону
    player.update(side)

    all_tiles.update()

    if player.get_x() > WIDTH + 45:
        player.set_x(-45)

    elif player.get_x() < - 45:
        player.set_x(WIDTH)

    if player.get_y() - player.rect.height > HEIGHT:
        texts = ['Вы проиграли!', 'Нажмите любую клавищу для перезапуска']
        text_coord = 250
        font = 0
        for line in texts:
            string_rendered = fonts[font].render(line, 1, 'red')
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
            font += 1
        lose_f = True
    # обновляем кадр

    pg.display.flip()


