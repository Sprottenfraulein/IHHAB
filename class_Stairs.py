import pygame

class Stairs:

    def __init__(self, gameboard, rules, stairs_type, x, y):
        self.gameboard = gameboard

        self.screen = self.gameboard.screen
        self.width = self.gameboard.square_width
        self.height = self.gameboard.square_height
        self.x = x
        self.y = y
        self.drawing_depth = 5
        self.visible = False
        self.anim_prev = None

        self.rules = rules
        if 'stairs_type' not in self.rules:
            self.rules['stairs_type'] = stairs_type

        self.get_media(self.rules['media'])

        self.temp_anim = False
        self.temp_anim_timer = 0
        self.anim_forced = False

        self.gameboard.render_interior_list.append(self)

        self.checkme()

    def get_media(self, media):
        # Get animation
        self.anim_set = self.gameboard.tables.table_roll(media, 'animation_table')
        for name, anim_name in self.anim_set.items():
            self.anim_set[name] = self.gameboard.resources.animations[self.anim_set[name]]
        self.default_anim = self.anim_set['downstairs']
        self.animation = self.default_anim
        self.gameboard.set_offset_scale(self)

        # Get sounds
        self.sound_set = self.gameboard.tables.table_roll(media, 'sound_table')
        if self.sound_set is not False:
            for name, sound_name in self.sound_set.items():
                self.sound_set[name] = self.gameboard.audio.sound_bank[sound_name]

        # Get text
        self.text_set = self.gameboard.tables.table_roll(media, 'text_table')
        if self.text_set is not False:
            for name, text_name in self.text_set.items():
                self.text_set[name] = self.gameboard.resources.text_bank[text_name]

    def checkme(self):
        if self.rules['stairs_type'] == -1:
            self.animation = self.anim_set['upstairs']
        elif self.rules['stairs_type'] == 1:
            self.animation = self.anim_set['downstairs']
        else:
            self.gameboard.render_interior_list.remove(self)
        self.gameboard.set_offset_scale(self)

    def tick(self):
        if self.visible:
            self.gameboard.animtick_set.add(self.animation)

    def blitme(self):
        # Draw the piece at its current location.

        self.image = self.animation.frames[self.animation.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.x - self.gameboard.view_x + self.actual_offset_x, \
                            self.y - self.gameboard.view_y + self.actual_offset_y
        self.screen.blit(pygame.transform.scale(self.image, (self.width, self.height)), self.rect)
