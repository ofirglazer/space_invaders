import pygame
from enum import Enum
from spritesheet import SpriteSheet
import random

SCR_WIDTH = 540
SCR_HEIGHT = 380
SCALING_FACTOR = 1.5
ALIEN0_WIDTH = 24
ALIEN1_WIDTH = 22
ALIEN2_WIDTH = 16
SPRITE_HEIGHT = 16
PLAYER_WIDTH = 26


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


pygame.init()


class Images:
    def __init__(self, filename):
        sprite_sheet = SpriteSheet(filename)

        alien2_rects = [(8, 8, ALIEN2_WIDTH, SPRITE_HEIGHT),
                        (40, 8, ALIEN2_WIDTH, SPRITE_HEIGHT)]
        alien1_rects = [(69, 8, ALIEN1_WIDTH, SPRITE_HEIGHT),
                        (101, 8, ALIEN1_WIDTH, SPRITE_HEIGHT)]
        alien0_rects = [(132, 8, ALIEN0_WIDTH, SPRITE_HEIGHT),
                        (164, 8, ALIEN0_WIDTH, SPRITE_HEIGHT)]
        player_rect = (163, 40, PLAYER_WIDTH, SPRITE_HEIGHT)
        laser_rect = (79, 42, 2, 14)
        bomb_rect = (109, 42, 6, 14)
        self.ALIEN2_IMGS = sprite_sheet.images_at(alien2_rects)
        self.ALIEN1_IMGS = sprite_sheet.images_at(alien1_rects)
        self.ALIEN0_IMGS = sprite_sheet.images_at(alien0_rects)
        self.PLAYER_IMG = sprite_sheet.image_at(player_rect)
        self.LASER_IMG = sprite_sheet.image_at(laser_rect)
        self.BOMB_IMG = sprite_sheet.image_at(bomb_rect)


class Player:

    def __init__(self, imgs):
        self.img = imgs.PLAYER_IMG
        self.x = SCR_WIDTH // 2
        self.y = 340
        self.vel = 3

    def update(self, action):
        if action[0]:
            self.x -= self.vel
        elif action[2]:
            self.x += self.vel

        if self.x <= 0:
            self.x = 0
        elif (self.x + PLAYER_WIDTH) >= SCR_WIDTH:
            self.x = SCR_WIDTH - PLAYER_WIDTH


class Projectile:

    def __init__(self, img, x, y, direction):
        self.img = img
        self.x = x
        self.y = y
        self.direction = direction
        self.vel = 10
        self.valid = True

    def update(self):
        if self.direction == Direction.UP:
            self.y -= self.vel
        else:
            self.y += self.vel

        if self.y <= 0 or self.y >= SCR_HEIGHT:
            self.valid = False


class Alien:

    def __init__(self, imgs, alien_type, x, y):
        img_str = "ALIEN" + str(alien_type) + "_IMGS"
        self.img = getattr(imgs, img_str)
        self.x = x
        self.y = y
        self.vel = 1

        if alien_type == 0:
            self.width = ALIEN0_WIDTH
        elif alien_type == 1:
            self.width = ALIEN1_WIDTH
        else:
            self.width = ALIEN2_WIDTH


class Swarm:

    def __init__(self, imgs):
        x_init = 20
        y_init = 10
        self.vel_x = 1
        self.vel_y = 10
        self.direction = Direction.RIGHT
        self.aliens = list()
        spacing = ALIEN0_WIDTH + 10
        self.sprite_number = 0

        for row in range(0, 5):
            alien_row = list()
            for col in range(0, 11):
                alien_type = row // 2
                x = col * spacing + x_init
                if alien_type == 1:
                    x += 1
                elif alien_type == 2:
                    x += 4
                y = (4 - row) * spacing + y_init
                alien_row.append(Alien(imgs, alien_type, x, y))
            self.aliens.append(alien_row)

    def get_edges(self):
        edges = [SCR_WIDTH, 0, 0]  # left, bottom, right]
        for alien_row in self.aliens:
            for alien in alien_row:
                if alien.x < edges[0]:
                    edges[0] = alien.x
                if (alien.x + alien.width) > edges[2]:
                    edges[2] = alien.x + alien.width
                if (alien.y + SPRITE_HEIGHT) > edges[1]:
                    edges[1] = alien.y + SPRITE_HEIGHT
        return edges

    def update(self, frame_number):
        if frame_number % 10 == 0:
            self.sprite_number = (self.sprite_number + 1) % 2

        edges = self.get_edges()
        if self.direction == Direction.RIGHT:
            if edges[2] < SCR_WIDTH - self.vel_x:
                self.move_x(self.vel_x)
            else:
                self.move_y()
                self.direction = Direction.LEFT
        else:
            if edges[0] > self.vel_x:
                self.move_x(-self.vel_x)
            else:
                self.move_y()
                self.direction = Direction.RIGHT

    def move_x(self, step):
        for alien_row in self.aliens:
            for alien in alien_row:
                alien.x += step

    def move_y(self):
        for alien_row in self.aliens:
            for alien in alien_row:
                alien.y += self.vel_y


class Game:
    def __init__(self, speed=20):
        # set display
        self.speed = speed
        self.canvas = pygame.Surface((SCR_WIDTH, SCR_HEIGHT))
        self.display = pygame.display.set_mode((SCR_WIDTH * SCALING_FACTOR,
                                                SCR_HEIGHT * SCALING_FACTOR))
        pygame.display.set_caption('SPACE INVADERS! game by Ofir')
        # self.font_style = pygame.font.SysFont("bahnschrift", 50)
        # self.score_font = pygame.font.SysFont("comicsansms", 30)

        filename = 'invaders_sheet.png'
        self.imgs = Images(filename)
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.swarm = Swarm(self.imgs)
        self.player = Player(self.imgs)
        self.projectiles = list()
        self.frame_number = 0
        self.game_over = False

    def redraw(self):
        self.canvas.fill([0, 0, 0])
        to_draw = list()

        for alien_row in self.swarm.aliens:
            for alien in alien_row:
                to_draw.append((alien.img[self.swarm.sprite_number], (alien.x, alien.y)))
        for projectile in self.projectiles:
            to_draw.append((projectile.img, (projectile.x, projectile.y)))
        to_draw.append((self.player.img, (self.player.x, self.player.y)))
        self.canvas.blits(to_draw)

        # transform from screen to display
        self.display.blit(pygame.transform.scale(self.canvas,
                                                 self.display.get_rect().size), (0, 0))
        pygame.display.flip()

    def get_action(self):
        action = [False, False, False]  # left, shoot, right
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            action[2] = True
        elif keys[pygame.K_LEFT]:
            action[0] = True
        if keys[pygame.K_SPACE]:
            action[1] = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True

        return action

    def check_laser_hit(self, laser):
        for alien_row in self.swarm.aliens:
            for alien in alien_row[:]:
                if laser.x in range(alien.x, alien.x + alien.width) and\
                        laser.y in range(alien.y, alien.y + SPRITE_HEIGHT):
                    alien_row.remove(alien)
                    laser.valid = False

    def check_bomb_hit(self, bomb):
        if bomb.x in range(self.player.x - 1, self.player.x + PLAYER_WIDTH + 1) and\
                bomb.y in range(self.player.y, self.player.y + SPRITE_HEIGHT):
            self.game_over = True

    def fire_laser(self):
        laser_active = False
        for projectile in self.projectiles:
            if projectile.direction == Direction.UP:
                laser_active = True
                break
        if not laser_active:
            x = self.player.x + PLAYER_WIDTH // 2 - 1
            laser = Projectile(self.imgs.LASER_IMG, x, self.player.y, Direction.UP)
            self.projectiles.append(laser)

    def update_projectiles(self):
        # advance and check if hits
        for projectile in self.projectiles:
            projectile.update()
            if projectile.direction == Direction.UP:
                self.check_laser_hit(projectile)
            else:
                self.check_bomb_hit(projectile)

        # drop bombs
        for alien_row in self.swarm.aliens:
            for alien in alien_row:
                self.drop_bomb(alien)

        # remove if at end of screen
        for projectile in self.projectiles[:]:
            if not projectile.valid:
                self.projectiles.remove(projectile)

    def drop_bomb(self, alien):
        chance_drop_bomb = 8  # /10000
        if random.randint(1, 10000) <= chance_drop_bomb:
            x = alien.x + alien.width // 2 - 1
            bomb = Projectile(self.imgs.BOMB_IMG, x, alien.y + SPRITE_HEIGHT, Direction.DOWN)
            self.projectiles.append(bomb)

    def game_step(self):
        action = self.get_action()
        if action[1]:
            self.fire_laser()

        self.swarm.update(self.frame_number)
        self.update_projectiles()
        self.player.update(action)

        self.clock.tick(self.speed)
        self.frame_number += 1
        self.redraw()

    def game_loop(self):
        while not self.game_over:
            self.game_step()
        pygame.quit()
        quit()


if __name__ == '__main__':
    space_invaders_game = Game()
    space_invaders_game.game_loop()
