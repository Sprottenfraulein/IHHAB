import random
from class_SolidBlock import SolidBlock
from class_Interior import Interior
from class_Door import Door
from class_Item import Item
from class_Mob import Mob
from class_Stairs import Stairs
from class_Spotlight import Spotlight
from class_Trap import Trap


class Labyrinth:

    doorlock_exponential_ratio = 1.2
    trapdiff_exponential_ratio = 1.2

    def __init__(self, gameboard):
        self.gameboard = gameboard

        self.lab_catalogue = {}
        cat_list = self.gameboard.resources.read_file('./res/data/maps/legend.data')
        for t in cat_list:
            if '=' in t and t[0] != '#':
                labcat_name, labcat_props = t.split("=")
                self.lab_catalogue[labcat_name] = labcat_props.split(' ')

        # self.spotlight = Spotlight(self.gameboard, 'eff_spotlight', 0, 0)

        # self.interior_list = []
        self.door_list = []
        self.room_list = []
        self.mob_list = []
        self.discovered_rooms = []
        self.stairs_list = []

    # TODO town generation and people (trading, fixing, talking, etc.)

    def dungeon_create(self, dungeon_id, level, depth, entry):
        self.dungeon_id = dungeon_id
        self.depth = depth

        self.labyrinth_rules = self.gameboard.tables.table_roll(dungeon_id, 'dungeon_table')
        self.lab_settings = self.gameboard.tables.table_roll(self.labyrinth_rules['architecture'] + str(self.depth), 'labyrinth_table')

        self.gameboard.ui.uitext_caption_change(
            self.gameboard.ui.uielements['ui_scene_info'].uielement['dyn_textobj_dict']['dung_title'],
            (self.labyrinth_rules['name'] + ',_' + str(self.depth) + self.gameboard.get_number_suffix(
                self.depth) + '_floor.'), (255, 255, 255))

        self.lab_tileset = {}
        animation_list = self.gameboard.resources.read_file('./res/data/anims/sets/' + self.lab_settings['anim_set'] + '.data')
        for t in animation_list:
            if '=' in t and t[0] != '#':
                tile_type, animation_names = t.split("=")
                self.lab_tileset[tile_type] = animation_names.split(',')

        floor_index = self.gameboard.resources.file_read_param(dungeon_id + str(depth),
                                                 self.gameboard.resources.path + '/save/' + str(
                                                     self.gameboard.player_char.game_id) + '/world/world_index.sav')
        if floor_index is not False:
            self.gameboard.resources.load_dungeon(dungeon_id, self.depth, self.gameboard.player_char)
        else:
            if self.lab_settings['bld_alg'] == 'maze':
                self.generate_maze(self.lab_settings, level)
            if self.lab_settings['bld_alg'] == 'halls':
                self.generate_halls(self.lab_settings, level)

            self.interior_build(self.labyrinth)

            self.mob_list = self.get_mobs(self.lab_settings['mob_set'], self.lab_settings['mob_types'], level)

            upstairs_x, upstairs_y, downstairs_x, downstairs_y, keepopen_list = self.get_exit_locations(self.labyrinth,
                                                                                                        self.room_list)
            self.set_stairs('stairs', upstairs_x, upstairs_y, -1)
            if self.labyrinth_rules['depth'] > self.depth:
                self.set_stairs('stairs', downstairs_x, downstairs_y, 1)

            self.labyrinth_doors(self.labyrinth, self.room_list, keepopen_list, level, self.depth)

            self.gameboard.resources.save_dungeon(self.gameboard.player_char)
            self.gameboard.resources.worldindex_update(self.gameboard, self.gameboard.player_char.game_id, dungeon_id, self.depth)

            self.gameboard.player_char.stats.gain_exp(self.gameboard.player_char.stats.char_stats_modified['level'] * 50)

        self.gameboard.resources.file_write_param('pc_location', dungeon_id,
                                                  self.gameboard.resources.path + '/save/' + str(
                                                      self.gameboard.player_char.game_id) + '/world/world_index.sav')

        for stairs in self.stairs_list:
            if stairs.rules['stairs_type'] == -1 and entry == 'descended':
                self.start_x = stairs.x
                self.start_y = stairs.y
            elif stairs.rules['stairs_type'] == 1 and entry == 'ascended':
                self.start_x = stairs.x
                self.start_y = stairs.y

        self.gameboard.player_char.x, self.gameboard.player_char.y = self.start_x, self.start_y
        self.gameboard.player_char.dest_x, self.gameboard.player_char.dest_y = self.gameboard.player_char.x, self.gameboard.player_char.y
        self.gameboard.player_char.update_view(True)
        self.room_discover(self.gameboard.player_char)

    def generate_maze(self, lab_settings, level):
        self.labyrinth = [[]]

        self.directions = ['north', 'south', 'west', 'east']

        self.bytemap_clear('%')
        self.dungeon_clear()

        for i in range(0, lab_settings['room_tries']):
            box = self.rnd_space_square(0, 0, lab_settings['lab_w'], lab_settings['lab_h'], lab_settings['room_w_min'], lab_settings['room_h_min'],
                                        lab_settings['room_w_max'], lab_settings['room_h_min'], 1)
            if not self.roomlist_collide(box, self.room_list, 3):
                self.room_list.append(box)

        for room in self.room_list:
            self.square_fill('.', room)

        if len(self.room_list) > 1:
            self.connect_rooms_pathtrace(self.room_list)

        for room in self.room_list:
            self.labyrinth[room[0] - 1][room[1] - 1] = self.labyrinth[room[0] - 1][room[3] + 1] = \
                self.labyrinth[room[2] + 1][room[1] - 1] = self.labyrinth[room[2] + 1][room[3] + 1] = '%'

        hollow_list = self.find_hollows(self.labyrinth)
        for i in hollow_list:
            self.labyrinth[i[1]][i[0]] = '%'

        self.generate_traps(self.labyrinth_rules['trap_base_chance'], self.lab_settings['trap_set'],
                            self.lab_settings['trap_types'], self.lab_settings['trap_chance'], level)

        self.lab_clean(self.labyrinth, '%')

    def generate_halls(self, lab_settings, level):
        self.labyrinth = [[]]

        self.directions = ['north', 'south', 'west', 'east']

        self.bytemap_clear('%')
        self.dungeon_clear()

        for i in range(0, lab_settings['room_tries']):
            box = self.rnd_space_square(1, 1, lab_settings['lab_w'], lab_settings['lab_h'], lab_settings['room_w_min'],
                                        lab_settings['room_h_min'],
                                        lab_settings['room_w_max'], lab_settings['room_h_min'], 2)
            if not self.roomlist_collide(box, self.room_list, 3):
                self.room_list.append(box)

        for room in self.room_list:
            self.square_fill('.', room)

        if len(self.room_list) > 1:
            for room in self.room_list:
                for i in self.directions:
                    x, y = self.get_entrance_rnd(room, i)
                    while (i in ('north', 'south') and x // 2 != x / 2) or (i in ('west', 'east') and y // 2 != y / 2):
                        x, y = self.get_entrance_rnd(room, i)
                    dir_x = -1
                    dir_y = 0
                    if i == 'north':
                        dir_x = 0
                        dir_y = -1
                    if i == 'south':
                        dir_x = 0
                        dir_y = 1
                    if i == 'west':
                        dir_x = -1
                        dir_y = 0
                    if i == 'east':
                        dir_x = 1
                        dir_y = 0
                    self.shoot_path(self.labyrinth, x, y, dir_x, dir_y, '0')

        hollow_list = self.find_hollows(self.labyrinth)
        for i in hollow_list:
            self.labyrinth[i[1]][i[0]] = '%'

        self.generate_traps(self.labyrinth_rules['trap_base_chance'], self.lab_settings['trap_set'],
                            self.lab_settings['trap_types'], self.lab_settings['trap_chance'], level)

        self.lab_clean(self.labyrinth, '%')

    def get_mobs(self, set_name, types_number, level):
        mob_list = []
        for i in range(0, types_number):
            rnd_mob = self.gameboard.tables.table_roll(set_name, 'mob_table')
            if rnd_mob is not False and rnd_mob['level'] <= level:
                mob_list.append(rnd_mob)
        if mob_list is not False:
            return mob_list
        else:
            return False

    def connect_rooms_pathtrace(self, room_list):
        room_sides = []
        for i in range(0, len(room_list)):
            new_list = ['north', 'south', 'west', 'east']
            room_sides.append(new_list)

        for i in range(0, len(room_list)):
            room1 = room_list[i]
            if i == len(room_list) - 1:
                room2 = room_list[0]
            else:
                room2 = room_list[i + 1]

            room1_side = room_sides[i][random.randrange(0, len(room_sides[i]))]
            room_sides[i].remove(room1_side)
            if i == len(room_sides) - 1:
                room2_side = room_sides[0][random.randrange(0, len(room_sides[0]))]
                room_sides[0].remove(room2_side)
            else:
                room2_side = room_sides[i + 1][random.randrange(0, len(room_sides[i + 1]))]
                room_sides[i + 1].remove(room2_side)

            x, y = self.get_entrance_rnd(room1, room1_side)
            a, b = self.get_entrance_rnd(room2, room2_side)

            self.trace_path(self.labyrinth, x, y, a, b, room1_side, '0', ['.'], 400)

    def labyrinth_doors(self, labyrinth, room_list, keepopen_list, level, depth):
        for room in room_list:
            rnd_door = self.gameboard.tables.table_roll(self.labyrinth_rules['doors'], 'labyrinth_table')
            print(rnd_door)
            if rnd_door['name'] == 'common_doorway':
                continue
            doors_hor_list, doors_ver_list = self.find_doors(labyrinth, room, 'd')
            print(doors_hor_list, doors_ver_list)
            if self.labyrinth_rules['one_door_treasuries'] == 1 and len(doors_hor_list) + len(doors_ver_list) == 1 and room not in keepopen_list:
                rnd_door['lock'] = self.gameboard.exponential(self.doorlock_exponential_ratio, level,
                                                              self.labyrinth_rules['doorlock_multiplier'])
            elif rnd_door['lock'] == 1 and rnd_door['m_lock'] == 0:
                print(room, keepopen_list)
                if room not in keepopen_list:
                    rnd_door['lock'] = self.gameboard.exponential(self.doorlock_exponential_ratio, level,
                                                              self.labyrinth_rules['doorlock_multiplier'])
                else:
                    rnd_door['lock'] = 0
            elif rnd_door['m_lock'] == 1 and room in keepopen_list:
                rnd_door['m_lock'] = 0
                rnd_door['lock'] = 0
            self.set_doors(labyrinth, doors_hor_list, doors_ver_list, rnd_door)
            print(self.door_list)

    def rnd_space_square(self, start_x, start_y, finish_x, finish_y, min_room_width, min_room_height, max_room_width,
                         max_room_height, step):
        top = random.randrange(start_x + 3, finish_y - 3 - (min_room_height - 1), step)
        left = random.randrange(start_y + 3, finish_x - 3 - (min_room_width - 1), step)
        max_bottom = min(top + max_room_height, finish_y - 3)
        max_right = min(left + max_room_width, finish_x - 3)
        if top + (min_room_height - 1) == max_bottom:
            bottom = max_bottom
        else:
            bottom = random.randrange(top + (min_room_height - 1), max_bottom, step)
        if left + (min_room_width - 1) == max_right:
            right = max_right
        else:
            right = random.randrange(left + (min_room_width - 1), max_right, step)
        return top, left, bottom, right

    def fill_square_box(self, walls, floors, space_sizes):
        self.square_fill(floors, space_sizes)
        self.square_frame(walls, space_sizes)

    def square_frame(self, interior, space_sizes):
        top, left, bottom, right = space_sizes
        for i in range(left - 1, right + 1):
            self.labyrinth[top][i] = interior
            self.labyrinth[bottom][i] = interior

        for i in range(top + 1, bottom):
            self.labyrinth[i][left - 1] = interior
            self.labyrinth[i][right] = interior

    def square_fill(self, interior, space_sizes):
        top, left, bottom, right = space_sizes
        for i in range(top, bottom + 1):
            for j in range(left, right + 1):
                self.labyrinth[i][j] = interior

    def get_roomside(self, room, side):
        room_side = {
            'x': [],
            'y': []
        }
        if side == 'north':
            for i in range(room[1], room[3] + 1):
                room_side['x'].append(i)
            room_side['y'].append(room[0] - 1)
        if side == 'south':
            for i in range(room[1], room[3] + 1):
                room_side['x'].append(i)
            room_side['y'].append(room[2] + 1)
        if side == 'west':
            for i in range(room[0], room[2] + 1):
                room_side['y'].append(i)
            room_side['x'].append(room[1] - 1)
        if side == 'east':
            for i in range(room[0], room[2] + 1):
                room_side['y'].append(i)
            room_side['x'].append(room[3] + 1)
        return room_side

    def get_entrance_rnd(self, room, side):
        ent_available = self.get_roomside(room, side)

        rnd_x = ent_available['x'][random.randrange(0, len(ent_available['x']))]
        rnd_y = ent_available['y'][random.randrange(0, len(ent_available['y']))]

        return rnd_x, rnd_y

    def trace_path(self, labyrinth, start_x, start_y, finish_x, finish_y, direction, map_byte, avoid_bytes, c_limit):
        x, y = start_x, start_y
        counter = 0
        if direction == 'north':
            mov_x = 0
            mov_y = -1
        elif direction == 'south':
            mov_x = 0
            mov_y = 1
        elif direction == 'east':
            mov_x = 1
            mov_y = 0
        elif direction == 'west':
            mov_x = -1
            mov_y = 0
        asap_north = False
        asap_south = False
        asap_east = False
        asap_west = False
        while counter < c_limit:
            labyrinth[y][x] = '0'
            if x == finish_x and y == finish_y:
                labyrinth[finish_y][finish_x] = 'd'
                labyrinth[start_y][start_x] = 'd'
                return
            if (abs(finish_x - x) == 1 and abs(finish_y - y) == 0) or (
                    abs(finish_x - x) == 0 and abs(finish_y - y) == 1):
                labyrinth[finish_y][finish_x] = 'd'
                labyrinth[start_y][start_x] = 'd'
                return
            if not self.check_corners(labyrinth, x + mov_x, y + mov_y, ['.']) or (
                    x + mov_x == finish_x and y + mov_y == finish_y):
                x += mov_x
                y += mov_y
            else:
                if mov_y == 0 and y < finish_y:
                    mov_y = 1
                    mov_x = 0
                elif mov_y == 0 and y >= finish_y:
                    mov_y = -1
                    mov_x = 0
                elif mov_x == 0 and x < finish_x:
                    mov_y = 0
                    mov_x = 1
                elif mov_x == 0 and x >= finish_x:
                    mov_y = 0
                    mov_x = -1
            if mov_x == 1 and x > finish_x:
                if y > finish_y:
                    asap_north = True
                if y < finish_y:
                    asap_south = True
            if mov_x == -1 and x <= finish_x:
                if y > finish_y:
                    asap_north = True
                if y < finish_y:
                    asap_south = True
            if mov_y == 1 and y > finish_y:
                if x > finish_x:
                    asap_west = True
                if x < finish_x:
                    asap_east = True
            if mov_y == -1 and y <= finish_y:
                if x > finish_x:
                    asap_west = True
                if x < finish_x:
                    asap_east = True
            if asap_north:
                if not self.check_corners(labyrinth, x, y - 1, ['.']):
                    mov_x = 0
                    mov_y = -1
                    asap_north = False
            if asap_south:
                if not self.check_corners(labyrinth, x, y + 1, ['.']):
                    mov_x = 0
                    mov_y = 1
                    asap_south = False
            if asap_east:
                if not self.check_corners(labyrinth, x + 1, y, ['.']):
                    mov_x = 1
                    mov_y = 0
                    asap_east = False
            if asap_west:
                if not self.check_corners(labyrinth, x - 1, y, ['.']):
                    mov_x = -1
                    mov_y = 0
                    asap_west = False
            counter += 1

    def check_corners(self, labyrinth, x, y, byte_list):
        if 0 < x < self.lab_settings['lab_w'] - 1 and 0 < y < self.lab_settings['lab_h'] - 1:
            if labyrinth[y - 1][x - 1] not in byte_list and labyrinth[y - 1][x + 1] not in byte_list and \
                    labyrinth[y + 1][x - 1] not in byte_list and labyrinth[y + 1][x + 1] not in byte_list:
                return False
        return True

    def shoot_path(self, labyrinth, start_x, start_y, dir_x, dir_y, map_byte):
        x, y = start_x, start_y
        dig = 1
        while dig == 1:
            x += dir_x
            y += dir_y
            if labyrinth[y + dir_x][x + dir_y] in ['0','.'] or labyrinth[y - dir_x][x - dir_y] in ['0','.']:
                dig = 0
                print('Dead end!')
            if x + dir_x == 0 or x + dir_x == self.lab_settings['lab_w'] - 1 or y + dir_y == 0 or y + dir_y == self.lab_settings['lab_h'] - 1:
                dig = 0
                print('Dead end!')
            if labyrinth[y + dir_y][x + dir_x] == '.':
                dig = 2
                print('Found room!')
            if labyrinth[y + dir_y][x + dir_x] == '0':
                dig = 3
                print('Cross section!')
        if dig == 0:
            return False
        if dig == 2:
            labyrinth[y][x] = 'd'
            while start_x != x or start_y != y:
                x -= dir_x
                y -= dir_y
                labyrinth[y][x] = map_byte
            labyrinth[y][x] = 'd'
            return True
        if dig == 3:
            labyrinth[y][x] = '0'
            while start_x != x or start_y != y:
                x -= dir_x
                y -= dir_y
                labyrinth[y][x] = map_byte
            labyrinth[y][x] = 'd'
            return True
        return False

    def set_doors(self, labyrinth, doors_hor_list, doors_ver_list, rules=None):
        if rules is None:
            rules = {'default': 0}
        print(rules)
        doors = 0
        rules['align'] = 'hor'
        for door in doors_hor_list:
            self.spawn_door(rules, door[0], door[1])
            doors += 1
        rules['align'] = 'ver'
        for door in doors_ver_list:
            self.spawn_door(rules, door[0], door[1])
            doors += 1
        return doors

    def set_stairs(self, id_roll, lab_x, lab_y, stairs_type):
        self.labyrinth[lab_y][lab_x] = '*'
        stairs = self.gameboard.tables.table_roll(id_roll, 'labyrinth_table')
        new_stairs = Stairs(self.gameboard, stairs, stairs_type, lab_x * self.gameboard.square_width,
                            lab_y * self.gameboard.square_height)
        self.stairs_list.append(new_stairs)

    def find_doors(self, labyrinth, room, ent_byte):
        top, left, bottom, right = room
        doorways_hor_list = []
        doorways_ver_list = []
        pattern = [
            ['?', '?', '?'],
            [['.','0'], 'd', ['.','0']],
            ['?', '?', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, left - 2, top - 2, right + 3, bottom + 3, pattern, 1, 1, 1, 1)
        if locations is not False:
            doorways_ver_list.extend(locations)
        pattern = [
            ['?', ['.','0'], '?'],
            ['?', 'd', '?'],
            ['?', ['.','0'], '?']
        ]
        locations = self.find_grid_pattern(labyrinth, left - 2, top - 2, right + 3, bottom + 3, pattern, 1, 1, 1, 1)
        if locations is not False:
            doorways_hor_list.extend(locations)
        print(doorways_hor_list, doorways_ver_list)
        return doorways_hor_list, doorways_ver_list

    def test_room(self, labyrinth, room, map_byte):
        for i in range(room[0] - 1, room[2] + 2):
            for j in range(room[1] - 1, room[3] + 2):
                if labyrinth[i][j] == map_byte:
                    return True
        return False

    def get_exit_locations(self, labyrinth, room_list):
        exit_list = []
        room1, side1, room2, side2, keepopen_list = self.get_opposite_ends(labyrinth, room_list)
        room1_x = random.randrange(room1[1] + 1, room1[3])
        room1_y = random.randrange(room1[0] + 1, room1[2])
        room2_x = random.randrange(room2[1] + 1, room2[3])
        room2_y = random.randrange(room2[0] + 1, room2[2])
        while room1_x == room2_x and room1_y == room2_y and room1 == room2:
            room1_x = random.randrange(room1[1] + 1, room1[3])
            room1_y = random.randrange(room1[0] + 1, room1[2])
            room2_x = random.randrange(room2[1] + 1, room2[3])
            room2_y = random.randrange(room2[0] + 1, room2[2])
        exit_list.append([room1_x, room1_y])
        exit_list.append([room2_x, room2_y])
        rnd_boolean = random.randrange(0, 2)
        upstairs_x, upstairs_y = exit_list[rnd_boolean * -1]
        downstairs_x, downstairs_y = exit_list[(1 - rnd_boolean) * -1]
        print(exit_list)
        print('EXIT INDEXES:', rnd_boolean * -1, (1 - rnd_boolean) * -1)
        return upstairs_x, upstairs_y, downstairs_x, downstairs_y, keepopen_list

    def get_opposite_ends(self, labyrinth, room_list):
        keepopen_list = []
        if self.lab_settings['lab_h'] > self.lab_settings['lab_w']:
            min_top = self.lab_settings['lab_h']
            top_room = None
            max_bottom = 0
            bottom_room = None
            for room in room_list:
                if room[0] < min_top:
                    min_top = room[0]
                    top_room = room
                if room[2] > max_bottom:
                    max_bottom = room[2]
                    bottom_room = room
            if top_room == None:
                try:
                    top_room = room_list[random.randrange(0, len(room_list))]
                except ValueError:
                    top_room = room_list[0]
            if bottom_room == None:
                try:
                    bottom_room = room_list[random.randrange(0, len(room_list))]
                except ValueError:
                    bottom_room = room_list[0]
            keepopen_list.append(top_room)
            keepopen_list.append(bottom_room)
            return top_room, 'west', bottom_room, 'east', keepopen_list
        else:
            min_left = self.lab_settings['lab_w']
            left_room = None
            max_right = 0
            right_room = None
            for room in room_list:
                if room[1] < min_left:
                    min_left = room[1]
                    left_room = room
                if room[3] > max_right:
                    max_right = room[3]
                    right_room = room
            if left_room == None:
                try:
                    left_room = room_list[random.randrange(0, len(room_list))]
                except ValueError:
                    left_room = room_list[0]
            if right_room == None:
                try:
                    right_room = room_list[random.randrange(0, len(room_list))]
                except ValueError:
                    right_room = room_list[0]
            keepopen_list.append(left_room)
            keepopen_list.append(right_room)
            return left_room, 'west', right_room, 'east', keepopen_list

    def find_hollows(self, labyrinth):
        locations_list = []
        pattern = [
            ['0', '0', '0'],
            ['0', '0', '0'],
            ['0', '0', '0']
        ]
        locations = self.find_grid_pattern(labyrinth, 0, 0, self.lab_settings['lab_w'], self.lab_settings['lab_h'], pattern, 1, 1, 1, 1)
        if locations is not False:
            locations_list.extend(locations)
        return locations_list

    # Spawning objects
    def spawn_interior(self, anim_name, is_solid, is_covering, desc, x, y):
        new_interior = Interior(self.gameboard, anim_name, is_solid, is_covering, x * self.gameboard.square_width, y * self.gameboard.square_height)
        # self.interior_list.append(new_interior)
        return new_interior

    def spawn_door(self, rules, x, y):
        x *= self.gameboard.square_width
        y *= self.gameboard.square_height
        """for i in self.door_list:
            if i.x == x and i.y == y:
                i.door = rules
                return i
        print(rules)"""
        new_door = Door(self.gameboard, rules, x, y)
        self.door_list.append(new_door)
        return new_door

    def spawn_item(self, item, level, x, y):
        new_item = Item(self.gameboard, item, level, x, y)
        return new_item

    def roomlist_collide(self, box, box_list, distance):
        for i in box_list:
            if self.room_collide(box, i, distance):
                return True
        return False

    def room_collide(self, box1, box2, distance):
        if box1[0] - distance <= box2[2] and box1[2] + distance >= box2[0] and \
                box1[1] - distance <= box2[3] and box1[3] + distance >= box2[1] or \
                (box1[0] == box2[0] and box1[1] == box2[1] and box1[2] == box2[2] and box1[3] == box2[3]):
            return True
        return False

    def find_nearby_space(self, start_x, start_y, space_number, toavoid_list, square_width, square_height,
                          white_list=None, r=None, r_max=None):
        if white_list is None:
            white_list = [[start_x, start_y]]
            r = 1
        spaces_list = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        random.shuffle(spaces_list)
        for tile_x, tile_y in spaces_list:
            is_white = True
            abs_x, abs_y = start_x + tile_x * square_width, start_y + tile_y * square_height
            for obj_list in toavoid_list:
                if not self.free_of_objects(abs_x, abs_y, obj_list):
                    is_white = False
                    break
            if is_white and ([abs_x, abs_y] not in white_list):
                white_list.append([abs_x, abs_y])
        if len(white_list) < space_number and (r_max == None or r < r_max):
            for i in range(r, len(white_list)):
                self.find_nearby_space(white_list[i][0], white_list[i][1],
                                       space_number, toavoid_list, square_width,
                                       square_height, white_list, r + 1, r_max)
        return white_list

    def find_grid_pattern(self, labyrinth, start_x, start_y, end_x, end_y, pattern_matrix, step_hor, step_ver, offset_x,
                          offset_y):
        match_list = []
        matrix_height = len(pattern_matrix)
        matrix_width = len(pattern_matrix[0])
        for i in range(start_x, end_x - matrix_width + 1, step_hor):
            for j in range(start_y, end_y - matrix_height + 1, step_ver):
                if self.compare_grid_pattern(labyrinth, i, j, pattern_matrix, matrix_width, matrix_height):
                    match_list.append([i + offset_x, j + offset_y])
        if len(match_list) > 0:
            return match_list
        else:
            return False

    def compare_grid_pattern(self, labyrinth, lab_x, lab_y, pattern_matrix, matrix_width, matrix_height):
        for m in range(0, matrix_height):
            for n in range(0, matrix_width):
                try:
                    lab_byte = labyrinth[lab_y + m][lab_x + n]
                except IndexError:
                    lab_byte = ' '
                if lab_byte not in pattern_matrix[m][n] and pattern_matrix[m][n] != '?':
                    return False
        return True

    def free_of_objects(self, x, y, obj_list):
        for obj_inst in obj_list:
            if obj_inst.x == x and obj_inst.y == y:
                return False
        return True

    def dungeon_clear(self):
        self.room_list.clear()
        # self.interior_list.clear()
        self.door_list.clear()
        self.stairs_list.clear()
        self.discovered_rooms.clear()
        self.gameboard.render_text_list.clear()
        self.gameboard.render_effects_list.clear()
        self.gameboard.render_interior_list.clear()
        self.gameboard.render_interior_covering_list.clear()
        self.gameboard.render_items_list.clear()
        self.gameboard.solid_list.clear()
        self.gameboard.render_mobs_list.clear()
        self.gameboard.render_trap_list.clear()

    def lab_clean(self, labyrinth, map_byte):
        pattern = [
            [['%',' '], ['%',' '], ['%',' ']],
            [['%',' '], '?',       ['%',' ']],
            [['%',' '], ['%',' '], ['%',' ']]
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:

            for location in locations:
                labyrinth[location[1]][location[0]] = ' '

        for i in range(- 1, self.lab_settings['lab_h'] - 1):
            print(''.join(labyrinth[i]))

    def bytemap_clear(self, map_byte):
        # generate byte-map
        self.labyrinth = []
        self.labyrinth.clear()
        for i in range(0, self.lab_settings['lab_h']):
            self.labyrinth.append([map_byte] * self.lab_settings['lab_w'])

    def delete_rooms(self, del_list):
        for room in del_list:
            self.square_fill('%', room)
            self.room_list.remove(room)
        del_list.clear()

    def interior_build(self, labyrinth):
        for i in range(0, len(labyrinth)):
            for j in range(0, len(labyrinth[i])):
                map_byte = labyrinth[i][j]
                if map_byte in ['0']:
                    self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', j, i)
                if map_byte in ['.','*']:
                    self.spawn_interior(self.get_labtile('floor_room_small'), 0, 0, 'floor', j, i)

        pattern = [
            ['?', '?', '?'],
            [['%','d'], '%', '%'],
            ['?', '?', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_hor'), 1, 0, 'wall', location[0], location[1])
        pattern = [
            ['?', ['%','d'], '?'],
            ['?', '%', '?'],
            ['?', '%', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_ver'), 1, 0, 'wall', location[0], location[1])
        pattern = [
            ['?', '?', '?'],
            [['.', '0'], '%', '%'],
            ['?', ['.', '0'], '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', location[0], location[1])
                self.spawn_interior(self.get_labtile('wall_corner_lb'), 1, 0, 'wall', location[0], location[1])
        pattern = [
            ['?',       '?',        '?'],
            [' ', '%',        '%'],
            ['?',       ' ',  '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_corner_lb'), 1, 0, 'wall', location[0], location[1])

        pattern = [
            ['?',       ['%','d'],          '?'],
            [['%','d'],       '%',          ['.',' ','0']],
            ['?',       ['.',' ','0'],    '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_corner_rb'), 1, 0, 'wall', location[0], location[1])
        pattern = [
            ['?',       ['.','0'],        '?'],
            ['?',       '%',              ['.','0']],
            ['?',       '%',              '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', location[0], location[1])
                self.spawn_interior(self.get_labtile('wall_corner_rt'), 1, 0,'wall', location[0], location[1])
        pattern = [
            ['?', ' ', '?'],
            ['?', '%', ' '],
            ['?', '%', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_corner_rt'), 1, 0, 'wall', location[0], location[1])
        pattern = [
            ['?', '?', '?'],
            ['?', '%', '%'],
            ['?', '%', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_corner_lt'), 1, 0,'wall', location[0], location[1])

        pattern = [
            ['?', '%', '?'],
            [['.','0'], '%', ['.','0']],
            ['?', ['.','0'], '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', location[0], location[1])
                self.spawn_interior(self.get_labtile('wall_end_bottom'), 1, 0,'wall', location[0], location[1])
        pattern = [
            ['?', ['.','0'], '?'],
            ['%', '%', ['.','0']],
            ['?', ['.','0'], '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', location[0], location[1])
                self.spawn_interior(self.get_labtile('wall_end_right'), 1, 0,'wall', location[0], location[1])

        pattern = [
            ['?', '?',       '?'],
            [['%','d'], '%',              'd'],
            ['?', ['.', '0'],       '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_door_hor_left'), 1, 0,'wall', location[0], location[1])

        pattern = [
            ['?', '?', '?'],
            ['%', 'd', '%'],
            ['?', ['.', '0'], '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', location[0], location[1])
                self.spawn_interior(self.get_labtile('wall_door_hor_right'), 0, 1, 'wall', location[0], location[1])

        pattern = [
            ['?', '%', '?'],
            ['?', 'd', ['.', '0']],
            ['?', '%', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', location[0], location[1])
                self.spawn_interior(self.get_labtile('wall_door_ver_bottom'), 0, 1, 'wall', location[0], location[1])

        pattern = [
            ['?', ['%','d'], '?'],
            ['?', '%', ['.', '0']],
            ['?', 'd', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_door_ver_top'), 1, 0,'wall', location[0], location[1])

        pattern = [
            ['?', '?', '?'],
            ['?', '%', 'd'],
            ['?', 'd', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_door_lt_lefttop'), 1, 0,'wall', location[0], location[1])
        pattern = [
            ['?', '?', '?'],
            ['?', '%', '%'],
            ['?', 'd', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_door_lt_left'), 1, 0,'wall', location[0], location[1])
        pattern = [
            ['?', '?', '?'],
            ['?', '%', 'd'],
            ['?', '%', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('wall_door_lt_top'), 1, 0,'wall', location[0], location[1])
        pattern = [
            ['?', ['.', '0'], '?'],
            ['?', '%', ['.', '0']],
            ['?', 'd', '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', location[0], location[1])
                self.spawn_interior(self.get_labtile('wall_door_rt'), 1, 0,'wall', location[0], location[1])
        pattern = [
            ['?', '?', '?'],
            [['.', '0'], '%', 'd'],
            ['?', ['.', '0'], '?']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', location[0], location[1])
                self.spawn_interior(self.get_labtile('wall_door_lb'), 1, 0,'wall', location[0], location[1])
        pattern = [
            ['0', '0', '0'],
            ['0', '%', '0'],
            ['0', '0', '0']
        ]
        locations = self.find_grid_pattern(labyrinth, -1, -1, self.lab_settings['lab_w'] + 1, self.lab_settings['lab_h'] + 1, pattern, 1, 1, 1, 1)
        if locations is not False:
            for location in locations:
                self.spawn_interior(self.get_labtile('floor_small'), 0, 0, 'floor', location[0], location[1])
                self.spawn_interior(self.get_labtile('wall_statue'), 1, 0, 'wall', location[0], location[1])

    def room_discover(self, player):
        if self.gameboard.labyrinth:
            self.gameboard.player_in_room = False
            self.gameboard.area_visible(True, 0, 0,
                                        self.lab_settings['lab_h'] * self.gameboard.square_height,
                                        self.lab_settings['lab_w'] * self.gameboard.square_width)
            """self.gameboard.area_visible(True, player.y - self.gameboard.square_height * 3, player.x - self.gameboard.square_width * 3,
                                        player.y + self.gameboard.square_height * 3, player.x + self.gameboard.square_width * 3)"""
            for room in self.gameboard.labyrinth.room_list:
                if (room[1] - 1) * self.gameboard.square_width <= player.x <= (room[3] + 1) * self.gameboard.square_width and \
                        (room[0] - 1) * self.gameboard.square_height <= player.y <= (room[2] + 1) * self.gameboard.square_height:
                    self.gameboard.player_in_room = True
                    if room not in self.discovered_rooms:
                        self.room_enter(room)
                    self.gameboard.area_visible(False, 0, 0,
                                                self.lab_settings['lab_h'] * self.gameboard.square_height,
                                                self.lab_settings['lab_w'] * self.gameboard.square_width)
                    self.gameboard.area_visible(True,
                                                (room[0] - 1) * self.gameboard.square_height,
                                                (room[1] - 1) * self.gameboard.square_width,
                                                (room[2] + 1) * self.gameboard.square_height,
                                                (room[3] + 1) * self.gameboard.square_width)
                else:
                    self.gameboard.area_visible(False,
                                                (room[0]) * self.gameboard.square_height,
                                                (room[1]) * self.gameboard.square_width,
                                                (room[2]) * self.gameboard.square_height,
                                                (room[3]) * self.gameboard.square_width)

    def room_enter(self, room):
        self.discovered_rooms.append(room)
        self.gameboard.audio.sound_bank['room_reveal'].play()
        self.gameboard.reveal_traps_area(
            (room[0] - 1) * self.gameboard.square_height,
            (room[1] - 1) * self.gameboard.square_width,
            (room[2] + 1) * self.gameboard.square_height,
            (room[3] + 1) * self.gameboard.square_width)
        self.room_mobs_generate(self.mob_list, self.labyrinth_rules['mob_base_count'], self.lab_settings['crowd_offset'], room, self.depth)
        self.gameboard.player_char.stats.gain_exp(self.gameboard.player_char.stats.char_stats_modified['level'] * 10)

    def room_mobs_generate(self, mob_list, mob_base_count, crowd_offset, room, depth):
        mobs_base_number = mob_base_count + depth
        print('Mobs base number:', mobs_base_number)

        mn_modifier = random.randrange(50, 151) + crowd_offset     # in percents
        mobs_number = mobs_base_number * mn_modifier // 100
        print('Modifier:', mn_modifier)
        print('Mobs modified number:', mobs_number)

        mob_number_limiter = (room[3] - room[1] + 1) * (room[2] - room[0] + 1) // 2
        mobs_number = min(mobs_number, mob_number_limiter)
        print('Room limiter:', mob_number_limiter)
        print('Final mob number:', mobs_number)

        center_x = (room[1] + room[3]) // 2 * self.gameboard.square_width
        center_y = (room[0] + room[2]) // 2 * self.gameboard.square_height
        spaces_list = self.find_nearby_space(center_x, center_y, mobs_number,
                                             [self.gameboard.solid_list, self.door_list, [self.gameboard.player_char]
                                              ], self.gameboard.square_width,
                                             self.gameboard.square_height, r_max=6)

        for i in range(0, mobs_number):
            mob_rnd_index = random.randrange(0, len(mob_list))
            mob_rules = mob_list[mob_rnd_index]
            mob_x, mob_y = spaces_list.pop()
            self.spawn_enemy(mob_rules, mob_x, mob_y)

    def spawn_enemy(self, mob_rules, x, y):
        new_enemy = Mob(self.gameboard, mob_rules, self.gameboard.player_char.stats.char_stats_modified['level'], x, y)

    def drop_loot(self, loot_list, x, y, not_include_center):
        spaces_list = self.find_nearby_space(x, y, len(loot_list) + not_include_center,
                                             [self.gameboard.solid_list, self.gameboard.render_mobs_list,
                                              self.gameboard.render_items_list, self.door_list,
                                              [self.gameboard.player_char]], self.gameboard.square_width,
                                             self.gameboard.square_height, r_max=4)
        n = -1
        for n in range(0, len(spaces_list) - not_include_center):
            dest_x, dest_y = spaces_list[n + not_include_center]
            loot_list[n].visible = True
            loot_list[n].dropme(x, y, dest_x, dest_y)
            if n == len(loot_list) - 1:
                break
        leftoff = loot_list[n + 1:]
        if len(leftoff) > 0:
            self.drop_loot_forced(leftoff, x, y, False)

    def drop_loot_forced(self, loot_list, x, y, not_include_center):
        spaces_list = self.find_nearby_space(x, y, len(loot_list) + not_include_center,
                                             [self.gameboard.solid_list, self.door_list,
                                              ], self.gameboard.square_width,
                                             self.gameboard.square_height, r_max=4)
        n = not_include_center
        for m in range(0, len(loot_list)):
            dest_x, dest_y = spaces_list[n]
            loot_list[n].visible = True
            loot_list[m].dropme(x, y, dest_x, dest_y)
            n += 1
            if n == len(spaces_list):
                n = not_include_center

    def get_labtile(self, tile_type):
        tile_list = self.lab_tileset[tile_type]
        if len(tile_list) > 1:
            rnd_index = random.randrange(0, len(tile_list))
            return tile_list[rnd_index]
        else:
            try:
                return tile_list[0]
            except IndexError:
                return 'in_floor_red_square'

    def generate_traps(self, trap_base_chance, trap_set, trap_types, trap_chance, level):
        trap_list = []
        trap_count = 0
        for i in range(0, trap_types):
            new_trap_type = self.gameboard.tables.table_roll(trap_set, 'labyrinth_table')
            if new_trap_type is not False:
                trap_list.append(new_trap_type)
        if len(trap_list) > 0:
            trap_chance_total = trap_base_chance + trap_chance
            for y in range(0, self.lab_settings['lab_h']):
                for x in range(0, self.lab_settings['lab_w']):
                    if self.labyrinth[y][x] in ['.', '0']:
                        rnd_roll = random.randrange(0, 1000)
                        if rnd_roll <= trap_chance_total:
                            trap_index = random.randrange(0, len(trap_list))
                            self.spawn_trap(trap_list[trap_index], x, y, level)
                            trap_count += 1
        return trap_count

    def spawn_trap(self, trap_rules, x, y, level):
        new_trap_rules = trap_rules.copy()
        new_trap_rules['difficulty'] = self.gameboard.exponential(self.trapdiff_exponential_ratio, level,
                                                                  self.labyrinth_rules['trapdiff_multiplier'])
        if new_trap_rules['hidden'] > 0:
            new_trap_rules['hidden'] = self.gameboard.exponential(self.trapdiff_exponential_ratio, level,
                                                                  self.labyrinth_rules['trapdiff_multiplier'])
        new_trap_rules['level'] = level
        new_trap = Trap(self.gameboard, new_trap_rules, x * self.gameboard.square_width, y * self.gameboard.square_height)

    def labobj_to_str(self, labobj):
        labobj_list = [
            str(labobj.x),
            str(labobj.y),
            str(labobj.drawing_depth),
            str(int(labobj.visible))
        ]
        labobj_rules_list = self.gameboard.resources.dict_to_str(labobj.rules, ':', ';')
        total_list = []
        for labobj_rules in labobj_rules_list:
            print(' '.join(labobj_list + [labobj_rules]))
            total_list.append(' '.join(labobj_list + [labobj_rules]))
        return total_list

    def interior_to_str(self, interior):
        interior_str = ' '.join([
            str(interior.x),
            str(interior.y),
            str(interior.drawing_depth),
            str(int(interior.visible)),
            str(int(interior in self.gameboard.solid_list)),
            str(interior.animation.anim_name)
        ])
        return interior_str


