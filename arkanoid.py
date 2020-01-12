import pygame
import math
import os
import random

size = width, height = 600, 600

#класс для отображения и управления платформой
class Platform(pygame.sprite.Sprite):
    def __init__(self, pos=int(width * 0.5)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 5))
        self.image.fill(pygame.Color('gray'))
        self.rect = pygame.Rect((pos, int(height * 0.75)), (50, 5))
        self.mask = pygame.mask.from_surface(self.image)

    #возвращает позицию верхнего левого угла платформы
    def get_pos(self):
        return self.rect.topleft

    #устанавливает позицию верхнего левого угла платформы
    def set_pos(self, pos):
        if pos + self.rect.width <= width:
            self.rect.left = pos

    #рисует платформу на экране
    def draw(self, screen):
        screen.blit(self.image, self.rect)

#класс, реализующий логику движения шарика
class Ball(pygame.sprite.Sprite):
    def __init__(self, coord=(int(width * 0.5), int(height * 0.5)), angle=0.0):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((14, 14))
        self.image.set_colorkey(pygame.Color('black'))
        pygame.draw.circle(self.image, pygame.Color('red'), (7, 7), 7, 0)
        self.velocity = 100 #задает скорость мяча
        self.rect = pygame.Rect(coord, (14, 14))
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = angle
        self.clock = pygame.time.Clock()
        self.position = coord
        self.out_of_the_game = False #флаг, определяющий находится ли мяч в игре

    #определяет находится ли мяч в игре
    def ball_in_the_game(self):
        return not self.out_of_the_game

    def return_ball_in_the_game(self):
        self.out_of_the_game = False

    def draw(self, surf):
        surf.blit(self.image, self.position)

    def set_speed(self, velocity):
        self.velocity = velocity

    #реализует логику движения шара
    def move(self):
        delta = int(self.velocity / 30)
        pos_x = self.position[0]
        pos_y = self.position[1]
        delta_x = delta * math.cos(self.angle)
        delta_y = delta * math.sin(self.angle)
        if (delta_x >= 0) and (pos_x + delta_x + self.image.get_width()) <= width:
            pos_x += delta_x
        elif delta_x < 0 and (pos_x + delta_x) >= 0:
            pos_x += delta_x
        elif pos_x + delta_x + self.image.get_width() > width:
            pos_x = width - self.image.get_width()
            self.set_angle(bounce_angle(self.angle, True))
        elif pos_x + delta_x < 0:
            pos_x = 0
            self.set_angle(bounce_angle(self.angle, True))

        if (delta_y >= 0) and (pos_y + delta_y + self.image.get_height()) <= height:
            pos_y += delta_y
        elif delta_y < 0 and (pos_y + delta_y) >= 0:
            pos_y += delta_y
        elif pos_y + delta_y > height - self.image.get_height():
            self.out_of_the_game = True
            pos_y = height - self.image.get_height()
            self.set_angle(bounce_angle(self.angle, False))

        elif pos_y + delta_y <= 0:
            pos_y = 0
            self.set_angle(bounce_angle(self.angle, False))
        self.set_pos((pos_x, pos_y))
        self.clock.tick(30)

    def hit_bricks(self, brks):
        return pygame.sprite.spritecollide(self, brks, False, pygame.sprite.collide_mask)
        #return pygame.sprite.spritecollide(self, brks, False)

    def hit_platform(self, pltfrm):
        if pygame.sprite.collide_mask(self, pltfrm) is None:
            return False
        else:
            return True
        #return pygame.sprite.collide_rect(self, pltfrm)

    def set_pos(self, coord):
        self.position = coord
        self.rect.topleft = coord

    def get_pos(self):
        return self.rect.topleft

    def set_angle(self, angle):
        self.angle = angle

    def get_angle(self):
        return self.angle


#словарь для цветов кирпичей
colors = {0: 'gray', #серые кирпичи не выбиваются
          1: 'blue', #синие кирпичи выбиваются с 1 раза
          2: 'red', #красные кирпичи выбиваются с 2 раза
          3: 'green'} #зеленые кирпичи выбиваются с 3 раза
#класс для отображения "кирпичиков"
class Brick(pygame.sprite.Sprite):
    def __init__(self, clr, coord=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.clr = clr
        self.image = pygame.Surface((30, 10))
        self.image.fill(pygame.Color(colors[self.clr]))
        self.rect = pygame.Rect(coord, (30, 10))
        self.mask = pygame.mask.from_surface(self.image)
        self.remaining_hits = clr #атрибут, хранящий количество ударов до выбивания

    def set_pos(self, coord):
        self.rect.topleft = coord

    def get_width(self):
        return self.rect.width

    def get_height(self):
        return self.rect.height

    #уменьшает количество ударов до выбивания и возвращает его наружу
    def hitted(self):
        if self.remaining_hits > 0:
            self.remaining_hits -= 1
        return self.remaining_hits

#функция, создающая уровень игры
def level_one_create_layout(lst_gray, lst_colored):
    #зануляем списки кирпичиков
    lst_gray.empty() #серые кирпичи хранятся отдельно
    lst_colored.empty()
    #расставляем в цикле, выбирая цвет рандомно
    for i in range(10):
        for j in range(10):
            rndm = random.choice(list(colors.keys()))
            brick = Brick(rndm)
            brick.set_pos((1.5 * i * brick.get_width() + 10, 2 * j * brick.get_height() + 10))
            if rndm == 0:
                lst_gray.add(brick)
            else:
                lst_colored.add(brick)

#вычисляет отраженный угол в зависимости от начального угла и оси отражения
def bounce_angle(angle, axe):
    if axe is True: #ось у
        if 0 <= angle <= 0.5 * math.pi:
            angle = math.pi - angle
        elif 0.5 * math.pi <= angle <= math.pi:
            angle = -math.pi - angle
        elif math.pi <= angle <= 1.5 * math.pi:
            angle = 3 * math.pi - angle
        elif 1.5 * math.pi <= angle <= 2 * math.pi:
            angle = 3 * math.pi - angle

    else: #ось х
        if 0 <= angle <= 0.5 * math.pi:
            angle = 2 * math.pi - angle
        elif 0.5 * math.pi <= angle <= math.pi:
            angle = 2 * math.pi - angle
        elif math.pi <= angle <= 1.5 * math.pi:
            angle = - angle
        elif 1.5 * math.pi <= angle <= 2 * math.pi:
            angle = 2 * math.pi - angle


    if angle > 2 * math.pi:
        angle -= 2 * math.pi
    elif angle < -2 * math.pi:
        angle = 2 * math.pi - angle
    if angle < 0:
        angle = 2 * math.pi + angle
    new_angle = angle
    return new_angle

#создает surface из файла. Файлы должны быть в папке Data.
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

#рисует счетчик оставшихся жизней
def draw_count(scrn, count, rect):
    pygame.font.init()
    font = pygame.font.Font(None, 50)
    text = font.render(str(count), 1, pygame.Color('red'))
    scrn.blit(text, rect.topleft)

#выставить правильную позицию и угол мяча в зависимости от грани, с которой он столкнулся
def reflect_ball_from_rect(rect, ball):
    bottomline = pygame.Rect(rect.bottomleft, rect.bottomright)
    topline = pygame.Rect(rect.topleft, rect.topright)
    leftline = pygame.Rect(rect.topleft, rect.bottomleft)
    rightline = pygame.Rect(rect.topright, rect.bottomright)
    new_angle = 0
    if bottomline.colliderect(ball.rect):
        new_angle = bounce_angle(ball.get_angle(), False)
        ball.set_pos((ball.get_pos()[0], bottomline.top))
    elif topline.colliderect(ball.rect):
        new_angle = bounce_angle(ball.get_angle(), False)
        ball.set_pos((ball.get_pos()[0], topline.top - ball.rect.height))
    elif leftline.colliderect(ball.rect):
        new_angle = bounce_angle(ball.get_angle(), True)
        ball.set_pos((leftline.left - ball.rect.width, ball.get_pos()[1]))
    elif rightline.colliderect(ball.rect):
        new_angle = bounce_angle(ball.get_angle(), True)
        ball.set_pos((rightline.left, ball.get_pos()[1]))
    ball.set_angle(new_angle)

screen = pygame.display.set_mode(size)
running = True
game_is_over = False
platform = Platform()
count_of_lives = 3
plat_move = False
bricks = pygame.sprite.Group()
gray_bricks = pygame.sprite.Group()
colored_bricks = pygame.sprite.Group()
ball = Ball(angle=(math.pi/6 + random.random() * math.pi / 2))
ball.set_speed(200)
level_one_create_layout(gray_bricks, colored_bricks)
#игровой цикл
while running:
    if not game_is_over: #ветка для логики продолжающейся игры
        if len(colored_bricks) == 0: #проверяем остались ли цветные кирпичи, если нет, то подготавливаем заставку победы
            game_is_over = True
            image = load_image('win.jpg')
            velocity = 200
            clock = pygame.time.Clock()
            position = -(image.get_width())
            screen.fill(pygame.Color('blue'))
            delta_x = int(velocity / 30)
            if (position + delta_x + image.get_width()) <= width:
                position += delta_x
            else:
                position = width - image.get_width()
            screen.blit(image, (position, 0))
            pygame.display.flip()
            clock.tick(30)
        else: #ветка, когда остались цветные кирпичи, продолжаем выбивать
            flag = True
            background = load_image('background.jpg')
            screen.blit(background, (0, 0))
            gray_bricks.draw(screen)
            colored_bricks.draw(screen)
            #определяем попали ли в какой-либо кирпич. Если серый, то не выбиваем.
            brcks = ball.hit_bricks(gray_bricks)
            if len(brcks) > 0:
                last_brick = brcks[len(brcks) - 1]
                reflect_ball_from_rect(last_brick.rect, ball)
            brcks = ball.hit_bricks(colored_bricks)
            if len(brcks) > 0:
                last_brick = brcks[len(brcks) - 1]
                reflect_ball_from_rect(last_brick.rect, ball)
                remaining_hits = last_brick.hitted()
                print(remaining_hits)
                if remaining_hits == 0:
                    colored_bricks.remove(brcks)


            if ball.hit_platform(platform):
                ball.set_angle(ball.get_angle() + random.random() * math.pi / 20)
                reflect_ball_from_rect(platform.rect, ball)

            if not ball.ball_in_the_game(): #если мяч вылетел за пределы поля
                if count_of_lives > 1: #жизни остались
                    count_of_lives -= 1
                    ball.return_ball_in_the_game()
                    ball.set_pos((int(width * 0.5), int(height * 0.5)))
                    ball.set_angle(math.pi / 6)
                else: #игра проиграна, подготовка к отрисовки заставки
                    game_is_over = True
                    image = load_image('my_gameover.png')
                    velocity = 200
                    clock = pygame.time.Clock()
                    position = -(image.get_width())
            ball.move()
            ball.draw(screen)
            platform.draw(screen)
            draw_count(screen, count_of_lives, pygame.Rect(width - 50, height - 50, 50, 50))

    else: #отрисовка анимированной заставки победы или проигрыша
        screen.fill(pygame.Color('blue'))
        delta_x = int(velocity / 30)
        if (position + delta_x + image.get_width()) <= width:
            position += delta_x
        else:
            position = width - image.get_width()
        screen.blit(image, (position, 0))
        pygame.display.flip()
        clock.tick(30)

    #обработка событий: передвижение платформы при помощи левой кнопки мыши, ее перетаскивания с нажатой кнопкой, перезапуск игры и выход из нее
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                plat_move = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                plat_move = False
        elif event.type == pygame.MOUSEMOTION:
            if plat_move is True:
                platform.set_pos(event.pos[0])
        elif event.type == pygame.KEYDOWN:
            if game_is_over:
                if event.key == pygame.K_r:
                      game_is_over = False
                      count_of_lives = 3
                      plat_move = False
                      level_one_create_layout(gray_bricks, colored_bricks)
                      ball.return_ball_in_the_game()
                      ball.set_pos((int(width * 0.5), int(height * 0.5)))
                      ball.set_angle(math.pi/6 + random.random() * math.pi / 2)
                elif event.key == pygame.K_q:
                    running = False
        elif event.type == pygame.QUIT:
            running = False
    pygame.display.flip()