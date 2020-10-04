import random


class Tables:

    def __init__(self, gameboard):
        self.gameboard = gameboard

    def table_roll(self, index, tablename):
        table_list = self.gameboard.resources.read_file(self.gameboard.resources.tables[tablename])
        entry = self.find_row(index, table_list)
        return entry

    def find_row(self, index, table_list):
        for t in table_list:
            if len(t) > 0 and t[0] != '#' and ('!' in t or '>' in t):
                table_row = t.split()
                if len(table_row) >= 5 and table_row[0] == index:
                    entry = self.read_row(table_row, table_list)
                    return entry
        return False

    def read_row(self, row, table_list):
        if row[1] == '>':
            prob_total = int(row[2])
            if len(row) < 3 + prob_total * 2:
                return False
            prob_list = row[3: 3 + prob_total]
            picks_list = row[3 + prob_total:]
            pick = self.gameboard.pick_random(prob_list, picks_list)
            return self.find_row(pick, table_list)
        if row[1] == '!':
            vals_total = int(row[2])
            if len(row) < 3 + vals_total * 2:
                return False
            entry = {}
            for i in range(3, len(row), 2):
                entry[row[i]] = self.actual_value(row[i + 1])
            return entry
        return False

    def actual_value(self, value):
        try:
            a_value = int(value)
            return a_value
        except ValueError:
            if '~' in value:
                v_splitted = value.split('~')
                try:
                    min_v = int(v_splitted[0])
                    max_v = int(v_splitted[-1])
                    a_value = random.randrange(min_v, max_v + 1)
                    return a_value
                except ValueError:
                    a_value = str(value)
                    return a_value
            else:
                a_value = str(value)
                return a_value
