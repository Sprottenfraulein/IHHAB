import pygame
from pygame import freetype


class Text:

    fonts = {
        'default': './res/fonts/slkscr.ttf',
        'default1': './res/fonts/manaspc.ttf',
        'system': './res/fonts/vgasysr.fon'
    }

    def __init__(self, gameboard, caption, x, y, font, size, color, h_align, v_align, timer, mov_x, mov_y):
        self.gameboard = gameboard
        self.screen = self.gameboard.screen
        self.x = x
        self.y = y
        self.font = font
        self.size = size
        self.color = color
        self.caption = caption.replace('_',' ')
        self.timer = timer * self.gameboard.fps
        self.mov_x = mov_x
        self.mov_y = mov_y
        self.h_align = h_align
        self.v_align = v_align

        self.visible = True
        self.shadow = 1
        self.sh_dist_x = 2
        self.sh_dist_y = 2

        freetype.set_default_resolution(self.gameboard.square_height)
        self.text_font = freetype.Font(self.fonts[self.font], self.size)

        self.gameboard.render_text_list.append(self)

    def tick(self):
        if self.timer > 0:
            self.timer -= 1
            self.x += self.mov_x
            self.y += self.mov_y
        if self.timer == 0:
            self.gameboard.render_text_list.remove(self)

    def align(self, rect, h_align, v_align):
        rect.left = self.x - self.gameboard.view_x
        if h_align == 'center':
            rect.centerx = self.x - self.gameboard.view_x
        if h_align == 'right':
            rect.right = self.x - self.gameboard.view_x
        rect.top = self.y - self.gameboard.view_y
        if v_align == 'middle':
            rect.centery = self.y - self.gameboard.view_y
        if v_align == 'bottom':
            rect.bottom = self.y - self.gameboard.view_y

    def blitme(self):
        # Draw the piece at its current location.
        self.image, self.rect = self.text_font.render(self.caption, self.color, size=self.size)
        self.align(self.rect, self.h_align, self.v_align)

        if self.shadow:
            self.im_shadow, self.rect_shadow = self.text_font.render(self.caption, (0, 0, 0), size=self.size)
            self.align(self.rect_shadow, self.h_align, self.v_align)
            self.rect_shadow.left += self.sh_dist_x
            self.rect_shadow.top += self.sh_dist_y

        if self.visible and self.in_sight():
            if self.shadow:
                self.screen.blit(self.im_shadow, self.rect_shadow)
            self.screen.blit(self.image, self.rect)

    def in_sight(self):
        if self.x + self.rect.width > self.gameboard.view_x and \
                self.x < self.gameboard.view_x + self.gameboard.sight_width and \
                self.y + self.rect.height > self.gameboard.view_y and \
                self.y < self.gameboard.view_y + self.gameboard.sight_height:
            return True

        return False