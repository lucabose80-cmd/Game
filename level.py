import pygame
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
        WORLD_MAP = [
            'xxxxxxxxxxxxxxxxxxxx',
            'x                  x',
            'x  r      r        x',
            'x     x            x',
            'x                  x',
            'x      p           x',
            'x             x    x',
            'x    x             x',
            'x                  x',
            'xxxxxxxxxxxxxxxxxxxx'
        ]

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

        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE
                if col == 'x':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'invisible')
                if col == 'r':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', rock_img)
                if col == 'p':
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites, self.create_magic)

    def create_magic(self, pos):
        mouse_pos = pygame.mouse.get_pos()
        
        # Convert screen mouse pos to world pos based on zoom and offset
        world_mouse_x = (mouse_pos[0] - self.visible_sprites.half_width) / self.visible_sprites.zoom_scale + self.player.rect.centerx
        world_mouse_y = (mouse_pos[1] - self.visible_sprites.half_height) / self.visible_sprites.zoom_scale + self.player.rect.centery
        
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
        self.offset = pygame.math.Vector2()
        
        # Zoom setup
        self.zoom_scale = 1.0
        self.internal_surface_size = (2500, 2500)
        self.internal_surface = pygame.Surface(self.internal_surface_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surface.get_rect(center = (self.half_width, self.half_height))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surface_size)

    def custom_draw(self, player, grass_img):
        self.internal_surface.fill(BG_COLOR)

        self.offset.x = player.rect.centerx - self.internal_surface_size[0] // 2
        self.offset.y = player.rect.centery - self.internal_surface_size[1] // 2

        # Draw grass
        for x in range(0, 30):
            for y in range(0, 20):
                pos = (x * TILESIZE - self.offset.x, y * TILESIZE - self.offset.y)
                self.internal_surface.blit(grass_img, pos)

        # Draw sprites
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'invisible':
                continue
            offset_pos = sprite.rect.topleft - self.offset
            self.internal_surface.blit(sprite.image, offset_pos)

        # Scale and blit internal surface
        scaled_surf = pygame.transform.scale(self.internal_surface, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center = (self.half_width, self.half_height))
        self.display_surface.blit(scaled_surf, scaled_rect)
