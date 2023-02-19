import pygame as pg
import functions as func
from random import randint, choice
import socket
import os

# переставляем наше окно на позицию 450, 35
os.environ['SDL_VIDEO_WINDOW_POS'] = '450, 35'

# инициализация модуль pygame
pg.init()
# выставляем рамеры окна
size = WIDTH, HEIGHT = 300, 400
# создаём прямоугольник нашего окна
screen_rect = (0, 0, WIDTH, HEIGHT)
# выставляем кадры в секунду
FPS = 60
# устанавливаем таймер
clock = pg.time.Clock()
# создаём наш холст с размерами size
screen = pg.display.set_mode(size)
# ставим название нашего приложения
pg.display.set_caption('Doodle Jump')
# ставим иконку нашего приложения(формат .ico не поддердивается)
pg.display.set_icon(func.load_image('icon.png'))
# загружаем шрифты для игры и стартового окна
fonts_lose = {'40': pg.font.Font(None, 40), '35': pg.font.Font(None, 35), 'score': pg.font.Font(None, 30)}
fonts_start = {'30': pg.font.Font(None, 30), '20': pg.font.Font(None, 20)}
# загружаем изображения игрока в обычном состоянии и состоянии прыжка
player_img = {'normal': pg.transform.scale(func.load_image('doodler.png'), (90, 70)),
              'jump': pg.transform.scale(func.load_image('doodler_jump.png'), (90, 70))}
# загружаем изображения нормальной, двигающийся и ломающийся платформы
platform_images = {'normal': pg.transform.scale(func.load_image('normal.jpg'), (60, 10)),
                   'moving': pg.transform.scale(func.load_image('moving.jpg'), (60, 10)),
                   'breaking': pg.transform.scale(func.load_image('breaking.jpg'), (60, 10))}
# загружаем изображения частиц, т.е. кусков ломающийся платформы
particles_images = {'left': func.load_image("broke_left.png"),
                    'right': func.load_image('broke_right.png')}
# загружаем звук проигрыша
lose = pg.mixer.Sound('data/sounds/pada.wav')
# создаём группы для всех спрайтов, платформ, игроков, частиц
all_sprites = pg.sprite.Group()
all_tiles = pg.sprite.Group()
all_players = pg.sprite.Group()
all_particles = pg.sprite.Group()
# устанавливаем максимальный рекорд
max_score = 0
# считываем имя компьютера
myhost = socket.gethostname()
# пробуем считать прошлый максимальный рекорд, если такой есть или есть файл, иначе создаём файл
try:
    # открываем файл с рекордами
    with open("data/score.csv") as f:
        # считываем все строки с файла
        massive = f.readlines()
        # проходимся по строкам
        for line in massive:
            # извлекаем из строки название рекордсмена и сам рекорд
            name, score = line.split(';')
            # если имя рекордсмена совпадает с именем компьютера, то сравниваем макслимальный рекорд с рекордом из файла
            # и записываем результат в переменную msx_score
            if name == myhost:
                max_score = max(max_score, int(score))
    # если данного файла нет, то создаём его и записываем начальную строку
except FileNotFoundError:
    with open('data/score.csv', 'w+') as f:
        f.writelines('name;score\n')
# задаём переменные
# запущен ли стартовый экран**
running_start_screen = True
# идёт ли игра
running = True
# проиграли ли мы
lose_f = False
# тот же максимальный рекорд, что и в прошлом
same_score_f = False
# проигрался ли звук проигрыша один раз
single_use = False


# инициализация класса игрока
class Player(pg.sprite.Sprite):
    # инициализация класса, которая получает на вход его позицию по Оу и Ох, а также группы, к которым он принадлежит
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        # выставляем картинку игрока из заранее заданных
        self.image = player_img['normal']
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
        # изменена ли картинка, т.е. повёрнута ли она
        self.transformed = False
        # звук прыжка игрока
        self.jump_sound = pg.mixer.Sound("data/sounds/jump.wav")

    # функция обновления положения игрока
    def update(self, side):
        # проверяем, касается ли игрок патформы
        platform_collided = pg.sprite.spritecollideany(self, all_tiles)
        # если игрок касается платформы, касается платформы по маске, расстояние между игроком и платформой в промежутке
        # [1;15] и игрок не в прыжке, то мы прыгаем
        if platform_collided \
                and pg.sprite.collide_mask(self, platform_collided) \
                and 1 <= (self.get_y() + self.rect.height) - platform_collided.rect.y <= 15 \
                and not self.jump:
            # изменяем временную высоту
            self.temp_y = -10
            # включаем состояние прыжка
            self.jump = True
            # проигрываем звук прыжка
            self.jump_sound.play()
        # изменяем высоту
        self.rect.y += self.temp_y
        # изменяем времменую высоту, прибавляя гравитацию
        self.temp_y += self.gravity
        # если временная высоту больше нуля, то игрок не в прыжке
        if self.temp_y >= 0:
            # отключаем состояние прыжка
            self.jump = False
        # если сторона, в которую смотрит игроку определена, то изменяем сторону, иначе старая сторона сохраняется
        if side is not None:
            # присваиваем игроку сторону движения
            self.side = side
        # по стороне движения двигаем персонажа
        self.rect.x += self.x_speed * self.side
        # если персонаж смотрит влево (-1), то разворачиваем картинку
        if self.side == -1:
            # если персонаж в прыжке, то используем картинку в прыжке
            if self.jump:
                self.image = pg.transform.flip(pg.transform.scale(player_img['jump'], (90, 70)), True, False)
            # иначе используем обычную картинку
            else:
                self.image = pg.transform.flip(pg.transform.scale(player_img['normal'], (90, 70)), True, False)
            # и считаем, что картинка изменена
            self.transformed = True
        # если же мы смотрим вправо (1), то картинку не изменяем
        elif self.side == 1:
            # если персонаж в прыжке, то используем картинку в прыжке
            if self.jump:
                self.image = player_img['jump']
            # иначе используем обычную картинку
            else:
                self.image = player_img['normal']
            # и считаем, что картинка не изменена
            self.transformed = False
        # если сторона неопределена(None) то сохраняем предыдущее состояние
        else:
            # если картинка изменена, то будем её разворачивать
            if self.transformed:
                # если персонаж в прыжке, то используем картинку в прыжке
                if self.jump:
                    self.image = pg.transform.flip(pg.transform.scale(player_img['jump'], (90, 70)), True, False)
                # иначе используем обычную картинку
                else:
                    self.image = pg.transform.flip(pg.transform.scale(player_img['normal'], (90, 70)), True, False)
            # иначе используем обычную картинку
            else:
                # если персонаж в прыжке, то используем картинку в прыжке
                if self.jump:
                    self.image = player_img['jump']
                # иначе используем обычную картинку
                else:
                    self.image = player_img['normal']

    # функция для получения позиции игрока по оси у
    def get_y(self):
        return self.rect.y

    # функция для получения позиции игрока по оси х
    def get_x(self):
        return self.rect.x

    # функция для выставления позиции игрока по оси х
    def set_x(self, x):
        self.rect.x = x

    # функция для выставления позиции игрока по оси у
    def set_y(self, y):
        self.rect.y = y


# инициализация класса платформы
class Platform(pg.sprite.Sprite):
    # функция инициализации класса, которая на вход принимает позицию по Ох и Оу, а также может ли платформа двигаться
    # или ломаться, а также предзаписанный набор групп
    def __init__(self, x, y, moveable=0, breakable=0, groups=[all_tiles, all_sprites]):
        super().__init__(groups)
        # создаём прямоугольник с которым мы будем взаимодействовать
        self.rect = pg.Rect(x, y, 60, 10)
        # загружаем картинку нормальной платформы
        self.image = platform_images['normal']
        # если не задали заранее переменную moveable, то случайным образом определяем: двигается ли платформа или нет
        if moveable == 0:
            self.moveable = True if randint(0, 10) == 1 else False
        else:
            self.moveable = False
        # аналагично с ломанием
        if breakable == 0:
            self.breakable = True if randint(0, 20) == 1 else False
        else:
            self.breakable = False
        # если же платформа двигается, то меняем ей картинку и определяем её границы
        if self.moveable:
            self.image = platform_images['moving']
            self.x_speed = -1 if randint(0, 10) in (1, 2, 3, 4, 5) else 1
            self.borders = (self.rect.x - 200 if self.rect.x - 200 >= 60 else 60,
                            self.rect.x + 200 if self.rect.x + 200 <= HEIGHT - 60 else HEIGHT - 60)
        # если платформв ломаемая, то загружаем звук ломания и загружаем изображения ломающийся платформы
        if self.breakable:
            self.broke = pg.mixer.Sound('data/sounds/lomise.wav')
            self.image = platform_images['breaking']

    def update(self):
        # если платформа двигается, то каждую тик двигаем её до границ, если она касается границ,
        # то она меняет напрпавление движения
        if self.moveable:
            self.rect.x += self.x_speed
            if self.rect.x <= self.borders[0]:
                self.x_speed = 1
            elif self.rect.x >= self.borders[1]:
                self.x_speed = -1
        # если же платформа ломаемая, то проверяем, касатеся ли она игрока, касание по маске, не в прыжке ли игрок
        # и расстояние между платформой и игроком
        if self.breakable:
            player_collided = pg.sprite.spritecollideany(self, all_players)
            if player_collided \
                    and pg.sprite.collide_mask(self, player_collided) and not all_players.sprites()[0].jump \
                    and -15 <= self.rect.y - (player_collided.rect.y + player_collided.rect.height) <= 15:
                # потом убираем её хитбокс
                self.rect = pg.Rect(self.rect.x, self.rect.y, 0, 0)
                # убираем её изображение
                self.image = pg.Surface((0, 10))
                # проигрываем звук ломания
                self.broke.play()
                # и создаём частицы сломанной платформы
                Particle((self.rect.x, self.rect.y), randint(1, 5) * choice([1, -1]),
                         randint(1, 5) * choice([1, -1]), 'left')
                Particle((self.rect.x, self.rect.y), randint(1, 5) * choice([1, -1]),
                         randint(1, 5) * choice([1, -1]), 'right')


# создаём класс частиц
class Particle(pg.sprite.Sprite):
    # инициализируем класс с данными о позиции платформы, скоростями по Ох и Оу, т.е. вектором,
    # а также с частью сломанной платформы
    def __init__(self, pos, dx, dy, part):
        super().__init__(all_particles, all_sprites)
        self.image = particles_images[part]
        self.rect = self.image.get_rect()
        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos
        # гравитация будет одинаковой
        self.gravity = 0.4

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # если частица за пределами экрана, то удаляем её
        if not self.rect.colliderect(screen_rect):
            self.kill()


# создаём начальные платформы, одна из которых точно не двигается и не ломается
def generate_platforms():
    Platform(175, 580, moveable=1, breakable=1)
    for i in range(20):
        Platform(randint(0, WIDTH - 40), 580 - (50 * (i + 1)))


# убиваем все платформы
def kill_platforms():
    for tile in all_tiles:
        tile.kill()

# убиваем всех игроков
def kill_player():
    for pl in all_players:
        pl.kill()


class Camera:
    # зададим начальный сдвиг камеры и рекорд игры
    def __init__(self):
        self.dy = 0
        self.score = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target, lose_f):
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
        # если смещение меньше нуля и игра не проиграна, то не двигаем камеру
        if self.dy < 0 and not lose_f:
            self.dy = 0
        # если проиграли, то смещение всегда отрицательное и двигается вниз
        elif lose_f:
            self.dy = -20
        # иначе прибавляем к нашему счёту позитивное смещение камеры
        else:
            self.score += self.dy

    # функция получения рекорда
    def get_score(self):
        return self.score

    # функция, которая ставит значение рекорда
    def set_score(self, score):
        self.score = score


# рисуем "клеточки" которые имитируют клетчатую бумагу, как в оригинале
def draw_grid(blocksize=50):
    # задаём размер блока
    block_size = blocksize
    # пробегаемся по холсту и рисуем прямоугольники
    for x in range(0, WIDTH, block_size):
        for y in range(0, HEIGHT, block_size):
            rect = pg.Rect(x, y, block_size, block_size)
            pg.draw.rect(screen, 'black', rect, 1)


# здесь начинается инициализация стартового экрана
# инициализируем Камеру
camera = Camera()
# игрока
player = Player(170, 300, all_sprites, all_players)
# цикл стартового экрана
while running_start_screen:
    # задаём таймер, зависящий от кадров в секундц
    tick = clock.tick(FPS)
    # создаём начальную платформу
    Platform(175, 380, moveable=1, breakable=1)
    # заполняем экран белым
    screen.fill('white')
    # рисуем сетку
    draw_grid()
    # обновляем положение камеры, относительно игрока
    camera.update(player, lose_f)
    # смещаем все объекты относительно игрока
    for sprite in all_sprites:
        camera.apply(sprite)
    # обновляем группу игрока
    all_players.update(None)
    # отрисовываем игрока и платформа
    all_players.draw(screen)
    all_tiles.draw(screen)
    # отрисовываем текст
    texts = ['Doodle Jump', 'Нажмите любую клавишу для старта', f'Ваш лучший рекорд:{max_score}']
    text_coord = 10
    font = 0
    # пробегаемся по линиям в тексте и выбираем какой шрифт мы используем
    for line in texts:
        if font == 0:
            string_rendered = fonts_start['30'].render(line, True, 'red')
        else:
            string_rendered = fonts_start['20'].render(line, True, 'red')
        # берём прямоугольник текста
        intro_rect = string_rendered.get_rect()
        # из именяем положение текста по Оy
        text_coord += 10
        intro_rect.top = text_coord
        # не меняем положение по Ох
        intro_rect.x = 10
        # предотвращаем наложение текста
        text_coord += intro_rect.height
        # отрисовываем текст
        screen.blit(string_rendered, intro_rect)
        # изменяем шрифт
        font += 1
    # пробегаемся по событиям
    for event in pg.event.get():
        # если клавиша нажата, то заканчиваем цикл и переходим к игре
        if event.type == pg.KEYDOWN:
            running_start_screen = False
        # если выходим, то заканчиваем программу
        if event.type == pg.QUIT:
            running_start_screen = False
            # заканчиваем программу
            func.terminate()
    # обнавляем холст
    pg.display.flip()

# убиваем игроков и платформы
kill_player()
kill_platforms()
# меняем размеры окна и прямоугольника экрана
WIDTH, HEIGHT = 550, 700
size = WIDTH, HEIGHT
screen_rect = (0, 0, WIDTH + 50, HEIGHT + 50)
pg.display.set_mode(size)
# пересоздаём игрока, камеру, платформы
player = Player(170, 500, all_sprites, all_players)
camera = Camera()
generate_platforms()
# игровой цикл
while running:
    # задаём единицу времени
    tick = clock.tick(FPS)
    # сторона прыжка (лево или право)
    side = None
    # последняя платформа
    last_tile = None
    # заполняем экран белым, рисуем сетку и отрисовываем все спрайты и частицы
    screen.fill('white')
    draw_grid()
    all_sprites.draw(screen)
    all_particles.draw(screen)

    # обновляем положение камеры
    camera.update(player, lose_f)
    # если платформы есть, то берём последнюю платформу
    if len(all_tiles.sprites()) > 0:
        last_tile = all_tiles.sprites()[-1]
        # если позиция по Оу у последней платформы больше 50, то создаём новую платформу
        if last_tile.rect.y > 50:
            x, y = randint(0, WIDTH - 60), -randint(0, 5)
            Platform(x, y)
            # если новая платформа ломаемая, то создаём новую неломаемую платформу, которая не пересекается по Ох,
            # но с такими же параметрами
            if all_tiles.sprites()[-1].breakable:
                x1 = randint(0, WIDTH - 60)
                while x < x1 < x + 60 or x - 60 < x1 < x:
                    x1 = randint(0, WIDTH - 60)
                Platform(x1, y, moveable=last_tile.moveable, breakable=1,
                         groups=last_tile.groups())

    # передвигаем все спрайты относительно игрока при помощи камеры
    for sprite in all_sprites:
        camera.apply(sprite)
        # если спрайт за пределами экрана, то убиваем его
        if not sprite.rect.colliderect(screen_rect):
            sprite.kill()

    # считываем максимальный рекорд у камеры и сравниваем его с нынешним и устанавливаем значение в переменную max_score
    max_score = max(max_score, camera.get_score())
    # преврашаем наш рекорд в текст
    text = str(camera.get_score())
    # отрисовываем на текст
    score_rendered = fonts_lose['score'].render(text, True, 'blue')
    screen.blit(score_rendered, (5, 5))

    # пробегаемся по событиям
    for event in pg.event.get():
        # если выход, то завершаем цикл и записываем рекорд
        if event.type == pg.QUIT:
            # останавливаем цикл
            runnning = False
            # открываем файл и смотрим, одинаковые ли рекорды
            # если рекорды одинаковы, то не записываем его
            with open('data/score.csv') as f:
                name, score = f.readlines()[-1].split(';')
                if name == myhost and int(score) == max_score:
                    same_score_f = True
            # если рекорды неодинаковы, то записываем рекорд в файл
            if not same_score_f:
                with open('data/score.csv', 'a') as f:
                    f.write(f'{myhost};{max_score}\n')
            # заканчиваем программу
            func.terminate()
        # если кнопка нажата, то выбираем сторону движения
        if event.type == pg.KEYDOWN:
            # вправо
            if event.key in (pg.K_d, pg.K_RIGHT):
                side = 1
            # влево
            elif event.key in (pg.K_a, pg.K_LEFT):
                side = -1
            # если проиграли и нажали клавишу, то пересоздаём игру
            if lose_f:
                # обнуляем рекорд
                camera.set_score(0)
                # убиваем платформы
                kill_platforms()
                # обнуляем флаг проигрыша и флаг единоразового проигрывания звука проигрыша
                lose_f = False
                single_use = False
                # пересоздаём игрока
                player = Player(170, 500, all_sprites, all_players)
                # создаём платформы
                generate_platforms()
        # если кнопка отжата, то приравниваем сторону к нулю
        if event.type == pg.KEYUP:
            if event.key in (pg.K_d, pg.K_RIGHT):
                side = 0
            elif event.key in (pg.K_a, pg.K_LEFT):
                side = 0

    # передвигаем игрока в сторону и передвигаем платформы и частицы
    player.update(side)
    all_tiles.update()
    all_particles.update()
    # если игрок вышел за пределы экрана по Ох, то переносим его на другую сторону
    if player.get_x() > WIDTH - 45:
        player.set_x(-45)
    elif player.get_x() < -45:
        player.set_x(WIDTH - 45)
    # если игрок выпал за пределы экрана по Оу, то засчитываем проигрыш
    if player.get_y() - player.rect.height > HEIGHT:
        # проигрываем звук, если не проиграли раньше
        if not single_use:
            lose.play()
            single_use = True
        # отображаем текст аналогично прошлому
        texts = ['Вы проиграли!', 'Нажмите любую клавишу для перезапуска', f'Ваш рекорд:{camera.get_score()}',
                 f'Лучший рекорд:{max_score}']
        text_coord = 220
        font = 0
        for line in texts:
            if font == 0:
                string_rendered = fonts_lose['40'].render(line, True, 'red')
            else:
                string_rendered = fonts_lose['35'].render(line, True, 'red')
            intro_rect = string_rendered.get_rect()
            text_coord += 30
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
            font += 1
        # поднимаем флаг проигрыша
        lose_f = True

    # обновляем кадh
    pg.display.flip()
