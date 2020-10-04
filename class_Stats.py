import random
from class_Text import Text


class Stats:
    dam_types = {
        'dam_cut': {'dam_base': 'strength', 'dam_max': 'dexterity', 'dam_median_mod': 'intelligence'},
        'dam_pierce': {'dam_base': 'strength', 'dam_max': 'dexterity', 'dam_median_mod': 'intelligence'},
        'dam_bash': {'dam_base': 'strength', 'dam_max': 'dexterity', 'dam_median_mod': 'intelligence'},
        'dam_poison': {'dam_base': 'strength', 'dam_max': 'dexterity', 'dam_median_mod': 'intelligence'},
        'dam_fire': {'dam_base': 'strength', 'dam_max': 'dexterity', 'dam_median_mod': 'intelligence'},
        'dam_ice': {'dam_base': 'strength', 'dam_max': 'dexterity', 'dam_median_mod': 'intelligence'},
        'dam_lightning': {'dam_base': 'strength', 'dam_max': 'dexterity', 'dam_median_mod': 'intelligence'},
        'dam_arcane': {'dam_base': 'strength', 'dam_max': 'dexterity', 'dam_median_mod': 'intelligence'}
    }
    def_types = ['def_cut', 'def_pierce', 'def_bash', 'def_poison', 'def_fire', 'def_ice', 'def_lightning', 'def_arcane']
    levelup_hp_bonus = 10
    levelup_mp_bonus = 10
    levelup_sp_bonus = 9

    def __init__(self, gameboard, character, rules):
        self.gameboard = gameboard
        self.character = character
        self.char_stats = {
            'char': None,
            'class': 'fighter',
            'level': 1,
            'strength': 10,
            'dexterity': 5,
            'intelligence': 1,
            'mp_max': 0,
            'hp_max': 10,
            'ap_max': 1,
            'food_max': 100,
            'provoke_mobs': 0,          # in squares, affects aggr_distance. can be negative. integer
            'reflect_damage': 0,        # in percents x10 (100% = 1000), returns all kind of damages to attacker.
            'find_traps': 0,            # number competes against trap level x10 to reveal traps in whole room or trap on nearest square in coridors. based on intelligence
            'disarm_traps': 0,          # number competes against trap level x10 to remove trap on contact. fail triggers trap. based on dexterity
            'pick_locks': 0,            # number competes against door level x10 to open locked doors. based on dexterity, use lockpicks
            'find_gold': 0,             # in percents x10 (100% = 1000), increases gold amounts dropped.
            'find_food': 0,             # in percents x10 (100% = 1000), increases food amounts dropped.
            'find_ammo': 0,             # in percents x10 (100% = 1000), increases food amounts dropped.
            'find_ore': 0,              # number competes against ore deposit level x10 to successfully drop an ore. based on intelligence
            'crafting': 0,              # number competes against item difficulty to successfully craft. based on intelligence
            'find_magic': 0,            # 1-1000 add to drop better items. increase chance of better drop
            'exp_bonus': 0              # in percents x10 (100% = 1000), increases exp amounts received.
        }
        self.stat_points = 0
        self.char_effects = {}
        self.char_pools = {
            'mp_cur': 0,
            'hp_cur': 0,
            'ap_cur': 0,
            'food_cur': 0,
            'experience': 0,
        }
        for rule, value in rules.items():
            if rule in self.char_stats:
                self.char_stats[rule] = value
        self.char_stats_modified = self.char_stats.copy()

        self.char_pools_maximize()

    def gain_exp(self, exp):
        self.char_pools['experience'] += exp
        new_level = self.level_calculate(self.char_pools['experience'])
        if new_level > self.char_stats['level']:
            self.char_stats['level'] = new_level
            self.levelup_bonus(self.levelup_hp_bonus, self.levelup_mp_bonus, self.levelup_sp_bonus)
            self.stats_recalc()
            self.char_pools_maximize()
            new_text = Text(self.gameboard, 'LEVEL UP!', self.character.x + self.character.width // 2, self.character.y,
                            'default', 18, (255, 255, 255), 'center', 'top', 1, 0, -0.5)
            self.gameboard.audio.sound_bank['tiny_needle'].play()
        elif new_level < self.char_stats['level']:
            self.char_stats['level'] = new_level
            self.levelup_bonus(self.levelup_hp_bonus * -1, self.levelup_mp_bonus * -1, self.levelup_sp_bonus * -1)
            self.stats_recalc()
            self.char_pools_check()
            new_text = Text(self.gameboard, 'LEVEL DOWN!', self.character.x + self.character.width // 2, self.character.y,
                            'default', 18, (255, 0, 0), 'center', 'top', 1, 0, -0.5)
            self.gameboard.audio.sound_bank['deep_vortex'].play()
        else:
            exp_caption = self.gameboard.resources.text_bank['exp_gain'].replace('%1', str(exp))
            new_text = Text(self.gameboard, exp_caption, self.character.x + self.character.width // 2, self.character.y,
                            'default', 18, (255, 255, 255), 'center', 'top', 1, 0, -0.5)
        self.gameboard.ui.stats_refresh()

    def level_calculate(self, experience):
        exp_value = 0
        level = 1
        for x in range(0, 101):
            exp_value += self.gameboard.exponential(1.4, x, 100)
            level_value = x + 2
            if self.char_pools['experience'] >= exp_value:
                level = level_value
        return level

    def levelup_bonus(self, hp_bonus, mp_bonus, sp_bonus):
        if self.char_stats_modified['class'] == 'fighter':
            self.char_stats['hp_max'] += round(hp_bonus * 1.5)
            self.char_stats['mp_max'] += round(mp_bonus * 0.5)
        if self.char_stats_modified['class'] == 'ranger':
            self.char_stats['hp_max'] += hp_bonus
            self.char_stats['mp_max'] += mp_bonus
        if self.char_stats_modified['class'] == 'sorcerer':
            self.char_stats['hp_max'] += round(hp_bonus * 0.5)
            self.char_stats['mp_max'] += round(mp_bonus * 1.5)
        self.stat_points += sp_bonus

    def checkme(self):
        if self.char_pools['hp_cur'] <= 0:
            self.char_stats_modified['char'].dead()

    def get_modifiers_dict(self, inventory):
        max_parameters = 3
        modifiers_dict = {}

        for part, equipment in inventory.equipped.items():
            if part == 'ammo_slot' and (inventory.equipped['main_hand'] is None or
                                        'ranged' not in inventory.equipped['main_hand'].rules):
                continue
            if equipment is not None:
                self.update_modifiers_dict(modifiers_dict, equipment.rules, max_parameters)
                if 'ranged' in equipment.rules:
                    modifiers_dict['ranged'] = equipment.rules['ranged']
                if 'affixes' in equipment.rules:
                    for affix in equipment.rules['affixes']:
                        self.update_modifiers_dict(modifiers_dict, affix, max_parameters)
        for status_id, effect in self.char_effects.items():
            self.update_modifiers_dict(modifiers_dict, effect, max_parameters)

        print('STATS MODIFIERS:\n', modifiers_dict)
        return modifiers_dict

    def update_modifiers_dict(self, modifiers_dict, rules, max_parameters):
        for number in range(1, max_parameters + 1):
            digits = 'digits' + str(number)
            value = 'value' + str(number)
            parameter = 'parameter' + str(number)
            buff = 'buff' + str(number)
            debuff = 'debuff' + str(number)
            try:
                self.modifier_add(modifiers_dict, rules[parameter], rules[value], rules[digits])
            except KeyError:
                print('Property is impotent!')
            try:
                self.buff_add(rules[buff], rules['level'])
            except KeyError:
                print('No effect.')
            try:
                self.debuff_add(modifiers_dict, rules[debuff], rules['level'])
            except KeyError:
                print('No effect.')

    def modifier_add(self, modifiers_dict, parameter, value, digits):
        if parameter not in modifiers_dict:
            modifiers_dict[parameter] = {}
        if digits not in modifiers_dict[parameter]:
            modifiers_dict[parameter][digits] = [value]
        else:
            modifiers_dict[parameter][digits].append(value)

    def buff_add(self, effect, effect_level):
        effect_dict = self.get_effect(effect, effect_level)
        self.char_effects[effect] = effect_dict

    def debuff_add(self, modifiers_dict, effect, effect_level):
        if 'debuffs' not in modifiers_dict:
            modifiers_dict['debuffs'] = {}
        effect_dict = self.get_effect(effect, effect_level)
        modifiers_dict['debuffs'][effect] = effect_dict

    def get_effect(self, effect, effect_level):
        effect_dict = self.gameboard.tables.table_roll(effect, 'status_table.tab')
        effect_dict['level'] = effect_level
        return effect_dict

    def get_attacks(self, char_stats, modifier_dict):
        print('ATTACK START:')
        attack_list = []
        for dam_type in self.dam_types.keys():
            if dam_type in modifier_dict:
                if 'points' in modifier_dict[dam_type]:
                    if 'force' in modifier_dict[dam_type]:
                        val_number = len(modifier_dict[dam_type]['force'])
                        forced_value = round(sum(modifier_dict[dam_type]['force']) / val_number)
                        dam_subtotal = forced_value
                        print('Forced damage', dam_subtotal)
                    else:
                        dam_item_base = sum(modifier_dict[dam_type]['points'])
                        print('Item base damage', dam_item_base)
                        if 'percent' in modifier_dict[dam_type]:
                            dam_percent_mod = sum(modifier_dict[dam_type]['percent'])
                        else:
                            dam_percent_mod = 0
                        print('% damage bonus', dam_percent_mod)
                        try:
                            base_stat_name = self.dam_types[dam_type]['dam_base']
                            base_stat = char_stats.char_stats_modified[base_stat_name]
                        except KeyError:
                            base_stat = 0
                        try:
                            max_stat_name = self.dam_types[dam_type]['dam_max']
                            max_stat = char_stats.char_stats_modified[max_stat_name]
                        except KeyError:
                            max_stat = 0
                        try:
                            median_mod_name = self.dam_types[dam_type]['dam_median_mod']
                            median_mod = char_stats.char_stats_modified[median_mod_name]
                        except KeyError:
                            median_mod = 0
                        print('Min % modifier', base_stat)
                        print('Max % modifier', max_stat)
                        print('Median % modifier', median_mod)
                        dam_min = dam_item_base + round(dam_item_base * base_stat / 100) + round(
                            dam_item_base * dam_percent_mod / 100)
                        dam_median = dam_item_base + round(
                            dam_item_base * round((base_stat + max_stat) / 2) / 100) + round(
                            dam_item_base * median_mod / 100)
                        dam_max = dam_median + round(dam_item_base * max_stat / 100)
                        print('Min damage =', dam_item_base, '+', round(dam_item_base * base_stat / 100), '+', round(
                            dam_item_base * dam_percent_mod / 100), '=', dam_min)
                        print('Median =', dam_item_base, '+', round(
                            dam_item_base * round((base_stat + max_stat) / 2) / 100), '+', round(
                            dam_item_base * median_mod / 100), '=', dam_median)
                        print('Max damage =', dam_median, '+', round(dam_item_base * max_stat / 100), '=', dam_max)

                        #  possible other modifications
                        if dam_max > dam_min:
                            dam_subtotal = random.randrange(dam_min, dam_max + 1)
                        else:
                            dam_subtotal = min(dam_min, dam_max)
                            print('Handicapped by Max damage!')
                        print('Sub Total =', dam_subtotal)

                    dam_total = dam_subtotal
                    print('Final Total =', dam_total)

                    if 'ranged' in modifier_dict:
                        attack_type = 'ranged'
                    else:
                        attack_type = 'melee'

                    print(attack_type.capitalize(), 'attack inflicts effects:')
                    try:
                        attack_effects = modifier_dict['debuffs']
                        print([i for i in modifier_dict['debuffs'].keys()])
                    except KeyError:
                        attack_effects = None
                        print('(no effects)')

                    attack_dict = {
                        'damage': dam_total,
                        'attack_type': attack_type,
                        'damage_type': dam_type,
                        'inflict_status': attack_effects
                    }

                    attack_list.append(attack_dict)
        return attack_list

    def get_damage_minmax(self, dam_type, char_stats, modifier_dict):
        min_list = []
        max_list = []
        if dam_type in modifier_dict:
            if 'points' in modifier_dict[dam_type]:
                if 'force' in modifier_dict[dam_type]:
                    val_number = len(modifier_dict[dam_type]['force'])
                    forced_value = round(sum(modifier_dict[dam_type]['force']) / val_number)
                    dam_min = dam_max = forced_value
                else:
                    dam_item_base = sum(modifier_dict[dam_type]['points'])
                    if 'percent' in modifier_dict[dam_type]:
                        dam_percent_mod = sum(modifier_dict[dam_type]['percent'])
                    else:
                        dam_percent_mod = 0
                    try:
                        base_stat_name = self.dam_types[dam_type]['dam_base']
                        base_stat = char_stats.char_stats_modified[base_stat_name]
                    except KeyError:
                        base_stat = 0
                    try:
                        max_stat_name = self.dam_types[dam_type]['dam_max']
                        max_stat = char_stats.char_stats_modified[max_stat_name]
                    except KeyError:
                        max_stat = 0
                    try:
                        median_mod_name = self.dam_types[dam_type]['dam_median_mod']
                        median_mod = char_stats.char_stats_modified[median_mod_name]
                    except KeyError:
                        median_mod = 0
                    dam_min = dam_item_base + round(dam_item_base * base_stat / 100) + round(
                        dam_item_base * dam_percent_mod / 100)
                    dam_median = dam_item_base + round(
                        dam_item_base * round((base_stat + max_stat) / 2) / 100) + round(
                        dam_item_base * median_mod / 100)
                    dam_max = dam_median + round(dam_item_base * max_stat / 100)

                    #  possible other modifications
                    if dam_max <= dam_min:
                        dam_min = dam_max

                min_list.append(dam_min)
                max_list.append(dam_max)
        total_min = sum(min_list)
        total_max = sum(max_list)
        if total_max <= total_min:
            total_min = total_max
        return total_min, total_max

    def stats_recalc(self):
        self.char_stats['find_traps'] = self.char_stats['intelligence']  # number competes against trap level x10 to reveal traps in whole room or trap on nearest square in coridors. based on intelligence
        self.char_stats['disarm_traps'] = self.char_stats['dexterity']  # number competes against trap level x10 to remove trap on contact. fail triggers trap. based on dexterity
        self.char_stats['pick_locks'] = self.char_stats['dexterity']  # number competes against door level x10 to open locked doors. based on dexterity, use lockpicks
        self.char_stats['find_ore'] = self.char_stats['intelligence']  # number competes against ore deposit level x10 to successfully drop an ore. based on intelligence
        self.char_stats['crafting'] = self.char_stats['intelligence']  # number competes against item difficulty to successfully craft. based on intelligence

        self.modifiers_dict = self.get_modifiers_dict(self.character.inventory)
        self.char_stats_modified = self.char_stats.copy()
        for parameter, values in self.modifiers_dict.items():
            if parameter in self.char_stats_modified:
                if 'force' in values:
                    val_number = len(values['force'])
                    forced_value = round(sum(values['force']) / val_number)
                    self.char_stats_modified[parameter] = forced_value
                else:
                    if 'percent' in values:
                        percent_value = sum(values['percent'])
                        self.char_stats_modified[parameter] += round(self.char_stats_modified[parameter] * percent_value / 100)
                    if 'points' in values:
                        points_value = sum(values['points'])
                        self.char_stats_modified[parameter] += points_value

        #  possible other modifications
        total_dam_min = 0
        total_dam_max = 0
        for dam_type in self.dam_types.keys():
            dam_min, dam_max = self.get_damage_minmax(dam_type, self, self.modifiers_dict)
            total_dam_min += dam_min
            total_dam_max += dam_max

        self.char_stats_modified['total_damage_info'] = str(total_dam_min) + '-' + str(total_dam_max)

        self.char_pools_check()

    def char_pools_check(self):
        self.char_pools['mp_cur'] = min(self.char_pools['mp_cur'], self.char_stats_modified['mp_max'])
        self.char_pools['hp_cur'] = min(self.char_pools['hp_cur'], self.char_stats_modified['hp_max'])
        self.char_pools['ap_cur'] = min(self.char_pools['ap_cur'], self.char_stats_modified['ap_max'])
        self.char_pools['food_cur'] = min(self.char_pools['food_cur'], self.char_stats_modified['food_max'])
        if self.character == self.gameboard.player_char:
            self.gameboard.ui.hud_refresh()

    def char_pools_maximize(self):
        self.char_pools['hp_cur'] = self.char_stats_modified['hp_max']
        self.char_pools['mp_cur'] = self.char_stats_modified['mp_max']
        self.char_pools['ap_cur'] = self.char_stats_modified['ap_max']
        self.char_pools['food_cur'] = self.char_stats_modified['food_max']
        if self.character == self.gameboard.player_char:
            self.gameboard.ui.hud_refresh()

    def effects_tick(self):
        changed = False
        new_eff_dict = self.char_effects.copy()
        for eff_id, effect in self.char_effects.items():
            if effect['time'] > 1:
                effect['time'] -= 1
            elif effect['time'] != -1:
                del new_eff_dict[eff_id]
                changed = effect
                sounds = self.gameboard.tables.table_roll(effect['media'], 'sound_table')
                self.gameboard.audio.sound_bank[sounds['end']].play()
        self.char_effects = new_eff_dict
        if changed is not False:
            self.stats_recalc()
        return changed

    def effect_add(self, effect_id):
        effect_dict = self.gameboard.tables.table_roll(effect_id, 'status_table')
        self.char_effects[effect_id] = effect_dict
        self.stats_recalc()
        if self.character == self.gameboard.player_char:
            self.gameboard.ui.stats_refresh()
            self.gameboard.ui.effects_refresh()

    def effect_remove(self, effect_id):
        del self.char_effects[effect_id]
        self.stats_recalc()
        if self.character == self.gameboard.player_char:
            self.gameboard.ui.stats_refresh()
            self.gameboard.ui.effects_refresh()

