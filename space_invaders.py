import pygame
import os, sys
import time
import random
from button import Button




pygame.font.init()  # font importing

WIDTH, HEIGHT = 950, 950  # display size
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # surface, window display
pygame.display.set_caption("Space Shooter Game")  # display game name

# LOAD IMAGES
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))  # load image from folder wuth "os.path.join"
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# PLAYER
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# LASERS
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# BACKGROUND IMAGE
BG_1 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background_1.png")),
                            (WIDTH, HEIGHT))  # scaled image with dimensions "WIDTH, HEIGHT"
BG_2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background_2.png")),
                            (WIDTH, HEIGHT))


Menu_BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "main_menu_BG.png")), (WIDTH, HEIGHT))

Opening_BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "opening_bg.png")), (WIDTH, HEIGHT))

HS_BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "HS_BG.png")), (WIDTH, HEIGHT))


# main menu screen
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GALAXY SPACE WARS")



def get_font(size): # Font type for main menu
    return pygame.font.Font("Font/VerminVibes1989.ttf", size)



class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y < height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):  # position and health of the ship
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 5
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
        self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health),
        10))


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60  # frame per second
    level = 0  # levels in game
    lives = 5  # lives in game

    main_font = pygame.font.Font("font/VerminVibes1989.ttf", 50)  # creating main font and size (lives & level)
    lost_font = pygame.font.Font("font/VerminVibes1989.ttf", 60)  # creating game over font and size

    enemies = []
    wave_lenght = 4
    enemy_vel = 1  # enemy ship speed

    player_vel = 5  # player ship speed
    laser_vel = 5  # laser speed

    player = Player(400, 750)  # starting position of player ship

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():  # redrawing the screen


        if level < 5:     #changing backgrounds for level in the game
            WIN.blit(BG_1, (0, 0))  # drawing "BG" picture on 0 coordinate position
        elif level >= 5:
            WIN.blit(BG_2, (0, 0))

        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))  # format lives on screen with render
        level_label = main_font.render(f"Level: {level}", 1, (255, 0, 0))  # format level on screen with render

        WIN.blit(lives_label, (10, 10))  # drawing "lives" on screen with coordinations
        WIN.blit(level_label,
                 (WIDTH - level_label.get_width() - 10, 10))  # drawing "level" on screen with coordinations

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("YOU LOST!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()  # refresh screen for update version

    while run:
        clock.tick(FPS)  # clock set on 60 frames per second
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_lenght += 3

            if level > 1:
                lives += 1

            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

            if wave_lenght % 5 == 0:  # every 5 lvl speed up lasers & player ship
                laser_vel += 1
                player_vel += 1

        for event in pygame.event.get():  # check for event
            if event.type == pygame.QUIT:  # if we press X on top off the screen it will QUIT
                run = False
                pygame.quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
            player.y += player_vel

        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 3 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 5
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def score():   #high score
    while True:
        SCORE_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.blit(HS_BG, (0, 0))

        SCORE_TEXT = get_font(45).render("High Score screen COMING SOON", True, "Gold")
        SCORE_RECT = SCORE_TEXT.get_rect(center=(480, 360))
        SCREEN.blit(SCORE_TEXT, SCORE_RECT)

        SCORE_BACK = Button(image=None, pos=(480, 460),
                            text_input="GO BACK", font=get_font(75), base_color="White", hovering_color="Gold")

        SCORE_BACK.changeColor(SCORE_MOUSE_POS)
        SCORE_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if SCORE_BACK.checkForInput(SCORE_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(Menu_BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(90).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 125))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 200),
                             text_input="PLAY", font=get_font(35), base_color="#d7fcd4", hovering_color="White")
        SCORE_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 265),
                              text_input="HIGH SCORE", font=get_font(35), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 330),
                             text_input="QUIT", font=get_font(35), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, SCORE_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    main()
                if SCORE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    score()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


def opening_screen():
    title_font_1 = pygame.font.Font("font/VerminVibes1989.ttf", 70)
    title_font_2 = pygame.font.Font("font/VerminVibes1989.ttf", 70)
    run = True

    while run:
        WIN.blit(Opening_BG, (0, 0))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main_menu()

    pygame.quit()

opening_screen()


