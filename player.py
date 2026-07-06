import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_magic):
        super().__init__(groups)
        self.create_magic = create_magic
        try:
            image = pygame.image.load('assets/player.jpg').convert()
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
            self.image = pygame.transform.scale(image, (TILESIZE, TILESIZE))
        except:
            self.image = pygame.Surface((TILESIZE, TILESIZE))
            self.image.fill('red')
            
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -26)

        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites
        
        # Magic cooldown
        self.can_shoot = True
        self.shoot_time = 0
        self.shoot_cooldown = 400 # ms

    def input(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        if mouse_buttons[0] and self.can_shoot: # Left click
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            self.create_magic(self.rect.center)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_shoot:
            if current_time - self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def update(self):
        self.input()
        self.cooldowns()
        self.move(self.speed)
