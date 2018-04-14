from precode2 import *
from config import *
import pygame
import math


class Screen:
    def __init__(self):
        self.screen = pygame.display.set_mode(screen_res)
        self.fps = fps

        self.rect = self.screen.get_rect()

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

        self.score = 0
        self.fuel = starting_fuel

        self.last_shot = pygame.time.get_ticks()
        print(pygame.time.get_ticks())
        self.cooldown = 500

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
        angle = self.angle - 90
        self.angle_rad = radians(angle)

        if not key[up]:
            self.current_speed -= 0.10
            if self.current_speed <= 0:
                self.current_speed = 0

        if key[up]:

            self.current_speed += 0.05

            self.fuel -= 10

            if self.current_speed >= max_speed:
                self.current_speed = max_speed



        if self.fuel > 0:
            self.velocity.x = self.current_speed * math.cos(self.angle_rad)
            self.velocity.y = self.current_speed * math.sin(self.angle_rad)

            self.pos += self.velocity
            self.rect.center = (self.pos.x, self.pos.y)

        else:
            self.fuel = 0

    def fire(self, shoot_key, image, a_list, a_group):
        key = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        if key[shoot_key]:
            if now - self.last_shot >= self.cooldown:
                self.last_shot = now
                self.fuel -= 200

                a_bullet = Bullet(image)
                a_bullet.pos = Vector2D(self.pos.x, self.pos.y)
                a_bullet.velocity.x = 15 * math.cos(self.angle_rad)
                a_bullet.velocity.y = 15 * math.sin(self.angle_rad)

                a_bullet.rect.center = (a_bullet.pos.x, a_bullet.pos.y)

                a_list.append(a_bullet)
                a_group.add(a_bullet)

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
            self.fuel = starting_fuel

            self.score -= 1

    def collide_fuel_pad(self, fuel_pad):
        if pygame.sprite.collide_rect(self, fuel_pad):

            self.pos.y = self.original_pos.y

            if self.pos.y <= fuel_pad.rect.top and self.angle < 340 and self.angle > 20:
                self.current_speed = 0
                self.velocity = Vector2D(0, 0)
                self.fuel = starting_fuel

                self.pos.x = self.original_pos.x

                self.score -= 1

            self.fuel += 20
            if self.fuel >= starting_fuel:
                self.fuel = starting_fuel

            self.rect.center = (self.pos.x, self.pos.y)
            self.image = self.image_original
            self.angle = 0

    def collide_screen(self, screen):
        if pygame.sprite.collide_rect(self, screen) == 0:
            self.pos = self.original_pos

            self.image = self.image_original
            self.rect.center = (self.pos.x, self.pos.y)
            self.angle = 0

            self.velocity = Vector2D(0, 0)
            self.current_speed = 0
            self.fuel = starting_fuel

            self.score -= 1

    def collide_bullet(self, bullet, other_player):
        if pygame.sprite.collide_rect(self, bullet):
            self.pos = self.original_pos

            self.image = self.image_original
            self.rect.center = (self.pos.x, self.pos.y)
            self.angle = 0

            self.velocity = Vector2D(0, 0)
            self.current_speed = 0
            self.fuel = starting_fuel

            other_player.score += 1


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)

        self.image = image

        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)


class FuelPad(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)

        self.image = image

        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)

        self.image = image

        self.velocity = Vector2D(0, 0)
        self.pos = Vector2D(0, 0)
        self.rect = self.image.get_rect()

    def move(self):
        self.pos += self.velocity
        self.rect.center = (self.pos.x, self.pos.y)

    def collide(self, a_list, group, obstacle, collide=1):
        if pygame.sprite.collide_rect(self, obstacle) == collide:
            group.remove(self)
            if self in a_list:
                a_list.remove(self)


class UI:
    def __init__(self, name, pos):
        pygame.font.init()

        self.name = name
        self.score = 0
        self.fuel = starting_fuel

        self.font = pygame.font.SysFont("Times New Roman", 30)
        self.pos = Vector2D(pos.x, pos.y)

        self.surface = None
        self.fuel_surface = None

    def update_ui(self, score, fuel):
        self.score = score
        self.fuel = fuel

        self.surface = self.font.render(self.name + ": " + str(self.score), 1, (255, 255, 255))
        self.fuel_surface = self.font.render("Fuel: " + str(self.fuel), 1, (255, 255, 255))

    def draw_ui(self, screen):
        screen.blit(self.surface, (self.pos.x, self.pos.y))
        screen.blit(self.fuel_surface, (self.pos.x, self.pos.y + 25))


def game():
    the_screen = Screen()
    the_group = pygame.sprite.Group()

    bullet_list_p1 = []
    bullet_list_p2 = []

    player1 = Player(pygame.image.load("player1.png"), Vector2D(80, 495))
    player2 = Player(pygame.image.load("player2.png"), Vector2D(720, 495))

    obstacle1 = Obstacle(pygame.image.load("obstacle.png"), 400, 275)
    obstacle2 = Obstacle(pygame.image.load("obstacle.png"), 400, 500)
    obstacle3 = Obstacle(pygame.image.load("obstacle.png"), 400, 50)

    fuel_pad1 = FuelPad(pygame.image.load("fuel_pad.png"), 80, 530)
    fuel_pad2 = FuelPad(pygame.image.load("fuel_pad.png"), 720, 530)

    player1_score = UI("P1", Vector2D(10, 10))
    player2_score = UI("P2", Vector2D(475, 10))

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

        player1.accelerate(pygame.K_w, 15)
        player1.grav()

        player1.fire(pygame.K_f, pygame.image.load("player1_bullet.png"), bullet_list_p1, the_group)

        player1.collide_obstacle(obstacle1)
        player1.collide_obstacle(obstacle2)
        player1.collide_obstacle(obstacle3)

        player1.collide_screen(the_screen)
        player1.collide_obstacle(player2)

        player1.collide_fuel_pad(fuel_pad1)
        player1.collide_fuel_pad(fuel_pad2)

        player2.accelerate(pygame.K_UP, 15)
        player2.grav()

        player2.fire(pygame.K_RCTRL, pygame.image.load("player2_bullet.png"), bullet_list_p2, the_group)

        player2.collide_obstacle(obstacle1)
        player2.collide_obstacle(obstacle2)
        player2.collide_obstacle(obstacle3)

        player2.collide_screen(the_screen)
        player2.collide_obstacle(player1)

        player2.collide_fuel_pad(fuel_pad1)
        player2.collide_fuel_pad(fuel_pad2)

        player1_score.update_ui(player1.score, player1.fuel)
        player2_score.update_ui(player2.score, player2.fuel)

        for bullets in bullet_list_p1:
            bullets.move()

            player2.collide_bullet(bullets, player1)
            bullets.collide(bullet_list_p1, the_group, player2)

            bullets.collide(bullet_list_p1, the_group, obstacle1)
            bullets.collide(bullet_list_p1, the_group, obstacle2)
            bullets.collide(bullet_list_p1, the_group, obstacle3)

            bullets.collide(bullet_list_p1, the_group, the_screen, 0)

            bullets.collide(bullet_list_p1, the_group, fuel_pad1)
            bullets.collide(bullet_list_p1, the_group, fuel_pad2)

        for bullets in bullet_list_p2:
            bullets.move()

            player1.collide_bullet(bullets, player2)
            bullets.collide(bullet_list_p2, the_group, player1)

            bullets.collide(bullet_list_p2, the_group, obstacle1)
            bullets.collide(bullet_list_p2, the_group, obstacle2)
            bullets.collide(bullet_list_p2, the_group, obstacle3)

            bullets.collide(bullet_list_p2, the_group, the_screen, 0)

            bullets.collide(bullet_list_p2, the_group, fuel_pad1)
            bullets.collide(bullet_list_p2, the_group, fuel_pad2)

        the_group.update()
        the_screen.render()

        the_group.draw(the_screen.screen)
        the_group.draw(the_screen.screen)
        player1_score.draw_ui(the_screen.screen)
        player2_score.draw_ui(the_screen.screen)

        pygame.display.flip()


if __name__ == '__main__':
    game()
