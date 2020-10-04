class Animation:

    def __init__(self, resources, anim_name, filename):
        # load animation file
        # set variables from file
        # get tileset object (by name from animation file) from resources and set animation_images from it
        self.resources = resources
        self.anim_name = anim_name

        self.offset_x = self.offset_y = 0
        self.squares_w = 1
        self.squares_h = 1

        animation_list = self.resources.read_file(filename)
        for a in animation_list:
            if '=' in a and a[0] != '#':
                var, val = a.split("=")
                # setting animation variables from file
                if var == 'tileset':
                    self.tileset = val
                if var == 'frames_total':
                    self.frames_total = int(val)
                if var == 'rows':
                    self.rows = int(val)
                if var == 'cols':
                    self.cols = int(val)
                if var == 'x_margin':
                    self.x_margin = int(val)
                if var == 'x_padding':
                    self.x_padding = int(val)
                if var == 'y_margin':
                    self.y_margin = int(val)
                if var == 'y_padding':
                    self.y_padding = int(val)
                if var == 'rest_time':
                    self.rest_time = int(val)
                if var == 'step':
                    self.step = int(val)
                if var == 'frame_index':
                    self.frame_index = int(val)
                if var == 'width':
                    self.width = int(val)
                if var == 'height':
                    self.height = int(val)
                if var == 'transparent':
                    self.transparent = int(val)
                if var == 'offset_x':
                    self.offset_x = int(val)
                if var == 'offset_y':
                    self.offset_y = int(val)
                if var == 'squares_w':
                    self.squares_w = int(val)
                if var == 'squares_h':
                    self.squares_h = int(val)

        self.rest_timer = self.rest_time

        self.frames = self.resources.tilesets[self.tileset].load_grid_images(self.transparent, self.width, self.height,
                                                                             self.rows, self.cols, self.x_margin,
                                                                             self.x_padding, self.y_margin,
                                                                             self.y_padding)
        self.frames_total = len(self.frames)

    def tick(self):
        if self.rest_timer > 0:
            self.rest_timer -= 1
        if self.rest_timer == 0:
            self.frame_index += self.step
            self.checkme()
            self.rest_timer = self.rest_time

    def checkme(self):
        if self.frame_index >= self.frames_total:
            self.frame_index -= self.frames_total
            self.checkme()
        if self.frame_index < 0:
            self.frame_index += self.frames_total
            self.checkme()
