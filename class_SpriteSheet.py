import pygame


class SpriteSheet:

    def __init__(self, filename):
        # Load the sheet.
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectangle, colorkey=False):
        # Load a specific image from a specific rectangle.
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey:
            image.set_colorkey((0,255,0), pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey=False):
        # Load a whole bunch of images and return them as a list.
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey=False):
        # Load a whole strip of images, and return them as a list.
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

    def load_grid_images(self, colorkey, width, height, num_rows, num_cols, x_margin=0, x_padding=0,
                         y_margin=0, y_padding=0):
        # Load a grid of images.
        # x_margin is space between top of sheet and top of first row.
        # x_padding is space between rows.
        # Assumes symmetrical padding on left and right.
        # Same reasoning for y.
        # Calls self.images_at() to get list of images.

        sheet_rect = self.sheet.get_rect()
        sheet_width, sheet_height = sheet_rect.size

        # To calculate the size of each sprite, subtract the two margins, 
        #   and the padding between each row, then divide by num_cols.
        # Same reasoning for y.

        x_sprite_size = width
        y_sprite_size = height

        sprite_rects = []
        for row_num in range(num_rows):
            for col_num in range(num_cols):
                # Position of sprite rect is margin + one sprite size
                #   and one padding size for each row. Same for y.
                x = x_margin + col_num * (x_sprite_size + x_padding)
                y = y_margin + row_num * (y_sprite_size + y_padding)
                sprite_rect = (x, y, x_sprite_size, y_sprite_size)
                sprite_rects.append(sprite_rect)

        grid_images = self.images_at(sprite_rects, colorkey)
        print(f"Loaded {len(grid_images)} grid images.")

        return grid_images
