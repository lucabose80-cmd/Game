import pygame
import math
from settings import *

class MagicProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos, groups, obstacle_sprites):
        super().__init__(groups)
        try:
            image = pygame.image.load('assets/magic.png').convert_alpha()
            self.image = pygame.transform.scale(image, (TILESIZE//2, TILESIZE//2))
        except:
            self.image = pygame.Surface((TILESIZE//2, TILESIZE//2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, 'blue', (TILESIZE//4, TILESIZE//4), TILESIZE//4)
        
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
            # Rotate image to face target
            angle = math.degrees(math.atan2(-dy, dx))
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.hitbox.center = self.rect.center
        
        # Check collision with rocks
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if getattr(sprite, 'sprite_type', '') == 'object':
                    sprite.kill()
                self.kill()
