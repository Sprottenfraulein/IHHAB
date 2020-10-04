from class_SpriteSheet import SpriteSheet
from class_Animation import Animation
from class_Item import Item
from class_Interior import Interior
from class_Door import Door
from class_Stairs import Stairs
from class_Trap import Trap
from class_Mob import Mob
import os
from datetime import datetime



class Resources:
    path = os.getcwd()
    animations = {}
    animation_files = {}
    tilesets = {}
    labtiles = {}
    tables = {}
    text_bank = {}
    uielements = {}

    def __init__(self):
        print("The current working directory is %s" % self.path)

        self.load_tilesets('./res/data/images/tilesets/tilesets.data')
        self.load_animations('./res/data/anims/animations.data')
        self.load_tables('./res/data/rulebook/tables/tables.data')
        self.load_texts('./res/data/text/text.data')
        self.load_uielements('./res/data/ui/uielements.data')

    def load_tilesets(self, filename):
        # loading list of entries in the following format:
        # <TilesetName> = <Path\Filename>
        # creating spritesheet objects for entries and saving them to dictionary self.tilesets
        tileset_list = self.read_file(filename)
        for t in tileset_list:
            if '=' in t and t[0] != '#':
                tileset_name, tileset_file = t.split("=")
                self.tilesets[tileset_name] = SpriteSheet(tileset_file)

    def load_animations(self, filename):
        # loading list of entries in the following format:
        # <AnimationName> = <Path\Filename>
        # creating animation objects for entries and saving them to dictionary self.animations
        animation_list = self.read_file(filename)
        for t in animation_list:
            if '=' in t and t[0] != '#':
                animation_name, animation_file = t.split("=")
                self.animations[animation_name] = Animation(self, animation_name, animation_file)
                self.animation_files[animation_name] = animation_file

    def load_tables(self, filename):
        # loading list of entries in the following format:
        # <TilesetName> = <Path\Filename>
        # creating spritesheet objects for entries and saving them to dictionary self.tilesets
        table_list = self.read_file(filename)
        for t in table_list:
            if '=' in t and t[0] != '#':
                table_name, table_file = t.split("=")
                self.tables[table_name] = table_file

    def load_uielements(self, filename):
        # loading list of entries in the following format:
        # <TilesetName> = <Path\Filename>
        # creating spritesheet objects for entries and saving them to dictionary self.tilesets
        element_list = self.read_file(filename)
        for e in element_list:
            if '=' in e and e[0] != '#':
                element_name, element_file = e.split("=")
                self.uielements[element_name] = element_file

    def load_texts(self, filename):
        # loading list of entries in the following format:
        # <TilesetName> = <Path\Filename>
        # creating spritesheet objects for entries and saving them to dictionary self.tilesets
        text_list = self.read_file(filename)
        for t in text_list:
            if '=' in t and t[0] != '#':
                text_name, text_body = t.split("=")
                self.text_bank[text_name] = text_body

    def read_file(self, filename):
        try:
            with open(filename) as myfile:
                return myfile.read().splitlines()
        except FileNotFoundError:
            return False

    def write_file(self, text_list, filename):
        f = open(filename, "w")
        for line in text_list:
            f.write(line)
            f.write('\n')
        f.close()
        return True

    def file_read_param(self, parameter, filename):
        param_list = self.read_file(filename)
        for param in param_list:
            if '=' in param and param[0] != '#':
                param_name, param_value = param.split('=')
                if param_name == parameter and len(param_value) > 0:
                    try:
                        value = int(param_value)
                    except ValueError:
                        value = param_value
                    return value
        return False

    def file_write_param(self, parameter, value, filename):
        param_file = open(filename, "r")
        param_list = param_file.readlines()
        param_file.close()
        edited = False
        for i in range(0, len(param_list)):
            if '=' in param_list[i] and param_list[i][0] != '#':
                param_name, param_value = param_list[i].split('=')
                if param_name == parameter:
                    param_list[i] = param_name + '=' + str(value) + '\n'
                    edited = True
        if not edited:
            param_list.append(parameter + '=' + str(value) + '\n')
        param_file = open(filename, "w")
        content = ''.join(param_list)
        param_file.write(content)
        param_file.close()
        return True

    def load_save(self, saveslot_index):
        game_id = self.file_read_param(saveslot_index, self.path + '/save/player_characters.data')
        hub_id = self.file_read_param('pc_location', self.path + '/save/' + str(game_id) + '/world/world_index.sav')
        progress_depth = self.file_read_param(hub_id + '_depth',
                                             self.path + '/save/' + str(game_id) + '/world/world_index.sav')
        return game_id, hub_id, progress_depth

    def savegame_format(self, game_id):
        saveslot = self.saveslot_get(self.path + '/save/player_characters.data')
        if saveslot is not False:
            self.file_write_param(saveslot, str(game_id), self.path + '/save/player_characters.data')

            try:
                os.rmdir(self.path + '/save/' + str(game_id))
            except OSError:
                print("Deletion of the directory %s failed" % self.path)
            else:
                print("Successfully deleted the directory %s" % self.path)

            try:
                os.mkdir(self.path + '/save/' + str(game_id))
            except OSError:
                print("Creation of the directory %s failed" % self.path)
            else:
                print("Successfully created the directory %s" % self.path)

            try:
                os.mkdir(self.path + '/save/' + str(game_id) + '/char')
            except OSError:
                print("Creation of the directory %s failed" % self.path)
            else:
                print("Successfully created the directory %s" % self.path)

            try:
                os.mkdir(self.path + '/save/' + str(game_id) + '/world')
            except OSError:
                print("Creation of the directory %s failed" % self.path)
            else:
                print("Successfully created the directory %s" % self.path)

            self.write_file([''], self.path + '/save/' + str(game_id) + '/world/world_index.sav')

            return True
        else:
            return False

    def saveslot_get(self, filename):
        for i in range(0, 14):
            slotname = 'save-' + str(i)
            slot = self.file_read_param(slotname, filename)
            if slot is False:
                return slotname
        return False

    def get_save_info(self, game_id):
        # reading player info
        pc_summary = self.read_file(self.path + '/save/' + str(game_id) + '/char/summary.sav')
        if pc_summary is False:
            return False

        time_str = pc_summary[0]

        pc_stat_list = pc_summary[1].split(',')

        char_stats = {}
        char_stats['name'], \
        char_stats['class'], \
        char_stats['level'], \
        char_stats['strength'], \
        char_stats['dexterity'], \
        char_stats['intelligence'], \
        char_stats['mp_max'], \
        char_stats['hp_max'], \
        char_stats['ap_max'], \
        char_stats['food_max'], \
        char_stats['provoke_mobs'], \
        char_stats['reflect_damage'], \
        char_stats['find_traps'], \
        char_stats['disarm_traps'], \
        char_stats['pick_locks'], \
        char_stats['find_gold'], \
        char_stats['find_food'], \
        char_stats['find_ammo'], \
        char_stats['find_ore'], \
        char_stats['crafting'], \
        char_stats['find_magic'], \
        char_stats['exp_bonus'], \
        char_stats['pc_experience'], \
        char_stats['stat_points'], \
        char_stats['pc_bp_max'], \
        char_stats['pc_backpack_cur'], \
        char_stats['pc_bank_max'], \
        char_stats['pc_bank_cur'], \
        char_stats['pc_spellbook_cur'] \
            = pc_stat_list

        # reading world info
        known_hubs = {}
        total_hubs = self.file_read_param('hub_count', self.path + '/save/' + str(game_id) + '/world/world_index.sav')
        for i in range(0, total_hubs):
            hub_name = self.file_read_param('hub' + str(i),
                                            self.path + '/save/' + str(game_id) + '/world/world_index.sav')
            hub_depth = self.file_read_param(hub_name + '_depth',
                                             self.path + '/save/' + str(game_id) + '/world/world_index.sav')

            known_hubs[hub_name] = hub_depth

        return time_str, char_stats, known_hubs

    def worldindex_update(self, gameboard, game_id, dungeon_id, depth):
        self.file_write_param(dungeon_id + str(depth), '1',
                              self.path + '/save/' + str(game_id) + '/world/world_index.sav')
        hub_max_depth = self.file_read_param(dungeon_id + '_depth',
                                             self.path + '/save/' + str(game_id) + '/world/world_index.sav')
        if hub_max_depth is False or hub_max_depth < depth:
            self.file_write_param(dungeon_id + '_depth', str(depth),
                                  self.path + '/save/' + str(game_id) + '/world/world_index.sav')

        total_hubs = self.file_read_param('hub_count', self.path + '/save/' + str(game_id) + '/world/world_index.sav')
        hub_exists = False
        for i in range(0, total_hubs):
            hub_name = self.file_read_param('hub' + str(i),
                                            self.path + '/save/' + str(game_id) + '/world/world_index.sav')
            if hub_name == dungeon_id:
                hub_exists = True
        if not hub_exists:
            new_index = gameboard.get_counter_new('hub_count',
                                                  self.path + '/save/' + str(game_id) + '/world/world_index.sav')
            self.file_write_param('hub' + str(new_index), dungeon_id,
                                  self.path + '/save/' + str(game_id) + '/world/world_index.sav')

    def save_pc(self, pc_obj):
        save_timestamp = [self.timestamp_get()]

        pc_stats_str = ','.join([
            pc_obj.rules['name'],
            pc_obj.stats.char_stats['class'],
            str(pc_obj.stats.char_stats['level']),
            str(pc_obj.stats.char_stats['strength']),
            str(pc_obj.stats.char_stats['dexterity']),
            str(pc_obj.stats.char_stats['intelligence']),
            str(pc_obj.stats.char_stats['mp_max']),
            str(pc_obj.stats.char_stats['hp_max']),
            str(pc_obj.stats.char_stats['ap_max']),
            str(pc_obj.stats.char_stats['food_max']),
            str(pc_obj.stats.char_stats['provoke_mobs']),
            str(pc_obj.stats.char_stats['reflect_damage']),
            str(pc_obj.stats.char_stats['find_traps']),
            str(pc_obj.stats.char_stats['disarm_traps']),
            str(pc_obj.stats.char_stats['pick_locks']),
            str(pc_obj.stats.char_stats['find_gold']),
            str(pc_obj.stats.char_stats['find_food']),
            str(pc_obj.stats.char_stats['find_ammo']),
            str(pc_obj.stats.char_stats['find_ore']),
            str(pc_obj.stats.char_stats['crafting']),
            str(pc_obj.stats.char_stats['find_magic']),
            str(pc_obj.stats.char_stats['exp_bonus']),
            str(pc_obj.stats.char_pools['experience']),
            str(pc_obj.stats.stat_points),
            str(pc_obj.inventory.bp_max),
            str(len(pc_obj.inventory.backpack)),
            str(pc_obj.inventory.bank_max),
            str(len(pc_obj.inventory.bank)),
            str(len(pc_obj.gameboard.magic.player_spellbook)),
        ])
        # equipped spell
        if pc_obj.gameboard.magic.player_spell is not None and pc_obj.gameboard.magic.magic_item is None:
            player_spell = self.dict_to_str(pc_obj.gameboard.magic.player_spell, ':', ';')
        else:
            player_spell = ['-']
        # equipped items
        equip_list = []
        for eq_item in pc_obj.inventory.equipped.values():
            if eq_item is not None:
                equip_list.extend(self.dict_to_str(eq_item.rules, ':', ';'))
            else:
                equip_list.append('-')
        # backpack items
        inv_list = []
        if len(pc_obj.inventory.backpack) > 0:
            for itm in pc_obj.inventory.backpack:
                inv_list.extend(self.dict_to_str(itm.rules, ':', ';'))
        # bank items
        bank_list = []
        if len(pc_obj.inventory.bank) > 0:
            for itm in pc_obj.inventory.bank:
                bank_list.extend(self.dict_to_str(itm.rules, ':', ';'))
        # spells
        spell_list = []
        if len(pc_obj.gameboard.magic.player_spellbook) > 0:
            for spell in pc_obj.gameboard.magic.player_spellbook:
                spell_list.extend(self.dict_to_str(spell, ':', ';'))
        save_list = save_timestamp + [pc_stats_str] + player_spell + equip_list + inv_list + bank_list + spell_list

        return self.write_file(save_list, self.path + '/save/' + str(pc_obj.game_id) + '/char/summary.sav')

    def dict_to_str(self, dct, sep_keyvalue, sep_pairs):
        total_list = []
        dict_list = []
        sub_dict_list = []
        for key, value in dct.items():
            if type(value) is dict:
                dict_list.append(sep_keyvalue.join([key, str(len(value))]))
                sub_dict_list.append(value)
            elif type(value) is list:
                for i in range(0, len(value)):
                    sub_dict_list.append(self.sub_convert(key, value[i]))
                dict_list.append(sep_keyvalue.join([key, str(len(value))]))
            else:
                dict_list.append(sep_keyvalue.join([key, str(value)]))
        dict_str = sep_pairs.join(dict_list)
        if len(dict_list) > 0:
            total_list.append(dict_str)
        for dct in sub_dict_list:
            total_list.extend(self.dict_to_str(dct, sep_keyvalue, sep_pairs))
        return total_list

    def sub_convert(self, key, list_value):
        if key == 'affixes':
            return list_value
        elif key == 'container':
            return list_value.rules

    def load_pc(self, pc_obj):
        pc_summary = self.read_file(self.path + '/save/' + str(pc_obj.game_id) + '/char/summary.sav')
        if pc_summary is False:
            return False

        line_cur = 0
        time_str = pc_summary[line_cur]

        line_cur += 1
        pc_stat_list = pc_summary[line_cur].split(',')

        char_stats = {}
        pc_obj.rules['name'], \
        pc_obj.stats.char_stats['class'], \
        char_stats['level'], \
        char_stats['strength'], \
        char_stats['dexterity'], \
        char_stats['intelligence'], \
        char_stats['mp_max'], \
        char_stats['hp_max'], \
        char_stats['ap_max'], \
        char_stats['food_max'], \
        char_stats['provoke_mobs'], \
        char_stats['reflect_damage'], \
        char_stats['find_traps'], \
        char_stats['disarm_traps'], \
        char_stats['pick_locks'], \
        char_stats['find_gold'], \
        char_stats['find_food'], \
        char_stats['find_ammo'], \
        char_stats['find_ore'], \
        char_stats['crafting'], \
        char_stats['find_magic'], \
        char_stats['exp_bonus'], \
        pc_experience, \
        pc_stat_points, \
        pc_bp_max, pc_backpack_cur, pc_bank_max, pc_bank_cur, pc_spellbook_cur \
            = pc_stat_list

        for key, value in char_stats.items():
            try:
                pc_obj.stats.char_stats[key] = int(value)
            except ValueError:
                pc_obj.stats.char_stats[key] = 1

        pc_obj.stats.char_effects.clear()

        try:
            pc_obj.stats.stat_points = int(pc_stat_points)
            pc_obj.stats.char_pools['experience'] = int(pc_experience)
            pc_obj.inventory.bp_max = int(pc_bp_max)
            pc_backpack_cur = int(pc_backpack_cur)
            pc_obj.inventory.bank_max = int(pc_bank_max)
            pc_bank_cur = int(pc_bank_cur)
            pc_spellbook_cur = int(pc_spellbook_cur)
        except ValueError:
            return False

        line_cur += 1

        if pc_summary[line_cur] == '-':
            pc_obj.gameboard.magic.player_spell = None
            line_cur += 1
        else:
            pc_obj.gameboard.magic.player_spell, line_cur = self.str_unpack(pc_obj, pc_summary, line_cur, ':', ';')

        # equipped items
        for part in pc_obj.inventory.equipped.keys():
            if pc_summary[line_cur] == '-':
                pc_obj.inventory.equipped[part] = None
                line_cur += 1
            else:
                pc_obj.inventory.equipped[part], line_cur = self.item_load(pc_obj, pc_summary, line_cur)
        # backpack items
        pc_obj.inventory.backpack.clear()
        for i in range(0, pc_backpack_cur):
            bp_item, line_cur = self.item_load(pc_obj, pc_summary, line_cur)
            pc_obj.inventory.backpack.append(bp_item)
        # bank items
        pc_obj.inventory.bank.clear()
        for i in range(0, pc_bank_cur):
            bank_item, line_cur = self.item_load(pc_obj, pc_summary, line_cur)
            pc_obj.inventory.bank.append(bank_item)
        # spells
        pc_obj.gameboard.magic.player_spellbook.clear()
        for i in range(0, pc_spellbook_cur):
            spell, line_cur = self.str_unpack(pc_obj, pc_summary, line_cur, ':', ';')
            pc_obj.gameboard.magic.player_spellbook.append(spell)
        return True

    def item_load(self, pc_obj, pc_summary, line_cur, cur_mov=1):
        itm_rules, line_cur = self.str_unpack(pc_obj, pc_summary, line_cur, ':', ';', cur_mov)
        new_item = Item(pc_obj.gameboard, itm_rules, itm_rules['level'], 0, 0, upgrade=False)
        return new_item, line_cur

    def str_unpack(self, pc_obj, pc_summary, line_cur, sep_keyvalue, sep_pairs, cur_mov=1):
        pack_dict = {}
        print('UNPACKING STRING :', pc_summary[line_cur].split()[-1])
        pack_pairs = pc_summary[line_cur].split()[-1].split(sep_pairs)
        for pair in pack_pairs:
            key, value = pair.split(sep_keyvalue)
            try:
                value = int(value)
            except ValueError:
                value = str(value)

            if key == 'container':
                temp_list = []
                if type(value) is int and value > 0:
                    for i in range(0, value):
                        item, line_cur = self.item_load(pc_obj, pc_summary, line_cur + 1, cur_mov=0)
                        temp_list.append(item)
                pack_dict[key] = temp_list
            elif key == 'affixes':
                if type(value) is int and value > 0:
                    temp_list = []
                    for i in range(0, value):
                        aff_dict, line_cur = self.str_unpack(pc_obj, pc_summary, line_cur + 1, ':', ';', cur_mov=0)
                        temp_list.append(aff_dict)
                    pack_dict[key] = temp_list
                else:
                    continue
            elif key in ['spell_media', 'anim_set', 'sound_set', 'text_set']:
                if type(value) is int and value > 0:
                    aff_dict, line_cur = self.str_unpack(pc_obj, pc_summary, line_cur + 1, ':', ';', cur_mov=0)
                    pack_dict[key] = aff_dict
                else:
                    continue
            else:
                pack_dict[key] = value
        line_cur += cur_mov
        return pack_dict, line_cur

    def save_dungeon(self, pc_obj):
        hub_name = pc_obj.gameboard.labyrinth.dungeon_id
        depth = pc_obj.gameboard.labyrinth.depth
        path_savefile = self.path + '/save/' + str(pc_obj.game_id) + '/world/' + hub_name + '/floor' + str(
            depth) + '.sav'

        filtered_interior_list = pc_obj.gameboard.render_interior_list.copy()
        for stairs in pc_obj.gameboard.labyrinth.stairs_list:
            filtered_interior_list.remove(stairs)
        for door in pc_obj.gameboard.labyrinth.door_list:
            filtered_interior_list.remove(door)

        # bg interiors
        bg_interior_list = []
        for interior in filtered_interior_list:
            bg_interior_list.append(pc_obj.gameboard.labyrinth.interior_to_str(interior))

        # fg interiors
        fg_interior_list = []
        for interior in pc_obj.gameboard.render_interior_covering_list:
            fg_interior_list.append(pc_obj.gameboard.labyrinth.interior_to_str(interior))

        # rooms
        room_list = []
        discovered_room_list = []
        for room in pc_obj.gameboard.labyrinth.room_list:
            if room in pc_obj.gameboard.labyrinth.discovered_rooms:
                discovered_room_list.append('%s,%s,%s,%s' % tuple(room))
            else:
                room_list.append('%s,%s,%s,%s' % tuple(room))

        # doors
        door_list = []
        door_count = len(pc_obj.gameboard.labyrinth.door_list)
        for door in pc_obj.gameboard.labyrinth.door_list:
            door_list.extend(pc_obj.gameboard.labyrinth.labobj_to_str(door))

        # stairs
        stairs_list = []
        stairs_count = len(pc_obj.gameboard.labyrinth.stairs_list)
        for stairs in pc_obj.gameboard.labyrinth.stairs_list:
            stairs_list.extend(pc_obj.gameboard.labyrinth.labobj_to_str(stairs))

        # traps
        trap_list = []
        trap_count = len(pc_obj.gameboard.render_trap_list)
        for trap in pc_obj.gameboard.render_trap_list:
            trap_list.extend(pc_obj.gameboard.labyrinth.labobj_to_str(trap))

        # items
        item_list = []
        item_count = len(pc_obj.gameboard.render_items_list)
        for itm in pc_obj.gameboard.render_items_list:
            item_list.extend(pc_obj.gameboard.labyrinth.labobj_to_str(itm))
        print('LIST', item_list)

        # mob randomizer
        mob_pool_list = []
        mob_pool_count = len(pc_obj.gameboard.labyrinth.mob_list)
        for mob in pc_obj.gameboard.labyrinth.mob_list:
            mob_pool_list.extend(self.dict_to_str(mob, ':', ';'))

        # mobs generated
        mob_list = []
        mob_count = len(pc_obj.gameboard.render_mobs_list)
        for mob in pc_obj.gameboard.render_mobs_list:
            mob_list.extend(pc_obj.gameboard.labyrinth.labobj_to_str(mob))

        save_list = [str(len(bg_interior_list))] + bg_interior_list + [
            str(len(fg_interior_list))] + fg_interior_list + [
                        str(len(room_list))] + room_list + [str(len(discovered_room_list))] + discovered_room_list + [
                        str(door_count)] + door_list + [str(stairs_count)] + stairs_list + [
                        str(trap_count)] + trap_list + [str(item_count)] + item_list + [
                        str(mob_pool_count)] + mob_pool_list + [str(mob_count)] + mob_list
        if not os.path.exists(self.path + '/save/' + str(pc_obj.game_id) + '/world/' + hub_name):
            os.makedirs(self.path + '/save/' + str(pc_obj.game_id) + '/world/' + hub_name)
        return self.write_file(save_list, path_savefile)

    def load_dungeon(self, hub_name, depth, pc_obj):
        path_savefile = self.path + '/save/' + str(pc_obj.game_id) + '/world/' + hub_name + '/floor' + str(
            depth) + '.sav'

        dungeon_summary = self.read_file(path_savefile)
        if dungeon_summary is False:
            return False

        # load bg interiors
        pc_obj.gameboard.solid_list.clear()
        pc_obj.gameboard.render_interior_list.clear()
        bg_int_number = int(dungeon_summary[0])
        line_cur = 1
        for i in range(0, bg_int_number):
            int_str = dungeon_summary[line_cur]
            self.str_to_interior(int_str, False, pc_obj)
            line_cur += 1

        # load fg interiors
        pc_obj.gameboard.render_interior_covering_list.clear()
        fg_int_number = int(dungeon_summary[line_cur])
        line_cur += 1
        for i in range(0, fg_int_number):
            int_str = dungeon_summary[line_cur]
            self.str_to_interior(int_str, True, pc_obj)
            line_cur += 1

        # load rooms
        pc_obj.gameboard.labyrinth.room_list.clear()
        room_number = int(dungeon_summary[line_cur])
        line_cur += 1
        for i in range(0, room_number):
            top, left, bottom, right = dungeon_summary[line_cur].split(',')
            room_list = [int(top), int(left), int(bottom), int(right)]
            pc_obj.gameboard.labyrinth.room_list.append(room_list)
            line_cur += 1

        pc_obj.gameboard.labyrinth.discovered_rooms.clear()
        dis_room_number = int(dungeon_summary[line_cur])
        line_cur += 1
        for i in range(0, dis_room_number):
            top, left, bottom, right = dungeon_summary[line_cur].split(',')
            room_list = [int(top), int(left), int(bottom), int(right)]
            pc_obj.gameboard.labyrinth.room_list.append(room_list)
            pc_obj.gameboard.labyrinth.discovered_rooms.append(room_list)
            line_cur += 1

        # load doors
        pc_obj.gameboard.labyrinth.door_list.clear()
        door_number = int(dungeon_summary[line_cur])
        line_cur += 1
        for i in range(0, door_number):
            x, y, drawing_depth, visible, labobj_dict, line_cur = self.str_to_labobj(dungeon_summary, line_cur, pc_obj)
            new_door = Door(pc_obj.gameboard, labobj_dict, x, y)
            new_door.drawing_depth = drawing_depth
            new_door.visible = visible
            new_door.checkme()
            pc_obj.gameboard.labyrinth.door_list.append(new_door)
            # line_cur += 1

        # load stairs
        pc_obj.gameboard.labyrinth.stairs_list.clear()
        stairs_number = int(dungeon_summary[line_cur])
        line_cur += 1
        for i in range(0, stairs_number):
            x, y, drawing_depth, visible, labobj_dict, line_cur = self.str_to_labobj(dungeon_summary, line_cur, pc_obj)
            new_stairs = Stairs(pc_obj.gameboard, labobj_dict, None, x, y)
            new_stairs.drawing_depth = drawing_depth
            new_stairs.visible = visible
            new_stairs.checkme()
            pc_obj.gameboard.labyrinth.stairs_list.append(new_stairs)

        # load traps
        pc_obj.gameboard.render_trap_list.clear()
        trap_number = int(dungeon_summary[line_cur])
        line_cur += 1
        for i in range(0, trap_number):
            x, y, drawing_depth, visible, labobj_dict, line_cur = self.str_to_labobj(dungeon_summary, line_cur, pc_obj)
            new_trap = Trap(pc_obj.gameboard, labobj_dict, x, y)
            new_trap.drawing_depth = drawing_depth
            new_trap.visible = visible
            # line_cur += 1

        # load items
        pc_obj.gameboard.render_items_list.clear()
        item_number = int(dungeon_summary[line_cur])
        line_cur += 1
        for i in range(0, item_number):
            x, y, drawing_depth, visible, labobj_dict, line_cur = self.str_to_labobj(dungeon_summary, line_cur, pc_obj)
            new_item = Item(pc_obj.gameboard, labobj_dict, labobj_dict['level'], x, y)
            new_item.x, new_item.y = x, y
            new_item.drawing_depth = drawing_depth
            new_item.visible = visible
            pc_obj.gameboard.render_items_list.append(new_item)

        # load mob pool
        pc_obj.gameboard.labyrinth.mob_list.clear()
        pool_mob_number = int(dungeon_summary[line_cur])
        line_cur += 1
        for i in range(0, pool_mob_number):
            pool_mob, line_cur = self.str_unpack(pc_obj, dungeon_summary, line_cur, ':', ';')
            pc_obj.gameboard.labyrinth.mob_list.append(pool_mob)

        # load mobs
        pc_obj.gameboard.render_mobs_list.clear()
        mob_number = int(dungeon_summary[line_cur])
        line_cur += 1
        for i in range(0, mob_number):
            x, y, drawing_depth, visible, labobj_dict, line_cur = self.str_to_labobj(dungeon_summary, line_cur, pc_obj)
            new_mob = Mob(pc_obj.gameboard, labobj_dict, labobj_dict['level'], x, y)
            new_mob.drawing_depth = drawing_depth
            new_mob.visible = visible
            # line_cur += 1

        return True

    def str_to_interior(self, int_str, covering, pc_obj):
        int_list = int_str.split()
        x = int(int_list[0])
        y = int(int_list[1])
        drawing_depth = int(int_list[2])
        visible = int(int_list[3])
        solid = int(int_list[4])
        anim_name = int_list[5]

        new_interior = Interior(pc_obj.gameboard, anim_name, solid, covering, x, y)
        return new_interior

    def str_to_labobj(self, dungeon_summary, line_cur, pc_obj):
        labobj_str = dungeon_summary[line_cur]
        labobj_list = labobj_str.split()
        x = int(labobj_list[0])
        y = int(labobj_list[1])
        drawing_depth = int(labobj_list[2])
        visible = int(labobj_list[3])
        rules_str = labobj_list[4]
        labobj_dict, line_cur = self.str_unpack(pc_obj, dungeon_summary, line_cur, ':', ';')
        print('END OF ITEM UNPACKING')
        return x, y, drawing_depth, visible, labobj_dict, line_cur

    def timestamp_get(self):
        return datetime.now().strftime('%d-%m-%y %H:%M')
