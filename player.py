import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_magic):
        super().__init__(groups)
        self.create_magic = create_magic
        
        self.frames = []
        try:
            # Load individual frames
            frame_files = ['assets/player.png', 'assets/mage_cast_1.png', 'assets/mage_cast_2.png']
            for file in frame_files:
                img = pygame.image.load(file).convert_alpha()
                self.frames.append(pygame.transform.scale(img, (TILESIZE, int(TILESIZE * 1.5))))
        except:
            # Fallback frames
            for _ in range(3):
                surf = pygame.Surface((TILESIZE, TILESIZE))
                surf.fill('red')
                self.frames.append(surf)
                
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-20, -30)

        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites
        
        # Magic cooldown and animation
        self.is_casting = False
        self.shoot_time = 0
        self.shoot_cooldown = 400 # ms

    def input(self):
        if self.is_casting:
            self.direction.x = 0
            self.direction.y = 0
            return

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

        if mouse_buttons[0]: # Left click
            self.is_casting = True
            self.shoot_time = pygame.time.get_ticks()
            self.create_magic(self.rect.center)

    def cooldowns_and_animations(self):
        current_time = pygame.time.get_ticks()
        if self.is_casting:
            time_passed = current_time - self.shoot_time
            if time_passed >= self.shoot_cooldown:
                self.is_casting = False
                self.image = self.frames[0]
            else:
                # Calculate which frame to show
                progress = time_passed / self.shoot_cooldown
                frame_idx = int(progress * 3) # 0, 1, or 2
                if frame_idx > 2: frame_idx = 2
                self.image = self.frames[frame_idx]
        else:
            self.image = self.frames[0]

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        
        if not self.is_casting:
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
        self.cooldowns_and_animations()
        self.move(self.speed)
