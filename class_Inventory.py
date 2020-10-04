from class_Item import Item


class Inventory:

    def __init__(self, character, bp_max, bank_max):
        self.equipped = {
            'ammo_slot': None,
            'main_hand': None,
            'off_hand': None,
            'head': None,
            'chest': None,
            'ring1': None,
            'ring2': None
        }
        self.mouse_hand = None  # one inventory place for dragging items with mouse
        self.backpack = []
        self.bank = []

        self.character = character
        self.tables = self.character.gameboard.tables
        self.bp_max = bp_max
        self.bank_max = bank_max

    def get_items_from_table(self, index):
        starter_pack = self.tables.table_roll(index, 'starter_table')
        for item, amount in starter_pack.items():
            item_rules = self.tables.table_roll(item, 'treasure_table')
            print(item_rules)
            for i in range(0, amount):
                new_item = Item(self.character.gameboard, item_rules, self.character.stats.char_stats['level'], 0, 0)
                self.character.gameboard.container_item_not_fit(new_item, self.backpack, self.bp_max)

        print('Inventory:\n', self.backpack)

    """def calculate_equipment_mods(self):
        for item in self.backpack:
            if 'equipped' in item.rules"""
