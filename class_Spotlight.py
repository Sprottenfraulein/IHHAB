import pygame

class Spotlight:

    def __init__(self, gameboard, anim_name, x, y):
        self.gameboard = gameboard

        self.screen = self.gameboard.screen
        self.x = x * self.gameboard.square_width
        self.y = y * self.gameboard.square_height
        self.drawing_depth = 100
        self.visible = True
        self.animation = self.gameboard.resources.animations[anim_name]

        self.gameboard.set_offset_scale(self)

    def tick(self):
        if self.visible:
            self.gameboard.animtick_set.add(self.animation)

    def blitme(self):
        # Draw the piece at its current location.
        if self.visible and self.in_sight():
            self.image = self.animation.frames[self.animation.frame_index]
            self.rect = self.image.get_rect()
            self.rect.topleft = self.x - self.gameboard.view_x + self.actual_offset_x, self.y - self.gameboard.view_y + self.actual_offset_y
            self.screen.blit(pygame.transform.scale(self.image, (self.width, self.height)), self.rect)

    def in_sight(self):
        if self.x + self.width > self.gameboard.view_x and \
           self.x < self.gameboard.view_x + self.gameboard.sight_width and \
           self.y + self.height > self.gameboard.view_y and \
           self.y < self.gameboard.view_y + self.gameboard.sight_height:
            return True

        return False
