import pygame
from settings import *
from player import Player

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10) # 3D overlap effect

class Level:
    def __init__(self):
        # Get display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite groups
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # Setup level
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

        # Load images safely
        try:
            rock_img = pygame.transform.scale(pygame.image.load('assets/rock.jpg').convert_alpha(), (TILESIZE, TILESIZE))
        except:
            rock_img = pygame.Surface((TILESIZE, TILESIZE))
            rock_img.fill('gray')
            
        try:
            self.grass_img = pygame.transform.scale(pygame.image.load('assets/grass.jpg').convert_alpha(), (TILESIZE, TILESIZE))
        except:
            self.grass_img = pygame.Surface((TILESIZE, TILESIZE))
            self.grass_img.fill('green')

        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE
                
                if col == 'x':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'invisible') # Border
                if col == 'r':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', rock_img)
                if col == 'p':
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)

    def draw_bg(self):
        # Draw grass tiles everywhere for testing
        for x in range(-5, 25):
            for y in range(-5, 15):
                pos = (x * TILESIZE - self.visible_sprites.offset.x, y * TILESIZE - self.visible_sprites.offset.y)
                self.display_surface.blit(self.grass_img, pos)

    def run(self):
        self.draw_bg()
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # Get offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # Draw sprites sorted by Y
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            # Only draw if not invisible border
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'invisible':
                continue
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
