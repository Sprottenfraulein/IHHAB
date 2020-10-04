import pygame
from class_Animation import Animation


class Particle:

    def __init__(self, gameboard, animation, sound, timer, speed_x, speed_y, x, y):
        self.gameboard = gameboard

        if animation is not None:
            self.animation = animation

        else:
            self.animation = None
        if sound is not None:
            self.sound = self.gameboard.audio.sound_bank[sound]
            self.sound.play()

        self.timer = timer
        self.speed_x = speed_x
        self.speed_y = speed_y

        if self.speed_x < 0 and abs(self.speed_x) >= abs(self.speed_y):
            self.rotation_angle = 90
        elif self.speed_y > 0 and abs(self.speed_y) >= abs(self.speed_x):
            self.rotation_angle = 180
        elif self.speed_x > 0 and abs(self.speed_x) >= abs(self.speed_y):
            self.rotation_angle = 270
        else:
            self.rotation_angle = 0

        # Initialize attributes to represent the character.
        self.image = None

        self.screen = self.gameboard.screen

        # Absolute coordinates in pixels.
        self.x, self.y = x, y

        self.width = self.gameboard.square_width
        self.height = self.gameboard.square_height
        self.drawing_depth = 6
        self.gameboard.set_offset_scale(self)

        self.visible = True

        self.gameboard.render_effects_list.append(self)

    def tick(self):
        if self.animation is not None:
            self.gameboard.animtick_set.add(self.animation)

        if self.timer > 0:
            self.x += self.speed_x
            self.y += self.speed_y
            self.timer -= 1
        else:
            self.gameboard.render_effects_list.remove(self)

    def blitme(self):
        # Draw the piece at its current location.
        if self.animation is not None:
            self.image = self.animation.frames[self.animation.frame_index]

            if self.rotation_angle > 0:
                self.image = pygame.transform.rotate(self.image, self.rotation_angle)

            self.image = pygame.transform.scale(self.image, (self.width, self.height))

            self.rect = self.image.get_rect()
            self.rect.center = self.x - self.gameboard.view_x + self.actual_offset_x, \
                                self.y - self.gameboard.view_y + self.actual_offset_y
            self.screen.blit(self.image, self.rect)
