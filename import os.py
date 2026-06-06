import os
import random
import math
import pygame
from os import listdir, name
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 800, 600
FPS=60 
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]
           
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites= []
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
        
    return all_sprites

def get_block(size):
    path = join("assets", "terrain", "Terrain.png")
    image= pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("main_characters", "ninja_frog", 32, 32, True)
    SPRITES = load_sprite_sheets("main_characters", "virtual_guy", 32, 32, True)
    SPRITES = load_sprite_sheets("main_characters", "pink_man", 32, 32, True)
    SPRITES = load_sprite_sheets("main_characters", "masked_dude", 32, 32, True)
    print("Choose your character: 1.ninja frog, 2.virtual guy, 3.pink man, 4.masked dude: ")
    choice = input("please enter 1, 2, 3, or 4: ")
    if choice == "1":
        SPRITES = load_sprite_sheets("main_characters", "ninja_frog", 32, 32, True)
    elif choice == "2":
        SPRITES = load_sprite_sheets("main_characters", "virtual_guy", 32, 32, True)
    elif choice == "3":
        SPRITES = load_sprite_sheets("main_characters", "pink_man", 32, 32, True)
    elif choice == "4":
        SPRITES = load_sprite_sheets("main_characters", "masked_dude", 32, 32, True)
    else:
        print("Invalid choice, defaulting to pink man.")
        SPRITES = load_sprite_sheets("main_characters", "pink_man", 32, 32, True)
    ANIMATION_DELAY = 2

    def __init__(self, x, y,width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0 
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel   
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()
    
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit" 
        elif self.y_vel < 0:
            if self.fall_count ==1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY *2:
            sprite_sheet = "fall"
        elif self.x_vel !=0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //self.ANIMATION_DELAY) % len(sprites) 
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask=pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))



class Object(pygame.sprite.Sprite):
    def __init__ (self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)




class Fire(Object):
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("traps", "fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"


    def on(self):
        self.animation_name = "on"
    
    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites) 
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask=pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
            self.animation_count = 0

def get_background(name):
    #rearrange files and folders in assets then edit code below 
    image = pygame.image.load(join("assets", "background", name))
    _,_, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH//width + 1):
        for j in range(HEIGHT//height + 1):
            pos = (i*width, j*height)
            tiles.append(pos)
    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x, offset_y):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    player.x_vel = 0
    if (keys[pygame.K_LEFT] and not collide_left) or (keys[pygame.K_a] and not collide_left):
        player.move_left(PLAYER_VEL)
    elif (keys[pygame.K_RIGHT] and not collide_right) or (keys[pygame.K_d] and not collide_right):
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    print("Welcome to the platformer game!")
    print("Use the arrow keys or WASD to move and jump")
    print("Before we start, choose your bg color, 1. blue, 2.brown, 3.gray, 4.green, 5.pink, 6.purple, 7.yellow")
    color_choice = input("please enter 1, 2, 3, 4, 5, 6, or 7: ")
    if color_choice == "1":
        background, bg_image = get_background("Blue.png")
    elif color_choice == "2":
        background, bg_image = get_background("Brown.png")
    elif color_choice == "3":
        background, bg_image = get_background("Gray.png")
    elif color_choice == "4":
        background, bg_image = get_background("Green.png")
    elif color_choice == "5":
        background, bg_image = get_background("Pink.png")
    elif color_choice == "6":
        background, bg_image = get_background("Purple.png")
    elif color_choice == "7":
        background, bg_image = get_background("Yellow.png")
    else:
        print("Invalid choice, defaulting to pink.")
        background, bg_image = get_background("Pink.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) 
            for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, fire, Block(0, HEIGHT - block_size * 2, block_size),
                Block(block_size * 5, HEIGHT - block_size * 6, block_size),
                Block(block_size * 9, HEIGHT - block_size * 6, block_size),
                Block(block_size * 10, HEIGHT - block_size * 7, block_size),
                Block(block_size * 10, HEIGHT - block_size * 9, block_size),
                Block(block_size * 6, HEIGHT - block_size * 10, block_size),
                Block(block_size * 3, HEIGHT - block_size * 10, block_size),
                Block(block_size * 0, HEIGHT - block_size * 10, block_size),
                Block(block_size * -2, HEIGHT - block_size * 8, block_size),
                Block(block_size * -4, HEIGHT - block_size * 6, block_size),
                Block(block_size * -6, HEIGHT - block_size * 4, block_size),
                Block(block_size * -4, HEIGHT - block_size * 2, block_size),
                Block(block_size * 3, HEIGHT - block_size * 4, block_size),]


    offset_x = 0
    offset_y = 0
    scroll_area_width = 200
    scroll_area_height = 150
    #blocks= [Block(0, HEIGHT - block_size, block_size)]

    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if event.type == pygame.KEYDOWN:
                if event.key == (pygame.K_SPACE and player.jump_count < 2) or (event.key == pygame.K_UP and player.jump_count < 2) or (event.key == pygame.K_w and player.jump_count < 2):
                    player.jump() 


        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x, offset_y)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        if ((player.rect.top - offset_y >= HEIGHT - scroll_area_height) and player.y_vel > 0) or ((player.rect.bottom - offset_y <= scroll_area_height) and player.y_vel < 0):
            offset_y += player.y_vel
        

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)