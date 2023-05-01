import pygame
import os
import math
import random

pygame.init()

# controls the screen size
screen_height = 800
screen_width = 600

# class Knight()
# player = Knight(screen_height, screen_width)

screen = pygame.display.set_mode((screen_height, screen_width))
pygame.display.set_caption("Fable")
scroll_thresh = 0
scroll = 2
bg_scroll = 0
level = 1
gravity = 1
rows = 16
cols = 150
tile_size = screen_height // rows
tile_types = 21

# COLORS
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
font = pygame.font.SysFont('arial', 20, bold=True)
text = font.render("Move: W,A,S,D.   Attack: K (hold, atm)", True, white)
textrect = text.get_rect()
textrect.center = ((600, 30 ))
# here is where I define the action variables
move_left = False
move_right = False
player_attack = False
player_attacking = False

# AI VARIABLES
enemy_attack = False
ai_moving_left = False
ai_moving_right = False

# LOADS THE BACKGROUND IMAGE
imgbg = pygame.image.load("img/background.png")
bg = pygame.transform.scale(imgbg, (imgbg.get_width() * 1.7, imgbg.get_height() * 1.5))
stagePosX = 0
startScroolingPosX = screen.get_width() / 2

bg_width = bg.get_width()
bg_height = bg.get_height()

circleRadious = 25
circlePodX = circleRadious

# LOAD ITENS
imgheartitem = pygame.image.load('img/heart.png').convert_alpha()
heartitem = pygame.transform.scale(imgheartitem, (imgheartitem.get_width() * 0.009, imgheartitem.get_height() * 0.009))
item_box = {
    'Health': heartitem
}


tiles = math.ceil(screen_width / bg_width) + 1

def draw_bg():
    screen.fill(bg)



# here is a class Knight to build the character with his atributes
class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, strength, speed, health):
        pygame.sprite.Sprite.__init__(self)
        self.dx = 0
        self.dy = 0
        self.health = health
        self.max_health = self.health
        self.side = 1
        self.alive = True
        self.gravity = 1
        self.y_speed = 0
        self.strength = strength
        self.y = y
        self.x = x
        self.char_type = char_type
        self.scale = scale
        self.speed = speed
        self.direction = 1
        self.jump = False
        self.jumped = False
        self.flip = False
        self.move_counter = 0
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0-idle, 1-run, 2-jump, 3- attack 4- death
        self.update_time = pygame.time.get_ticks()
        self.num_frames = len(os.listdir(f'img/Knight/attack'))

        # AI VARIABLES ONLY
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.visionarea = pygame.Rect(0, 0, 40, 20)

        # GET A LIST OF ANIMATIONS AND FEEDS IT INTO AN ARRAY
        animation_types = ['idle', 'run', 'jump', 'attack', 'death']
        for animation in animation_types:
            # renews temp list of sprites
            temp_list = []
            # count sprites on the folder
            num_frames = len(os.listdir(f'img/{self.char_type}/{animation}')) - 1
            for i in range(num_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{animation}{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)



    def checkhealth(self):
        if self.health <= 0:
            self.alive = False
            self.speed = 0
            self.update_action(4)
            pygame.time.wait(4)
            self.kill()
            if self.char_type == 'Knight':
                if enemy.alive:
                    enemy.update_action(0)
                if enemy2.alive:
                    enemy2.update_action(0)


    def move(self, move_left, move_right):
        screen_scroll = 0
        # this changes the movement variable back to 0
        dx = 0
        dy = 0

        # MOVES THE CHARACTER, LEFT AND RIGHT, DEPENDS ON THE BUTTON PRESSED
        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if not player_attack:
            # MAKES THE PLAYER JUMP
            if self.jump == True and self.jumped == False:
                self.y_speed = -20
                self.speed = 7
                self.jump = False
                self.jumped = True

        # MAKES SO IT IS EFFECTED BY "GRAVITY"
        self.y_speed += self.gravity
        if self.y_speed > 10:
            self.y_speed -= 1
        dy += self.y_speed

        # CHECKS CHARACTER COLISION
        if self.rect.bottom + dy > 480:
            dy = 480 - self.rect.bottom
            self.jumped = False
            self.speed = 4

        self.rect.x += dx
        self.rect.y += dy


        if self.rect.left < scroll_thresh or self.rect.right > screen_width + 200:
            self.rect.x -= dx
            screen_scroll = -dx

        return screen_scroll

    # DRAWNS THE CHARACTER
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def draw_health_bar(self, health, x, y):
        ratio = self.health / 100
        pygame.draw.rect(screen, green, (x, y, 400 * ratio, 10), 2)

    # DEFINES ENEMY INTELIGENCE
    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.idling = True
                self.update_action(0)  # idle action
                self.idling_counter = 50

            # CHECK IF AI CAN SEE THE PLAYER
            if self.visionarea.colliderect(player.rect):
                # stop running and look at the player
                self.Attack()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # RUN ACTION
                    self.move_counter += 1

                    # UPDATE AI VISION AS THE ENEMY MOVES
                    self.visionarea.center = (self.rect.centerx + 20 * self.direction, self.rect.centery)

                    if self.move_counter > random.randint(30, 200):
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

    def update_animation(self):
        animation_cooldown = 100
        if player_attack:
            animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]

        # CHECK IF IT PASSED ENOUGH TIME BETWEEN ANIMATIONS
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 4:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

        # this will change the side where the character will hit
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            self.side = 0
        if key[pygame.K_d]:
            self.side = 1

    # ATTACK DEFINITION
    def Attack(self):
        self.update_action(3)
        side = self.direction
        if self.char_type == 'Knight':
            if side == 1:
                attack_rect = pygame.Rect(self.rect.x + 75, self.rect.y, self.scale * 20, self.scale * 30)
            if side == -1:
                attack_rect = pygame.Rect(self.rect.x - 10, self.rect.y, self.scale * 20, self.scale * 30)
        else:
            if side == 1:
                attack_rect = pygame.Rect(self.rect.x + 75, self.rect.y, self.scale * 5, self.scale * 30)
            if side == -1:
                attack_rect = pygame.Rect(self.rect.x - 10, self.rect.y, self.scale * 5, self.scale * 30)
        enemy_hitbox = pygame.Rect(enemy.rect.x + 25, enemy.rect.y, enemy.scale * 20, enemy.scale * 30)
        enemy2_hitbox = pygame.Rect(enemy2.rect.x + 25, enemy2.rect.y, enemy2.scale * 20, enemy2.scale * 30)

        if self.char_type == 'Knight':
            if attack_rect.colliderect(enemy_hitbox):
                if self.frame_index in (4, 5, 6):
                    enemy.health -= self.strength
                    enemy.rect.x += player.direction * 10
            elif attack_rect.colliderect(enemy2_hitbox):
                if self.frame_index in (4, 5, 6):
                    enemy2.health -= self.strength
                    enemy2.rect.x += player.direction * 10

        elif attack_rect.colliderect(player.rect):
            if self.frame_index == 6:
                player.health -= self.strength
                player.rect.x += enemy.direction * 20

    def update(self):

        self.rect = pygame.Rect(self.rect.x, self.rect.y, player.scale * 15, player.scale * 30)

#THIS WILL CREATE THE SIDE-SCROLLING EFFECT USING TILES. I'LL COME BACK TO THIS LATER.(UNFINISHED)
# class World():
#     def __init__(self):
#         self.obstacle_list = []
#
#     def process_data(self, data):
#         #FIND OUT WHERE IS THE ITEMS WITHIN THE LEVEL
#         for y, row in enumerate(data):
#             for x, tile in enumerate(row):
#                 if tile >= 0:
#                     img = img_list[tile]
#                     img_rect = img.get_rect()
#                     img_rect.x = x * tile_size
#                     img_rect.y = y * tile_size
#                     tile_data = (img, img_rect)
#                     if tile >= 0 and tile <= 0:
#                         self.obstacle_list.append(tile_data)
#                     elif tile >= 9 and tile <= 10:
#                         pass#water
#                     elif tile >= 11 and tile <= 14:
#                         pass#decoration
#                     elif tile == 15:#create player
#                         player = Character("Knight", x = tile_size, y = tile_size)
#                         player_health = HealthBar(10, 10, player.health, player.max_health)
#                     elif tile == 16:#create enemy
#                         enemy = Character("Bandit", x = tile_size, y = tile_size)
#                         enemy_group.add(enemy)


# CLASS TO CONTROL THE ITENS, AND IF THE PLAYER GOT THEM
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_box[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                print("got it")
                player.health += 125
                if player.health > player.max_health:
                    player.health = player.max_health
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        pygame.draw.rect(screen, red, (self.x, self.y, self.max_health * 10, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, self.health * 10, 20))


#THIS WILL BE SOME SORT OF AN SHOOT ABILITY. BEEING IT FOR THE PLAYER OR THE ENEMY. (UNFINISHED)
# class shot(pygame.sprite.Sprite):
#     def __init__(self, x, y, direction):
#         pygame.sprite.Sprite.__init__(self)
#         self.speed = 10
#         for magic in magicbook:
#             self.image = (f'img/{magic}')
#         self.direction = direction
#         self.rect.center = (x, y)


# FPS CONTROL
clock = pygame.time.Clock()
fps = 50

# GROUPS THE SPRITES
item_box_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

itembox = ItemBox('Health', 100, 300)
item_box_group.add(itembox)

player = Character("Knight", 400, 420, 4, 10, 4, 30)
player_health = HealthBar(10, 10, player.health, player.max_health)

# ENEMY
enemy = Character("Bandit", 600, 420, 4, 7, 3, 200)
enemy_group.add(enemy)
enemy2 = Character("Bandit", 500, 420, 4, 7, 3, 200)

# CREATE WORLD LEVEL
# world_data = []
# for row in range(rows):
#     r = [-1] * cols
#     world_data.append(r)

# CREATE WORLD
# with open(f'level{level}_data.csv', newline='') as csvfile:
#     reader = csv.reader(csvfile, delimiter=',')
#     for x, row in enumerate(reader):
#         for y, tile in enumerate(row):
#             world_data[x][y] = int(tile)
#

while True:
    # CONTROLS FPS
    clock.tick(fps)
    print(player.frame_index)
    i = 0

    screen.blit(bg, (bg.get_width() * i + 6, 0))


    if abs(scroll) > bg.get_width():
        scroll = 0
    # BLIT THE SAME IMAGE X TIMES
    # for i in range(0, tiles):
    #     screen.blit(bg, (i * bg_width + screen_scroll , 0))
    #     bg_width = bg_width + i * bg_width * screen_scroll
    #     # pygame.draw.rect(screen, red, bg_rect, 1)

    # scrolls the background

    # reset scroll
    # if abs(scroll) > bg_width:
    #     scroll = 0

    player.checkhealth()
    player.draw()
    player.update_animation()
    player_health.draw(player.health)
    player.move(move_left, move_right)
    # for enemy in enemy_group:
    #     enemy.update()
    enemy.checkhealth()
    enemy.draw()
    enemy.draw()
    enemy.update_animation()
    enemy.ai()

    enemy2.checkhealth()
    enemy2.draw()
    enemy2.draw()
    enemy2.update_animation()
    enemy2.ai()

    item_box_group.draw(screen)
    item_box_group.update()

    screen.blit(text, textrect)
    # MAKES THE CHARACTER TO JUMP - NOT WORKING -
    # if player.jump:
    #     player.y -= y_speed
    #     y_speed -= y_gravity
    #     if y_speed < -jump_height:
    #         player.jump = False

    if player.alive:
        if player_attack:
            player.Attack()  # attack action
        elif player.jumped:
            player.update_action(2)  # jump action
        elif move_left or move_right:
            player.update_action(1)  # 1 means that it will run - REMEMBER TO CHANGE TO WALK LATER
        else:
            player.update_action(0)  # so it remains idle

        screen_scroll = player.move(move_left, move_right)

    # CLOSES THE WINDOW IF THE QUIT BUTTON IS PRESSED
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            exit()

        # CONTROLS CHARACTER
        if player.alive:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_a:
                    move_left = True
                if e.key == pygame.K_d:
                    move_right = True
                if e.key == pygame.K_w and player.alive:
                    player.jump = True
                if e.key == pygame.K_k and player.alive:
                    player_attack = True

        if e.type == pygame.KEYUP:
            if e.key == pygame.K_a:
                move_left = False
            if e.key == pygame.K_d:
                move_right = False
            if e.key == pygame.K_k:
                player_attack = False

        # CHECKS IF ENEMY HAS DIED
        if enemy.health <= 0:
            enemy.update_action(4)
            enemy.alive = False
            enemy.kill()
    player.draw()

    pygame.display.update()
