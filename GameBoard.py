import sys

import pygame
import math
import random

from class_Settings import Settings
from class_Resources import Resources
from class_PlayerChar import PlayerChar
from class_Labyrinth import Labyrinth
from class_Tables import Tables
from class_Text import Text
from class_Audio import Audio
from class_Stats import Stats
from class_Inventory import Inventory
from class_Particle import Particle
from class_Item import Item
from class_Magic import Magic
from class_UI import UI


class GameBoard:
    # Overall class to manage game assets and behavior.

    def __init__(self):
        # Initialize the game, and create resources.
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mixer.init()

        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Gameboard")
        self.fps = 60

        self.resources = Resources()

        # list of interior objects that has to be drawn
        self.render_interior_list = []

        # list of interior objects that has to be drawn and hover above player
        self.render_interior_covering_list = []

        # list of all created in-game item objects
        self.render_items_list = []

        # list of all rendering texts
        self.render_text_list = []

        # list of all rendering mobs
        self.render_mobs_list = []

        # lis of all rendering traps
        self.render_trap_list = []

        self.render_effects_list = []

        self.animtick_set = set()
        self.solid_list = []
        self.objects_count = 0
        self.objects_number = 0

        self.view_x = 0
        self.view_y = 0
        self.sight_width = self.settings.screen_width
        self.sight_height = self.settings.screen_height
        self.square_width = 72
        self.square_height = 72
        self.map_sight_width = self.square_width * 18
        self.map_sight_height = self.square_height * 10
        self.default_speed_x = self.square_width // 4
        self.default_speed_y = self.square_height // 4

        self.player_char = None
        self.players_turn = False
        self.mobs_turn = False
        self.move_player = False
        self.player_in_room = False

        self.reserved_xy_list = []

        self.mouse_hand = None

        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_idle_ticks = 0
        self.mouse_idle_max = 60
        self.controls_shift = False

        # self.game_rules = self.load_rules('./res/data/rulebook/pc_classes/' + self.game_class + '.rlb')

        self.ui = UI(self)
        self.audio = Audio(self)
        self.tables = Tables(self)
        self.labyrinth = Labyrinth(self)
        self.magic = Magic(self)

        self.set_defence_types()

        self.ui.ui_block()
        self.ui.active_ui_flags['ui_title'] = True

    def run_game(self):
        self.clock = pygame.time.Clock()
        # Start the main loop for the game.
        while True:
            # create? and draw player character
            # https://ehmatthes.github.io/pcc_2e/beyond_pcc/pygame_sprite_sheets/
            self._check_events()
            self._update_screen(self.tick_objects())

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.sight_width, self.sight_height = event.w, event.h
                pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                # Window1.blit(Window1copy, (0, 0))
                pygame.display.update()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:

                if self.ui.active_ui_flags['ui_characters']:
                    self.ui.hero_name_input(event)
                else:
                    if event.key == pygame.K_q:
                        sys.exit()

                    if event.key == pygame.K_w:
                        wpn_item = self.tables.table_roll('wpn_shortsword_base', 'treasure_table')
                        new_wpn = Item(self, wpn_item, 1, self.player_char.x, self.player_char.y)
                        self.player_char.inventory.backpack.append(new_wpn)

                    if event.key == pygame.K_l:
                        self.player_char.stats.stat_points += 10

                    if event.key == pygame.K_d and len(self.player_char.inventory.backpack) > 0:
                        chest_item = self.tables.table_roll('cnt_chest_common', 'treasure_table')
                        new_chest = Item(self, chest_item, 1, self.player_char.x, self.player_char.y)
                        new_chest.rules['container'] = [itm for itm in self.player_char.inventory.backpack]
                        self.player_char.inventory.backpack.clear()
                        self.player_char.inventory.backpack.append(new_chest)
                        self.labyrinth.drop_loot(self.player_char.inventory.backpack, self.player_char.x,
                                                 self.player_char.y, True)
                        self.player_char.inventory.backpack.clear()
                        self.ui.ragdoll_refresh(self.ui.container_crumps[-1])

                    if event.key == pygame.K_b:
                        chest_item = self.tables.table_roll('cnt_chest_common', 'treasure_table')
                        new_chest = Item(self, chest_item, 1, self.player_char.x, self.player_char.y)
                        self.player_char.inventory.backpack.append(new_chest)

                if self.player_char and self.players_turn and not self.player_char.stop:
                    if event.key == pygame.K_DOWN:
                        self.player_char.move_key = 'down'
                        self.move_player = True
                    elif event.key == pygame.K_UP:
                        self.player_char.move_key = 'up'
                        self.move_player = True
                    elif event.key == pygame.K_LEFT:
                        self.player_char.move_key = 'left'
                        self.move_player = True
                    elif event.key == pygame.K_RIGHT:
                        self.player_char.move_key = 'right'
                        self.move_player = True

                if event.key == pygame.KMOD_SHIFT:
                    self.controls_shift = True

            elif self.player_char is not None and event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN and self.player_char.move_key == 'down':
                    self.player_char.move_key = None
                    self.move_player = False
                elif event.key == pygame.K_UP and self.player_char.move_key == 'up':
                    self.player_char.move_key = None
                    self.move_player = False
                elif event.key == pygame.K_LEFT and self.player_char.move_key == 'left':
                    self.player_char.move_key = None
                    self.move_player = False
                elif event.key == pygame.K_RIGHT and self.player_char.move_key == 'right':
                    self.player_char.move_key = None
                    self.move_player = False

                if event.key == pygame.KMOD_SHIFT:
                    self.controls_shift = False

            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = event.button
                if not self.ui.control_capture_mouse('mouse_down', mouse_button, self.mouse_x, self.mouse_y):
                    if self.player_char is not None and self.mouse_hand is None and not self.player_char.stop and \
                            not self.ui.active_ui_flags['ui_pause'] and not self.ui.active_ui_flags[
                                'ui_message'] and not self.ui.active_ui_flags['ui_dialogue']:
                        if mouse_button == 1 and (
                                self.player_char.inventory.equipped['main_hand'] is None or 'ranged' not in
                                self.player_char.inventory.equipped['main_hand'].rules or self.mouse_on_object(
                            self.mouse_x + self.view_x, self.mouse_y + self.view_y, self.render_mobs_list) is False):
                            self.move_player = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_button = event.button
                if mouse_button == 1:
                    self.move_player = False
                if not self.ui.control_capture_mouse('mouse_up', mouse_button, self.mouse_x, self.mouse_y) and \
                        not self.ui.active_ui_flags['ui_pause'] and not self.ui.active_ui_flags[
                            'ui_message'] and not self.ui.active_ui_flags['ui_dialogue']:
                    if self.mouse_hand is None:
                        if mouse_button == 3:
                            if self.player_char is not None and not self.player_char.stop and self.magic.player_spell is not None:
                                self.magic.spell_mouse()

                    if self.player_char and self.mouse_hand is not None and mouse_button == 1 and not self.player_char.stop:
                        if 'curse' in self.mouse_hand.rules:
                            new_text = Text(self, self.resources.text_bank['cant_drop_cursed'],
                                            self.player_char.x + self.player_char.width // 2, self.player_char.y,
                                            'default', 22, (255,255,255), 'center', 'top', 1, 0, 0)
                            self.mouse_hand.sound_set['pickup'].play()
                        else:
                            if 'container' in self.mouse_hand.rules:
                                self.player_char.inventory.backpack.extend(self.pick_cursed_items(self.mouse_hand.rules['container']))
                                self.ui.ragdoll_refresh(self.ui.container_crumps[-1])
                            self.labyrinth.drop_loot([self.mouse_hand], self.player_char.x, self.player_char.y, True)
                            self.mouse_hand.sound_set['pickup'].play()
                            self.mouse_hand = None
                    if mouse_button == 1 and self.player_char is not None and not self.player_char.stop:
                        self.player_char.ranged_attack_check(self.mouse_x + self.view_x, self.mouse_y + self.view_y)

            if pygame.mouse.get_rel() != (0, 0):
                self.mouse_idle_ticks = 0

    def tick_objects(self):
        draw_list = []
        self.animtick_set.clear()

        if self.mouse_idle_ticks < self.mouse_idle_max:
            self.mouse_idle_ticks += 1
        self.ui.control_mouse_over(self.mouse_x, self.mouse_y)

        if len(self.render_interior_list) > self.objects_count:
            self.render_interior_list.sort(key=lambda x: x.drawing_depth)

        for i in self.render_interior_list:
            if i.visible and self.in_sight(i):
                i.tick()
                draw_list.append(i)

        for i in self.render_trap_list:
            if i.visible and i.rules['hidden'] == 0 and self.in_sight(i):
                i.tick()
                draw_list.append(i)

        for i in self.render_items_list:
            if i.visible:
                i.tick()
            elif self.player_char:
                self.discover_check(self.player_char.x, self.player_char.y, 1, i)
            if i.visible and self.in_sight(i):
                draw_list.append(i)

        mobs_active = False
        for i in self.render_mobs_list:
            if self.player_char and self.get_distance(i.x, i.y, self.player_char.x, self.player_char.y) <= i.rules[
                'live_distance']:
                i.tick()
                if self.player_char and not i.visible:
                    self.discover_check(self.player_char.x, self.player_char.y, 3, i)
                if i.visible:
                    draw_list.append(i)
                if i.stats.char_pools['ap_cur'] > 0 or i.moving:
                    mobs_active = True
        if self.mobs_turn and not mobs_active:
            self.next_turn()

        if self.player_char:
            self.player_char.tick()
            draw_list.append(self.player_char)

        for i in self.render_interior_covering_list:
            if i.visible and self.in_sight(i):
                i.tick()
                draw_list.append(i)

        """if self.labyrinth.spotlight is not None and not self.player_in_room:
            self.labyrinth.spotlight.tick()
            draw_list.append(self.labyrinth.spotlight)"""

        for i in self.render_effects_list:
            if i.visible:
                i.tick()
                draw_list.append(i)

        for i in self.render_text_list:
            if i.visible:
                i.tick()
                draw_list.append(i)

        self.ui.register_animations()

        for i in self.animtick_set:
            i.tick()

        return draw_list

    def _update_screen(self, draw_list):
        self.screen.fill(self.settings.bg_color)

        for i in draw_list:
            i.blitme()

        if self.ui.active:
            self.ui.show_ui()

        self.draw_cursor()

        pygame.display.update((0, 0, self.sight_width, self.sight_height))

        self.clock.tick(self.fps)

    def create_new_player(self, pc_class, pc_name, game_id):
        rules = self.tables.table_roll(pc_class, 'pc_table')
        if rules is False:
            rules = self.tables.table_roll('fighter', 'pc_table')
        self.player_char = PlayerChar(self, game_id, rules)
        self.ui.inventory_refresh(self.player_char.inventory.backpack)
        self.player_char.rules['name'] = pc_name
        self.players_turn = True
        self.player_char.stats.stats_recalc()
        self.ui.hud_refresh()
        self.ui.stats_refresh()

    def new_game_start(self, pc_class, pc_name):
        new_pc_id = self.get_counter_new('pc_id_vendor', './save/player_characters.data')
        self.create_new_player(pc_class, pc_name, new_pc_id)
        self.resources.savegame_format(new_pc_id)
        self.resources.save_pc(self.player_char)
        self.labyrinth.dungeon_create('test_chambers', self.player_char.stats.char_stats_modified['level'], 1, 'descended')

    def get_counter_new(self, counter_param, filename):
        last_count = self.resources.file_read_param(counter_param, filename)
        if not last_count:
            last_count = 0
        self.resources.file_write_param(counter_param, last_count + 1, filename)
        return last_count

    def load_game(self, game_id, hub_id, depth):
        if self.player_char is not None:
            del self.player_char
        rules = self.tables.table_roll('default', 'pc_table')
        self.player_char = PlayerChar(self, game_id, rules)

        self.resources.load_pc(self.player_char)
        self.player_char.get_media(self.player_char.rules['media'])

        self.players_turn = True
        self.player_char.stats.stats_recalc()
        self.player_char.stats.char_pools_maximize()

        self.ui.create_unique_uis(self.player_char.stats.char_stats['class'])

        self.ui.inventory_refresh(self.player_char.inventory.backpack)
        self.ui.hud_refresh()
        self.ui.stats_refresh()
        self.ui.spellbook_refresh()
        self.ui.effects_refresh()

        self.labyrinth.dungeon_create(hub_id, self.player_char.stats.char_stats_modified['level'], depth, 'descended')
        self.ui.active_ui_flags['ui_hud'] = True
        self.ui.active_ui_flags['ui_scene_info'] = True

    def save_game(self):
        self.resources.save_pc(self.player_char)
        self.resources.save_dungeon(self.player_char)

    def save_delete(self, slot_index):
        for i in range(slot_index, 14):
            game_id = self.resources.file_read_param('save-' + str(i + 1), self.resources.path + '/save/player_characters.data')
            if game_id is not False:
                self.resources.file_write_param('save-' + str(i), game_id, self.resources.path + '/save/player_characters.data')
            else:
                self.resources.file_write_param('save-' + str(i), '',
                                                self.resources.path + '/save/player_characters.data')
        self.ui.ui_variables['ui_gameload']['save_choice'] = -1
        self.ui.gameload_refresh()

    def reset_game(self):
        self.labyrinth.dungeon_clear()
        self.player_char = None

    def draw_cursor(self):
        if self.mouse_hand is not None:
            image = self.mouse_hand.animation.frames[
                self.mouse_hand.animation.frame_index]
            rect = image.get_rect()
            rect.topleft = self.mouse_x - self.mouse_hand.width // 2, self.mouse_y - self.mouse_hand.height // 2
            self.screen.blit(pygame.transform.scale(image, (
                self.mouse_hand.width, self.mouse_hand.height)), rect)

    def next_turn(self):
        self.players_turn, self.mobs_turn = self.mobs_turn, self.players_turn
        self.reserved_xy_list.clear()
        if self.players_turn:
            self.player_char.stats.char_pools['ap_cur'] = self.player_char.stats.char_stats_modified['ap_max']
            self.ui.uielements['ui_hud'].uielement['tr_tile_dict']['tr_ui_hud_clock']['animations']['default'].step = 0
            if self.player_char.stats.effects_tick() is not False:
                self.ui.effects_refresh()
        else:
            self.player_char.stats.char_pools['food_cur'] -= self.player_char.stats.char_pools['ap_cur']
            if self.player_char.stats.char_pools['food_cur'] <= 0:
                self.player_char.defeated(None)

            self.ui.uielements['ui_hud'].uielement['tr_tile_dict']['tr_ui_hud_clock']['animations'][
                'default'].step = 1
            print('restore enemy ap')
            for i in self.render_mobs_list:
                i.stats.char_pools['ap_cur'] = i.stats.char_stats_modified['ap_max']
                i.stats.effects_tick()
        self.player_char.checkme()
        self.ui.hud_refresh()
        self.ui.stats_refresh()

    def discover_check(self, x, y, radius, obj):
        if self.get_distance(obj.x, obj.y, x, y) <= radius:
            obj.visible = True
        else:
            obj.visible = False

    def area_visible(self, visible, top, left, bottom, right):
        for i in self.render_interior_list:
            if left <= i.x <= right and top <= i.y <= bottom:
                i.visible = visible
        for i in self.render_interior_covering_list:
            if left <= i.x <= right and top <= i.y <= bottom:
                i.visible = visible
        for i in self.render_items_list:
            if left <= i.x <= right and top <= i.y <= bottom:
                i.visible = visible
        for i in self.render_trap_list:
            if left <= i.x <= right and top <= i.y <= bottom:
                i.visible = visible
        for i in self.render_mobs_list:
            if left <= i.x <= right and top <= i.y <= bottom:
                i.visible = visible

    def reveal_traps_area(self, top, left, bottom, right):
        for trap in self.render_trap_list:
            if left <= trap.x <= right and top <= trap.y <= bottom and trap.rules['hidden'] > 0:
                trap.reveal(self.player_char)

    def move_object(self, obj, dest_x, dest_y):
        if obj is not self.player_char and [dest_x, dest_y] in self.reserved_xy_list:
            return False
        solid = self.collidelist(obj, dest_x, dest_y, self.solid_list, 0)
        if solid:
            return False
        door = self.collidelist(obj, dest_x, dest_y, self.labyrinth.door_list, 0)
        if door:
            if door.rules['closed'] == 1:
                if door.rules['lock'] == 0:
                    door.rules['closed'] = False
                    door.checkme()
                    door.sound_set['open'].play()
                    return False
                elif door.rules['lock'] > 0 and obj == self.player_char:
                    door.picklock(obj)
                    return False
                else:
                    return False

        if obj == self.player_char:
            trap = self.collidelist(obj, dest_x, dest_y, self.render_trap_list, 0)
            if trap:
                if trap.rules['hidden'] == 0:
                    if trap.disarm(obj) is True:
                        return False
                elif trap.reveal(obj) is True:
                    return False

        char = self.collidelist(obj, dest_x, dest_y, self.render_mobs_list, 0)
        if char:
            if obj == self.player_char:
                if self.player_char.inventory.equipped['main_hand'] is not None:
                    if 'ranged' in self.player_char.inventory.equipped['main_hand'].rules:
                        obj.ranged_attack_check(char.x + char.width // 2, char.y + char.height // 2)
                    else:
                        obj.attack(char)

            return False
        item = self.collidelist(obj, dest_x, dest_y, self.render_items_list[::-1], 0)
        if item:
            if 'space' in item.rules and item.unpackme():
                return False
            else:
                self.lootme(item, obj)
            # return False
        obj.dest_x = dest_x
        obj.dest_y = dest_y
        obj.moving = True
        obj.sound_set['walk'].play()
        self.reserved_xy_list.append([dest_x, dest_y])
        return True

    def collidelist(self, char, dest_x, dest_y, object_list, circle_coll):
        if circle_coll:
            for obj in object_list:
                try:
                    coll_x = obj.dest_x + self.square_width // 2
                    coll_y = obj.dest_y + self.square_height // 2
                except AttributeError:
                    coll_x = obj.x + self.square_width // 2
                    coll_y = obj.y + self.square_height // 2
                if math.sqrt(abs(coll_x - dest_x) ** 2 + abs(coll_y - dest_y) ** 2) <= circle_coll:
                    return obj
            return False
        else:
            for obj in object_list:
                try:
                    coll_x = obj.dest_x
                    coll_y = obj.dest_y
                except AttributeError:
                    coll_x = obj.x
                    coll_y = obj.y
                if dest_x < coll_x + obj.width and dest_x + char.width > coll_x and dest_y < coll_y + obj.height and dest_y + char.height > coll_y:
                    return obj
            return False

    def object_mouse_point(self):
        aim = self.mouse_on_object(self.mouse_x + self.view_x, self.mouse_y + self.view_y, [self.player_char])
        if aim is False:
            aim = self.mouse_on_object(self.mouse_x + self.view_x, self.mouse_y + self.view_y, self.render_mobs_list)
        if aim is False:
            aim = self.mouse_on_object(self.mouse_x + self.view_x, self.mouse_y + self.view_y, self.render_items_list)
        if aim is False:
            aim = self.mouse_on_object(self.mouse_x + self.view_x, self.mouse_y + self.view_y, self.labyrinth.door_list)
        if aim is False:
            aim = None
        return aim


    def mouse_on_object(self, mouse_x, mouse_y, object_list):
        for obj in object_list:
            if obj.visible:
                if obj.x <= mouse_x <= obj.x + obj.width and \
                        obj.y <= mouse_y <= obj.y + obj.height:
                    return obj
        return False

    def sign(self, x):
        sign = 0
        if x > 0:
            sign = 1
        elif x < 0:
            sign = -1
        return sign

    def get_distance(self, target_x, target_y, origin_x, origin_y):
        tile_distance = int(round(math.sqrt((abs(target_x - origin_x) // self.square_width) ** 2 + (
                abs(target_y - origin_y) // self.square_height) ** 2)))
        return tile_distance

    def get_direction(self, target_x, target_y, origin_x, origin_y):
        dir_x = self.sign(target_x - origin_x)
        dir_y = self.sign(target_y - origin_y)
        return dir_x, dir_y

    def test_arrow(self, from_x, from_y, to_x, to_y):
        dist_x = to_x - from_x
        dist_y = to_y - from_y
        if abs(dist_x) >= abs(dist_y):
            if dist_x != 0:
                step_y = round(abs(dist_y / dist_x) * self.sign(dist_y) * self.square_height)
            else:
                step_y = 0
            step_x = round(self.sign(dist_x) * self.square_width)
        else:
            step_y = round(self.sign(dist_y) * self.square_height)
            if dist_y != 0:
                step_x = round(abs(dist_x / dist_y) * self.sign(dist_x) * self.square_width)
            else:
                step_x = 0
        temp_x = from_x
        temp_y = from_y
        hit = False
        while (abs(temp_x - to_x) >= self.square_width or abs(temp_y - to_y) >= self.square_height) and not hit:
            print(temp_x, temp_y, to_x, to_y)
            obj = self.collidelist(None, temp_x, temp_y, self.solid_list, self.square_width // 2)
            door = self.collidelist(None, temp_x, temp_y, self.labyrinth.door_list, self.square_width // 2)
            if obj or (door and door.rules['closed'] == 1):
                hit = True
            # test ray calculation
            new_particle = Particle(self, self.resources.animations['damage_mark_blood'],
                                    None, 60, 0, 0, temp_x, temp_y)
            temp_x += step_x
            temp_y += step_y
        if hit:
            return False
        else:
            return True

    def load_rules(self, filename):
        rules_list = self.resources.read_file(filename)
        rule_dict = {}
        for r in rules_list:
            if '=' in r and r[0] != '#':
                var, val = r.split("=")
                # setting rules variables from file
                try:
                    rule_dict[var] = int(val)
                except ValueError:
                    rule_dict[var] = val
        return rule_dict

    def set_rules(self, char, rules):
        char.stats = Stats(self, char, rules)
        char.inventory = Inventory(char, rules['bp_max'], rules['bank_max'])
        if 'inventory' in rules:
            char.inventory.get_items_from_table(rules['inventory'])
            if char.inventory.equipped['main_hand'] is None and \
                    char.inventory.backpack[0].rules['item_class'] in ('wpn', 'mgc'):
                char.inventory.equipped['main_hand'] = char.inventory.backpack[0]
                del char.inventory.backpack[0]

    def get_affix(self, level, affix_class, affix_type):
        affix_table = self.resources.read_file(self.resources.tables['affix_table'])
        sorted_table = []
        for i in affix_table:
            row = i.split()
            if len(row) > 0 and row[0] != '#':
                affix = self.tables.read_row(row, affix_table)
                print('AFFIX FISHING', affix)
                if int(affix['min_level']) <= level and affix_class in affix['affix_class'] and affix[
                    'type'] == affix_type:
                    sorted_table.append(affix)
        print('AFFIX FISHING', level, sorted_table)
        if len(sorted_table) > 0:
            random_index = random.randrange(0, len(sorted_table))
            return sorted_table[random_index]
        else:
            return False

    def get_char_name(self, char_class):
        name_table = self.resources.read_file(self.resources.tables['name_table'])
        sorted_table = []
        for i in name_table:
            row = i.split()
            if len(row) > 0 and row[0] != '#':
                name = self.tables.read_row(row, name_table)
                print('NAME FISHING', name)
                if char_class in name['char_class']:
                    sorted_table.append(name)
        print('NAME FISHING', name, sorted_table)
        if len(sorted_table) > 0:
            random_index = random.randrange(0, len(sorted_table))
            return sorted_table[random_index]
        else:
            return False

    def inventory_check(self, char):
        dropped = 0
        if len(char.inventory.backpack) > char.inventory.bp_max:
            dropped += 1
            # item_index = random.randrange(0, len(char.inventory.backpack))
            item_index = len(char.inventory.backpack) - 1
            self.labyrinth.drop_loot([char.inventory.backpack[item_index]], char.dest_x, char.dest_y, True)
            del char.inventory.backpack[item_index]
            dropped += self.inventory_check(char)
        if char == self.player_char:
            self.ui.ragdoll_refresh(self.ui.container_crumps[-1])
        return dropped

    def inventory_find_item(self, inventory, item_class=None, item_id=None, object_id=None):
        if item_id is None and item_class is None and object_id is None:
            return False
        for inv_item in inventory[::-1]:
            if (inv_item.rules['id'] == item_id and inv_item.rules['item_class'] == item_class) or \
                    (item_id is None and inv_item.rules['item_class'] == item_class) or \
                    (inv_item.rules['id'] == item_id and item_class is None) or \
                    (object_id is not None and inv_item == object_id):
                return inv_item, inventory
            if 'container' in inv_item.rules:
                result = self.inventory_find_item(inv_item.rules['container'], item_class, item_id)
                if result is not False:
                    return result
        return False

    def lootme(self, loot_item, looter):
        loot_item.sound_set['pickup'].play()
        cap_text = loot_item.text_set['pickup']
        if 'amount_cur' in loot_item.rules:
            amount = int(loot_item.rules['amount_cur'])
            cap_text = cap_text.replace('%1', str(amount))
            if amount > 1:
                cap_text = cap_text.replace('%2', 's')
            else:
                cap_text = cap_text.replace('%2', '')
        else:
            cap_text = cap_text.replace('%1', loot_item.compose_full_title())
        cap_x, cap_y = loot_item.x + loot_item.width // 2, loot_item.y
        cap_color = (255, 255, 255)

        self.set_anim(loot_item, 'tile', False)

        if looter is not self.player_char or self.player_char.autoequip(loot_item) is False:
            left_item = self.container_item_not_fit(loot_item, looter.inventory.backpack, looter.inventory.bp_max)
            if left_item:
                looter.inventory.backpack.append(left_item)
        else:
            self.ui.ragdoll_refresh(self.ui.container_crumps[-1])

        self.render_items_list.remove(loot_item)

        if self.inventory_check(looter) > 0:
            cap_text = 'Inventory full!'
            cap_color = (255, 255, 0)

        new_caption = Text(self, cap_text, cap_x, cap_y, 'default',
                           20, cap_color, 'center', 'top', 1, 0, 0)

    def container_item_not_fit(self, loot_item, container, space):
        if 'amount_cur' in loot_item.rules:
            for item in container:
                if self.items_may_stack(loot_item, item):
                    add_amount = min(item.rules['amount_max'] - item.rules['amount_cur'], loot_item.rules['amount_cur'])
                    item.rules['amount_cur'] += add_amount
                    loot_item.rules['amount_cur'] -= add_amount
                    if loot_item.rules['amount_cur'] == 0:
                        return False
        if len(container) >= space:
            for itm in container:
                if 'space' in itm.rules:
                    if 'container' not in itm.rules:
                        itm.rules['container'] = []
                    return self.container_item_not_fit(loot_item, itm.rules['container'], itm.rules['space'])
            return loot_item
        container.append(loot_item)
        return False

    def set_defence_types(self):
        self.def_indexes = {
            'dam_cut': 'def_cut',
            'dam_pierce': 'def_pierce',
            'dam_bash': 'def_bash',
            'dam_poison': 'def_poison',
            'dam_fire': 'def_fire',
            'dam_ice': 'def_ice',
            'dam_lightning': 'def_lightning',
            'dam_arcane': 'def_arcane',
        }

    def woundme(self, attacker, char, damage, attack_type, damage_type, inflict_status):
        actual_damage = damage
        defence_type = self.def_indexes[damage_type]
        modifiers_dict = char.stats.get_modifiers_dict(char.inventory)

        if defence_type in modifiers_dict:
            if 'force' in modifiers_dict[defence_type]:
                val_number = len(modifiers_dict[defence_type]['force'])
                forced_value = round(sum(modifiers_dict[defence_type]['force']) / val_number)
                actual_damage -= forced_value
            else:
                if 'points' in modifiers_dict[defence_type]:
                    actual_damage -= sum(modifiers_dict[defence_type]['points'])
                if 'percent' in modifiers_dict[defence_type]:
                    actual_damage -= round(actual_damage * sum(modifiers_dict[defence_type]['percent']) / 100)

        actual_damage = max(actual_damage, 0)
        char.stats.char_pools['hp_cur'] -= actual_damage

        if char.stats.char_pools['hp_cur'] <= 0:
            char.defeated(attacker)
        else:
            if char == self.player_char:
                char.equipment_break(10, ['arm', 'hlm', 'shl', 'acc'])
                self.ui.hud_refresh()
                self.ui.stats_refresh()

            if inflict_status is not None:
                char.stats.char_effects.update(inflict_status)
                char.stats.stats_recalc()
                if char is self.player_char:
                    self.ui.effects_refresh()

        self.show_damage(char, actual_damage, damage_type)

    def show_damage(self, char, actual_damage, damage_type):
        rand_x = char.x + random.randrange(0, char.width + 1)
        rand_y = char.y + random.randrange(0, round(char.height * 0.6))
        cap_text = '' + str(actual_damage)
        if damage_type in ['dam_cut', 'dam_pierce', 'dam_bash']:
            particle_anim = self.resources.animations['damage_mark_blood']
            new_particle = Particle(self, particle_anim, None, 15, 0, 4, rand_x, rand_y)
            new_caption = Text(self, cap_text, rand_x, rand_y, 'default', 22, (255, 0, 0), 'center', 'middle', 0.75, 0,
                               -0.2)
        elif damage_type == 'dam_poison':
            particle_anim = self.resources.animations['damage_mark_poison']
            new_particle = Particle(self, particle_anim, None, 15, 0, 1, rand_x, rand_y)
            new_caption = Text(self, cap_text, rand_x, rand_y, 'default', 22, (0, 255, 0), 'center', 'middle', 0.75, 0,
                               -0.2)
        elif damage_type == 'dam_fire':
            particle_anim = self.resources.animations['damage_mark_fire']
            new_particle = Particle(self, particle_anim, None, 15, 0, -1, rand_x, rand_y)
            new_caption = Text(self, cap_text, rand_x, rand_y, 'default', 22, (255, 255, 0), 'center', 'middle', 0.75, 0,
                               -0.2)
        elif damage_type == 'dam_ice':
            particle_anim = self.resources.animations['damage_mark_ice']
            new_particle = Particle(self, particle_anim, None, 15, 0, -1, rand_x, rand_y)
            new_caption = Text(self, cap_text, rand_x, rand_y, 'default', 22, (0, 0, 255), 'center', 'middle', 0.75, 0,
                               -0.2)
        elif damage_type == 'dam_lightning':
            particle_anim = self.resources.animations['damage_mark_lightning']
            new_particle = Particle(self, particle_anim, None, 15, 0, 0, rand_x, rand_y)
            new_caption = Text(self, cap_text, rand_x, rand_y, 'default', 22, (0, 255, 255), 'center', 'middle', 0.75, 0,
                               -0.2)
        elif damage_type == 'dam_arcane':
            particle_anim = self.resources.animations['damage_mark_arcane']
            new_particle = Particle(self, particle_anim, None, 15, 0, 0, rand_x, rand_y)
            new_caption = Text(self, cap_text, rand_x, rand_y, 'default', 22, (255, 0, 255), 'center', 'middle', 0.75, 0,
                               -0.2)

    def show_hit(self, char, target_x, target_y, attack_type, dam_type):
        if attack_type == 'melee':
            x = char.x + self.sign(target_x - char.x) * self.square_width
            y = char.y + self.sign(target_y - char.y) * self.square_height
        elif attack_type == 'ranged':
            x = target_x
            y = target_y
        if dam_type == 'dam_cut':
            particle_anim = self.resources.animations['hit_mark_slice']
            particle_anim.frame_index = 0
            part_x = x + (random.randrange(-3, 4) / 10 * self.square_width)
            part_y = y + (random.randrange(-3, 4) / 10 * self.square_height)
            new_particle = Particle(self, particle_anim, 'hit_slice', 12, 0, 0, part_x, part_y)
        elif dam_type == 'dam_pierce':
            particle_anim = self.resources.animations['hit_mark_pierce']
            particle_anim.frame_index = 0
            part_x = x + (random.randrange(-3, 4) / 10 * self.square_width)
            part_y = y + (random.randrange(-3, 4) / 10 * self.square_height)
            new_particle = Particle(self, particle_anim, 'tiny_metal_break', 12, 0, 0, part_x, part_y)
        elif dam_type == 'dam_bash':
            particle_anim = self.resources.animations['hit_mark_bash']
            particle_anim.frame_index = 0
            part_x = x + (random.randrange(-3, 4) / 10 * self.square_width)
            part_y = y + (random.randrange(-3, 4) / 10 * self.square_height)
            new_particle = Particle(self, particle_anim, 'tun', 12, 0, 0, part_x, part_y)

    def set_anim(self, char, anim_name, forced):
        if char.animation is not char.anim_set[anim_name] and (not char.anim_forced or forced):
            char.temp_anim = False
            char.anim_forced = forced
            char.anim_prev = char.animation
            char.animation = char.anim_set[anim_name]
            char.animation.frame_index = 0

            self.set_offset_scale(char)

    def set_temp_anim(self, char, anim_name, timer, forced):
        if char.animation is not char.anim_set[anim_name] and (not char.anim_forced or forced):
            char.temp_anim = True
            char.anim_forced = forced
            char.temp_anim_timer = timer
            char.anim_prev = char.animation
            char.animation = char.anim_set[anim_name]
            char.animation.frame_index = 0

            self.set_offset_scale(char)

    def anim_check(self, char):
        if char.temp_anim:
            if char.temp_anim_timer == 0:
                if char.anim_prev is not None:
                    char.animation = char.anim_prev
                else:
                    char.animation = char.default_anim
                char.temp_anim = False
                char.anim_forced = False

                self.set_offset_scale(char)
            else:
                char.temp_anim_timer -= 1

    def set_offset_scale(self, char):
        char.width = round(self.square_width * char.animation.squares_w)
        char.height = round(self.square_height * char.animation.squares_h)

        char.actual_offset_x = round(char.animation.offset_x * (char.height / char.animation.height))
        char.actual_offset_y = round(char.animation.offset_y * (char.width / char.animation.width))

    def generate_drop(self, set_index, level):
        table_list = self.resources.read_file(self.resources.tables['treasure_table'])
        set_dict = self.tables.find_row(set_index, table_list)
        drop_list = []
        for t_roll, amount in set_dict.items():
            for i in range(0, amount):
                treasure = self.tables.find_row(t_roll, table_list)
                if treasure is not False and 'level' not in treasure or treasure['level'] <= level:
                    new_item = self.labyrinth.spawn_item(treasure, level, 0, 0)
                    self.item_add_affix(new_item, level)
                    new_item.checkme()
                    drop_list.append(new_item)
                else:
                    support_roll = self.tables.find_row('roll_gold', table_list)
                    if support_roll is not False:
                        new_item = self.labyrinth.spawn_item(support_roll, level, 0, 0)
                        new_item.checkme()
                        drop_list.append(new_item)
        return drop_list

    def item_add_affix(self, item, level):
        rare_chances = []
        rare_types = []
        for rare_type, params in item.rare_dict.items():
            if level >= params['level']:
                rare_chances.append(params['chance'])
                rare_types.append(rare_type)
        rare_pick = self.pick_random(rare_chances, rare_types, offset=self.player_char.stats.char_stats_modified['find_magic'])
        affix_number = item.rare_dict[rare_pick]['affix_number']
        if affix_number > 1:
            for i in range(0, affix_number - 1):
                item.set_affix(self.get_affix(level, item.rules['item_class'], 'prefix'))
        if affix_number > 0:
            affix_type = random.choice(['prefix', 'suffix'])
            item.set_affix(self.get_affix(level, item.rules['item_class'], affix_type))

    def pick_random(self, prob_list, picks_list, offset=0):
        rnd_list = [0]
        for prob in prob_list:
            new_prob = int(prob) + rnd_list[-1]
            rnd_list.append(new_prob)
        roll = random.randrange(1, rnd_list[-1] + 1) + offset
        print('Roll table:')
        print(rnd_list)
        print(roll)
        for i in range(1, len(rnd_list)):
            if rnd_list[i - 1] < roll <= rnd_list[i]:
                pick = picks_list[i - 1]
                print(pick, '\nFinished roll')
                return pick

    def get_number_suffix(self, number):
        if str(number)[-1] == '1':
            return 'st'
        if str(number)[-1] == '2':
            return 'nd'
        if str(number)[-1] == '3':
            return 'rd'
        return 'th'

    def in_sight(self, instance):
        if instance.x + instance.width > self.view_x and \
                instance.x < self.view_x + self.sight_width and \
                instance.y + instance.height > self.view_y and \
                instance.y < self.view_y + self.sight_height:
            return True
        return False

    def curse_item_check(self, container):
        for itm in container:
            if 'curse' in itm.rules:
                return True
            if 'container' in itm.rules:
                self.curse_item_check(itm.container)
        return False

    def pick_cursed_items(self, container):
        pick_list = []
        for itm in container:
            if 'curse' in itm.rules:
                pick_list.append(itm)
            if 'container' in itm.rules:
                pick_list.extend(self.pick_cursed_items(itm.rules['container']))
        for itm in pick_list:
            try:
                container.remove(itm)
            except ValueError:
                pass
        return pick_list

    def exponential(self, ratio, value, multiplier):
        return round(ratio ** value * multiplier)

    def items_may_stack(self, items_to_add, items_add_to):
        # self.gameboard.mouse_hand.rules['id'] == inv_slot.rules[
        #    'id'] and 'amount_cur' in self.gameboard.mouse_hand.rules
        toadd_lvl = 'level' in items_to_add.rules
        addto_lvl = 'level' in items_add_to.rules
        if toadd_lvl + addto_lvl == 1 or (toadd_lvl + addto_lvl == 2 and
                                          items_to_add.rules['level'] != items_add_to.rules['level']):
            return False
        if items_to_add.rules['id'] != items_add_to.rules['id']:
            return False
        if 'amount_cur' not in items_add_to.rules or 'amount_cur' not in items_to_add.rules:
            return False
        if items_add_to.rules['amount_cur'] >= items_add_to.rules['amount_max']:
            return False
        if items_to_add.rules['item_class'] == 'amm' and items_add_to.rules['item_class'] == 'amm':
            for i in range(1, 7):
                value = 'value' + str(i)
                parameter = 'parameter' + str(i)
                digits = 'digits' + str(i)
                if parameter in items_to_add.rules:
                    if parameter in items_add_to.rules:
                        if items_to_add.rules[parameter] != items_add_to.rules[parameter] or \
                                items_to_add.rules[value] != items_add_to.rules[value] or \
                                items_to_add.rules[digits] != items_add_to.rules[digits]:
                            return False
                    else:
                        return False
        return True

if __name__ == '__main__':
    game_board = GameBoard()
    game_board.run_game()
