import pygame
from pygame import freetype


class UIText:
    fonts = {
        'default': './res/fonts/slkscr.ttf',
        'default1': './res/fonts/manaspc.ttf',
        'system': './res/fonts/vgasysr.fon'
    }

    def __init__(self, gameboard, text_id, caption, x, y, font, size, color, bg_color, h_align, v_align, max_width, max_height,
                 timer, mov_x, mov_y):
        self.gameboard = gameboard
        self.screen = self.gameboard.screen
        self.x = x
        self.y = y
        self.font = font
        self.size = size
        self.color = color
        self.bg_color = bg_color
        self.text_id = text_id
        self.caption = caption.replace('_', ' ')
        self.timer = timer * self.gameboard.fps
        self.mov_x = mov_x
        self.mov_y = mov_y
        self.h_align = h_align
        self.v_align = v_align
        self.max_width = round(max_width * self.gameboard.square_width)

        self.redraw = True
        self.visible = True
        self.shadow = 0
        self.sh_dist_x = 1
        self.sh_dist_y = 1

        freetype.set_default_resolution(self.gameboard.square_height)
        self.text_font = pygame.freetype.Font(self.fonts[self.font], self.size)
        self.space_size = self.text_font.get_rect(' ')

        self.line_spacing = self.text_font.get_sized_height()
        self.actual_width, self.max_height = self.get_text_height()

    def tick(self):
        if self.timer > 0:
            self.timer -= 1
            self.x += self.mov_x
            self.y += self.mov_y
        if self.timer == 0:
            # self.render_list.remove(self)
            pass

    def get_text_height(self):
        text = self.caption.split()
        x, y = 0, self.line_spacing
        max_x = 0
        for text_word in text:
            if text_word == '$n':
                x, y = 0, y + self.line_spacing
                continue
            word_bounds = self.text_font.get_rect(text_word)
            if x + word_bounds.width + word_bounds.x >= self.max_width:
                x, y = 0, y + self.line_spacing
            x += word_bounds.width + self.space_size.width
            max_x = max(x, max_x)
        text_height = y + self.line_spacing
        return max_x, text_height

    def align(self, rect, ui_x, ui_y, h_align, v_align):
        rect.left = round(self.x * self.gameboard.square_width) + ui_x
        if h_align == 'center':
            rect.centerx = round(self.x * self.gameboard.square_width) + ui_x
        if h_align == 'right':
            rect.right = round(self.x * self.gameboard.square_width) + ui_x
        rect.top = round(self.y * self.gameboard.square_height + ui_y)
        if v_align == 'middle':
            rect.centery = round(self.y * self.gameboard.square_height + ui_y)
        if v_align == 'bottom':
            rect.bottom = round(self.y * self.gameboard.square_height + ui_y)

    def blitme(self, ui_x, ui_y):
        # Draw the piece at its current location.
        if self.redraw:
            self.redraw = False
            caption = self.caption.split()
            self.image = self.blit_text(caption, self.color, 0, 0)
            self.rect = self.image.get_rect()

            if self.shadow:
                self.im_shadow = self.blit_text(caption, (1, 1, 1), 0, 0)
                self.rect_shadow = self.im_shadow.get_rect()

        if self.shadow:
            self.align(self.rect_shadow, ui_x, ui_y, self.h_align, self.v_align)
            self.rect_shadow.left += self.sh_dist_x
            self.rect_shadow.top += self.sh_dist_y
            self.screen.blit(self.im_shadow, self.rect_shadow)

        self.align(self.rect, ui_x, ui_y, self.h_align, self.v_align)
        self.screen.blit(self.image, self.rect)

    def blit_text(self, text, color, offset_x, offset_y):
        text_board = pygame.Surface((self.max_width, self.max_height))
        text_board.fill(self.bg_color)
        colorkey = text_board.get_at((0, 0))
        text_board.set_colorkey(colorkey, pygame.RLEACCEL)
        self.text_font.origin = True

        x, y = 0, self.line_spacing
        for text_word in text:
            if text_word == '$n':
                x, y = 0, y + self.line_spacing
                continue
            word_bounds = self.text_font.get_rect(text_word)
            if x + word_bounds.width + word_bounds.x >= self.max_width:
                x, y = 0, y + self.line_spacing
            self.text_font.render_to(text_board, (x, y), None, color)
            x += word_bounds.width + self.space_size.width
        return text_board
