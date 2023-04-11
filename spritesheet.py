import pygame


class SpriteSheet:

    def __init__(self, filename):
        """Load the sheet."""
        try:
            self.sheet = pygame.image.load(filename)  # convert()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectangle, colorkey=None):
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size)  # convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey=None):
        """Load a whole bunch of images and return them as a list."""
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey=None):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((200, 200))
    # screen.fill((255, 255, 255))

    filename = 'invaders_sheet.png'
    sprite_sheet = SpriteSheet(filename)
    alien1_rects = [(5, 5, 25, 20), (40, 5, 25, 20)]
    ALIEN1_IMGS = sprite_sheet.images_at(alien1_rects)
    screen.blit(ALIEN1_IMGS[1], (0, 0, 25, 20))    # transform from screen to display
    pygame.display.flip()
