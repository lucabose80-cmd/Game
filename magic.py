import pygame
import math
from settings import *

class MagicProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos, groups, obstacle_sprites):
        super().__init__(groups)
        try:
            image = pygame.image.load('assets/magic.jpg').convert()
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
            self.image = pygame.transform.scale(image, (TILESIZE//2, TILESIZE//2))
        except:
            self.image = pygame.Surface((TILESIZE//2, TILESIZE//2))
            self.image.fill('blue')
        
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, 0)
        
        self.speed = 10
        self.obstacle_sprites = obstacle_sprites
        
        # Calculate direction
        dx = target_pos[0] - pos[0]
        dy = target_pos[1] - pos[1]
        distance = math.hypot(dx, dy)
        
        if distance == 0:
            self.direction = pygame.math.Vector2(0, 1)
        else:
            self.direction = pygame.math.Vector2(dx/distance, dy/distance)

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.hitbox.center = self.rect.center
        
        # Check collision with rocks
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                # Destroy the rock (remove from all groups)
                if getattr(sprite, 'sprite_type', '') == 'object':
                    sprite.kill()
                # Destroy projectile
                self.kill()
