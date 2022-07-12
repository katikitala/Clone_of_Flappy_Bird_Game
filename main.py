import pygame
from pygame.locals import * 
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 675
screen_height = 732
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Flappy Bird')

#define font
font = pygame.font.SysFont('Bauhaus 93', 30)

#define colours
white = (255, 255, 255)

#game variables.
ground_scroll = 0
scroll_speed = 4 
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1200 # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
top_score = 0
pass_pipe = False

#loading images.
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.count = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
            #gravity
            self.vel += 0.5
            if self.vel > 6.25:
                self.vel = 6.25
            if self.rect.bottom < 600:
                self.rect.y += int(self.vel)

        if game_over == False:
            #jumping
            keys=pygame.key.get_pressed()
            if pygame.mouse.get_pressed()[0] == 1 or keys[K_SPACE] == 1:
                if self.clicked == False:
                    self.vel = -7.8
                    self.clicked = True
            if pygame.mouse.get_pressed()[0] == 0 or keys[K_SPACE] == 0:
                self.clicked = False

            #animation
            self.count += 1
            flap_cooldown = 5

            if self.count > flap_cooldown:
                self.count = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #rotating the images(bird)
            self.image = pygame.transform.rotate(self.images[self.index], (-2) * self.vel)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        
        #pipe_gap varies with the score
        if score<100:
            pipe_gap=random.randint(300-2*score,400-2*score)
        else:
            pipe_gap=random.randint(75,125)
        #postion 1 is from top, -1 id from bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        #get mouse position
        mpos = pygame.mouse.get_pos()

        #check if mouse is over button
        if self.rect.collidepoint(mpos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #check for space bar action
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] == 1:
            action = True

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

#create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

run = True
while run:

    clock.tick(fps)

    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    #draw the ground
    screen.blit(ground_img, (ground_scroll, 600))

    #check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 5
                pass_pipe = False
    draw_text("Score:", font, white, int(100), 10)         
    draw_text(str(score), font, white, int(170), 10)
    draw_text("Best Score:", font, white, int(screen_width - 200), 10)
    draw_text(str(top_score), font, white, int(screen_width - 80), 10)

    #checking for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    #checking for ending of game
    if flappy.rect.bottom > 600:
        game_over = True
        flying = False


    if game_over == False and flying == True:

        #generating pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-80, 80)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        pipe_group.update()

        #moving the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    #reset after game over
    if game_over == True:
        if button.draw() == True:
            game_over = False
            if score > top_score:
                top_score = score
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        keys=pygame.key.get_pressed()
        if event.type == pygame.MOUSEBUTTONDOWN or keys[K_SPACE] == 1: 
            if flying == False and game_over == False:
                flying = True

    pygame.display.update()

pygame.quit()