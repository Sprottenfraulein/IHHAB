import pygame
import random
from class_Animation import Animation
from class_Particle import Particle
from class_Stats import Stats
from class_Inventory import Inventory
from class_Text import Text
from class_Item import Item


class Mob:
    mob_class = 'test_class'

    mob_exponential_ratio = 1.2
    # mob_exponential_multiplier = 5

    def __init__(self, gameboard, rules, level, x, y):
        self.gameboard = gameboard

        # Initialize attributes to represent the character.
        self.image = None

        self.screen = self.gameboard.screen

        # Absolute coordinates in pixels.
        self.x, self.y = x, y
        self.dest_x, self.dest_y = self.x, self.y
        self.moving = False
        self.easing = 0.5
        self.mirrored = False

        self.width = self.gameboard.square_width
        self.height = self.gameboard.square_height
        self.drawing_depth = 30
        self.visible = True
        self.anim_prev = None

        self.rules = rules.copy()
        # Adding Character Stats and Inventory
        self.gameboard.set_rules(self, self.rules)
        self.upgrade(level)
        self.get_media(self.rules['media'])

        self.gameboard.render_mobs_list.append(self)

        self.temp_anim = False
        self.temp_anim_timer = 0
        self.anim_forced = False

        self.turn_timer = 0

    def get_media(self, media):
        # Get animation
        self.anim_set = self.gameboard.tables.table_roll(media, 'animation_table')
        for name, anim_name in self.anim_set.items():
            self.anim_set[name] = Animation(self.gameboard.resources, anim_name, self.gameboard.resources.animation_files[self.anim_set[name]])
        self.default_anim = self.anim_set['idle']
        self.animation = self.default_anim
        self.gameboard.set_offset_scale(self)

        # Get sounds
        self.sound_set = self.gameboard.tables.table_roll(media, 'sound_table')
        for name, sound_name in self.sound_set.items():
            self.sound_set[name] = self.gameboard.audio.sound_bank[sound_name]

        # Get text
        self.text_set = self.gameboard.tables.table_roll(media, 'text_table')
        for name, text_name in self.text_set.items():
            self.text_set[name] = self.gameboard.resources.text_bank[text_name]

    def upgrade(self, level):
        self.stats.char_stats['strength'] = round(self.gameboard.exponential(self.mob_exponential_ratio, level, self.stats.char_stats['strength']))
        self.stats.char_stats['dexterity'] = round(self.gameboard.exponential(self.mob_exponential_ratio, level, self.stats.char_stats['dexterity']))
        self.stats.char_stats['intelligence'] = round(self.gameboard.exponential(self.mob_exponential_ratio, level, self.stats.char_stats['intelligence']))
        self.stats.char_stats['hp_max'] = round(self.gameboard.exponential(self.mob_exponential_ratio, level, self.stats.char_stats['hp_max']))
        self.stats.char_stats['mp_max'] = round(self.gameboard.exponential(self.mob_exponential_ratio, level, self.stats.char_stats['mp_max']))
        self.rules['exp'] = round(self.gameboard.exponential(self.mob_exponential_ratio, level, self.rules['exp']))
        self.stats.char_stats['level'] = level
        self.stats.stats_recalc()
        print('NEW MOB LEVEL:', self.stats.char_stats_modified['level'])
        self.stats.char_pools_maximize()
        print('MOB UPGRADED TO LEVEL', level, self.stats.char_stats_modified)

    def tick(self):
        self.gameboard.animtick_set.add(self.animation)

        if self.turn_timer > 0:
            self.turn_timer -= 1

        if self.moving:
            self.gameboard.set_anim(self, 'walk', False)
            self.moveme()
        elif self.turn_timer == 0:
            if self.visible:
                self.turn_timer = 30
            self.my_turn()

        self.gameboard.anim_check(self)

    def moveme(self):
        mov_x = self.gameboard.sign(self.dest_x - self.x) * (self.gameboard.square_width // 12)
        mov_y = self.gameboard.sign(self.dest_y - self.y) * (self.gameboard.square_height // 12)
        if mov_x or mov_y:
            self.x += mov_x
            self.y += mov_y
            if mov_x:
                self.mirrored = mov_x > 0
        else:
            self.x = self.dest_x
            self.y = self.dest_y
            self.moving = False

    def attack(self, target):
        distance = self.gameboard.get_distance(target.x, target.y, self.x, self.y)
        mob_attack = self.gameboard.tables.table_roll(self.rules['attack'], 'combat_table')

        # Mob strikes
        if distance == 1 or ('ranged' in mob_attack and 1 < distance < self.rules[
            'aggr_distance'] and self.gameboard.test_arrow(self.x + self.width // 2, self.y + self.height // 2,
                                                           target.dest_x + target.width // 2,
                                                           target.dest_y + target.height // 2)):

            self.stats.stats_recalc()
            mob_attack = self.attack_update(mob_attack)

            modifiers_dict = self.stats.get_modifiers_dict(self.inventory)
            self.stats.update_modifiers_dict(modifiers_dict, mob_attack, 3)

            inflict_status = {}
            if 'debuff' in mob_attack:
                status_list = mob_attack['debuff'].split(',')
                for i in status_list:
                    status = self.gameboard.tables.table_roll(i, 'status_table')
                    inflict_status[i] = status
            attack_list = self.stats.get_attacks(self.stats, modifiers_dict)
            for attack in attack_list:
                self.gameboard.woundme(self, target, attack['damage'], attack['attack_type'], attack['damage_type'],
                                       inflict_status)

            self.sound_set['attack'].play()

            if target.x > self.x:
                self.mirrored = True
            elif target.x < self.x:
                self.mirrored = False
            self.gameboard.set_temp_anim(self, 'attack', 16, True)

            if 'ranged' in mob_attack:
                speed_x = (target.dest_x - self.x) / 16
                speed_y = (target.dest_y - self.y) / 16
                new_particle = Particle(self.gameboard, self.anim_set['missile'], None, 16, speed_x, speed_y,
                                        self.x + self.width // 2, self.y + self.height // 2)

        # Mob move towards target
        elif 1 < distance <= self.rules['aggr_distance']:
            self.gameboard.set_anim(self, 'walk', False)
            dir_x, dir_y = self.gameboard.get_direction(target.dest_x, target.dest_y, self.x, self.y)
            if abs(dir_y) > abs(dir_x) or (abs(dir_y) == abs(dir_x) and random.randrange(0, 2) == 0):
                self.gameboard.move_object(self, self.x, self.y + self.gameboard.square_height * dir_y)
            else:
                self.gameboard.move_object(self, self.x + self.gameboard.square_width * dir_x, self.y)
        # Mob stays idle
        else:
            pass

    def attack_update(self, mob_attack):
        for i in range(1, 7):
            value = 'value' + str(i)
            try:
                print('MOB LEVEL:', self.stats.char_stats_modified['level'])
                mob_attack[value] = round(
                    self.gameboard.exponential(self.mob_exponential_ratio, self.stats.char_stats_modified['level'],
                                               mob_attack[value]))
                print('MOB DAMAGE:', mob_attack[value])
            except:
                pass
        return mob_attack

    def my_turn(self):
        if self.gameboard.mobs_turn and self.stats.char_pools['ap_cur'] > 0 and not self.moving and not self.gameboard.player_char.stop:
            self.attack(self.gameboard.player_char)
            self.stats.char_pools['ap_cur'] -= 1
            print('enemy ap left:', self.stats.char_pools['ap_cur'])
        else:
            self.gameboard.set_anim(self, 'idle', False)

    def defeated(self, attacker):
        attacker.stats.gain_exp(self.rules['exp'])
        my_drop = self.gameboard.generate_drop(self.rules['drop'], self.stats.char_stats_modified['level'])
        my_drop.extend(self.inventory.backpack)
        self.gameboard.labyrinth.drop_loot(my_drop, self.x, self.y, False)
        self.inventory.backpack.clear()

        self.gameboard.render_mobs_list.remove(self)
        self.sound_set['dead'].play()

    def blitme(self):
        # Draw the piece at its current location.
        self.image = self.animation.frames[self.animation.frame_index]

        if self.mirrored:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.topleft = self.x - self.gameboard.view_x + self.actual_offset_x, \
                                self.y - self.gameboard.view_y + self.actual_offset_y
        self.screen.blit(pygame.transform.scale(self.image, (self.width, self.height)), self.rect)
