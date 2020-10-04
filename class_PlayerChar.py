# Player character object
# includes:
# engine variables
# rpg rules statistics
# inventory
import pygame
from class_Animation import Animation
from class_Particle import Particle
from class_Stats import Stats
from class_Inventory import Inventory
from class_Text import Text
from class_Item import Item


class PlayerChar:
    pc_class = 'test_class'

    def __init__(self, gameboard, game_id, rules):
        self.gameboard = gameboard
        self.game_id = game_id

        # Initialize attributes to represent the character.
        self.image = None

        self.screen = self.gameboard.screen

        # Absolute coordinates in pixels.
        self.x, self.y = 0, 0
        self.dest_x, self.dest_y = self.x, self.y
        self.moving = False
        self.attacking = False
        self.easing = 0.5
        self.mirrored = False
        self.move_key = None

        self.width = self.gameboard.square_width
        self.height = self.gameboard.square_height
        self.drawing_depth = 15
        self.visible = True
        self.anim_prev = None

        self.rules = rules
        # Adding Character Stats and Inventory
        self.gameboard.set_rules(self, self.rules)
        self.get_media(self.rules['media'])
        self.stop = False

        self.temp_anim = False
        self.temp_anim_timer = 0
        self.anim_forced = False

        self.gameboard.ui.container_crumps = [self.inventory.backpack]

    def get_media(self, media):
        # Get animation
        self.anim_set = self.gameboard.tables.table_roll(media, 'animation_table')
        for name, anim_name in self.anim_set.items():
            self.anim_set[name] = Animation(self.gameboard.resources, anim_name, self.gameboard.resources.animation_files[self.anim_set[name]])
        self.default_anim = self.anim_set['walk_north']
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

    def tick(self):
        if not self.stop:
            if self.moving:
                self.gameboard.animtick_set.add(self.animation)
                self.moveme()
            else:
                if self.gameboard.players_turn and self.stats.char_pools['ap_cur'] == 0:
                    self.gameboard.next_turn()

            self.move_player_control()

        if self.attacking:
            self.gameboard.animtick_set.add(self.animation)
            self.attacking = False

        self.gameboard.anim_check(self)

        self.update_view()

    def move_player_control(self):
        if not self.moving and self.gameboard.move_player and self.gameboard.players_turn and self.stats.char_pools['ap_cur'] > 0:
            # if self.dest_x == self.x and self.dest_y == self.y:
            if self.move_key == 'down':
                self.gameboard.move_player = self.gameboard.move_object(self, self.dest_x,
                                                                        self.dest_y + self.gameboard.square_height)
            elif self.move_key == 'up':
                self.gameboard.move_player = self.gameboard.move_object(self, self.dest_x,
                                                                        self.dest_y - self.gameboard.square_height)
            elif self.move_key == 'left':
                self.gameboard.move_player = self.gameboard.move_object(self,
                                                                        self.dest_x - self.gameboard.square_width,
                                                                        self.dest_y)
            elif self.move_key == 'right':
                self.gameboard.move_player = self.gameboard.move_object(self,
                                                                        self.dest_x + self.gameboard.square_width,
                                                                        self.dest_y)
            else:
                x_dist = self.gameboard.mouse_x - (self.dest_x + (self.width // 2) - self.gameboard.view_x)
                y_dist = self.gameboard.mouse_y - (self.dest_y + (self.height // 2) - self.gameboard.view_y)
                if abs(x_dist) > abs(y_dist):
                    dest_x = self.dest_x + self.gameboard.square_width * self.gameboard.sign(x_dist)
                    self.gameboard.move_player = self.gameboard.move_object(self, dest_x, self.dest_y)
                else:
                    dest_y = self.dest_y + self.gameboard.square_height * self.gameboard.sign(y_dist)
                    self.gameboard.move_player = self.gameboard.move_object(self, self.dest_x, dest_y)

    def moveme(self):
        mov_x = self.gameboard.sign(self.dest_x - self.x) * (self.gameboard.square_width // 12)
        mov_y = self.gameboard.sign(self.dest_y - self.y) * (self.gameboard.square_height // 12)
        if mov_x or mov_y:
            self.x += mov_x
            self.y += mov_y
            if mov_x > 0:
                self.gameboard.set_anim(self, 'walk_east', False)
            elif mov_x < 0:
                self.gameboard.set_anim(self, 'walk_west', False)
            elif mov_y > 0:
                self.gameboard.set_anim(self, 'walk_south', False)
            elif mov_y < 0:
                self.gameboard.set_anim(self, 'walk_north', False)

            """if self.gameboard.labyrinth.spotlight is not None:
                self.gameboard.labyrinth.spotlight.x = self.x
                self.gameboard.labyrinth.spotlight.y = self.y"""
        else:
            self.x = self.dest_x
            self.y = self.dest_y
            self.moving = False
            self.step_turn()
            self.events_turn()

    def attack(self, target):  # attacker, char, damage, attack_type, damage_type, inflict_status
        distance = self.gameboard.get_distance(target.x, target.y, self.x, self.y)
        modifiers_dict = self.stats.get_modifiers_dict(self.inventory)
        attack_list = self.stats.get_attacks(self.stats, modifiers_dict)
        for attack in attack_list:
            self.gameboard.woundme(self, target, attack['damage'], attack['attack_type'], attack['damage_type'], attack['inflict_status'])
        dir_x = self.gameboard.sign(target.x - self.x)
        dir_y = self.gameboard.sign(target.y - self.y)
        if dir_x > 0:
            # self.gameboard.set_temp_anim(self, 'attack_east', 8, False)
            self.gameboard.set_anim(self, 'walk_east', False)
        elif dir_x < 0:
            # self.gameboard.set_temp_anim(self, 'attack_west', 8, False)
            self.gameboard.set_anim(self, 'walk_west', False)
        elif dir_y > 0:
            # self.gameboard.set_temp_anim(self, 'attack_south', 8, False)
            self.gameboard.set_anim(self, 'walk_south', False)
        elif dir_y < 0:
            # self.gameboard.set_temp_anim(self, 'attack_north', 8, False)
            self.gameboard.set_anim(self, 'walk_north', False)

        self.attacking = True
        self.equipment_break(50, ['wpn'])
        self.step_turn()

        if len(attack_list) > 0:
            self.attacking = True
            self.gameboard.show_hit(self, target.x, target.y, attack['attack_type'], attack['damage_type'])

    def ranged_attack_check(self, x, y):
        if self.inventory.equipped['main_hand'] is not None and 'ranged' in self.inventory.equipped['main_hand'].rules:
            if 'ammo_type' not in self.inventory.equipped['main_hand'].rules or (
                    self.inventory.equipped['ammo_slot'] is not None and
                    'ammo_type' in self.inventory.equipped['ammo_slot'].rules and
                    self.inventory.equipped['main_hand'].rules['ammo_type'] ==
                    self.inventory.equipped['ammo_slot'].rules['ammo_type']):
                obj_target = self.gameboard.mouse_on_object(x, y, self.gameboard.render_mobs_list)
                if obj_target is not False and self.gameboard.test_arrow(self.x + self.width // 2,
                                                                          self.y + self.height // 2,
                                                                          obj_target.x + obj_target.width // 2,
                                                                          obj_target.y + obj_target.height // 2):
                    if 'ammo_type' in self.inventory.equipped['main_hand'].rules:
                        if self.inventory.equipped['ammo_slot'].rules['amount_cur'] != 0:
                            speed_x = (obj_target.x - self.x) / 8
                            speed_y = (obj_target.y - self.y) / 8
                            new_particle = Particle(self.gameboard,
                                                    self.inventory.equipped['ammo_slot'].anim_set['tile'],
                                                    None, 8, speed_x, speed_y,
                                                    self.x + self.width // 2, self.y + self.height // 2)
                            if self.inventory.equipped['ammo_slot'].rules['amount_cur'] > 1:
                                self.inventory.equipped['ammo_slot'].rules['amount_cur'] -= 1
                            elif self.inventory.equipped['ammo_slot'].rules['amount_cur'] == 1:
                                self.inventory.equipped['ammo_slot'] = None
                            self.attack(obj_target)
                        self.gameboard.ui.ragdoll_refresh(self.gameboard.ui.container_crumps[-1])
                    return True
        return False

    def step_turn(self):
        self.checkme()
        self.stats.char_pools['ap_cur'] -= 1
        self.stats.char_pools['food_cur'] -= 1
        self.gameboard.ui.stats_refresh()
        if self.stats.char_pools['food_cur'] == 0:
            self.defeated(None)
        else:
            self.gameboard.ui.hud_refresh()

    def events_turn(self):
        # check traps
        trap = self.gameboard.collidelist(self, self.x, self.y, self.gameboard.render_trap_list, 0)
        if trap:
            trap.discharge(self)
        # check stairs
        stairs = self.gameboard.collidelist(self, self.x, self.y, self.gameboard.labyrinth.stairs_list, 0)
        if stairs:
            if stairs.rules['stairs_type'] == 1:
                self.gameboard.save_game()
                self.gameboard.labyrinth.dungeon_create(self.gameboard.labyrinth.dungeon_id, self.stats.char_stats_modified['level'], self.gameboard.labyrinth.depth + 1, 'descended')
            if stairs.rules['stairs_type'] == -1 and self.gameboard.labyrinth.depth > 1:
                self.gameboard.save_game()
                self.gameboard.labyrinth.dungeon_create(self.gameboard.labyrinth.dungeon_id, self.stats.char_stats_modified['level'], self.gameboard.labyrinth.depth - 1, 'ascended')

        self.gameboard.labyrinth.room_discover(self)

    def autoequip(self, loot_item):
        if self.inventory.equipped['main_hand'] is None and loot_item.rules['item_class'] == 'wpn' and \
                self.stats.char_stats_modified['class'] in loot_item.rules['class']:
            self.inventory.equipped['main_hand'] = loot_item
            self.stats.stats_recalc()
            return True
        return False

    def defeated(self, attacker):
        self.x, self.y = self.dest_x, self.dest_y
        self.gameboard.set_anim(self, 'dead', True)
        self.sound_set['dead'].play()
        self.stop = True

        dead_message = self.text_set['dead'].replace('%1', self.rules['name'])
        if attacker is not None:
            dead_message = dead_message.replace('%2', attacker.text_set['title'])
        else:
            dead_message = dead_message.replace('%2', 'the dungeon')
        dead_message = dead_message.replace('%3', str(self.gameboard.labyrinth.depth))
        dead_message = dead_message.replace('%5', self.gameboard.labyrinth.labyrinth_rules['name'])
        dead_message = dead_message.replace('%4', self.gameboard.get_number_suffix(self.gameboard.labyrinth.depth))

        for equip in self.inventory.equipped.keys():
            if self.inventory.equipped[equip] is not None:
                self.inventory.backpack.append(self.inventory.equipped[equip])
                self.inventory.equipped[equip] = None

        if len(self.inventory.backpack) > 0:
            sack_item = self.gameboard.tables.table_roll('cnt_sack_onetime', 'treasure_table')
            new_sack = Item(self.gameboard, sack_item, 1, self.x, self.y)
            new_sack.rules['container'] = []
            sticky_list = []
            sticky_list.extend(self.gameboard.pick_cursed_items(self.inventory.backpack))
            for i in range(0, len(self.inventory.backpack)):
                new_sack.rules['container'].append(self.inventory.backpack[i])
            self.gameboard.labyrinth.drop_loot([new_sack], self.x, self.y, False)
            self.inventory.backpack.clear()
            for i in sticky_list:
                self.inventory.backpack.append(i)
            self.gameboard.ui.ragdoll_refresh(self.gameboard.ui.container_crumps[0])

        self.gameboard.ui.ui_block()
        self.gameboard.ui.uitext_caption_change(
            self.gameboard.ui.uielements['ui_death'].uielement['dyn_textobj_dict']['necrolog0'], dead_message,
            (255,0,0))
        self.gameboard.ui.active_ui_flags['ui_death'] = True

    def equipment_break(self, percent, itemclass_list):
        for part, itm in self.inventory.equipped.items():
            if itm is not None and 'item_class' in itm.rules and itm.rules['item_class'] in itemclass_list:
                result = self.gameboard.pick_random([percent, 100 - percent], [1, 0])
                if result:
                    if itm.item_break(-1):
                        self.inventory.equipped[part] = None
                        self.gameboard.ui.ragdoll_refresh(self.gameboard.ui.container_crumps[-1])

    def checkme(self):
        if self.stats.char_pools['hp_cur'] < self.stats.char_stats_modified['hp_max'] // 4:
            if 'pc_hp_low' not in self.stats.char_effects:
                self.stats.effect_add('pc_hp_low')
        elif 'pc_hp_low' in self.stats.char_effects:
            self.stats.effect_remove('pc_hp_low')

        if self.stats.char_pools['food_cur'] < self.stats.char_stats_modified['food_max'] // 4:
            if 'pc_food_low' not in self.stats.char_effects:
                self.stats.effect_add('pc_food_low')
        elif 'pc_food_low' in self.stats.char_effects:
            self.stats.effect_remove('pc_food_low')

    def resurrect(self):
        # reappear on the start of current labyrinth with full hp and exp/item condition penalty
        self.stats.char_pools_maximize()

        self.gameboard.player_char.x, self.gameboard.player_char.y = self.gameboard.labyrinth.start_x, self.gameboard.labyrinth.start_y
        self.gameboard.player_char.dest_x, self.gameboard.player_char.dest_y = self.gameboard.player_char.x, self.gameboard.player_char.y

        self.anim_forced = False
        self.gameboard.set_anim(self, 'walk_south', False)
        self.stop = False
        self.gameboard.ui.ui_block()

        self.stats.char_effects.clear()
        self.stats.stats_recalc()
        self.gameboard.ui.stats_refresh()
        self.gameboard.ui.effects_refresh()

        self.gameboard.ui.active_ui_flags['ui_hud'] = True
        self.gameboard.ui.active_ui_flags['ui_scene_info'] = True
        self.gameboard.labyrinth.room_discover(self)

    def update_view(self, instant=False):
        """margin_x_left = 7
        margin_x_right = 6
        margin_y_top = 5
        margin_y_bottom = 5

        if (self.gameboard.view_x + self.gameboard.sight_width) - (self.x + self.gameboard.player_char.width) \
                < self.gameboard.square_width * margin_x_right:
            self.gameboard.view_x = self.x + self.gameboard.player_char.width - \
                                    self.gameboard.sight_width + self.gameboard.square_width * margin_x_right
        elif self.x - self.gameboard.view_x < self.gameboard.square_width * margin_x_left:
            self.gameboard.view_x = self.x - self.gameboard.square_width * margin_x_left

        if (self.gameboard.view_y + self.gameboard.sight_height) - (self.y + self.gameboard.player_char.height) \
                < self.gameboard.square_height * margin_y_bottom:
            self.gameboard.view_y = self.y + self.gameboard.player_char.height - \
                                    self.gameboard.sight_height + self.gameboard.square_height * margin_y_bottom
        elif self.y - self.gameboard.view_y < self.gameboard.square_height * margin_y_top:
            self.gameboard.view_y = self.y - self.gameboard.square_height * margin_y_top"""
        if instant:
            self.gameboard.view_x = self.x + self.width // 2 - self.gameboard.sight_width // 2
            self.gameboard.view_y = self.y + self.height // 2 - self.gameboard.sight_height // 2
        else:
            self.gameboard.view_x += (self.x + self.width // 2 - (
                        self.gameboard.view_x + self.gameboard.sight_width // 2)) * 0.1
            self.gameboard.view_y += (self.y + self.height // 2 - (
                        self.gameboard.view_y + self.gameboard.sight_height // 2)) * 0.1
        self.gameboard.view_x = round(self.gameboard.view_x)
        self.gameboard.view_y = round(self.gameboard.view_y)

    def blitme(self):
        # Draw the piece at its current location.

        self.image = self.animation.frames[self.animation.frame_index]

        if self.mirrored:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.topleft = self.x - self.gameboard.view_x + self.actual_offset_x, \
                                self.y - self.gameboard.view_y + self.actual_offset_y
        self.screen.blit(pygame.transform.scale(self.image, (self.width, self.height)), self.rect)
