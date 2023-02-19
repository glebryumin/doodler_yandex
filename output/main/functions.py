import os
import pygame
import sys

# загрузка изображения

def load_image(name, colorkey=None):
    # название файла
    fullname = os.path.join('data', name)

    # проверка существования файла
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    # если файл существует, то загружаем его
    image = pygame.image.load(fullname)

    # изменение альфа канала, если требуется
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    # возвращение изображения
    return image

# конец программы
def terminate():
    pygame.quit()
    sys.exit()