import pygame
import random
from settings import *
from player import Player
from magic import MagicProjectile

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        # Hitbox slightly smaller for depth
        self.hitbox = self.rect.inflate(0, -20)

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.create_map()

    def create_map(self):
        # Load new organic rock
        try:
            image = pygame.image.load('assets/rock_organic.png').convert_alpha()
            rock_img = pygame.transform.scale(image, (TILESIZE, TILESIZE))
        except:
            rock_img = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            pygame.draw.circle(rock_img, 'gray', (TILESIZE//2, TILESIZE//2), TILESIZE//2)
            
        # Load grass tuft
        try:
            tuft_img = pygame.image.load('assets/grass_tuft.png').convert_alpha()
            tuft_img = pygame.transform.scale(tuft_img, (TILESIZE//2, TILESIZE//2))
        except:
            tuft_img = pygame.Surface((TILESIZE//2, TILESIZE//2), pygame.SRCALPHA)
            pygame.draw.circle(tuft_img, 'darkgreen', (TILESIZE//4, TILESIZE//4), 5)

        WORLD_SIZE = 4000
        NUM_ROCKS = 500
        NUM_TUFTS = 1500
        
        self.player = Player((WORLD_SIZE//2, WORLD_SIZE//2), [self.visible_sprites], self.obstacle_sprites, self.create_magic)

        # Place grass tufts
        for _ in range(NUM_TUFTS):
            x = random.randint(0, WORLD_SIZE)
            y = random.randint(0, WORLD_SIZE)
            Tile((x, y), [self.visible_sprites], 'detail', tuft_img)

        # Place clusters of rocks
        for _ in range(NUM_ROCKS // 5):
            cx = random.randint(100, WORLD_SIZE - 100)
            cy = random.randint(100, WORLD_SIZE - 100)
            
            # Keep rocks away from player spawn
            if abs(cx - WORLD_SIZE//2) < 300 and abs(cy - WORLD_SIZE//2) < 300:
                continue

            for _ in range(random.randint(3, 8)):
                rx = cx + random.randint(-40, 40)
                ry = cy + random.randint(-40, 40)
                Tile((rx, ry), [self.visible_sprites, self.obstacle_sprites], 'object', rock_img)

    def create_magic(self, pos):
        mouse_pos = pygame.mouse.get_pos()
        cam_topleft_x = self.player.rect.centerx - (self.visible_sprites.half_width / self.visible_sprites.zoom_scale)
        cam_topleft_y = self.player.rect.centery - (self.visible_sprites.half_height / self.visible_sprites.zoom_scale)
        world_mouse_x = cam_topleft_x + (mouse_pos[0] / self.visible_sprites.zoom_scale)
        world_mouse_y = cam_topleft_y + (mouse_pos[1] / self.visible_sprites.zoom_scale)
        target_pos = (world_mouse_x, world_mouse_y)
        MagicProjectile(pos, target_pos, [self.visible_sprites, self.projectiles], self.obstacle_sprites)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.projectiles.update()

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.zoom_scale = 1.0

    def custom_draw(self, player):
        internal_size = (int(self.display_surface.get_width() / self.zoom_scale),
                         int(self.display_surface.get_height() / self.zoom_scale))
        internal_surface = pygame.Surface(internal_size)
        
        # Solid natural green ground, NO GRID
        internal_surface.fill('#5ca346') 

        offset_x = player.rect.centerx - internal_size[0] // 2
        offset_y = player.rect.centery - internal_size[1] // 2

        # Draw details first (grass tufts)
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'invisible':
                continue
            
            offset_pos = sprite.rect.topleft - pygame.math.Vector2(offset_x, offset_y)
            # Frustum culling
            if -100 < offset_pos.x < internal_size[0] + 100 and -100 < offset_pos.y < internal_size[1] + 100:
                internal_surface.blit(sprite.image, offset_pos)

        scaled_surf = pygame.transform.scale(internal_surface, self.display_surface.get_size())
        self.display_surface.blit(scaled_surf, (0, 0))
