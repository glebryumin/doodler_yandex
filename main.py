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
new_platform = False


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
        elif self.side == 'right':
            self.rect.x += self.x_speed

    def get_y(self):
        return self.rect.y



# инициализация класса платформы
class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.image = pg.Surface((60, 10))
        pg.draw.rect(self.image, 'black', (0, 0, 60, 10))
        self.rect = pg.Rect(x, y, 60, 10)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.max_y = -1
        self.dy = 0
        self.target_y = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
        if self.dy < 0:
            self.dy = 0


player = Player(170, 400, all_sprites)
platforms = [Platform(175, 480, all_tiles, all_sprites), Platform(120, 300, all_tiles, all_sprites),
             Platform(250, 120, all_tiles, all_sprites), Platform(175, -60, all_tiles, all_sprites),
             Platform(540, -240, all_tiles, all_sprites)]
camera = Camera()
# игровой цикл

while runnning:
    # единица времени
    tick = clock.tick(FPS)
    # сторона прыжка (лево или право)
    side = None
    # заполняем экран белым и отрисовываем все спрайты
    screen.fill('white')
    all_sprites.draw(screen)
    # обновляем положение камеры
    camera.update(player)
    # пробегаемся по платформам и отрисовываем их
    for i in range(len(platforms)):
        all_tiles.draw(screen)
        # если нужна новая платформа, то создаём её
        if new_platform:
            platforms.append(Platform(randint(0, WIDTH - 40), -randint(10, 50), all_tiles, all_sprites))
            new_platform = False
        if platforms[i].rect.y > HEIGHT + 100:
            platforms[i].kill()

    # передвигаем все спрайты относительно игрока при помощи камеры
    for sprite in all_sprites:
        camera.apply(sprite)
    # пробегаемся по событиям
    for event in pg.event.get():
        # если выход, то завершаем цыкл
        if event.type == pg.QUIT:
            runnning = False
        # если кнопка нажата, то выбираем сторону движения
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_d, pg.K_RIGHT):
                side = 'right'
            elif event.key in (pg.K_a, pg.K_LEFT):
                side = 'left'
        # если кнопка отжата, то приравниваем сторону к нулю
        if event.type == pg.KEYUP:
            if event.key in (pg.K_d, pg.K_RIGHT):
                side = 0
            elif event.key in (pg.K_a, pg.K_LEFT):
                side = 0
    # передвигаем игрока в сторону
    player.update(side)
    if player.get_y() < 250:
        new_platform = True
    # обновляем кадр
    pg.display.flip()
# заканчиваем программу
func.terminate()
