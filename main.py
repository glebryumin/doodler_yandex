import pygame as pg
import functions as func
from random import randint

# инициализация окна, шрифта, счётчика времени
pg.init()
size = WIDTH, HEIGHT = 400, 500
FPS = 60
font = pg.font.Font(None, 16)
clock = pg.time.Clock()
screen = pg.display.set_mode(size)
pg.display.set_caption('Doodler')
player_img = func.load_image('doodler.png')
all_sprites = pg.sprite.Group()
all_tiles = pg.sprite.Group()
runnning = True


# инициализация класса игрока
class Player(pg.sprite.Sprite):
    # инициализация иконки игрока, его размеров и положения
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        # подгоняем картинку под размер игрока
        self.image = pg.transform.scale(player_img, (90, 70))
        # выставляем размеры и позицию игрока
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
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

    # функция обновления положения игрока
    def update(self, side):
        # если игрок касается платформы, то прыгаем, изменяя временную высоту
        if pg.sprite.spritecollideany(self, all_tiles):
            # изменяем временную высоту
            self.temp_y = -10
        # изменяем высоту
        self.rect.y += self.temp_y
        # изменяем времменую высоту, прибавляя гравитацию
        self.temp_y += self.gravity
        #
        self.side = side if side is not None else self.side
        if self.side == 'left':
            self.rect.x -= self.x_speed
        elif self.side == 'right':
            self.rect.x += self.x_speed


# инициализация класса платформы
class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = pg.Surface((60, 10))
        pg.draw.rect(self.image, 'black', (0, 0, 60, 10))
        self.rect = pg.Rect(x, y, 60, 10)


player = Player(170, 400, all_sprites)
platforms = [Platform(175, 480, all_tiles, all_sprites)]
# игровой цикл

while runnning:
    # единица времени
    tick = clock.tick(FPS)

    side = None

    screen.fill('white')
    all_sprites.draw(screen)

    for i in range(len(platforms)):
        all_tiles.draw(screen)
        # platforms.append(Platform(randint(0, WIDTH), randint(0, HEIGHT), all_tiles, all_sprites))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            runnning = False
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_d, pg.K_RIGHT):
                side = 'right'
            elif event.key in (pg.K_a, pg.K_LEFT):
                side = 'left*'
    all_sprites.update(side)
    pg.display.flip()

func.terminate()