import pygame
from class_Text import Text


class Item:

    rare_dict = {
        'common': {
            'chance': 1000,
            'level': 1,
            'affix_number': 0
        },
        'enchanted': {
            'chance': 500,
            'level': 10,
            'affix_number': 1
        },
        'rare': {
            'chance': 200,
            'level': 30,
            'affix_number': 2
        },
        'legendary': {
            'chance': 100,
            'level': 40,
            'affix_number': 3
        }
    }
    item_exponential_ratio = 1.1
    # item_exponential_multiplier = 1

    def __init__(self, gameboard, rules, level, x, y, upgrade=True):
        self.gameboard = gameboard

        self.screen = self.gameboard.screen
        self.width = self.gameboard.square_width
        self.height = self.gameboard.square_height
        self.dest_x = self.x = x
        self.dest_y = self.y = y
        self.drawing_depth = 80
        self.visible = False
        self.anim_prev = None
        self.rules = rules.copy()
        if upgrade:
            self.upgrade(level)

        self.get_media(self.rules['media'])

        self.temp_anim = False
        self.temp_anim_timer = 0
        self.anim_forced = False

        # self.gameboard.render_items_list.append(self)

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
        for name, sound_name in self.sound_set.items():
            self.sound_set[name] = self.gameboard.audio.sound_bank[sound_name]

        # Get text
        self.text_set = self.gameboard.tables.table_roll(media, 'text_table')
        for name, text_name in self.text_set.items():
            self.text_set[name] = self.gameboard.resources.text_bank[text_name]

    def upgrade(self, level):
        if self.rules['id'] == 'gold':
            self.rules['amount_cur'] = min(self.rules['amount_max'], round(
                self.gameboard.exponential(self.item_exponential_ratio, level, self.rules['amount_cur'])))
        elif self.rules['id'] == 'gem':
            self.rules['amount_cur'] = min(self.rules['amount_max'], round(
                self.gameboard.exponential(self.item_exponential_ratio, level, self.rules['amount_cur'])))
        elif self.rules['item_class'] == 'wpn':
            for i in range(1, 7):
                value = 'value' + str(i)
                try:
                    self.rules[value] = round(self.gameboard.exponential(self.item_exponential_ratio, level, self.rules[value]))
                except KeyError:
                    pass
        elif self.rules['item_class'] == 'arm':
            for i in range(1, 7):
                value = 'value' + str(i)
                try:
                    self.rules[value] = round(self.gameboard.exponential(self.item_exponential_ratio, level, self.rules[value]))
                except KeyError:
                    pass
        elif self.rules['item_class'] == 'amm':
            for i in range(1, 7):
                value = 'value' + str(i)
                try:
                    self.rules[value] = round(self.gameboard.exponential(self.item_exponential_ratio, level, self.rules[value]))
                except KeyError:
                    pass

        if 'level' in self.rules:
            self.rules['level'] = level

    def set_affix(self, affix):
        if affix:
            try:
                self.rules['affixes'].append(affix)
            except KeyError or TypeError:
                self.rules['affixes'] = [affix]
            for i in range(1, 4):
                parameter = 'parameter' + str(i)
                digits = 'digits' + str(i)
                value = 'value' + str(i)
                try:
                    if affix[parameter] == 'condition':
                        if affix[digits] == 'force':
                            self.rules['condition_aff'] = affix[value]
                        elif affix[digits] == 'points':
                            self.rules['condition_aff'] = self.rules['condition_max'] + affix[value]
                        elif affix[digits] == 'percent':
                            self.rules['condition_aff'] = self.rules['condition_max'] + round(
                                self.rules['condition_max'] * affix[value] / 100)
                        self.rules['condition_cur'] = self.rules['condition_aff']
                except KeyError:
                    pass
                try:
                    if affix[parameter] == 'charges':
                        if affix[digits] == 'force':
                            self.rules['charges_aff'] = affix[value]
                        elif affix[digits] == 'points':
                            self.rules['charges_aff'] = self.rules['charges_max'] + affix[value]
                        elif affix[digits] == 'percent':
                            self.rules['charges_aff'] = self.rules['charges_max'] + round(
                                self.rules['charges_max'] * affix[value] / 100)
                        self.rules['charges_cur'] = self.rules['charges_aff']
                except KeyError:
                    pass

    def compose_full_title(self):
        title = self.text_set['title']
        if self.rules['id'] == 'spellbook':
            title = title.replace('%1', str(self.rules['level']))
        if 'affixes' in self.rules:
            prefix_list = []
            suffix_list = []
            for affix in self.rules['affixes']:
                if affix['type'] == 'prefix':
                    prefix_list.append(affix['name'])
                elif affix['type'] == 'suffix':
                    suffix_list.append(affix['name'])
            if len(prefix_list) > 1:
                if len(suffix_list) > 0:
                    str_before_title = '_'.join(prefix_list[:-1]) + '_'
                    str_before_suffix = prefix_list[-1] + '_'
                else:
                    str_before_title = '_'.join(prefix_list) + '_'
                    str_before_suffix = ''
            elif len(prefix_list) == 1:
                str_before_title = prefix_list[0] + '_'
                str_before_suffix = ''
            else:
                str_before_title = ''
                str_before_suffix = ''
            if len(suffix_list) > 1:
                str_after_title = '_and_'.join(suffix_list[:-1])
                str_of = '_of_'
            elif len(suffix_list) == 1:
                str_after_title = suffix_list[0]
                str_of = '_of_'
            else:
                str_after_title = ''
                str_of = ''
            full_title_string = str_before_title + title + str_of + str_before_suffix + str_after_title
        else:
            full_title_string = title
        full_title_string = full_title_string.capitalize()
        return full_title_string

    def tick(self):
        if self.visible:
            self.gameboard.animtick_set.add(self.animation)
            self.gameboard.anim_check(self)

            if abs(self.dest_x - self.x) > 0:
                self.x = (self.dest_x + self.x) // 2
                if abs(self.dest_x - self.x) == 1:
                    self.x = self.dest_x
            if abs(self.dest_y - self.y) > 0:
                self.y = (self.dest_y + self.y) // 2
                if abs(self.dest_y - self.y) == 1:
                    self.y = self.dest_y
            # self.x += self.gameboard.sign(self.dest_x - self.x) * 1
            # self.y += self.gameboard.sign(self.dest_y - self.y) * 1

    def useme(self, char, inventory):
        if 'class' not in self.rules or char.stats.char_stats_modified['class'] in self.rules['class']:
            if 'charges_cur' in self.rules and self.rules['charges_cur'] != 0:
                discharge_value = 0
                print("ITEM USE!")
                # potions and magic items cast spells
                if self.rules['item_class'] in 'foo':
                    char.stats.char_pools['food_cur'] = min(char.stats.char_stats_modified['food_max'],
                                                            char.stats.char_pools['food_cur'] + self.rules[
                                                                'food_value'])
                    discharge_value = -1

                if self.rules['item_class'] in 'foo':
                    if 'spell' in self.rules:
                        spell = self.gameboard.magic.spells_dict[self.rules['spell']].copy()
                        spell['cost_mp'] = 0
                        try:
                            spell['level'] = self.rules['level']
                        except KeyError:
                            spell['level'] = 1
                        self.gameboard.magic.spell_cast(spell, char, char)
                        discharge_value = -1

                if self.rules['item_class'] in 'ptn':
                    if 'spell' in self.rules:
                        spell = self.gameboard.magic.spells_dict[self.rules['spell']].copy()
                        spell['cost_mp'] = 0
                        try:
                            spell['level'] = self.rules['level']
                            spell['spell_media']['sound_set']['cast'] = None
                        except KeyError:
                            spell['level'] = 1
                        self.gameboard.magic.spell_cast(spell, char, char)
                        discharge_value = -1

                if self.rules['item_class'] in 'mgc':
                    if 'spell' in self.rules:
                        spell = self.gameboard.magic.spells_dict[self.rules['spell']].copy()
                        spell['cost_mp'] = 0
                        try:
                            spell['level'] = self.rules['level']
                        except KeyError:
                            spell['level'] = 1
                        self.gameboard.magic.player_spell = spell
                        self.gameboard.magic.magic_item = self
                        self.gameboard.ui.spellbook_refresh()
                        discharge_value = 0

                if self.rules['id'] == 'spellbook':
                    if 'spell' in self.rules:
                        if not self.gameboard.magic.spell_add(self.rules):
                            return
                        discharge_value = -1

                if self.rules['id'] == 'savebook':
                    self.gameboard.save_game()

                if self.discharge(discharge_value):
                    inventory.remove(self)

                self.gameboard.ui.ragdoll_refresh(inventory)

                try:
                    play_sound = self.sound_set['use'].play()
                except:
                    pass
        char.stats.char_pools['ap_cur'] -= 1
        self.gameboard.ui.hud_refresh()

    def unpackme(self):
        if 'container' in self.rules and len(self.rules['container']) > 0:
            self.gameboard.labyrinth.drop_loot(self.rules['container'], self.x, self.y, False)
            self.rules['container'].clear()
            if 'empty' in self.anim_set:
                self.gameboard.set_anim(self, 'empty', False)
            if 'capsule' in self.rules:
                self.gameboard.render_items_list.remove(self)
            return True
        return False

    def dropme(self, start_x, start_y, dest_x, dest_y):
        self.x = start_x
        self.y = start_y
        self.gameboard.render_items_list.append(self)
        if 'flash' in self.anim_set:
            self.gameboard.set_temp_anim(self, 'flash', 9, False)
        self.dest_x = dest_x
        self.dest_y = dest_y

    def item_break(self, value):
        if 'condition_cur' in self.rules:
            if 'condition_aff' in self.rules:
                self.rules['condition_cur'] = min(self.rules['condition_aff'], self.rules['condition_cur'] + value)
            elif 'condition_max' in self.rules:
                self.rules['condition_cur'] = min(self.rules['condition_max'], self.rules['condition_cur'] + value)
            else:
                self.rules['condition_cur'] += value

            if self.rules['condition_cur'] <= 0:
                if self.rules['item_class'] in ['arm', 'hlm', 'shl', 'acc']:
                    self.gameboard.audio.sound_bank['metal_clank04'].play()
                if self.rules['item_class'] in ['wpn']:
                    self.gameboard.audio.sound_bank['metal_clank02'].play()
                return True
        return False

    def discharge(self, charges_mod):
        if 'charges_cur' in self.rules and self.rules['charges_cur'] > 0:
            self.rules['charges_cur'] += charges_mod
            if self.rules['charges_cur'] == 0 and 'disposable' in self.rules:
                try:
                    self.rules['amount_cur'] -= 1
                    if self.rules['amount_cur'] == 0:
                        return True
                    else:
                        if 'charges_aff' in self.rules:
                            self.rules['charges_cur'] = self.rules['charges_aff']
                        else:
                            self.rules['charges_cur'] = self.rules['charges_max']
                except KeyError:
                    return True
                try:
                    play_sound = self.sound_set['spent'].play()
                except:
                    pass
        return False

    def checkme(self):
        type_code = '_base'
        if 'affixes' in self.rules:
            affix_number = len(self.rules['affixes'])
            if affix_number >= 3:
                type_code = '_leg'
            elif affix_number == 2:
                type_code = '_rare'
            elif affix_number == 1:
                type_code = '_ench'
        new_anim = self.anim_set['tile'].anim_name
        new_anim = new_anim.replace('_base', type_code)
        new_anim = new_anim.replace('_ench', type_code)
        new_anim = new_anim.replace('_rare', type_code)
        new_anim = new_anim.replace('_leg', type_code)
        self.anim_set['tile'] = self.gameboard.resources.animations[new_anim]

    def blitme(self):
        # Draw the piece at its current location.

        self.image = self.animation.frames[self.animation.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.x - self.gameboard.view_x + self.actual_offset_x, \
                            self.y - self.gameboard.view_y + self.actual_offset_y
        self.screen.blit(pygame.transform.scale(self.image, (self.width, self.height)), self.rect)
