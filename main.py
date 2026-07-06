import pygame
import sys
from settings import *
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Exploration Game')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    self.level.visible_sprites.zoom_scale += event.y * 0.1
                    # Clamp zoom
                    if self.level.visible_sprites.zoom_scale < 0.5:
                        self.level.visible_sprites.zoom_scale = 0.5
                    if self.level.visible_sprites.zoom_scale > 2.0:
                        self.level.visible_sprites.zoom_scale = 2.0

            self.screen.fill(BG_COLOR)
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
