from enum import Enum


class CellType(Enum):
    GAP = 1
    EMPTY = 2


class Buffer:
    def __init__(self):
        self.buffer_size = 50
        self.buffer = [CellType.EMPTY] * self.buffer_size
        self.gap_size = 10
        self.gap_left_index = 0
        self.gap_right_index = self.gap_left_index + self.gap_size - 1

        for i in range(self.gap_left_index, self.gap_right_index+1):
            self.buffer[i] = CellType.GAP

        self.size = 10

    def grow(self, position):
        a = self.size * [CellType.EMPTY]

        for i in range(position, self.size):
            a[i - position] = self.buffer[i]

        self.buffer += self.size * [CellType.EMPTY]

        for i in range(self.gap_size):
            self.buffer[i + position] = CellType.GAP

        for i in range(self.size):
            self.buffer[position + self.gap_size + i] = a[i]

        self.size += self.gap_size
        self.gap_right_index += self.gap_size

    def move_left(self, position): 

        while position < self.gap_left_index:
            self.gap_left_index -= 1
            self.gap_right_index -= 1
            self.buffer[self.gap_right_index + 1] = self.buffer[self.gap_left_index]
            self.buffer[self.gap_left_index] = CellType.GAP

    def move_right(self, position):

        while position > self.gap_left_index:
            self.gap_left_index += 1
            self.gap_right_index += 1
            self.buffer[self.gap_left_index - 1] = self.buffer[self.gap_right_index]
            self.buffer[self.gap_right_index] = CellType.GAP
        
    def move_gap(self, position):
        if position < self.gap_left_index:
            self.move_left(position)
        else:
            self.move_right(position)
  
    def move_cursor(self, position):
        if position < self.gap_left_index:
            self.move_left(position)
        
        else:
            self.move_right(position)
    
    def insert(self, input, cursor):
        pos_x = cursor.pos_x
        pos_y = cursor.pos_y

        # if pos_y > 0:
        #     pos_x = self.count_real_pos_x(pos_x, pos_y)

        if pos_x != self.gap_left_index:
            self.move_gap(pos_x)

        self.insert_input(input, pos_x)

    def insert_input(self, input, pos_x):
        i = 0
        while i < len(input):
            if self.gap_right_index == self.gap_left_index:
                self.grow(pos_x)

            self.buffer[self.gap_left_index] = input[i]
            self.gap_left_index += 1
            i += 1
            pos_x += 1

    def delete(self, cursor):
        pass
