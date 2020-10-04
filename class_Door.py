import pygame
from class_Text import Text


class Door:

    def __init__(self, gameboard, rules, x, y):
        self.gameboard = gameboard

        self.screen = self.gameboard.screen
        self.width = self.gameboard.square_width
        self.height = self.gameboard.square_height
        self.x = x
        self.y = y
        self.drawing_depth = 40
        self.visible = True
        self.anim_prev = None
        self.rules = rules.copy()

        self.get_media(self.rules['media'])

        self.temp_anim = False
        self.temp_anim_timer = 0
        self.anim_forced = False

        self.gameboard.render_interior_list.append(self)

        self.checkme()

    def get_media(self, media):
        # Get animation
        self.anim_set = self.gameboard.tables.table_roll(media + '_' + self.rules['align'], 'animation_table')
        for name, anim_name in self.anim_set.items():
            self.anim_set[name] = self.gameboard.resources.animations[self.anim_set[name]]
        self.default_anim = self.anim_set['opened']
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

    def picklock(self, char):
        if self.rules['m_lock'] == 1:
            new_text = Text(self.gameboard, self.text_set['m_lock'], self.x + self.width // 2, self.y, 'default', 18, (255,0,255), 'center', 'top', 1, 0,0)
            self.sound_set['m_lock'].play()
            return False
        else:
            lockpick = self.gameboard.inventory_find_item(char.inventory.backpack, item_id='lockpick')
            if lockpick is not False:
                char.stats.stats_recalc()
                print('Attempting to pick the lock. Difficulty', self.rules['lock'], ', skill', char.stats.char_stats_modified['pick_locks'], '.')
                result = self.gameboard.pick_random([char.stats.char_stats_modified['pick_locks'], self.rules['lock']], [1, 0])
                if result:
                    char.stats.gain_exp(self.rules['lock'])
                    self.rules['lock'] = 0
                    self.checkme()
                    self.sound_set['unlock_success'].play()
                    new_text = Text(self.gameboard, self.text_set['unlock_success'], self.x + self.width // 2, self.y,
                                    'default', 18, (255, 255, 255), 'center', 'top', 1, 0, 0)
                    print('Success!')

                    return True
                else:
                    if lockpick[0].rules['amount_cur'] > 1:
                        lockpick[0].rules['amount_cur'] -= 1
                    else:
                        lockpick[1].remove(lockpick[0])
                    self.gameboard.ui.ragdoll_refresh(self.gameboard.ui.container_crumps[-1])
                    self.sound_set['unlock_fail'].play()
                    new_text = Text(self.gameboard, self.text_set['unlock_fail'], self.x + self.width // 2, self.y,
                                    'default', 18, (255, 0, 0), 'center', 'top', 1, 0, 0)
                    print('Failed. Lockpick has broken.')
                    return False
            else:
                new_text = Text(self.gameboard, self.text_set['no_lockpick'], self.x + self.width // 2, self.y, 'default',
                                18, (255, 255, 0), 'center', 'top', 1, 0, 0)
                self.sound_set['no_lockpick'].play()
                return False

    def tick(self):
        if self.visible:
            self.gameboard.animtick_set.add(self.animation)

    def checkme(self):
        if self.rules['closed'] == 1:
            if self.rules['m_lock'] == 1:
                self.animation = self.anim_set['m_lock']
            elif self.rules['lock'] > 0:
                self.animation = self.anim_set['locked']
            else:
                self.animation = self.anim_set['closed']
        else:
            self.animation = self.anim_set['opened']
        self.gameboard.set_offset_scale(self)

    def blitme(self):
        # Draw the piece at its current location.
        self.image = self.animation.frames[self.animation.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.x - self.gameboard.view_x + self.actual_offset_x, \
                            self.y - self.gameboard.view_y + self.actual_offset_y
        self.screen.blit(pygame.transform.scale(self.image, (self.width, self.height)), self.rect)

