
import curses
import sys
import argparse


class Window:
    def __init__(self, n_rows, n_cols):
        self.n_rows = n_rows
        self.n_cols = n_cols
        


class Buffer:
    def __init__(self, lines):
        self.text = lines
        self.buffer = [""]*50
        self.gap_size = 10
        self.gap_left = 0
        self.gap_right = self.gap_size - self.gap_left - 1
        self.size = 10 


    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        return self.text[index]


    def grow(self, k, position): 
        a = self.size*[""]

        for i in range(position, self.size): 
            a[i - position] = self.buffer[i]; 


        for i in range(k): 
            self.buffer[i + position] = ''; 
 

        for i in range(k): 

            self.buffer[position + k + i] = a[i]; 

        self.size += k; 
        self.gap_right += k; 

 

    def move_left(self, position): 

        while position < self.gap_left:
            self.gap_left-=1 
            self.gap_right-=1
            self.buffer[self.gap_right + 1] = self.buffer[self.gap_left]; 
            self.buffer[self.gap_left] = ''

    def right(self, position) :
 
      
        # // Move the gap right character by character 
        # // and the buffers 
        while (position > self.gap_left):
         
            self.gap_left+=1
            self.gap_right+=1 
            self.buffer[self.gap_left - 1] = self.buffer[self.gap_right]; 
            self.buffer[self.gap_right] = '_'; 
        

  
    def move_cursor(self, position): 
    
        if position < self.gap_left:
            self.left(position); 
        
        else:
            self.right(position)
        
    
    def insert(self, input,  position):

        inp_len = len(input) 
        i = 0; 
    
        if position != self.gap_left: 
            self.move_cursor(position) 

        while (i < inp_len): 
        
             
            if self.gap_right == self.gap_left: 
                k = 10; 
                self.grow(k, position); 
            
            self.buffer[self.gap_left] =  input[i]; 
            self.gap_left+=1 
            i+=1
            position+=1
     

     
    


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


class Cursor:
    def __init__(self, pos_y, pos_x, buffer):
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.buffer = buffer

    def move_up(self, steps):
        self.pos_y = self.pos_y - steps if self.pos_y > 0 else self.pos_y
        self.pos_x = min(self.pos_x, len(self.buffer[self.pos_y]))

    def move_down(self, steps):
        if self.pos_y == len(self.buffer) - 1:
            self.pos_x = len(self.buffer[self.pos_y])
        else:
            self.pos_y = self.pos_y + steps if self.pos_y < len(
                self.buffer) - 1 else self.pos_y
            self.pos_x = min(self.pos_x, len(self.buffer[self.pos_y]))

    def move_right(self, steps):
        if self.pos_x < len(self.buffer[self.pos_y]):
            self.pos_x += steps
        else:
            if self.pos_y < len(self.buffer) - 1:
                self.pos_y += 1
                self.pos_x = 0

    def move_left(self, steps):
        if self.pos_x > 0:
            self.pos_x -= steps
        else:
            if self.pos_y > 0:
                self.pos_y -= 1
                self.pos_x = len(self.buffer[self.pos_y])


def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        buffer = Buffer(f.read().splitlines())
    window = Window(curses.LINES - 1, curses.COLS - 1)
    cursor = Cursor(0, 0, buffer)

    while True:
        stdscr.erase()
        for y, line in enumerate(buffer[:window.n_rows]):
            stdscr.addstr(y, 0, line[:window.n_cols])
        stdscr.move(cursor.pos_y, cursor.pos_x)

        k = stdscr.getkey()
        if k == "q":
            sys.exit(0)
        elif k == "KEY_UP":
            cursor.move_up(1)
        elif k == "KEY_DOWN":
            cursor.move_down(1)
        elif k == "KEY_LEFT":
            cursor.move_left(1)
        elif k == "KEY_RIGHT":
            cursor.move_right(1)
        elif k == "KEY_BACKSPACE":
            if (cursor.pos_y, cursor.pos_x) > (0, 0):
                cursor.move_left(1)
            
        else:
            buffer[cursor.pos_y].insert(k, cursor.pos_x)
            for _ in k:
                cursor.move_right(1)


if __name__ == "__main__":
    curses.wrapper(main)
