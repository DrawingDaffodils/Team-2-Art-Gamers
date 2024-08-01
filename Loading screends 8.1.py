import pygame
import sys
import time
import random
import math

# Initialize Pygame
pygame.init()
CLOCK = pygame.time.Clock()

# Animation intervals
ROCKET_SPEED = 4
FRUIT_SPEED = 4
SPAWN_INTERVAL = 1000
SPAWN_CHANCE = 0.05
GRAVITY = 0.45

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 830, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Space Jam')
background01 = pygame.image.load('SpaceJam.png')
background02 = pygame.image.load('background02.png')
background02 = pygame.transform.scale(background02, (int(SCREEN_WIDTH), int(SCREEN_HEIGHT)))

# Load background images
spacejam_image = pygame.image.load('SpaceJam.png').convert_alpha()
spacejam_image = pygame.transform.scale(spacejam_image, (int(SCREEN_WIDTH), int(SCREEN_HEIGHT)))

# Load buttons
play_image = pygame.image.load('play_image.png').convert_alpha()
exit_image = pygame.image.load('exit_image.png').convert_alpha()
rules_image = pygame.image.load('rules_image.png').convert_alpha()
back_image = pygame.image.load('back_image.png').convert_alpha()
start_image = pygame.image.load('start_image.png').convert_alpha()
track00_image = pygame.image.load('Track00.png').convert_alpha()
track01_image = pygame.image.load('Track01.png').convert_alpha()
track02_image = pygame.image.load('Track02.png').convert_alpha()


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False


class Rocket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        rocket_type = random.randint(0, 1)
        if rocket_type == 0:
            self.image = pygame.image.load('Rocket01.png')
        elif rocket_type == 1:
            self.image = pygame.image.load('Rocket02.png')

        pygame.transform.flip(self.image, False, True)
        self.rect = self.image.get_rect()
        random_y_pos = random.randint(200, 600)
        self.rect.center = (0, random_y_pos)

    def update(self):
        if self.rect.x != SCREEN_WIDTH:
            self.rect.x += ROCKET_SPEED

        elif self.rect.x >= SCREEN_WIDTH:
            rocket_group.remove(Rocket)


class Fruit(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        fruit_type = random.randint(0, 4)
        if fruit_type == 0:
            self.image = pygame.image.load('Banana.png')
        elif fruit_type == 1:
            self.image = pygame.image.load('Blueberry.png')
        elif fruit_type == 2:
            self.image = pygame.image.load('Mango.png')
        elif fruit_type == 3:
            self.image = pygame.image.load('Strawberry.png')
        elif fruit_type == 4:
            self.image = pygame.image.load('Watermelon.png')

        width = self.image.get_width()
        height = self.image.get_height()
        self.image = pygame.transform.scale(self.image, (int(width * 0.15), int(height * 0.15)))
        pygame.transform.flip(self.image, False, True)
        self.rect = self.image.get_rect()
        random_x_pos = random.randint(0, SCREEN_WIDTH)
        self.rect.center = (random_x_pos, 0)
        self.velocity = 0

    def update(self):
        if self.rect.y != SCREEN_HEIGHT:
            self.velocity += GRAVITY
            self.rect.y += FRUIT_SPEED

        elif self.rect.y >= SCREEN_HEIGHT:
            fruit_group.remove(Fruit)


def spawn_rocket():
    if random.random() < SPAWN_CHANCE:
        current_spawn_time = pygame.time.get_ticks()
        if current_spawn_time - last_spawn_time > SPAWN_INTERVAL:
            rocket = Rocket()
            rocket_group.add(rocket)
            all_sprites.add(rocket)


def spawn_fruit():
    if random.random() < SPAWN_CHANCE:
        current_spawn_time = pygame.time.get_ticks()
        if current_spawn_time - last_spawn_time > SPAWN_INTERVAL:
            fruit = Fruit()
            fruit_group.add(fruit)
            all_sprites.add(fruit)


# Create Groups
all_sprites = pygame.sprite.Group()
rocket_group = pygame.sprite.Group()
fruit_group = pygame.sprite.Group()
last_spawn_time = pygame.time.get_ticks()

# Main menu page (starting screen)
def main_page():
    # Create Buttons
    play_button = Button(SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 50, play_image, 0.5)
    exit_button = Button(SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 150, exit_image, 0.25)
    rules_button = Button(SCREEN_WIDTH - 50, (SCREEN_HEIGHT - 50), rules_image, .2)

    while True:
        screen.blit(background01, background01.get_rect())
        play_button.draw(screen)
        exit_button.draw(screen)
        rules_button.draw(screen)

        spawn_rocket()
        all_sprites.update()
        all_sprites.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif play_button.is_clicked(event):
                name_page()

            elif exit_button.is_clicked(event):
                goodbye_page()

            elif rules_button.is_clicked(event):
                rules_page()

        pygame.display.update()
        CLOCK.tick(60)

# Enter player name page
def name_page():
    # User input box
    font = pygame.font.SysFont('arial', 40)
    player1_text = ''
    player2_text = ''
    player1_input_rect = pygame.Rect(425, 210, 200, 50)
    player2_input_rect = pygame.Rect(425, 310, 200, 50)
    player1_color_active = pygame.Color('firebrick3')
    player2_color_active = pygame.Color('blue2')
    color_passive = pygame.Color('white')
    player1_color = color_passive
    player2_color = color_passive
    active_player1 = False
    active_player2 = False

    # Background images
    player1_image = pygame.image.load('player1_image.png').convert_alpha()
    player1_image = pygame.transform.scale(player1_image, (int(player1_image.get_width() * .25), int(player1_image.get_height() * .45)))

    player2_image = pygame.image.load('player2_image.png').convert_alpha()
    player2_image = pygame.transform.scale(player2_image, (int(player2_image.get_width() * .25), int(player2_image.get_height() * .45)))

    start_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT-150, start_image, .5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if player1_input_rect.collidepoint(event.pos):
                    active_player1 = True
                    active_player2 = False
                elif player2_input_rect.collidepoint(event.pos):
                    active_player1 = False
                    active_player2 = True
                else:
                    active_player1 = False
                    active_player2 = False

            if event.type == pygame.KEYDOWN:
                if active_player1:
                    if event.key == pygame.K_BACKSPACE:
                        player1_text = player1_text[:-1]
                    else:
                        player1_text += event.unicode
                elif active_player2:
                    if event.key == pygame.K_BACKSPACE:
                        player2_text = player2_text[:-1]
                    else:
                        player2_text += event.unicode

            if start_button.is_clicked(event):
                choose_track_page()

        screen.blit(background02, background02.get_rect())

        pygame.draw.rect(screen, player1_color_active if active_player1 else color_passive, player1_input_rect)
        pygame.draw.rect(screen, player2_color_active if active_player2 else color_passive, player2_input_rect)
        text_surface1 = font.render(player1_text, True, (0, 0, 0))
        text_surface2 = font.render(player2_text, True, (0, 0, 0))
        screen.blit(text_surface1, (player1_input_rect.x + 10, player1_input_rect.y + 5))
        screen.blit(text_surface2, (player2_input_rect.x + 10, player2_input_rect.y + 5))
        player1_input_rect.w = max(200, text_surface1.get_width() + 10)
        player2_input_rect.w = max(200, text_surface2.get_width() + 10)

        screen.blit(player1_image, (200, 200))
        screen.blit(player2_image, (205, 300))

        start_button.draw(screen)

        # Spaceships moving
        vessel_image = pygame.image.load('Vessel01.png').convert_alpha()
        vessel_image = pygame.transform.scale(vessel_image, (int(vessel_image.get_width() * .35), int(vessel_image.get_height() * .35)))
        t = pygame.time.get_ticks() / 2 % 1000
        x = t
        y = int(50 * math.sin(t/50.0) + 75)
        screen.blit(vessel_image, (x,y))

        pygame.display.update()

# Track page
def choose_track_page():
    while True:
        screen.blit(background02, background02.get_rect())
        font = pygame.font.SysFont('Comic Sans', 40, False, True)
        text_surface = font.render("CHOOSE YOUR TRACK...", True, (255, 255, 255))
        screen.blit(text_surface, (200, 20))

        track00_button = Button(300, 150, track00_image, 0.2)
        track00_button.draw(screen)
        blackberry_jam_image = pygame.image.load('blackberry_jam.png').convert_alpha()
        blackberry_jam_image = pygame.transform.scale(blackberry_jam_image, (int(blackberry_jam_image.get_width()) * .5, int(blackberry_jam_image.get_height() * .5)))
        screen.blit(blackberry_jam_image, (450, 130))

        track01_button = Button(300, 320, track01_image, 0.2)
        track01_button.draw(screen)
        strawberry_jam_image = pygame.image.load('strawberry_jam.png').convert_alpha()
        strawberry_jam_image = pygame.transform.scale(strawberry_jam_image, (int(strawberry_jam_image.get_width()) * .5, int(strawberry_jam_image.get_height() * .5)))
        screen.blit(strawberry_jam_image, (450, 305))

        track02_button = Button(300, 490, track02_image, 0.2)
        track02_button.draw(screen)
        mixedberry_jam_image = pygame.image.load('mixedberry_jam.png').convert_alpha()
        mixedberry_jam_image = pygame.transform.scale(mixedberry_jam_image, (int(mixedberry_jam_image.get_width()) * .5, int(mixedberry_jam_image.get_height() * .5)))
        screen.blit(mixedberry_jam_image, (450, 470))



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        ''' elif track00_button.is_clicked(event):
                go to track 00 page
             
            elif track01_button.is_clicked(event):
                go to track 01 page
        
            elif track02_button.is_clicked(event):
                got to track 02 page'''


        pygame.display.update()


# Game rules page
def rules_page():
    back_button = Button(50, SCREEN_HEIGHT - 50, back_image, .2)
    while True:
        screen.blit(background02, background02.get_rect())
        back_button.draw(screen)

        # Game Objective
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(30,30, 770, 150), 75, 10)
        font = pygame.font.SysFont('Comic Sans', 20, False, True)
        text_surface01 = font.render('GAME  PLAY', True, (255, 255, 255))
        screen.blit(text_surface01, ((SCREEN_WIDTH / 2) - (text_surface01.get_width() / 2), 50))

        text_surface02 = font.render(
            'Objective: Get your fleet of rockets to '
            'complete an average of 3 laps before your opponent. '
            'Sabotage your opponent by throwing fruit at their '
            'rockets to slow them down.',
            True, (255,255,255))
        screen.blit(text_surface02, (50, 80))

        # Fruit type
        banana_image = pygame.image.load('Banana.png').convert_alpha()
        banana_image = pygame.transform.scale(banana_image, (
        int(banana_image.get_width() * .1), int(banana_image.get_height() * .1)))
        screen.blit(banana_image, (250, 200))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(400, 200, 310, 50), 25, 10)
        text_surface03 = font.render('Slows opponent for 10 seconds', False, (255,255,255))
        screen.blit(text_surface03, (410, 210))

        watermelon_image = pygame.image.load('Watermelon.png').convert_alpha()
        watermelon_image = pygame.transform.scale(watermelon_image, (
        int(watermelon_image.get_width()) * .1, int(watermelon_image.get_height() * .1)))
        screen.blit(watermelon_image, (250, 275))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(400, 275, 310, 50), 25, 10)
        text_surface03 = font.render('Slows opponent for 8 seconds', False, (255, 255, 255))
        screen.blit(text_surface03, (410, 285))

        mango_image = pygame.image.load('Mango.png').convert_alpha()
        mango_image = pygame.transform.scale(mango_image, (
        int(mango_image.get_width()) * .1, int(mango_image.get_height() * .1)))
        screen.blit(mango_image, (250, 350))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(400, 350, 310, 50), 25, 10)
        text_surface03 = font.render('Slows opponent for 6 seconds', False, (255, 255, 255))
        screen.blit(text_surface03, (410, 360))

        strawberry_image = pygame.image.load('Strawberry.png').convert_alpha()
        strawberry_image = pygame.transform.scale(strawberry_image, (
        int(strawberry_image.get_width()) * .1, int(strawberry_image.get_height() * .1)))
        screen.blit(strawberry_image, (240, 425))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(400, 425, 310, 50), 25, 10)
        text_surface03 = font.render('Slows opponent for 4 seconds', False, (255, 255, 255))
        screen.blit(text_surface03, (410, 435))

        blueberry_image = pygame.image.load('Blueberry.png').convert_alpha()
        blueberry_image = pygame.transform.scale(blueberry_image, (
        int(blueberry_image.get_width()) * .08, int(blueberry_image.get_height() * .08)))
        screen.blit(blueberry_image, (265, 510))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(400, 510, 310, 50), 25, 10)
        text_surface03 = font.render('Slows opponent for 2 seconds', False, (255, 255, 255))
        screen.blit(text_surface03, (410, 520))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif back_button.is_clicked(event):
                return

        pygame.display.update()


def goodbye_page():
    timer = 0
    all_sprites.empty()
    rocket_group.empty()
    fruit_group.empty()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((250, 226, 135))

        CLOCK.tick(60)
        timer += 1 / 60

        if int(timer) < 5:
            spawn_fruit()
            all_sprites.update()
            all_sprites.draw(screen)

        elif 5 <= int(timer) <= 7:
            all_sprites.update()
            all_sprites.draw(screen)
            font = pygame.font.SysFont('Comic Sans', 100, True, True)
            text_surface = font.render("GOODBYE!", True, (255, 255, 255))
            screen.blit(text_surface, (150, 200))

        else:
            pygame.quit()
            sys.exit()
        pygame.display.update()


# Start with main page
main_page()

