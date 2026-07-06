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
        self.hitbox = self.rect.inflate(0, -10)

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.create_map()

    def create_map(self):
        # Load rock image
        try:
            image = pygame.image.load('assets/rock.jpg').convert()
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
            rock_img = pygame.transform.scale(image, (TILESIZE, TILESIZE))
        except:
            rock_img = pygame.Surface((TILESIZE, TILESIZE))
            rock_img.fill('gray')
            
        try:
            self.grass_img = pygame.transform.scale(pygame.image.load('assets/grass.jpg').convert(), (TILESIZE, TILESIZE))
        except:
            self.grass_img = pygame.Surface((TILESIZE, TILESIZE))
            self.grass_img.fill('green')

        # Procedural generation: Place rocks randomly within a 4000x4000 area
        # Center player at 2000, 2000
        WORLD_SIZE = 4000
        NUM_ROCKS = 400
        
        self.player = Player((WORLD_SIZE//2, WORLD_SIZE//2), [self.visible_sprites], self.obstacle_sprites, self.create_magic)

        # Place clusters of rocks
        for _ in range(NUM_ROCKS // 5):
            # Cluster center
            cx = random.randint(100, WORLD_SIZE - 100)
            cy = random.randint(100, WORLD_SIZE - 100)
            
            # Don't place on player
            if abs(cx - WORLD_SIZE//2) < 200 and abs(cy - WORLD_SIZE//2) < 200:
                continue

            for _ in range(random.randint(3, 8)):
                rx = cx + random.randint(-2, 2) * TILESIZE
                ry = cy + random.randint(-2, 2) * TILESIZE
                Tile((rx, ry), [self.visible_sprites, self.obstacle_sprites], 'object', rock_img)

    def create_magic(self, pos):
        mouse_pos = pygame.mouse.get_pos()
        
        # Convert screen mouse pos to world pos based on zoom and camera offset
        # camera screen center = visible_sprites.half_width
        
        cam_topleft_x = self.player.rect.centerx - (self.visible_sprites.half_width / self.visible_sprites.zoom_scale)
        cam_topleft_y = self.player.rect.centery - (self.visible_sprites.half_height / self.visible_sprites.zoom_scale)

        world_mouse_x = cam_topleft_x + (mouse_pos[0] / self.visible_sprites.zoom_scale)
        world_mouse_y = cam_topleft_y + (mouse_pos[1] / self.visible_sprites.zoom_scale)
        
        target_pos = (world_mouse_x, world_mouse_y)
        MagicProjectile(pos, target_pos, [self.visible_sprites, self.projectiles], self.obstacle_sprites)

    def run(self):
        self.visible_sprites.custom_draw(self.player, self.grass_img)
        self.visible_sprites.update()
        self.projectiles.update()

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        
        # Zoom setup
        self.zoom_scale = 1.0

    def custom_draw(self, player, grass_img):
        # Creating a dynamic internal surface based on zoom
        internal_size = (int(self.display_surface.get_width() / self.zoom_scale),
                         int(self.display_surface.get_height() / self.zoom_scale))
        internal_surface = pygame.Surface(internal_size)
        internal_surface.fill(BG_COLOR)

        # Camera offset is the player's position minus half the internal surface
        offset_x = player.rect.centerx - internal_size[0] // 2
        offset_y = player.rect.centery - internal_size[1] // 2

        # Draw grass grid seamlessly (only what is visible)
        start_x = int(offset_x // TILESIZE)
        start_y = int(offset_y // TILESIZE)
        cols = int(internal_size[0] // TILESIZE) + 2
        rows = int(internal_size[1] // TILESIZE) + 2

        for col in range(start_x, start_x + cols):
            for row in range(start_y, start_y + rows):
                pos = (col * TILESIZE - offset_x, row * TILESIZE - offset_y)
                internal_surface.blit(grass_img, pos)

        # Draw sprites
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'invisible':
                continue
            
            # Simple frustum culling: only draw if inside internal surface
            offset_pos = sprite.rect.topleft - pygame.math.Vector2(offset_x, offset_y)
            if -100 < offset_pos.x < internal_size[0] + 100 and -100 < offset_pos.y < internal_size[1] + 100:
                internal_surface.blit(sprite.image, offset_pos)

        # Scale to display and blit
        scaled_surf = pygame.transform.scale(internal_surface, self.display_surface.get_size())
        self.display_surface.blit(scaled_surf, (0, 0))
