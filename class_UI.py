from class_UIElement import UIElement
from class_Text import Text
import pygame


class UI:

    def __init__(self, gameboard):  # Initialize attributes to represent the character.
        self.active = True

        self.gameboard = gameboard
        self.container_crumps = []
        self.uielements = {
            'ui_hud': UIElement(gameboard, 'ui_hud'),
            # 'ui_inventory': UIElement(gameboard, 'ui_inventory_fighter'),
            'ui_scene_info': UIElement(gameboard, 'ui_scene_info'),
            'ui_stats_full': UIElement(gameboard, 'ui_stats_full'),
            'ui_death': UIElement(gameboard, 'ui_death'),
            'ui_title': UIElement(gameboard, 'ui_title'),
            'ui_gameload': UIElement(gameboard, 'ui_gameload'),
            'ui_characters': UIElement(gameboard, 'ui_characters'),
            'ui_spellbook': UIElement(gameboard, 'ui_spellbook'),
            'ui_details': UIElement(gameboard, 'ui_details'),
            'ui_pause': UIElement(gameboard, 'ui_pause'),
            'ui_dialogue': UIElement(gameboard, 'ui_dialogue'),
            'ui_message': UIElement(gameboard, 'ui_message')
        }
        self.active_ui_flags = {
            'ui_hud': False,
            'ui_inventory': False,
            'ui_stats': False,
            'ui_stats_full': False,
            'ui_scene_info': False,
            'ui_death': False,
            'ui_title': False,
            'ui_gameload': False,
            'ui_characters': False,
            'ui_spellbook': False,
            'ui_details': False,
            'ui_pause': False,
            'ui_dialogue': False,
            'ui_message': False
        }
        self.equip_ties = {
            'equip_ammo_slot': 'ammo_slot',
            'equip_main_hand': 'main_hand',
            'equip_off_hand': 'off_hand',
            'equip_head': 'head',
            'equip_chest': 'chest',
            'equip_ring1': 'ring1',
            'equip_ring2': 'ring2'
        }
        self.parameter_colors_dict = {
            'char': '0,0,0',
            'class': '0,0,0',
            'level': '0,0,0',
            'strength': '0,0,0',
            'dexterity': '0,0,0',
            'intelligence': '0,0,0',
            'mp_max': '0,0,0',
            'hp_max': '0,0,0',
            'ap_max': '0,0,0',
            'food_max': '0,0,0',
            'provoke_mobs': '0,0,0',
            'reflect_damage': '0,0,0',
            'find_traps': '0,0,0',
            'disarm_traps': '0,0,0',
            'pick_locks': '0,0,0',
            'find_gold': '0,0,0',
            'find_food': '0,0,0',
            'find_ammo': '0,0,0',
            'find_ore': '0,0,0',
            'crafting': '0,0,0',
            'find_magic': '0,0,0',
            'exp_bonus': '0,0,0',
            'dam_cut': '50,50,50',
            'dam_pierce': '0,0,0',
            'dam_bash': '0,0,0',
            'dam_poison': '0,0,0',
            'dam_fire': '0,0,0',
            'dam_ice': '0,0,0',
            'dam_lightning': '0,0,0',
            'dam_arcane': '0,0,0',
            'def_cut': '0,0,0',
            'def_pierce': '0,0,0',
            'def_bash': '0,0,0',
            'def_poison': '0,0,0',
            'def_fire': '0,0,0',
            'def_ice': '0,0,0',
            'def_lightning': '0,0,0',
            'def_arcane': '0,0,0',
        }
        self.ui_variables = {
            'ui_characters': {
                'hero_name': 'Mors_Gotha',
                'class_choice': 'fighter'
            },
            'ui_gameload': {
                'save_choice': -1
            },
            'ui_message': {
                'text': '',
                'icon': self.gameboard.resources.animations['ui_empty']
            },
            'ui_dialogue': {
                'text': '',
                'call_name': None,
                'call_params': None
            }
        }

    def calculate_ui_offset(self, uielement):
        # calculating offset
        if uielement.stick_hor != -1:
            offset_x = self.gameboard.sight_width * uielement.stick_hor + uielement.offset_x * self.gameboard.square_width
        else:
            offset_x = uielement.x
        if uielement.stick_ver != -1:
            offset_y = self.gameboard.sight_height * uielement.stick_ver + uielement.offset_y * self.gameboard.square_height
        else:
            offset_y = uielement.y
        return offset_x, offset_y

    def control_capture_mouse(self, control_event, mouse_buttons, mouse_x, mouse_y):
        for ui_name, flag in self.active_ui_flags.items():
            if self.active_ui_flags['ui_message'] and ui_name is not 'ui_message':
                continue
            elif self.active_ui_flags['ui_dialogue'] and ui_name is not 'ui_dialogue':
                continue
            elif self.active_ui_flags['ui_pause'] and ui_name is not 'ui_pause':
                continue
            if flag and (ui_name in self.uielements):
                offset_x, offset_y = self.calculate_ui_offset(self.uielements[ui_name])
                for trigger_id, trigger_params in self.uielements[ui_name].uielement['trigger_map'].items():
                    if trigger_params['left'] * self.gameboard.square_width + offset_x < mouse_x < trigger_params[
                        'right'] * self.gameboard.square_width + offset_x and \
                            trigger_params['top'] * self.gameboard.square_height + offset_y < mouse_y < trigger_params[
                        'bottom'] * self.gameboard.square_height + offset_y:

                        trigger_params['state'] = control_event
                        # element.event(trigger_id, control_event)
                        event_trigger = trigger_id + '-' + control_event
                        if event_trigger in self.uielements[ui_name].uielement['sound_list']:
                            self.gameboard.audio.sound_bank[
                                self.uielements[ui_name].uielement['sound_list'][event_trigger]].play()
                        self.proceed_event(event_trigger, mouse_buttons)
                        return True
                    else:
                        trigger_params['state'] = 'mouse_leave'
        return False

    def control_mouse_over(self, mouse_x, mouse_y):
        if self.active_ui_flags['ui_hud']:
            if not self.active_ui_flags['ui_details'] and not self.active_ui_flags['ui_pause'] and not \
                    self.active_ui_flags['ui_message'] and not self.active_ui_flags['ui_dialogue']:
                if self.gameboard.mouse_idle_ticks > 30 and len(
                        self.gameboard.player_char.stats.char_effects) > 0 and self.gameboard.mouse_hand is None:
                    offset_x, offset_y = self.calculate_ui_offset(self.uielements['ui_hud'])
                    for trigger_id, trigger_params in self.uielements['ui_hud'].uielement['trigger_map'].items():
                        if trigger_params['left'] * self.gameboard.square_width + offset_x < mouse_x < trigger_params[
                            'right'] * self.gameboard.square_width + offset_x and \
                                trigger_params['top'] * self.gameboard.square_height + offset_y < mouse_y < \
                                trigger_params['bottom'] * self.gameboard.square_height + offset_y:
                            if 'eff' in trigger_id:
                                if self.eff_item_details(trigger_id):
                                    self.active_ui_flags['ui_details'] = True
                                    self.gameboard.audio.sound_bank['soft_noise'].play()
            elif self.gameboard.mouse_idle_ticks == 1:
                self.active_ui_flags['ui_details'] = False
        if self.active_ui_flags['ui_inventory']:
            if not self.active_ui_flags['ui_details'] and not self.active_ui_flags['ui_pause'] and not \
                    self.active_ui_flags['ui_message'] and not self.active_ui_flags['ui_dialogue']:
                if self.gameboard.mouse_idle_ticks > 30 and self.gameboard.mouse_hand is None:
                    offset_x, offset_y = self.calculate_ui_offset(self.uielements['ui_inventory'])
                    for trigger_id, trigger_params in self.uielements['ui_inventory'].uielement['trigger_map'].items():
                        if trigger_params['left'] * self.gameboard.square_width + offset_x < mouse_x < trigger_params[
                            'right'] * self.gameboard.square_width + offset_x and \
                                trigger_params['top'] * self.gameboard.square_height + offset_y < mouse_y < \
                                trigger_params['bottom'] * self.gameboard.square_height + offset_y:
                            if 'equip' in trigger_id or 'inv_item' in trigger_id:
                                if self.inv_item_details(trigger_id):
                                    self.active_ui_flags['ui_details'] = True
                                    self.gameboard.audio.sound_bank['soft_noise'].play()
            elif self.gameboard.mouse_idle_ticks == 1:
                self.active_ui_flags['ui_details'] = False
        if self.active_ui_flags['ui_spellbook']:
            if not self.active_ui_flags['ui_details'] and not self.active_ui_flags['ui_pause'] and not \
                    self.active_ui_flags['ui_message'] and not self.active_ui_flags['ui_dialogue']:
                if self.gameboard.mouse_idle_ticks > 30 and self.gameboard.mouse_hand is None:
                    offset_x, offset_y = self.calculate_ui_offset(self.uielements['ui_spellbook'])
                    for trigger_id, trigger_params in self.uielements['ui_spellbook'].uielement['trigger_map'].items():
                        if trigger_params['left'] * self.gameboard.square_width + offset_x < mouse_x < trigger_params[
                            'right'] * self.gameboard.square_width + offset_x and \
                                trigger_params['top'] * self.gameboard.square_height + offset_y < mouse_y < \
                                trigger_params['bottom'] * self.gameboard.square_height + offset_y:
                            if 'spell' in trigger_id or 'select' in trigger_id:
                                if self.spell_details(trigger_id):
                                    self.active_ui_flags['ui_details'] = True
                                    self.gameboard.audio.sound_bank['soft_noise'].play()
            elif self.gameboard.mouse_idle_ticks == 1:
                self.active_ui_flags['ui_details'] = False

    def inv_item_details(self, trigger_id):
        # get item obj and fill info and return False or obj
        item_obj = None
        if trigger_id in self.equip_ties:
            item_obj = self.gameboard.player_char.inventory.equipped[self.equip_ties[trigger_id]]
        elif 'inv_item' in trigger_id:
            try:
                item_obj = self.container_crumps[-1][int(trigger_id.split('-')[1])]
            except IndexError:
                return False
        else:
            return False
        if item_obj is not None:  # wpn,amm,mgc,arm,hlm,shl,acc,ptn,tls,wlt,foo,rsr
            self.inv_details_compose(item_obj)
            return True
        else:
            return False

    def eff_item_details(self, trigger_id):
        # get item obj and fill info and return False or obj
        eff_key = trigger_id.split('-')[1]
        if eff_key in self.gameboard.player_char.stats.char_effects:
            effect_dict = self.gameboard.player_char.stats.char_effects[eff_key]
            self.eff_details_compose(effect_dict)
            return True
        else:
            return False

    def spell_details(self, trigger_id):
        # get item obj and fill info and return False or obj
        if 'select' not in trigger_id:
            spell_index = int(trigger_id.split('-')[1])
            if len(self.gameboard.magic.player_spellbook) > spell_index:
                spell_dict = self.gameboard.magic.player_spellbook[spell_index]
                self.spell_details_compose(spell_dict)
                return True
            else:
                return False
        else:
            if self.gameboard.magic.player_spell is not None:
                spell_dict = self.gameboard.magic.player_spell
                self.spell_details_compose(spell_dict)
                return True
            else:
                return False

    def proceed_event(self, event_trigger, mouse_button):
        if self.active_ui_flags['ui_message']:
            if event_trigger == 'message_text-mouse_up' and mouse_button == 1:
                self.active_ui_flags['ui_message'] = False
            return
        elif self.active_ui_flags['ui_dialogue']:
            if event_trigger == 'bttn_cancel-mouse_up' and mouse_button == 1:
                self.active_ui_flags['ui_dialogue'] = False
            if event_trigger == 'bttn_confirm-mouse_up' and mouse_button == 1:
                self.active_ui_flags['ui_dialogue'] = False
                if self.ui_variables['ui_dialogue']['call_name'] is not None:
                    self.ui_variables['ui_dialogue']['call_name'](*self.ui_variables['ui_dialogue']['call_params'])
                    self.ui_variables['ui_dialogue']['call_name'] = None
            return
        elif self.active_ui_flags['ui_pause']:
            if event_trigger == 'bttn_resume-mouse_up' and mouse_button == 1:
                self.active_ui_flags['ui_pause'] = False
            if event_trigger == 'bttn_exitsave-mouse_up' and mouse_button == 1:
                self.gameboard.save_game()
                self.gameboard.reset_game()
                self.ui_block()
                self.active_ui_flags['ui_title'] = True
            return

        if self.active_ui_flags['ui_hud']:
            if event_trigger == 'bttn_inventory-mouse_up' and mouse_button == 1:
                if self.active_ui_flags['ui_inventory']:
                    self.active_ui_flags['ui_inventory'] = False
                else:
                    self.active_ui_flags['ui_inventory'] = True
                    self.ragdoll_refresh(self.container_crumps[-1])
                    self.active_ui_flags['ui_stats'] = False
                    self.active_ui_flags['ui_stats_full'] = False
                    self.active_ui_flags['ui_spellbook'] = False
            elif event_trigger == 'bttn_stats-mouse_up' and mouse_button == 1:
                if self.active_ui_flags['ui_stats'] or self.active_ui_flags['ui_stats_full']:
                    self.active_ui_flags['ui_stats'] = False
                    self.active_ui_flags['ui_stats_full'] = False
                else:
                    self.active_ui_flags['ui_stats'] = True
                    self.stats_refresh()
                    self.active_ui_flags['ui_inventory'] = False
                    self.active_ui_flags['ui_stats_full'] = False
                    self.active_ui_flags['ui_spellbook'] = False
            elif event_trigger == 'bttn_magic-mouse_up' and mouse_button == 1:
                if self.active_ui_flags['ui_spellbook']:
                    self.active_ui_flags['ui_spellbook'] = False
                else:
                    self.active_ui_flags['ui_spellbook'] = True
                    self.active_ui_flags['ui_inventory'] = False
                    self.active_ui_flags['ui_stats'] = False
                    self.active_ui_flags['ui_stats_full'] = False
            elif 'tr_ui_hud_clock' in event_trigger and 'mouse_up' in event_trigger and mouse_button == 1:
                # self.gameboard.player_char.stats.char_pools['ap_cur'] -= 1
                # self.gameboard.ui.hud_refresh()
                if self.gameboard.players_turn:
                    self.gameboard.next_turn()

                new_caption = Text(self.gameboard, 'Waiting...',
                                   self.gameboard.player_char.x + self.gameboard.player_char.width // 2,
                                   self.gameboard.player_char.y, 'default', 20, (255,255,255), 'center', 'top', 0.5, 0, -1)
            elif event_trigger == 'bttn_pause-mouse_up' and mouse_button == 1:
                if self.active_ui_flags['ui_pause']:
                    self.active_ui_flags['ui_pause'] = False
                else:
                    self.active_ui_flags['ui_pause'] = True

            elif 'eff' in event_trigger and mouse_button == 1:
                self.effect_icon_click(event_trigger.split('-')[1])

        if self.active_ui_flags['ui_inventory']:
            if event_trigger == 'cont_close-mouse_up' and mouse_button == 1 and len(self.container_crumps) > 1:
                del self.container_crumps[-1]
                self.ragdoll_refresh(self.container_crumps[-1])
            elif 'inv_item' in event_trigger:
                item_number = int(event_trigger.split('-')[1])
                if 'mouse_up' in event_trigger and mouse_button == 1:
                    if item_number <= len(
                            self.container_crumps[-1]) - 1 and self.gameboard.mouse_hand is not None and 'space' in \
                            self.container_crumps[-1][item_number].rules and 'space' not in self.gameboard.mouse_hand.rules:
                        if 'container' not in self.container_crumps[-1][item_number].rules:
                            self.container_crumps[-1][item_number].rules['container'] = []
                        self.mhand_to_cont(self.container_crumps[-1][item_number])
                    else:
                        self.exchange_backpack(item_number, self.container_crumps[-1], 'pc_step03')
                    self.ragdoll_refresh(self.container_crumps[-1])
                if 'mouse_up' in event_trigger and mouse_button == 3:
                    if item_number <= len(self.container_crumps[-1]) - 1:
                        if 'space' in self.container_crumps[-1][item_number].rules:
                            if 'container' not in self.container_crumps[-1][item_number].rules:
                                self.container_crumps[-1][item_number].rules['container'] = []
                            self.container_crumps.append(self.container_crumps[-1][item_number].rules['container'])
                            self.ragdoll_refresh(self.container_crumps[-1])
                        else:
                            self.container_crumps[-1][item_number].useme(self.gameboard.player_char, self.container_crumps[-1])
            elif 'mouse_up' in event_trigger and mouse_button == 1:
                self.item_mouse_grab(event_trigger)

        if self.active_ui_flags['ui_death']:
            if event_trigger == 'bttn_resurrect-mouse_up' and mouse_button == 1:
                self.gameboard.player_char.resurrect()

        if self.active_ui_flags['ui_title']:
            if event_trigger == 'bttn_new_start-mouse_up' and mouse_button == 1:
                last_slot = self.gameboard.resources.file_read_param('save-13', self.gameboard.resources.path + \
                                                                     '/save/player_characters.data')
                if last_slot is False:
                    self.ui_block()
                    self.active_ui_flags['ui_characters'] = True
                    self.hero_name_input_display()
                else:
                    self.ui_variables['ui_message']['text'] = self.gameboard.resources.text_bank['no_free_saveslots']
                    self.ui_variables['ui_message']['icon'] = self.gameboard.resources.animations['itm_book_portable']
                    self.message_refresh()
                    self.active_ui_flags['ui_message'] = True
                    self.gameboard.audio.sound_bank['soft_noise'].play()

            elif event_trigger == 'bttn_continue-mouse_up' and mouse_button == 1:
                self.ui_block()
                self.gameload_refresh()
                self.active_ui_flags['ui_gameload'] = True

        if self.active_ui_flags['ui_characters']:
            if 'mouse_up' in event_trigger:
                for trigger in self.uielements['ui_characters'].uielement['trigger_map'].values():
                    trigger['state'] = 'default'
            if event_trigger == 'bttn_title-mouse_up' and mouse_button == 1:
                self.ui_block()
                self.active_ui_flags['ui_title'] = True
            elif event_trigger == 'bttn_fighter-mouse_up' and mouse_button == 1:
                self.ui_variables['ui_characters']['class_choice'] = 'fighter'
                self.ui_characters_class_select('bttn_fighter', 'ui_class_portrait_fighter_color')
            elif event_trigger == 'bttn_ranger-mouse_up' and mouse_button == 1:
                self.ui_variables['ui_characters']['class_choice'] = 'ranger'
                self.ui_characters_class_select('bttn_ranger', 'ui_class_portrait_ranger_color')
            elif event_trigger == 'bttn_sorcerer-mouse_up' and mouse_button == 1:
                self.ui_variables['ui_characters']['class_choice'] = 'sorcerer'
                self.ui_characters_class_select('bttn_sorcerer', 'ui_class_portrait_sorcerer_color')
            elif event_trigger == 'bttn_name_gen-mouse_up' and mouse_button == 1:
                random_name = self.gameboard.get_char_name(self.ui_variables['ui_characters']['class_choice'])
                self.ui_variables['ui_characters']['hero_name'] = random_name['name']
                self.hero_name_input_display()
            elif event_trigger == 'bttn_start-mouse_up' and mouse_button == 1:
                self.ui_block()
                self.active_ui_flags['ui_hud'] = True
                self.active_ui_flags['ui_scene_info'] = True

                self.create_unique_uis(self.ui_variables['ui_characters']['class_choice'])

                self.gameboard.new_game_start(self.ui_variables['ui_characters']['class_choice'], self.ui_variables['ui_characters']['hero_name'])
        if self.active_ui_flags['ui_stats']:
            if event_trigger == 'full_stats-mouse_up' and mouse_button == 1:
                self.active_ui_flags['ui_stats'] = False
                self.active_ui_flags['ui_stats_full'] = True
                self.stats_refresh()
            if event_trigger == 'bttn_str_up-mouse_up' and mouse_button == 1:
                if self.gameboard.player_char.stats.stat_points > 0:
                    self.gameboard.player_char.stats.char_stats['strength'] += 1
                    self.gameboard.player_char.stats.stat_points -= 1
                    self.gameboard.player_char.stats.stats_recalc()
                    self.stats_refresh()
            if event_trigger == 'bttn_dex_up-mouse_up' and mouse_button == 1:
                if self.gameboard.player_char.stats.stat_points > 0:
                    self.gameboard.player_char.stats.char_stats['dexterity'] += 1
                    self.gameboard.player_char.stats.stat_points -= 1
                    self.gameboard.player_char.stats.stats_recalc()
                    self.stats_refresh()
            if event_trigger == 'bttn_int_up-mouse_up' and mouse_button == 1:
                if self.gameboard.player_char.stats.stat_points > 0:
                    self.gameboard.player_char.stats.char_stats['intelligence'] += 1
                    self.gameboard.player_char.stats.stat_points -= 1
                    self.gameboard.player_char.stats.stats_recalc()
                    self.stats_refresh()
        if self.active_ui_flags['ui_stats_full']:
            if event_trigger == 'back_to_stats-mouse_up' and mouse_button == 1:
                self.active_ui_flags['ui_stats_full'] = False
                self.active_ui_flags['ui_stats'] = True
                self.stats_refresh()

        if self.active_ui_flags['ui_spellbook']:
            if event_trigger == 'select-mouse_up' and mouse_button == 1:
                self.gameboard.magic.player_spell = None
                self.gameboard.magic.magic_item = None
                self.spellbook_refresh()
            elif 'spell' in event_trigger:
                spell_number = int(event_trigger.split('-')[1])
                if spell_number < len(self.gameboard.magic.player_spellbook):
                    if 'mouse_up' in event_trigger and mouse_button == 1:
                        self.gameboard.magic.player_spell = self.gameboard.magic.player_spellbook[spell_number]
                        self.gameboard.magic.magic_item = None
                        self.spellbook_refresh()
                    elif 'mouse_up' in event_trigger and mouse_button == 3:
                        self.ui_variables['ui_dialogue']['text'] = 'Delete the spell from your compendium?'
                        self.ui_variables['ui_dialogue']['call_name'] = self.gameboard.magic.spell_delete
                        self.ui_variables['ui_dialogue']['call_params'] = [spell_number]
                        self.dialogue_refresh()
                        self.active_ui_flags['ui_dialogue'] = True
            else:
                return

        if self.active_ui_flags['ui_gameload']:
            if event_trigger == 'bttn_title-mouse_up' and mouse_button == 1:
                self.ui_block()
                self.active_ui_flags['ui_title'] = True
            elif event_trigger == 'bttn_delete-mouse_up' and self.ui_variables['ui_gameload'][
                'save_choice'] >= 0 and mouse_button == 1:
                slot_index = self.ui_variables['ui_gameload']['save_choice']
                self.ui_variables['ui_dialogue']['text'] = 'Delete this savegame forever?'
                self.ui_variables['ui_dialogue']['call_name'] = self.gameboard.save_delete
                self.ui_variables['ui_dialogue']['call_params'] = [slot_index]
                self.dialogue_refresh()
                self.active_ui_flags['ui_dialogue'] = True
            elif 'save' in event_trigger:
                save_number = int(event_trigger.split('-')[1])
                if 'mouse_up' in event_trigger and mouse_button == 1:
                    self.ui_variables['ui_gameload']['save_choice'] = save_number
                    self.gameload_refresh()
            elif 'bttn_load-mouse_up' in event_trigger and self.ui_variables['ui_gameload'][
                'save_choice'] >= 0 and mouse_button == 1:
                slotname = 'save-' + str(self.ui_variables['ui_gameload']['save_choice'])
                game_id = self.gameboard.resources.file_read_param(slotname,
                                                                   self.gameboard.resources.path + '/save/player_characters.data')
                if game_id is not False:
                    game_id, hub_id, depth = self.gameboard.resources.load_save(
                        'save-' + str(self.ui_variables['ui_gameload']['save_choice']))
                    self.ui_block()
                    self.gameboard.load_game(game_id, hub_id, depth)

    def item_mouse_grab(self, event_trigger):
        if event_trigger == 'equip_ammo_slot-mouse_up':
            exchange = self.exchange_equip(
                self.gameboard.player_char.inventory.equipped['ammo_slot'], 'amm', 'pc_step03')
            if exchange is not False:
                self.gameboard.player_char.inventory.equipped['ammo_slot'] = exchange
        elif event_trigger == 'equip_main_hand-mouse_up':
            exchange = self.exchange_equip(
                self.gameboard.player_char.inventory.equipped['main_hand'], 'wpn,mgc', 'pc_step03')
            if exchange is not False:
                self.gameboard.player_char.inventory.equipped['main_hand'] = exchange
        elif event_trigger == 'equip_off_hand-mouse_up':
            exchange = self.exchange_equip(
                self.gameboard.player_char.inventory.equipped['off_hand'], 'amm,shl,tls', 'pc_step03')
            if exchange is not False:
                self.gameboard.player_char.inventory.equipped['off_hand'] = exchange
        elif event_trigger == 'equip_head-mouse_up':
            exchange = self.exchange_equip(
                self.gameboard.player_char.inventory.equipped['head'], 'hlm', 'pc_step03')
            if exchange is not False:
                self.gameboard.player_char.inventory.equipped['head'] = exchange
        elif event_trigger == 'equip_chest-mouse_up':
            exchange = self.exchange_equip(
                self.gameboard.player_char.inventory.equipped['chest'], 'arm', 'pc_step03')
            if exchange is not False:
                self.gameboard.player_char.inventory.equipped['chest'] = exchange
        elif event_trigger == 'equip_ring1-mouse_up':
            exchange = self.exchange_equip(
                self.gameboard.player_char.inventory.equipped['ring1'], 'acc', 'pc_step03')
            if exchange is not False:
                self.gameboard.player_char.inventory.equipped['ring1'] = exchange
        elif event_trigger == 'equip_ring2-mouse_up':
            exchange = self.exchange_equip(
                self.gameboard.player_char.inventory.equipped['ring2'], 'acc', 'pc_step03')
            if exchange is not False:
                self.gameboard.player_char.inventory.equipped['ring2'] = exchange
        self.gameboard.player_char.stats.stats_recalc()
        self.ragdoll_refresh(self.container_crumps[-1])

    def exchange_equip(self, inv_slot, item_class, sound):
        if self.gameboard.mouse_hand is None:
            inv_slot, self.gameboard.mouse_hand = self.gameboard.mouse_hand, inv_slot
            return inv_slot
        elif 'item_class' in self.gameboard.mouse_hand.rules and self.gameboard.mouse_hand.rules[
            'item_class'] in item_class and ('class' not in self.gameboard.mouse_hand.rules or
                                             self.gameboard.player_char.stats.char_stats_modified['class'] in
                                             self.gameboard.mouse_hand.rules['class']):
            if inv_slot is not None and self.gameboard.items_may_stack(self.gameboard.mouse_hand, inv_slot):
                transfer_amount = min(inv_slot.rules['amount_max'] - inv_slot.rules['amount_cur'], self.gameboard.mouse_hand.rules['amount_cur'])
                inv_slot.rules['amount_cur'] += transfer_amount
                self.gameboard.mouse_hand.rules['amount_cur'] -= transfer_amount
                if self.gameboard.mouse_hand.rules['amount_cur'] == 0:
                    self.gameboard.mouse_hand = None
            else:
                if self.gameboard.mouse_hand:
                    self.gameboard.mouse_hand.sound_set['pickup'].play()
                inv_slot, self.gameboard.mouse_hand = self.gameboard.mouse_hand, inv_slot
            return inv_slot
        return False

    def exchange_backpack(self, item_index, container, sound):
        if item_index > len(container) - 1 and self.gameboard.mouse_hand is not None:
            self.gameboard.mouse_hand.sound_set['pickup'].play()
            if 'amount_cur' in self.gameboard.mouse_hand.rules:
                left_item = self.gameboard.container_item_not_fit(self.gameboard.mouse_hand, container, 12)
                if left_item is not False:
                    self.gameboard.mouse_hand = left_item
                else:
                    self.gameboard.mouse_hand = None
            else:
                container.append(self.gameboard.mouse_hand)
                self.gameboard.mouse_hand = None
        elif item_index < len(container) and self.gameboard.mouse_hand is None:
            #   container[item_index].sound_set['pickup'].play()
            self.gameboard.mouse_hand = container[item_index]
            del container[item_index]
        elif item_index < len(container) and self.gameboard.mouse_hand is not None:
            if self.gameboard.items_may_stack(self.gameboard.mouse_hand, container[item_index]):
                transfer_amount = min(
                    container[item_index].rules['amount_max'] - container[item_index].rules['amount_cur'],
                    self.gameboard.mouse_hand.rules['amount_cur'])
                container[item_index].rules['amount_cur'] += transfer_amount
                self.gameboard.mouse_hand.rules['amount_cur'] -= transfer_amount
                if self.gameboard.mouse_hand.rules['amount_cur'] == 0:
                    self.gameboard.mouse_hand = None
                container[item_index].sound_set['pickup'].play()
            else:
                self.gameboard.mouse_hand, container[item_index] = \
                    container[item_index], self.gameboard.mouse_hand
                container[item_index].sound_set['pickup'].play()
        self.gameboard.inventory_check(self.gameboard.player_char)

    def mhand_to_cont(self, container):
        # if len(container.rules['container']) < container.rules['space']:
        #    container.rules['container'].append(self.gameboard.mouse_hand)
        left_item = self.gameboard.container_item_not_fit(self.gameboard.mouse_hand, container.rules['container'], container.rules['space'])
        if left_item is False:
            self.gameboard.mouse_hand = None
            self.gameboard.audio.sound_bank['pc_step01'].play()

    def inventory_refresh(self, container):
        self.ragdoll_refresh(container)

    def ragdoll_refresh(self, container):
        if self.active_ui_flags['ui_inventory']:
            if self.gameboard.player_char.inventory.equipped['ammo_slot'] is not None:
                counter_text = self.uielements['ui_inventory'].uielement['dyn_textobj_dict']['ammo_amount']
                counter_text.caption = str(self.gameboard.player_char.inventory.equipped['ammo_slot'].rules['amount_cur'])
                counter_text.visible = True
                counter_text.redraw = True
            else:
                self.uielements['ui_inventory'].uielement['dyn_textobj_dict']['ammo_amount'].visible = False
            for tr_id, tie in self.equip_ties.items():
                if self.gameboard.player_char.inventory.equipped[tie] is not None:
                    new_anim = self.gameboard.player_char.inventory.equipped[tie].animation
                else:
                    new_anim = self.gameboard.resources.animations['ui_empty']
                self.uielements['ui_inventory'].uielement['tr_tile_dict'][tr_id]['animations'] = {
                    'default': new_anim
                }
            for i in range(0, len(container)):
                new_anim = container[i].animation
                self.uielements['ui_inventory'].uielement['tr_tile_dict']['inv_item-' + str(i)]['animations'] = {
                    'default': new_anim
                }
                counter_text = self.uielements['ui_inventory'].uielement['dyn_textobj_dict']['inv' + str(i)]
                if 'amount_cur' in container[i].rules:
                    counter_text.caption = str(container[i].rules['amount_cur'])
                    counter_text.visible = True
                    counter_text.redraw = True
                else:
                    counter_text.visible = False
            for i in range(len(container), 12):
                self.uielements['ui_inventory'].uielement['tr_tile_dict']['inv_item-' + str(i)]['animations'] = {
                    'default': self.gameboard.resources.animations['ui_empty']
                }
                counter_text = self.uielements['ui_inventory'].uielement['dyn_textobj_dict']['inv' + str(i)]
                counter_text.visible = False
            if len(self.container_crumps) > 1:
                self.uielements['ui_inventory'].uielement['tr_tile_dict']['cont_close']['animations'] = {
                    'default': self.gameboard.resources.animations['ui_cont_close_default'],
                    'mouse_down': self.gameboard.resources.animations['ui_cont_close_pressed'],
                    'mouse_up': self.gameboard.resources.animations['ui_cont_close_default'],
                    'mouse_leave': self.gameboard.resources.animations['ui_cont_close_default']
                }
            else:
                self.uielements['ui_inventory'].uielement['tr_tile_dict']['cont_close']['animations'] = {
                    'default': self.gameboard.resources.animations['ui_empty']
                }

    def hud_refresh(self):
        empty_hp = (self.gameboard.player_char.stats.char_pools['hp_cur'] / self.gameboard.player_char.stats.char_stats_modified['hp_max']) * \
                       (self.uielements['ui_hud'].uielement['trigger_map']['tr_ui_pool_hp']['bottom'] -
                        self.uielements['ui_hud'].uielement['trigger_map']['tr_ui_pool_hp']['top'])
        for position in self.uielements['ui_hud'].uielement['tr_tile_dict']['tr_ui_pool_hp']['positions']:
            position[1] = self.uielements['ui_hud'].uielement['trigger_map']['tr_ui_pool_hp']['bottom'] - empty_hp
        empty_mp = (self.gameboard.player_char.stats.char_pools['mp_cur'] /
                    self.gameboard.player_char.stats.char_stats_modified['mp_max']) * \
                   (self.uielements['ui_hud'].uielement['trigger_map']['tr_ui_pool_mp']['bottom'] -
                    self.uielements['ui_hud'].uielement['trigger_map']['tr_ui_pool_mp']['top'])
        for position in self.uielements['ui_hud'].uielement['tr_tile_dict']['tr_ui_pool_mp']['positions']:
            position[1] = self.uielements['ui_hud'].uielement['trigger_map']['tr_ui_pool_mp']['bottom'] - empty_mp
        empty_food = (self.gameboard.player_char.stats.char_pools['food_cur'] /
                    self.gameboard.player_char.stats.char_stats_modified['food_max']) * \
                   (self.uielements['ui_hud'].uielement['trigger_map']['tr_ui_pool_food']['bottom'] -
                    self.uielements['ui_hud'].uielement['trigger_map']['tr_ui_pool_food']['top'])
        for position in self.uielements['ui_hud'].uielement['tr_tile_dict']['tr_ui_pool_food']['positions']:
            position[1] = self.uielements['ui_hud'].uielement['trigger_map']['tr_ui_pool_food']['bottom'] - empty_food
        self.uielements['ui_hud'].uielement['tr_tile_dict']['tr_ui_hud_clock']['animations']['default'].frame_index = \
                        11 - self.gameboard.player_char.stats.char_pools['ap_cur']

    def effects_refresh(self):
        new_tile_dict = self.uielements['ui_hud'].uielement['tr_tile_dict'].copy()
        new_trigger_dict = self.uielements['ui_hud'].uielement['trigger_map'].copy()
        for key in self.uielements['ui_hud'].uielement['tr_tile_dict'].keys():
            if 'eff' in key:
                del new_tile_dict[key]
        for key in self.uielements['ui_hud'].uielement['trigger_map'].keys():
            if 'eff' in key:
                del new_trigger_dict[key]
        self.uielements['ui_hud'].uielement['tr_tile_dict'] = new_tile_dict
        self.uielements['ui_hud'].uielement['trigger_map'] = new_trigger_dict

        effect_index = 0
        for eff_id, effect in self.gameboard.player_char.stats.char_effects.items():
            trigger_id = 'eff-' + str(eff_id)
            pos_x = 4.5 + effect_index
            pos_y = 1.5
            effect_anims = self.gameboard.tables.table_roll(effect['media'], 'animation_table')
            self.uielements['ui_hud'].uielement['tr_tile_dict'][trigger_id] = {
                'trigger_id': trigger_id,
                'mirrored': 0,
                'flipped': 0,
                'width': 1,
                'height': 1,
                'positions': [[pos_x, pos_y]],
                'animations': {
                    'default': self.gameboard.resources.animations[effect_anims['icon']]
                }
            }
            self.uielements['ui_hud'].uielement['trigger_map'][trigger_id] = {
                'top': float(pos_y),
                'left': float(pos_x),
                'bottom': float(pos_y + 1),
                'right': float(pos_x + 1),
                'state': 'default',
                'key_code': 97
            }
            effect_index += 1

    def stats_refresh(self):
        if self.active_ui_flags['ui_stats']:
            self.stats_text_update(self.uielements['ui_stats'].uielement['dyn_textobj_dict'])
        if self.active_ui_flags['ui_stats_full']:
            self.stats_text_update(self.uielements['ui_stats_full'].uielement['dyn_textobj_dict'])

    def stats_text_update(self, id_list):
        for text_id, text_obj in id_list.items():
            try:
                self.uitext_caption_change(text_obj, str(self.gameboard.player_char.stats.char_stats_modified[text_id]))
            except KeyError:
                if text_id in self.gameboard.player_char.stats.dam_types:
                    dam_min, dam_max = self.gameboard.player_char.stats.get_damage_minmax(text_id, self.gameboard.player_char.stats,
                                                                                          self.gameboard.player_char.stats.modifiers_dict)
                    self.uitext_caption_change(text_obj, str(dam_min) + '-' + str(dam_max))
                elif text_id in self.gameboard.player_char.stats.def_types:
                    if text_id in self.gameboard.player_char.stats.modifiers_dict:
                        defence = self.gameboard.player_char.stats.modifiers_dict[text_id]
                        if 'force' in defence:
                            val_number = len(defence['force'])
                            forced_value = round(sum(defence['force']) / val_number)
                            self.uitext_caption_change(text_obj, '=' + str(forced_value))
                        else:
                            def_pts = False
                            def_perc = False
                            if 'points' in defence:
                                def_pts = sum(defence['points'])
                            if 'percent' in defence:
                                def_perc = sum(defence['percent'])
                            val_caption = ''
                            if def_pts is not False:
                                val_caption += (str(def_pts) + ' pts.')
                            if def_perc is not False:
                                if len(val_caption) > 0:
                                    val_caption += ', '
                                val_caption += (str(def_perc) + '%')
                            self.uitext_caption_change(text_obj, val_caption)
                    else:
                        self.uitext_caption_change(text_obj, '-')
                else:
                    if text_id in ['hp','mp','ap','food']:
                        new_text = str(self.gameboard.player_char.stats.char_pools[text_id + '_cur']) + '/' + str(
                            self.gameboard.player_char.stats.char_stats_modified[text_id + '_max'])
                        self.uitext_caption_change(text_obj, new_text)
                    elif text_id == 'experience':
                        self.uitext_caption_change(text_obj, str(self.gameboard.player_char.stats.char_pools['experience']))
                    elif text_id == 'stat_points':
                        self.uitext_caption_change(text_obj, str(self.gameboard.player_char.stats.stat_points))
                    elif text_id == 'name':
                        self.uitext_caption_change(text_obj, self.gameboard.player_char.rules['name'])
                    else:
                        self.uitext_caption_change(text_obj, '-')

    def spellbook_refresh(self):
        for i in range(0, len(self.gameboard.magic.player_spellbook)):
            spell = self.gameboard.magic.player_spellbook[i]
            trigger_id = 'spell-' + str(i)
            self.uielements['ui_spellbook'].uielement['tr_tile_dict'][trigger_id]['animations']['default'] = \
            self.gameboard.resources.animations[spell['spell_media']['anim_set']['icon']]
            self.uielements['ui_spellbook'].uielement['dyn_textobj_dict'][trigger_id].caption = str(spell['level'])
            self.uielements['ui_spellbook'].uielement['dyn_textobj_dict'][trigger_id].visible = True
            self.uielements['ui_spellbook'].uielement['dyn_textobj_dict'][trigger_id].redraw = True
        for i in range(len(self.gameboard.magic.player_spellbook), 24):
            trigger_id = 'spell-' + str(i)
            self.uielements['ui_spellbook'].uielement['tr_tile_dict'][trigger_id]['animations']['default'] = \
                self.gameboard.resources.animations['ui_empty']
            self.uielements['ui_spellbook'].uielement['dyn_textobj_dict'][trigger_id].visible = False
        if self.gameboard.magic.player_spell is not None:
            if self.gameboard.magic.magic_item is None:
                self.uielements['ui_spellbook'].uielement['tr_tile_dict']['select']['animations']['default'] = \
                    self.gameboard.resources.animations[
                        self.gameboard.magic.player_spell['spell_media']['anim_set']['icon']]
            else:
                self.uielements['ui_spellbook'].uielement['tr_tile_dict']['select']['animations']['default'] = \
                    self.gameboard.magic.magic_item.anim_set['tile']
            self.uielements['ui_spellbook'].uielement['dyn_textobj_dict']['select'].caption = str(
                self.gameboard.magic.player_spell['level'])
            self.uielements['ui_spellbook'].uielement['dyn_textobj_dict']['select'].visible = True
            self.uielements['ui_spellbook'].uielement['dyn_textobj_dict']['select'].redraw = True
        else:
            self.uielements['ui_spellbook'].uielement['tr_tile_dict']['select']['animations']['default'] = \
                self.gameboard.resources.animations['ui_empty']
            self.uielements['ui_spellbook'].uielement['dyn_textobj_dict']['select'].visible = False

    def gameload_refresh(self):
        if self.ui_variables['ui_gameload']['save_choice'] == -1:
            self.uielements['ui_gameload'].uielement['tr_tile_dict']['portrait']['animations']['default'] = \
                self.gameboard.resources.animations['ui_empty']
        for i in range(0, 14):
            slotname = 'save-' + str(i)
            game_id = self.gameboard.resources.file_read_param(slotname, self.gameboard.resources.path + '/save/player_characters.data')
            if game_id is not False:
                save_info = self.gameboard.resources.get_save_info(game_id)
                if save_info is not False:
                    time_str, pc_info, world_info = save_info
                else:
                    return False

                if self.ui_variables['ui_gameload']['save_choice'] == i:
                    self.uielements['ui_gameload'].uielement['tr_tile_dict']['portrait']['animations']['default'] = \
                        self.gameboard.resources.animations['ui_class_portrait_' + pc_info['class'] + '_color']
                    color = (255, 255, 0)

                    # TODO show text with save details
                else:
                    color = (200, 200, 200)

                self.uitext_caption_change(self.uielements['ui_gameload'].uielement['dyn_textobj_dict'][slotname],
                                           time_str + ': ' + pc_info['name'], color)

                self.uielements['ui_gameload'].uielement['dyn_textobj_dict'][slotname].visible = True
            else:
                self.uielements['ui_gameload'].uielement['dyn_textobj_dict'][slotname].visible = False
                if self.ui_variables['ui_gameload']['save_choice'] == i:
                    self.uielements['ui_gameload'].uielement['tr_tile_dict']['portrait']['animations']['default'] = \
                        self.gameboard.resources.animations['ui_empty']

    def message_refresh(self):
        self.uielements['ui_message'].uielement['tr_tile_dict']['icon']['animations']['default'] = \
            self.ui_variables['ui_message']['icon']
        self.uielements['ui_message'].uielement['dyn_textobj_dict']['message_text'].caption = \
        self.ui_variables['ui_message']['text'].replace('_', ' ')
        self.uielements['ui_message'].uielement['dyn_textobj_dict']['message_text'].visible = True
        self.uielements['ui_message'].uielement['dyn_textobj_dict']['message_text'].redraw = True

    def dialogue_refresh(self):
        self.uielements['ui_dialogue'].uielement['dyn_textobj_dict']['message_text'].caption = \
        self.ui_variables['ui_dialogue']['text'].replace('_', ' ')
        self.uielements['ui_dialogue'].uielement['dyn_textobj_dict']['message_text'].visible = True
        self.uielements['ui_dialogue'].uielement['dyn_textobj_dict']['message_text'].redraw = True

    def register_animations(self):
        for ui_name, flag in self.active_ui_flags.items():
            if flag and (ui_name in self.uielements):
                for tile in self.uielements[ui_name].uielement['tile_list']:
                    self.gameboard.animtick_set.add(tile['animation'])
                for tr_tile in self.uielements[ui_name].uielement['tr_tile_dict'].values():
                    for animation in tr_tile['animations'].values():
                        self.gameboard.animtick_set.add(animation)

    def show_ui(self):
        for ui_name, flag in self.active_ui_flags.items():
            if flag and (ui_name in self.uielements):
                self.uielements[ui_name].blitme()

    def inv_details_compose(self, item_obj):
        self.uielements['ui_details'].uielement['textobj_list'].clear()
        # creating details text objects dynamically:
        # text generator string: x, y, font, size, color, h_align, v_align, max_width, max_height, timer, mov_x, mov_y, caption
        item_title = item_obj.compose_full_title()
        offset_x = 0.2
        offset_y = 0.2
        offset_y += self.details_text_create(str(offset_x) + ' ' + str(offset_y) + ' default 20 34,32,52 238,195,154 left top 2.6 0 -1 0 0 ' + item_title)
        try:
            item_class_text = self.gameboard.resources.text_bank['item_class_' + item_obj.rules['item_class']]
        except KeyError:
            item_class_text = item_obj.rules['item_class']
        offset_y += self.details_text_create(
            str(offset_x) + ' ' + str(offset_y) + ' default 14 34,32,52 238,195,154 left top 2.6 0 -1 0 0 ' + item_class_text.capitalize())
        offset_y += 0.1
        for i in range(1, 4):
            parameter = 'parameter' + str(i)
            digits = 'digits' + str(i)
            value = 'value' + str(i)
            try:
                offset_y += self.details_compose_item_parameter(item_obj.rules[parameter], item_obj.rules[value],
                                                                item_obj.rules[digits], item_obj.rules['item_class'],
                                                                0, offset_x, offset_y)
            except KeyError:
                pass
        offset_y += 0.1
        if 'affixes' in item_obj.rules:
            for affix in item_obj.rules['affixes']:
                for i in range(1, 4):
                    parameter = 'parameter' + str(i)
                    digits = 'digits' + str(i)
                    value = 'value' + str(i)
                    try:
                        offset_y += self.details_compose_item_parameter(affix[parameter], affix[value],
                                                                        affix[digits], affix['type'],
                                                                        0, offset_x, offset_y)
                    except KeyError:
                        pass
        offset_y += 0.1
        if item_obj.rules['id'] == 'spellbook':
            offset_y += self.details_text_create(
                str(offset_x) + ' ' + str(offset_y) + ' default 14 34,32,52 238,195,154 left top 2.6 1.5 -1 0 0 ' +
                str(item_obj.rules['level']) + self.gameboard.get_number_suffix(item_obj.rules['level']) + '_level')
        try:
            offset_y += self.details_text_create(
                str(offset_x) + ' ' + str(offset_y) + ' default 14 34,32,52 238,195,154 left top 2.6 1.5 -1 0 0 ' +
                item_obj.text_set['description'])
        except KeyError:
            pass
        try:
            condition_cur = item_obj.rules['condition_cur']
            try:
                condition_max = item_obj.rules['condition_aff']
            except KeyError:
                condition_max = item_obj.rules['condition_max']
            condition_color = '15,15,15'
            if condition_cur < condition_max / 2:
                condition_color = '255,255,0'
            elif condition_cur < condition_max / 4 or condition_cur == 1:
                condition_color = '255,0,0'
            condition_str = 'Condition:_' + str(condition_cur) + '_of_' + str(condition_max)
            offset_y += 0.1
            offset_y += self.details_text_create(str(offset_x) + ' ' + str(
                offset_y) + ' default 14 ' + condition_color + ' 238,195,154 left top 2.6 0 -1 0 0 ' + condition_str)
        except KeyError:
            pass
        self.uielements['ui_details'].offset_y = self.uielements['ui_details'].offset_x = 0
        if self.gameboard.mouse_y + self.uielements[
            'ui_details'].offset_y + offset_y * self.gameboard.square_height > self.gameboard.sight_height:
            self.uielements['ui_details'].offset_y -= offset_y
        if self.gameboard.mouse_x + self.uielements[
            'ui_details'].offset_x + offset_x * self.gameboard.square_width > self.gameboard.sight_width:
            self.uielements['ui_details'].offset_x -= offset_x

    def eff_details_compose(self, effect_dict):
        self.uielements['ui_details'].uielement['textobj_list'].clear()
        # creating details text objects dynamically:
        # text generator string: x, y, font, size, color, h_align, v_align, max_width, max_height, timer, mov_x, mov_y, caption
        effect_text = self.gameboard.tables.table_roll(effect_dict['media'], 'text_table')
        offset_x = 0.1
        offset_y = 0.1
        effect_text_title = self.gameboard.resources.text_bank[effect_text['title']]
        offset_y += self.details_text_create('0.1 0.1 default 20 34,32,52 238,195,154 left top 2.6 0 -1 0 0 ' + effect_text_title)
        offset_y += 0.1
        for i in range(1, 4):
            parameter = 'parameter' + str(i)
            digits = 'digits' + str(i)
            value = 'value' + str(i)
            try:
                offset_y += self.details_compose_item_parameter(effect_dict[parameter], effect_dict[value],
                                                                effect_dict[digits], 'effect',
                                                                0, offset_x, offset_y)
            except KeyError:
                pass
        offset_y += 0.1
        effect_text_desc = self.gameboard.resources.text_bank[effect_text['description']]
        try:
            offset_y += self.details_text_create(
                str(offset_x) + ' ' + str(offset_y) + ' default 14 34,32,52 238,195,154 left top 2.6 1.5 -1 0 0 ' +
                effect_text_desc)
        except KeyError:
            pass
        try:
            time_cur = effect_dict['time']
            if time_cur != -1:
                time_color = '15,15,15'
                if time_cur == 1:
                    time_color = '255,0,0'
                time_str = 'Time_left:_' + str(time_cur) + '_turn%1.'
                if time_cur > 1:
                    time_str = time_str.replace('%1','s')
                else:
                    time_str = time_str.replace('%1', '')
                offset_y += 0.1
                offset_y += self.details_text_create(str(offset_x) + ' ' + str(
                    offset_y) + ' default 14 ' + time_color + ' 238,195,154 left top 2.6 0 -1 0 0 ' + time_str)
        except KeyError:
            pass
        self.uielements['ui_details'].offset_y = self.uielements['ui_details'].offset_x = 0
        if self.gameboard.mouse_y + self.uielements[
            'ui_details'].offset_y + offset_y * self.gameboard.square_height > self.gameboard.sight_height:
            self.uielements['ui_details'].offset_y -= offset_y
        if self.gameboard.mouse_x + self.uielements[
            'ui_details'].offset_x + offset_x * self.gameboard.square_width > self.gameboard.sight_width:
            self.uielements['ui_details'].offset_x -= offset_x

    def spell_details_compose(self, spell_dict):
        self.uielements['ui_details'].uielement['textobj_list'].clear()
        # creating details text objects dynamically:
        # text generator string: x, y, font, size, color, h_align, v_align, max_width, max_height, timer, mov_x, mov_y, caption
        spell_text = spell_dict['spell_media']['text_set']
        offset_x = 0.2
        offset_y = 0.2
        spell_text_title = spell_text['title']
        offset_y += self.details_text_create(
            str(offset_x) + ' ' + str(
                offset_y) + ' default 20 34,32,52 238,195,154 left top 2.6 0 -1 0 0 ' + spell_text_title)
        offset_y += 0.1
        spell_text_desc = spell_text['description']
        try:
            offset_y += self.details_text_create(
                str(offset_x) + ' ' + str(offset_y) + ' default 14 34,32,52 238,195,154 left top 2.6 1.5 -1 0 0 ' +
                spell_text_desc)
        except KeyError:
            pass
        self.uielements['ui_details'].offset_y = self.uielements['ui_details'].offset_x = 0
        if self.gameboard.mouse_y + self.uielements[
            'ui_details'].offset_y + offset_y * self.gameboard.square_height > self.gameboard.sight_height:
            self.uielements['ui_details'].offset_y -= offset_y
        if self.gameboard.mouse_x + self.uielements[
            'ui_details'].offset_x + offset_x * self.gameboard.square_width > self.gameboard.sight_width:
            self.uielements['ui_details'].offset_x -= offset_x

    def details_text_create(self, str_params):
        new_text = self.uielements['ui_details'].create_text(str_params)
        self.uielements['ui_details'].uielement['textobj_list'].append(new_text)
        print(new_text.max_height)
        offset_y = new_text.max_height / self.gameboard.square_height
        return offset_y

    def details_compose_item_parameter(self, parameter, value, digits, item_class, line_height, offset_x, offset_y):
        try:
            text_color = self.parameter_colors_dict[parameter]
        except KeyError:
            text_color = '34,32,52'
        try:
            text_caption = self.gameboard.resources.text_bank['par_' + parameter]
        except KeyError:
            text_caption = parameter
        str_value = str(value)
        if digits == 'force':
            composed_string = text_caption + '_=' + str_value
        elif digits == 'points':
            composed_string = '+' + str_value + '_' + text_caption
        elif digits == 'percent':
            composed_string = '+' + str_value + '%_' + text_caption
        if item_class == 'wpn':
            composed_string = composed_string.replace('+', '')
        offset = self.details_text_create(
            str(offset_x) + ' ' + str(offset_y) + ' default 14 ' + text_color + ' 238,195,154 left top 2.8 ' + str(
                line_height) + ' -1 0 0 ' + composed_string.capitalize())
        return offset

    def ui_block(self):
        for uielement in self.active_ui_flags.keys():
            self.active_ui_flags[uielement] = False

    def uitext_caption_change(self, uitext_object, caption, color=None):
        uitext_object.caption = caption.replace('_',' ')
        if color is not None:
            uitext_object.color = color
        uitext_object.redraw = True
        uitext_object.max_height, uitext_object.actual_width = uitext_object.get_text_height()

    def hero_name_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.ui_variables['ui_characters']['hero_name'] = self.ui_variables['ui_characters']['hero_name'][:-1]
        elif event.key == pygame.K_RETURN:
            pass
        elif len(self.ui_variables['ui_characters']['hero_name']) <= 19:
            str_char = event.unicode
            self.ui_variables['ui_characters']['hero_name'] += str_char
        self.hero_name_input_display()

    def hero_name_input_display(self):
        self.uitext_caption_change(self.uielements['ui_characters'].uielement['dyn_textobj_dict']['name_input'],
                                   'Name:_' + self.ui_variables['ui_characters']['hero_name'].replace(' ', '_'),
                                   (255, 255, 255))

    def ui_characters_class_select(self, trigger_id, anim_portrait_name):
        self.ui_characters_portraits_reset()
        self.uielements['ui_characters'].uielement['tr_tile_dict'][trigger_id]['animations'][
            'default'] = self.gameboard.resources.animations[anim_portrait_name]
        frame_left_x = self.uielements['ui_characters'].uielement['trigger_map'][trigger_id]['left'] - \
                       self.uielements['ui_characters'].uielement['tr_tile_dict']['selection_frame_left'][
                           'width']
        frame_left_y = self.uielements['ui_characters'].uielement['trigger_map'][trigger_id]['top']
        frame_right_x = self.uielements['ui_characters'].uielement['trigger_map'][trigger_id]['right']
        frame_right_y = self.uielements['ui_characters'].uielement['trigger_map'][trigger_id]['top']
        self.uielements['ui_characters'].uielement['tr_tile_dict']['selection_frame_left']['positions'] = [
            [frame_left_x, frame_left_y]]
        self.uielements['ui_characters'].uielement['tr_tile_dict']['selection_frame_right']['positions'] = [
            [frame_right_x, frame_right_y]]

        self.uielements['ui_characters'].uielement['tr_tile_dict']['selection_frame_left']['positions'] = []
        self.uielements['ui_characters'].uielement['tr_tile_dict']['selection_frame_right']['positions'] = []
        for position in self.uielements['ui_characters'].uielement['tr_tile_dict'][trigger_id]['positions']:
            selection_left_x = position[0] - self.uielements['ui_characters'].uielement['tr_tile_dict']['selection_frame_left'][
                           'width']
            self.uielements['ui_characters'].uielement['tr_tile_dict']['selection_frame_left']['positions'].append(
                [selection_left_x, position[1]])
            selection_right_x = position[0] + self.uielements['ui_characters'].uielement['tr_tile_dict'][trigger_id]['width']
            self.uielements['ui_characters'].uielement['tr_tile_dict']['selection_frame_right']['positions'].append(
                [selection_right_x, position[1]])

    def ui_characters_portraits_reset(self):
        self.uielements['ui_characters'].uielement['tr_tile_dict']['bttn_fighter']['animations'][
            'default'] = self.gameboard.resources.animations['ui_class_portrait_fighter_bw']
        self.uielements['ui_characters'].uielement['tr_tile_dict']['bttn_ranger']['animations'][
            'default'] = self.gameboard.resources.animations['ui_class_portrait_ranger_bw']
        self.uielements['ui_characters'].uielement['tr_tile_dict']['bttn_sorcerer']['animations'][
            'default'] = self.gameboard.resources.animations['ui_class_portrait_sorcerer_bw']

    def effect_icon_click(self, effect_id):
        if effect_id == 'pc_hp_low':
            potion = self.gameboard.inventory_find_item(self.gameboard.player_char.inventory.backpack,
                                                           item_id='ptn_healing')
            if potion is not False:
                item, inv = potion
                item.useme(self.gameboard.player_char, inv)

        elif effect_id == 'pc_food_low':
            food = self.gameboard.inventory_find_item(self.gameboard.player_char.inventory.backpack,
                                                           item_class='foo')
            if food is not False:
                item, inv = food
                item.useme(self.gameboard.player_char, inv)
            else:
                self.gameboard.audio.sound_bank['pc_step01'].play()

    # TODO Character trade screen, options screen, spellbook screen, pause screen

    def create_unique_uis(self, pc_class):
        self.uielements['ui_stats'] = UIElement(self.gameboard, 'ui_stats_' + pc_class)
        self.uielements['ui_inventory'] = UIElement(self.gameboard, 'ui_inventory_' + pc_class)
