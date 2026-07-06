import pygame
import math
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_magic):
        super().__init__(groups)
        self.create_magic = create_magic
        
        self.frames = []
        try:
            # Load master reference and poses
            frame_files = ['assets/mage_reference.png', 'assets/mage_charge.png', 'assets/mage_shoot.png']
            for file in frame_files:
                img = pygame.image.load(file).convert_alpha()
                self.frames.append(pygame.transform.smoothscale(img, (TILESIZE, TILESIZE)))
        except:
            # Fallback frames
            for _ in range(3):
                surf = pygame.Surface((TILESIZE, TILESIZE))
                surf.fill('red')
                self.frames.append(surf)
                
        try:
            self.fireball_raw = pygame.image.load('assets/fireball.png').convert_alpha()
        except:
            self.fireball_raw = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.fireball_raw, 'orange', (16, 16), 16)
                
        self.image = self.frames[0].copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-20, -30)

        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites
        
        # Magic animation states
        self.is_charging = False
        self.is_shooting = False
        self.action_time = 0
        self.charge_duration = 300 # ms (approx 18 frames)
        self.shoot_duration = 150 # ms

    def input(self):
        if self.is_charging or self.is_shooting:
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
            self.is_charging = True
            self.action_time = pygame.time.get_ticks()

    def cooldowns_and_animations(self):
        current_time = pygame.time.get_ticks()
        
        if self.is_charging:
            time_passed = current_time - self.action_time
            progress = min(time_passed / self.charge_duration, 1.0)
            
            # Start with charge frame
            self.image = self.frames[1].copy()
            
            # Draw growing fireball
            fb_scale = 0.2 + (progress * 1.0) # grows from 0.2x to 1.2x
            fb_size = int(TILESIZE * fb_scale)
            scaled_fb = pygame.transform.smoothscale(self.fireball_raw, (fb_size, fb_size))
            
            # Rotate fireball towards mouse
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - WIDTH // 2
            dy = mouse_pos[1] - HEIGHT // 2
            
            angle = 0
            if dx != 0 or dy != 0:
                angle = math.degrees(math.atan2(-dy, dx))
            
            rotated_fb = pygame.transform.rotate(scaled_fb, angle)
            
            # Position fireball dynamically around the mage in the direction of the mouse
            tip_distance = TILESIZE * 0.4
            rad = math.atan2(dy, dx)
            local_center_x = TILESIZE / 2
            local_center_y = TILESIZE / 2
            tip_x = local_center_x + math.cos(rad) * tip_distance
            tip_y = local_center_y + math.sin(rad) * tip_distance
            
            fb_rect = rotated_fb.get_rect(center=(tip_x, tip_y))
            self.image.blit(rotated_fb, fb_rect)
            
            if progress >= 1.0:
                # Shoot!
                self.is_charging = False
                self.is_shooting = True
                self.action_time = current_time
                world_tip_x = self.rect.x + tip_x
                world_tip_y = self.rect.y + tip_y
                self.create_magic((world_tip_x, world_tip_y))
                
        elif self.is_shooting:
            self.image = self.frames[2].copy()
            if current_time - self.action_time >= self.shoot_duration:
                self.is_shooting = False
                
        else:
            self.image = self.frames[0].copy()

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        
        if not (self.is_charging or self.is_shooting):
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
