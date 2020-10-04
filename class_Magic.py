from class_Text import Text
from class_Particle import Particle

class Magic:

    magic_exponential_ratio = 1.2

    def __init__(self, gameboard):
        self.gameboard = gameboard

        self.spells_dict = self.spells_load()

        self.player_spell = None
        self.player_spellbook = []
        self.magic_item = None

    def spell_cast(self, spell_dict, char, target):
        if char.stats.char_pools['mp_cur'] < spell_dict['cost_mp'] * spell_dict['level']:
            # message about low mp
            return

        cast = False
        spell_particle_cast = self.gameboard.resources.animations[spell_dict['spell_media']['anim_set']['cast']]
        spell_particle_effect = self.gameboard.resources.animations[spell_dict['spell_media']['anim_set']['effect']]
        if spell_dict['spell_media']['sound_set']['cast'] is not None:
            spell_sound = self.gameboard.audio.sound_bank[spell_dict['spell_media']['sound_set']['cast']]
        else:
            spell_sound = False
        spell_text = spell_dict['spell_media']['text_set']['cast']
        spell_particle_time = spell_dict['particle_time']

        if spell_dict['id'] == 'spl_healing_food':
            cast = True
            if target is not None:
                try:
                    target.stats.char_pools['hp_cur'] += self.gameboard.exponential(self.magic_exponential_ratio, spell_dict['level'], 5)
                except AttributeError:
                    pass

        if spell_dict['id'] == 'spl_heal':
            cast = True
            if target is not None:
                try:
                    target.stats.char_pools['hp_cur'] += self.gameboard.exponential(self.magic_exponential_ratio, spell_dict['level'], 50)
                except AttributeError:
                    pass

        if spell_dict['id'] == 'spl_dispel':
            if target is not None:
                try:
                    if 'm_lock' in target.rules and target.rules['m_lock'] == 1:
                        char.stats.stats_recalc()
                        result = self.gameboard.pick_random(
                            [spell_dict['level'] + char.stats.char_stats_modified['intelligence'], target.rules['lock']],
                            [1, 0])
                        if result:
                            char.stats.gain_exp(target.rules['lock'] * 10)
                            target.rules['lock'] = target.rules['m_lock'] = 0
                            target.checkme()
                            target.sound_set['unlock_success'].play()
                            new_text = Text(self.gameboard, target.text_set['unlock_success'], target.x + target.width // 2,
                                            target.y, 'default', 18, (255, 255, 255), 'center', 'top', 1, 0, 0)

                except AttributeError:
                    pass
                cast = True

        if cast:
            if target is not None:
                target_x = target.x
                target_y = target.y
            else:
                target_x = (self.gameboard.mouse_x + self.gameboard.view_x) // self.gameboard.square_width * self.gameboard.square_width
                target_y = (self.gameboard.mouse_y + self.gameboard.view_y) // self.gameboard.square_height * self.gameboard.square_height

            char.stats.char_pools['mp_cur'] -= spell_dict['cost_mp'] * spell_dict['level']
            if spell_dict['cost_mp'] > 0:
                char.stats.char_pools['ap_cur'] -= 1
            char.stats.char_pools_check()

            if char == self.gameboard.player_char:
                char.checkme()

            if spell_sound is not False:
                spell_sound.play()
            new_particle = Particle(self.gameboard, spell_particle_cast, None, spell_particle_time, 0, 0,
                                    char.x, char.y)
            new_particle = Particle(self.gameboard, spell_particle_effect, None, spell_particle_time, 0, 0,
                                    target_x, target_y)
            new_text = Text(self.gameboard, spell_text, char.x + char.width // 2, char.y, 'default', 22, (255,255,255),
                            'center', 'top', 1, 0, 0)


    def spell_add(self, spellbook_rules):
        for spell in self.player_spellbook:
            if spell['id'] == spellbook_rules['spell']:
                spell['level'] = spellbook_rules['level']
                self.gameboard.ui.spellbook_refresh()
                return True
        if len(self.player_spellbook) < 24:
            new_spell = self.spells_dict[spellbook_rules['spell']]
            new_spell['level'] = spellbook_rules['level']
            self.player_spellbook.append(new_spell)
            self.gameboard.ui.spellbook_refresh()
            return True
        return False


    def spells_load(self):
        spell_table = self.gameboard.resources.read_file(self.gameboard.resources.tables['spell_table'])
        spells_dict = {}
        for i in spell_table:
            row = i.split()
            if len(row) > 0 and row[0] != '#':
                spell_dict = self.gameboard.tables.read_row(row, spell_table)
                spells_dict[spell_dict['id']] = spell_dict
                self.spell_load_media(spell_dict)
        if len(spells_dict) > 0:
            return spells_dict
        else:
            return False

    def spell_load_media(self, spell_dict):
        spell_anims = self.gameboard.tables.table_roll(spell_dict['id'], 'animation_table')
        spell_sounds = self.gameboard.tables.table_roll(spell_dict['id'], 'sound_table')
        spell_texts = self.gameboard.tables.table_roll(spell_dict['id'], 'text_table')
        """
        for key, value in spell_anims.items():
            spell_anims[key] = self.gameboard.resources.animations[value]
        for key, value in spell_sounds.items():
            spell_sounds[key] = self.gameboard.audio.sound_bank[value]"""
        for key, value in spell_texts.items():
            spell_texts[key] = self.gameboard.resources.text_bank[value]

        spell_dict['spell_media'] = {
            'anim_set': spell_anims,
            'sound_set': spell_sounds,
            'text_set': spell_texts
        }

    def spell_mouse(self):
        spell_target = self.gameboard.object_mouse_point()
        self.spell_cast(self.player_spell, self.gameboard.player_char, spell_target)
        if self.magic_item is not None:
            if self.magic_item.discharge(-1):
                self.player_spell = None
                result = self.gameboard.inventory_find_item(self.gameboard.player_char.inventory.backpack, object_id=self.magic_item)
                if result is not False:
                    m_item, container = result
                    container.remove(m_item)
                self.magic_item = None
                self.gameboard.audio.sound_bank['metal_clank03'].play()
                self.gameboard.ui.ragdoll_refresh(self.gameboard.ui.container_crumps[-1])
                self.gameboard.ui.spellbook_refresh()

    def spell_delete(self, spell_number):
        if self.player_spell == self.player_spellbook[spell_number]:
            self.player_spell = None
        del self.player_spellbook[spell_number]
        self.gameboard.ui.spellbook_refresh()