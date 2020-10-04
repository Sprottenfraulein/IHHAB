import pygame

class Interior:

    def __init__(self, gameboard, anim_name, solid, is_covering, x, y):
        self.gameboard = gameboard
        self.screen = self.gameboard.screen

        self.x = x
        self.y = y
        self.drawing_depth = 5
        self.visible = True
        self.animation = self.gameboard.resources.animations[anim_name]

        self.gameboard.set_offset_scale(self)

        if is_covering:
            self.gameboard.render_interior_covering_list.append(self)
        else:
            self.gameboard.render_interior_list.append(self)
        if solid:
            self.gameboard.solid_list.append(self)

    def tick(self):
        if self.visible:
            self.gameboard.animtick_set.add(self.animation)

    def blitme(self):
        # Draw the piece at its current location.
        self.image = self.animation.frames[self.animation.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.x - self.gameboard.view_x + self.actual_offset_x, self.y - self.gameboard.view_y + self.actual_offset_y
        self.screen.blit(pygame.transform.scale(self.image, (self.width, self.height)), self.rect)

