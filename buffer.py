class CellType(Enum):
    GAP = 1
    EMPTY = 2


class Buffer:
    def __init__(self):
        self.buffer = [CellType.EMPTY]*50
        self.gap_size = 10
        self.gap_left_index = 0
        self.gap_right_index = self.gap_left_index_index + self.gap_size - 1

        for i in range(self.gap_left_index_index, self.gap_right_index+1):
            self.buffer[i] = CellType.GAP


    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        return self.text[index]


    def grow(self, k, position): 
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

    def right(self, position) :

        while position > self.gap_left_index:
            self.gap_left_index += 1
            self.gap_right_index += 1
            self.buffer[self.gap_left_index - 1] = self.buffer[self.gap_right_index]
            self.buffer[self.gap_right_index] = CellType.GAP
        
    def move_gap(self, position):
        if position < self.gap_left_index:
            self.left(position)
        else:
            self.right(position)
  
    def move_cursor(self, position): 
    
        if position < self.gap_left_index:
            self.left(position); 
        
        else:
            self.right(position)
    
    def insert(self, input, cursor):
        pos_x = cursor.pos_x
        pos_y = cursor.pos_y

        if pos_y > 0:
            pos_x = self.count_real_pos_x(pos_x, pos_y)

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
   
     

     
    


    # def insert(self, cursor, string):
    #     pos_x, pos_y = cursor.pos_x, cursor.pos_y
    #     current = self.lines.pop(pos_y)
    #     new = current[:pos_x] + string + current[pos_x:]
    #     self.lines.insert(pos_y, new)

    # def delete(self, cursor):
    #     pos_x, pos_y = cursor.pos_x, cursor.pos_y
    #     if (pos_y, pos_x) < (len(self.lines), len(self[pos_y])):
    #         current = self.lines.pop(pos_y)
    #         new = self.make_new_line(current, pos_x, pos_y)
    #         self.lines.insert(pos_y, new)

    # def make_new_line(self, current, pos_x, pos_y):
    #     if pos_x < len(current):
    #         return current[:pos_x] + current[pos_x + 1:]
    #     if self.lines:
    #         return current + self.lines.pop(pos_y)
    #     return current