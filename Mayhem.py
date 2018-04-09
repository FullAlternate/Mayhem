from precode2 import *
from config import *
import pygame
import math


class Screen:
    def __init__(self):
        self.screen = pygame.display.set_mode(screen_res)
        self.fps = fps

    def render(self):
        self.screen.fill([0, 0, 0])

    def fps_limit(self):
        clock = pygame.time.Clock()
        clock.tick(self.fps)


class Player(pygame.sprite.Sprite):
    def __init__(self, image, pos_vec):
        pygame.sprite.Sprite.__init__(self)

        self.image_original = image
        self.image = self.image_original.copy()

        self.rect = self.image_original.get_rect()
        self.original_pos = pos_vec
        self.pos = self.original_pos
        self.rect.center = (self.pos.x, self.pos.y)

        self.angle = 0
        self.angle_rad = 0

        self.current_speed = 0

        self.velocity = Vector2D(0, 0)

    def rotate(self, left, right):

        key = pygame.key.get_pressed()
        if key[left]:
            self.angle -= 3
            self.angle %= 360
            self.image = pygame.transform.rotate(self.image_original, (self.angle * -1))
            self.rect = self.image.get_rect(center=self.rect.center)

        if key[right]:
            self.angle += 3
            self.angle %= 360
            self.image = pygame.transform.rotate(self.image_original, (self.angle * -1))
            self.rect = self.image.get_rect(center=self.rect.center)

    def accelerate(self, up, max_speed):

        key = pygame.key.get_pressed()

        if not key[up]:
            self.current_speed -= 0.03
            if self.current_speed <= 0:
                self.current_speed = 0

        if key[up]:
            angle = self.angle - 90
            self.current_speed += 0.03

            if self.current_speed >= max_speed:
                self.current_speed = max_speed

            self.angle_rad = math.radians(angle)

        self.velocity.x = self.current_speed * math.cos(self.angle_rad)
        self.velocity.y = self.current_speed * math.sin(self.angle_rad)

        self.pos += self.velocity
        self.rect.center = (self.pos.x, self.pos.y)

    def grav(self):
        self.pos.y += gravity
        self.rect.center = (self.pos.x, self.pos.y)

    def collide_obstacle(self, obstacle):
        if pygame.sprite.collide_rect(self, obstacle):
            self.pos = self.original_pos

            self.image = self.image_original
            self.rect.center = (self.pos.x, self.pos.y)
            self.angle = 0

            self.velocity = Vector2D(0, 0)
            self.current_speed = 0

            return True

        return False

    def collide_fuel_pad(self, fuel_pad):
        if pygame.sprite.collide_rect(self, fuel_pad):

            self.pos.y = self.original_pos.y
            print(self.angle)

            if self.pos.y <= fuel_pad.rect.top and self.angle < 340 and self.angle > 20:
                print("fired")
                self.current_speed = 0
                self.velocity = Vector2D(0, 0)

                self.pos.x = self.original_pos.x

            self.rect.center = (self.pos.x, self.pos.y)
            self.image = self.image_original
            self.angle = 0

            return True

        return False


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)

        self.image = image

        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)


class Score(pygame.sprite.Sprite):
    pass


class FuelPad(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)

        self.image = image

        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)


def game():
    the_screen = Screen()
    the_group = pygame.sprite.Group()

    player1 = Player(pygame.image.load("player1.png"), Vector2D(80, 495))
    player2 = Player(pygame.image.load("player2.png"), Vector2D(720, 495))

    obstacle1 = Obstacle(pygame.image.load("obstacle.png"), 400, 275)
    obstacle2 = Obstacle(pygame.image.load("obstacle.png"), 400, 500)
    obstacle3 = Obstacle(pygame.image.load("obstacle.png"), 400, 50)

    fuel_pad1 = FuelPad(pygame.image.load("fuel_pad.png"), 80, 530)
    fuel_pad2 = FuelPad(pygame.image.load("fuel_pad.png"), 720, 530)

    the_group.add(player1)
    the_group.add(player2)

    the_group.add(obstacle1)
    the_group.add(obstacle2)
    the_group.add(obstacle3)

    the_group.add(fuel_pad1)
    the_group.add(fuel_pad2)

    while True:
        the_screen.fps_limit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        player1.rotate(pygame.K_a, pygame.K_d)
        player2.rotate(pygame.K_LEFT, pygame.K_RIGHT)

        player1.accelerate(pygame.K_w, 5)
        player1.grav()

        player1.collide_obstacle(obstacle1)
        player1.collide_obstacle(obstacle2)
        player1.collide_obstacle(obstacle3)
        player1.collide_obstacle(player2)
        player1.collide_fuel_pad(fuel_pad1)
        player1.collide_fuel_pad(fuel_pad2)

        player2.accelerate(pygame.K_UP, 5)
        player2.grav()

        player2.collide_obstacle(obstacle1)
        player2.collide_obstacle(obstacle2)
        player2.collide_obstacle(obstacle3)
        player2.collide_obstacle(player1)


        the_group.update()
        the_screen.render()

        the_group.draw(the_screen.screen)

        pygame.display.flip()






game()
