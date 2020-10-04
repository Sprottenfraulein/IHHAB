#   ui_dict = {
#       textobj_list = []
#       tile_list = [
#           tile = {
#               animations = {
#                   state_default =
#                   state_mdown =
#               }
#               trigger_id =
#               mirrored =
#               flipped
#               width =
#               height =
#               positions = [
#                   [x, y]
#                   [x, y]
#                   ...
#               ]
#           }
#           ...
#       ]
#
#       trigger_map = [
#           trigger_id = {
#               trigger_id =
#               top = [x, y]
#               left = [x, y]
#               bottom = [x, y]
#               right = [x, y]
#               state =
#               key_code =
#           }
#       ]
#       sound_set = {
#           sound = {
#               sound_name
#               trigger_id = {
#                   states = []
#               }
#           }
#       }
#   }

import pygame
from class_UIText import UIText


class UIElement:

    def __init__(self, gameboard, ui_name):
        # Initialize attributes to represent the character.

        self.gameboard = gameboard
        self.image = None
        self.screen = self.gameboard.screen

        self.mousefollow = 0
        self.stick_hor = -1
        self.stick_ver = -1
        self.offset_x = 0
        self.offset_y = 0

        self.textlayer_list = []
        self.uielement = self.load_uielement(ui_name)
        self.active = True
        self.x = 0
        self.y = 0

    def load_uielement(self, ui_name):
        textobj_list = []
        dyn_textobj_dict = {}
        trigger_map = {}
        tile_list = []
        tr_tile_dict = {}
        sound_list = {}

        uielement_list = self.gameboard.resources.read_file(self.gameboard.resources.uielements[ui_name])

        u = 0
        while u < len(uielement_list):
            if len(uielement_list[u]) > 0 and uielement_list[u][0] != '#':
                element_name, element_content = uielement_list[u].split("=")
                if element_name == 'alignment':
                    content_list = element_content.split()
                    self.mousefollow, self.stick_hor, self.stick_ver, self.offset_x, self.offset_y = float(
                        content_list[0]), float(content_list[1]), float(content_list[2]), float(content_list[3]), float(
                        content_list[4])
                if element_name == 'ui_topleft':
                    ui_x, ui_y = element_content.split(',')
                    self.x, self.y = int(ui_x), int(ui_y)
                if element_name == 'text':
                    new_text = self.create_text(element_content)
                    textobj_list.append(new_text)
                elif element_name == 'dyn_text':
                    new_text = self.create_dyn_text(element_content)
                    dyn_textobj_dict[new_text.text_id] = new_text
                elif element_name == 'trigger':
                    trigger_id, new_trigger = self.create_trigger(element_content)
                    trigger_map[trigger_id] = new_trigger
                elif element_name == 'tr_tile':
                    content_list = element_content.split()
                    if len(content_list) == 6:
                        anim_number = int(content_list[-1])
                        anim_rows = uielement_list[u + 2:u + 2 + anim_number]
                        position_list = uielement_list[u + 1].split()
                        new_tr_tile = self.create_tr_tile(content_list[:5], position_list, anim_rows)
                        tr_tile_dict[new_tr_tile['trigger_id']] = new_tr_tile
                        u += (2 + anim_number)
                elif element_name == 'tile':
                    content_list = element_content.split()
                    if len(content_list) == 4:
                        position_list = uielement_list[u + 1].split()
                        new_tile = self.create_tile(content_list[:4], position_list, uielement_list[u + 2])
                        tile_list.append(new_tile)
                        u += 2
                elif element_name == 'sound':
                    element_list = element_content.split()
                    sound_list[element_list[0]] = element_list[1]
            u += 1
        uielement_dict = {
            'textobj_list': textobj_list,
            'dyn_textobj_dict': dyn_textobj_dict,
            'trigger_map': trigger_map,
            'tr_tile_dict': tr_tile_dict,
            'tile_list': tile_list,
            'sound_list': sound_list
        }
        return uielement_dict

    def create_text(self, text_content):
        if len(text_content) < 12:
            return False
        x, y, font, size, color, bg_color, h_align, v_align, max_width, max_height, timer, mov_x, mov_y, caption = text_content.split()
        x = float(x)
        y = float(y)
        font = font
        size = float(size)
        r, g, b = color.split(',')
        color = (int(r), int(g), int(b))
        r, g, b = bg_color.split(',')
        bg_color = (int(r), int(g), int(b))
        h_align = h_align
        v_align = v_align
        max_width = float(max_width)
        max_height = float(max_height)
        timer = int(timer)
        mov_x = int(mov_x)
        mov_y = int(mov_y)
        new_text = UIText(self.gameboard, 'no_id', caption, x, y, font, size, color, bg_color, h_align, v_align, max_width, max_height, timer, mov_x, mov_y)
        return new_text

    def create_dyn_text(self, text_content):
        if len(text_content) < 12:
            return False
        text_id, x, y, font, size, color, bg_color, h_align, v_align, max_width, max_height, timer, mov_x, mov_y = text_content.split()
        x = float(x)
        y = float(y)
        font = font
        size = float(size)
        r, g, b = color.split(',')
        color = (int(r), int(g), int(b))
        r, g, b = bg_color.split(',')
        bg_color = (int(r), int(g), int(b))
        h_align = h_align
        v_align = v_align
        max_width = float(max_width)
        max_height = float(max_height)
        timer = int(timer)
        mov_x = int(mov_x)
        mov_y = int(mov_y)
        new_text = UIText(self.gameboard, text_id, '', x, y, font, size, color, bg_color, h_align, v_align, max_width, max_height, timer, mov_x, mov_y)
        return new_text

    def create_trigger(self, trigger_content):
        trigger_id, rect, key_code = trigger_content.split()
        if len(trigger_content) < 3:
            return False
        top, left, bottom, right = rect.split(',')
        trigger_dict = {
            # 'trigger_id': trigger_id,
            'top': float(top),
            'left': float(left),
            'bottom': float(bottom),
            'right': float(right),
            'state': 'default',
            'key_code': int(key_code)
        }
        return trigger_id, trigger_dict

    def create_tr_tile(self, content_list, position_list, anim_rows):
        trigger_id, mirrored, flipped, width, height = content_list
        tile_dict = {
            'trigger_id': trigger_id,
            'mirrored': int(mirrored),
            'flipped': int(flipped),
            'width': float(width),
            'height': float(height),
            'positions': [],
            'animations': {}
        }
        for position in position_list:
            pos_xy = position.split(',')
            print(pos_xy)
            pos_x = float(pos_xy[0])
            pos_y = float(pos_xy[1])
            tile_dict['positions'].append([pos_x, pos_y])
        for anim_row in anim_rows:
            state, anim = anim_row.split('=')
            tile_dict['animations'][state] = self.gameboard.resources.animations[anim]
        return tile_dict

    def create_tile(self, content_list, position_list, anim_row):
        mirrored, flipped, width, height = content_list
        tile_dict = {
            'mirrored': int(mirrored),
            'flipped': int(flipped),
            'width': float(width),
            'height': float(height),
            'positions': [],
            'animation': self.gameboard.resources.animations[anim_row]
        }
        for position in position_list:
            pos_xy = position.split(',')
            print(pos_xy)
            pos_x = float(pos_xy[0])
            pos_y = float(pos_xy[1])
            tile_dict['positions'].append([pos_x, pos_y])
        return tile_dict

    def blitme(self):
        if self.mousefollow:
            self.x, self.y = self.gameboard.mouse_x + self.offset_x * self.gameboard.square_width, self.gameboard.mouse_y + self.offset_y * self.gameboard.square_height
        else:
            if self.stick_hor != -1:
                self.x = self.gameboard.sight_width * self.stick_hor + self.offset_x * self.gameboard.square_width
            if self.stick_ver != -1:
                self.y = self.gameboard.sight_height * self.stick_ver + self.offset_y * self.gameboard.square_height

        # static tiles
        for tile in self.uielement['tile_list']:
            animation = tile['animation']
            image = animation.frames[animation.frame_index]
            mirrored, flipped = False, False
            if 'mirrored' in tile:
                mirrored = tile['mirrored']  # horisontal
            if 'flipped' in tile:
                flipped = tile['flipped']  # vertical
                image = pygame.transform.flip(image, mirrored, flipped)
            rect = image.get_rect()
            for x, y in tile['positions']:
                rect.topleft = round(x * self.gameboard.square_width + self.x), round(y * self.gameboard.square_height + self.y)
                # print(rect.topleft, self.gameboard.player_char.x, self.gameboard.player_char.y)
                self.screen.blit(pygame.transform.scale(image, (
                    round(tile['width'] * self.gameboard.square_width),
                    round(tile['height'] * self.gameboard.square_height))), rect)

        # trigger tiles
        for tr_id, tr_tile in self.uielement['tr_tile_dict'].items():
            anim_state = self.uielement['trigger_map'][tr_id]['state']
            if anim_state not in tr_tile['animations']:
                anim_state = 'default'
            animation = tr_tile['animations'][anim_state]
            animation.checkme()
            image = animation.frames[animation.frame_index]

            mirrored, flipped = False, False
            if 'mirrored' in tr_tile:
                mirrored = tr_tile['mirrored']  # horisontal
            if 'flipped' in tr_tile:
                flipped = tr_tile['flipped']  # vertical
            image = pygame.transform.flip(image, mirrored, flipped)
            rect = image.get_rect()

            for x, y in tr_tile['positions']:
                rect.topleft = round(x * self.gameboard.square_width + self.x), round(y * self.gameboard.square_height + self.y)
                # print(rect.topleft, self.gameboard.player_char.x, self.gameboard.player_char.y)
                self.screen.blit(pygame.transform.scale(image, (
                    round(tr_tile['width'] * self.gameboard.square_width),
                    round(tr_tile['height'] * self.gameboard.square_height))), rect)

        for text in self.uielement['textobj_list']:
            if text.visible:
                text.blitme(self.x, self.y)
        for text in self.uielement['dyn_textobj_dict'].values():
            if text.visible:
                text.blitme(self.x, self.y)
