import pygame
import random
import math
import time

white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
blue = (0,0,255)
yellow = (255,255,0)
green = (0,255,0)


SNAKE_SIZE = 15  # size of player.snake blocks
SNAKE_SPEED = SNAKE_SIZE * .5  # speed of player.snake

APPLE_SIZE = 15  # size of apple blocks
APPLE_EATS = 3  # how much length to add when apple is eaten
MAX_TASTIES = 2

POWERUP_LENGTH = 200  # how many ticks power ups stay on
POWERUP_MULTIPLIER = 1.5  # speed multiplier for power ups
POWERUP_EATS = 7  # how much length to add when eating power up
POWERUP_COLOR = yellow

PLAYER_NUM = 1  # 1, 2, or 3


class Snake:
    def __init__(self,x,y):
        self.length = 1
        self.blocks = [Block(x,y)]
        self.dir = 0

    def move(self,speed=SNAKE_SPEED):
        offset = (0,-speed) if self.dir == 0 else (speed,0) if self.dir == 1 else (0,speed) if self.dir == 2 else (-speed,0) if self.dir == 3 else (0,0)
        self.blocks.append(Block(self.blocks[-1].x+offset[0],self.blocks[-1].y+offset[1]))
        if len(self.blocks) > self.length:
            del self.blocks[0]

    def check_overlap(self,other=None):
        other = self if other is None else other
        for i,b in enumerate(other.blocks):
            for i2,b2 in enumerate(other.blocks):
                if not i2-2 <= i <= i2+2 and b.rect.colliderect(b2.rect):
                    return True

    def draw(self,color=blue):
        for b in self.blocks:
            b.update(color)
            display.blit(b.image,(b.x,b.y))


class Entity(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.x,self.y = x,y


class Block(Entity):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image = pygame.Surface((int(SNAKE_SIZE), int(SNAKE_SIZE)))
        self.update()
        self.image.convert()
        self.rect = pygame.Rect(x, y, int(SNAKE_SIZE), int(SNAKE_SIZE))

    def update(self,color=blue):
        self.image.fill(color)


class Apple(Entity):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image = pygame.Surface((int(APPLE_SIZE), int(APPLE_SIZE)))
        self.image.set_colorkey(white)
        self.update()
        self.image.convert()
        self.rect = pygame.Rect(x, y, int(APPLE_SIZE), int(APPLE_SIZE))

    def update(self):
        self.image.fill(white)
        pygame.draw.circle(self.image,red,(int(APPLE_SIZE/2),int(APPLE_SIZE/2)),int(APPLE_SIZE/2))


class PowerUp(Entity):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image = pygame.Surface((int(APPLE_SIZE), int(APPLE_SIZE)))
        self.image.set_colorkey(white)
        self.update()
        self.image.convert()
        self.rect = pygame.Rect(x, y, int(APPLE_SIZE), int(APPLE_SIZE))

    def update(self):
        self.image.fill(white)
        pygame.draw.circle(self.image,yellow,(int(APPLE_SIZE/2),int(APPLE_SIZE/2)),int(APPLE_SIZE/2))


class Player:
    def __init__(self,x,y,color=blue,controls=(pygame.K_UP,pygame.K_RIGHT,pygame.K_DOWN,pygame.K_LEFT)):
        self.snake = Snake(x,y)
        self.color = color
        self.controls = controls
        self.powered_up = False


display_width = 600
display_height = 600


def return_random_pos(padding=APPLE_SIZE):
    return random.randint(padding,display_width-padding),random.randint(padding,display_height-padding)

pygame.init()

display = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("Python Snake")
clock = pygame.time.Clock()

pygame.font.init()

header_font = pygame.font.SysFont('Comic Sans MS', 60)
small_font = pygame.font.SysFont('Comic Sans MS', 30)


while True:
    tasties = [Apple(*return_random_pos())]

    if PLAYER_NUM == 3:
        players = [Player(int(display_width / 2), int(display_height / 2)),
                   Player(int(display_width / 2), int(display_height / 2), color=red,
                          controls=(pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_a)),
                   Player(int(display_width / 2), int(display_height / 2), color=green,
                          controls=(pygame.K_i, pygame.K_l, pygame.K_k, pygame.K_j))]
    elif PLAYER_NUM == 2:
        players = [Player(int(display_width/2),int(display_height/2)),
                   Player(int(display_width/2),int(display_height/2),color=red,controls=(pygame.K_w,pygame.K_d,pygame.K_s,pygame.K_a))]
    elif PLAYER_NUM == 1:
        players = [Player(int(display_width/2),int(display_height/2))]

    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                for player in players:
                    original_dir = player.snake.dir
                    for c,control in enumerate(player.controls):
                        if event.key == control:
                            player.snake.dir = c
                            break
                    if player.snake.dir == original_dir+2 or player.snake.dir == original_dir-2:
                        player.snake.dir = original_dir

        display.fill(white)

        for player in players:
            if player.powered_up is not False:
                player.powered_up += 1
                if player.powered_up >= POWERUP_LENGTH:
                    player.powered_up = False

            player.snake.move(SNAKE_SPEED if player.powered_up is False else SNAKE_SPEED * POWERUP_MULTIPLIER)
            for other in players:
                if player.powered_up is False and player.snake.check_overlap(other.snake):
                    game_over = True
            player.snakepos = player.snake.blocks[-1].x,player.snake.blocks[-1].y
            if not 0 < player.snakepos[0] < display_width or not 0 < player.snakepos[1] < display_height:
                game_over = True
            player.snake.draw(player.color if player.powered_up is False else POWERUP_COLOR)

        for t in tasties:
            if isinstance(t,Apple):
                t.update()
                display.blit(t.image,(t.x,t.y))
                for player in players:
                    if t.rect.colliderect(player.snake.blocks[-1].rect):
                        player.snake.length += APPLE_EATS
                        del tasties[tasties.index(t)]
                        break
            elif isinstance(t,PowerUp):
                t.update()
                display.blit(t.image,(t.x,t.y))
                for player in players:
                    if t.rect.colliderect(player.snake.blocks[-1].rect):
                        player.powered_up = 0
                        player.snake.length += POWERUP_EATS
                        del tasties[tasties.index(t)]
                        break

        if len(tasties) < MAX_TASTIES:
            if random.randint(0,1) == 0:
                tasties.append(Apple(*return_random_pos()))
            else:
                tasties.append(PowerUp(*return_random_pos()))

        pygame.display.update()
        clock.tick(60)

    score = sum([p.snake.length for p in players])
    pygame.draw.rect(display,green,(int(display_width/2-100),int(display_height/2-100),200,200))
    text = header_font.render(str(score), False, black)
    display.blit(text,(int(display_width/2-len(str(score))*16),int(display_height/2-60)))
    text = small_font.render("Press Space", False, black)
    display.blit(text, (int(display_width / 2 - 83), int(display_height / 2 + 50)))
    pygame.display.update()

    restart = False

    while not restart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    restart = True
