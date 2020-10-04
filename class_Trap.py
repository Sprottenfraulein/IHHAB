import pygame
from class_Text import Text
from class_Particle import Particle

class Trap:

    def __init__(self, gameboard, rules, x, y):
        self.gameboard = gameboard

        self.screen = self.gameboard.screen
        self.width = self.gameboard.square_width
        self.height = self.gameboard.square_height
        self.x = x
        self.y = y
        self.drawing_depth = 5
        self.anim_prev = None

        self.rules = rules
        if self.rules['hidden'] == 0:
            self.visible = True
        else:
            self.visible = False

        self.get_media(self.rules['media'])

        self.temp_anim = False
        self.temp_anim_timer = 0
        self.anim_forced = False

        self.gameboard.render_trap_list.append(self)

    def get_media(self, media):
        # Get animation
        self.anim_set = self.gameboard.tables.table_roll(media, 'animation_table')
        for name, anim_name in self.anim_set.items():
            self.anim_set[name] = self.gameboard.resources.animations[self.anim_set[name]]
        self.default_anim = self.anim_set['tile']
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

    def reveal(self, char):
        char.stats.stats_recalc()
        print('Attempting to reveal the trap. Difficulty', self.rules['hidden'], ', skill',
              char.stats.char_stats_modified['find_traps'], '.')
        result = self.gameboard.pick_random([char.stats.char_stats_modified['find_traps'], self.rules['hidden']],
                                            [1, 0])
        if result:
            self.rules['hidden'] = 0
            self.visible = True
            self.sound_set['reveal'].play()
            new_text = Text(self.gameboard, self.text_set['reveal'], self.x + self.width // 2, self.y,
                            'default', 18, (255, 255, 255), 'center', 'top', 1, 0, 0)
            print('Success!')
            char.stats.gain_exp(self.rules['hidden'] // 2)
            return True
        else:
            return False

    def disarm(self, char):
        if self.rules['m_trap'] == 1:
            # magic traps cannot be disarmed with tools
            return False
        else:
            tool = self.gameboard.inventory_find_item(char.inventory.backpack, item_id='tool')
            if tool is not False:
                char.stats.stats_recalc()
                print('Attempting to disarm the trap. Difficulty', self.rules['difficulty'], ', skill',
                      char.stats.char_stats_modified['disarm_traps'], '.')
                result = self.gameboard.pick_random([char.stats.char_stats_modified['disarm_traps'], self.rules['difficulty']],
                                                    [1, 0])
                if result:
                    self.gameboard.render_trap_list.remove(self)
                    self.sound_set['disarm_success'].play()
                    new_text = Text(self.gameboard, self.text_set['disarm_success'], self.x + self.width // 2, self.y,
                                    'default', 18, (255, 255, 255), 'center', 'top', 1, 0, 0)
                    print('Success!')
                    char.stats.gain_exp(self.rules['difficulty'] // 2)
                    return True
                else:
                    if tool[0].rules['amount_cur'] > 1:
                        tool[0].rules['amount_cur'] -= 1
                    else:
                        tool[1].remove(tool[0])
                    self.gameboard.ui.ragdoll_refresh(self.gameboard.ui.container_crumps[-1])
                    # self.sound_set['unlock_fail'].play()
                    new_text = Text(self.gameboard, self.text_set['disarm_fail'], self.x + self.width // 2, self.y,
                                    'default', 18, (255, 0, 0), 'center', 'top', 1, 0, 0)
                    print('Failed. Tool is lost.')
                    return False
            else:
                new_text = Text(self.gameboard, self.text_set['no_tool'], self.x + self.width // 2, self.y,
                                'default',
                                18, (255, 255, 0), 'center', 'top', 1, 0, 0)
                # self.sound_set['no_tool'].play()
                return False

    def discharge(self, target):
        trap_attack = self.gameboard.tables.table_roll(self.rules['attack'], 'combat_table')
        damage = 0
        # trap strikes
        trap_attack = self.update_attack(trap_attack)

        inflict_status = {}
        if 'debuff' in trap_attack:
            status_list = trap_attack['debuff'].split(',')
            for i in status_list:
                status = self.gameboard.tables.table_roll(i, 'status_table')
                inflict_status[i] = status

        attack_list = self.get_discharges(trap_attack)
        for attack in attack_list:
            self.gameboard.woundme(self, target, attack['damage'], attack['attack_type'], attack['damage_type'],
                                   inflict_status)
        self.sound_set['discharge'].play()
        new_particle = Particle(self.gameboard, self.anim_set['discharge'], None, 16, 0, 0,
                                    self.x, self.y)
        if self.rules['charges'] > 0:
            self.rules['charges'] -= 1
            if self.rules['charges'] == 0:
                self.gameboard.render_trap_list.remove(self)


    def update_attack(self, attack):
        for i in range(1, 7):
            value = 'value' + str(i)
            try:
                attack[value] = attack[value] * self.rules['level'] * self.rules['damage_multiplier']
            except KeyError:
                pass
        return attack

    def get_discharges(self, attack):
        attack_list = []
        for i in range(1, 7):
            parameter = 'parameter' + str(i)
            value = 'value' + str(i)
            digits = 'digits' + str(i)
            try:
                attack_dict = {
                    'damage': attack[value],
                    'attack_type': 'melee',
                    'damage_type': attack[parameter],
                }
                attack_list.append(attack_dict)
            except KeyError:
                pass
        return attack_list

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
