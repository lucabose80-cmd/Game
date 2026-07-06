import pygame
import os

def remove_background(image_path, output_path, tolerance=50):
    pygame.init()
    # Need a display mode to convert images
    screen = pygame.display.set_mode((100, 100), pygame.HIDDEN)
    
    img = pygame.image.load(image_path).convert_alpha()
    width, height = img.get_size()
    
    # Get top-left pixel color as the background color
    bg_color = img.get_at((0, 0))
    
    for x in range(width):
        for y in range(height):
            pixel = img.get_at((x, y))
            # Check if pixel is within tolerance of background color
            r_diff = abs(pixel.r - bg_color.r)
            g_diff = abs(pixel.g - bg_color.g)
            b_diff = abs(pixel.b - bg_color.b)
            
            if r_diff <= tolerance and g_diff <= tolerance and b_diff <= tolerance:
                img.set_at((x, y), pygame.Color(0, 0, 0, 0)) # Set to transparent
                
    pygame.image.save(img, output_path)
    print(f"Saved {output_path}")
    pygame.quit()

if __name__ == "__main__":
    if os.path.exists("assets/rock_organic.jpg"):
        remove_background("assets/rock_organic.jpg", "assets/rock_organic.png", tolerance=80)
    if os.path.exists("assets/grass_tuft.jpg"):
        remove_background("assets/grass_tuft.jpg", "assets/grass_tuft.png", tolerance=80)
    if os.path.exists("assets/player.jpg"):
        remove_background("assets/player.jpg", "assets/player.png", tolerance=80)
    if os.path.exists("assets/mage_cast_1.jpg"):
        remove_background("assets/mage_cast_1.jpg", "assets/mage_cast_1.png", tolerance=80)
    if os.path.exists("assets/mage_cast_2.jpg"):
        remove_background("assets/mage_cast_2.jpg", "assets/mage_cast_2.png", tolerance=80)
