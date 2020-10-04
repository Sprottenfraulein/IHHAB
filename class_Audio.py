import pygame


class Audio:

    sound_bank = {}

    def __init__(self, gameboard):
        self.gameboard = gameboard
        self.load_sounds('./res/data/audio/sounds.data')

    def load_sounds(self, filename):
        # loading list of entries in the following format:
        # <TilesetName> = <Path\Filename>
        # creating spritesheet objects for entries and saving them to dictionary self.tilesets
        sound_list = self.gameboard.resources.read_file(filename)
        for s in sound_list:
            if '=' in s and s[0] != '#':
                sound_name, sound_file = s.split("=")
                self.sound_bank[sound_name] = pygame.mixer.Sound(sound_file)
