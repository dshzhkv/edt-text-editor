import curses
import sys
import argparse
from enum import Enum


class Window:
    def __init__(self, n_rows, n_cols):
        self.n_rows = n_rows
        self.n_cols = n_cols


class CellType(Enum):
    GAP = 1


class Buffer:
    def __init__(self):
        # self.text = lines
        self.buffer = [CellType.GAP] * 50
        self.gap_size = 10
        self.gap_left_index = 0
        self.gap_right_index = self.gap_left_index + self.gap_size - 1
        self.size = 10
        self.lines_len = dict()

    def __len__(self):
        return len(self.buffer)

    def __getitem__(self, index):
        return self.buffer[index]

    def grow(self, position):
        a = self.size * [CellType.GAP]

        for i in range(position, self.size):
            a[i - position] = self.buffer[i]

        self.buffer += self.size * [CellType.GAP]

        for i in range(self.gap_size):
            self.buffer[i + position] = CellType.GAP

        for i in range(self.size):
            self.buffer[position + self.gap_size + i] = a[i]

        self.size += self.gap_size
        self.gap_right_index += self.gap_size

    def left(self, position):
        while position < self.gap_left_index:
            self.gap_left_index -= 1
            self.gap_right_index -= 1
            self.buffer[self.gap_right_index + 1] = self.buffer[self.gap_left_index]
            self.buffer[self.gap_left_index] = CellType.GAP

    def right(self, position):
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

    def insert(self, input, position):
        inp_len = len(input)

        i = 0

        if position != self.gap_left_index:
            self.move_gap(position)

        while i < inp_len:
            if self.gap_right_index == self.gap_left_index:
                self.grow(position)

            self.buffer[self.gap_left_index] = input[i]
            self.gap_left_index += 1
            i += 1
            position += 1


class Cursor:
    def __init__(self, pos_y, pos_x, buffer):
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.buffer = buffer

    def move_right(self, steps):
        for i in range(steps):
            if self.pos_x + 1 <= self.buffer.lines_len[self.pos_y]:
                self.pos_x += 1
            else:
                if (self.pos_y + 1) in self.buffer.lines_len:
                    self.pos_x = 0
                    self.pos_y += 1

    def move_left(self, steps):
        for i in range(steps):
            if self.pos_x == 0 and self.pos_y > 0:
                self.pos_y -= 1
                self.pos_x = self.buffer.lines_len[self.pos_y]
            elif self.pos_x > 0:
                self.pos_x -= 1

def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        text = f.read()

    window = Window(curses.LINES - 1, curses.COLS - 1)
    buffer = Buffer()
    cursor = Cursor(0, 0, buffer)
    buffer.insert(text, cursor.pos_x)

    while True:
        stdscr.erase()

        pos_x = pos_y = 0

        for i in buffer.buffer:
            if i != CellType.GAP:
                if i == '\n':
                    buffer.lines_len[pos_y] = pos_x
                    pos_x = 0
                    pos_y += 1
                    continue
                stdscr.addstr(pos_y, pos_x, i)
                pos_x += 1
            if pos_x == curses.COLS:
                buffer.lines_len[pos_y] = pos_x
                pos_x = 0
                pos_y += 1

        buffer.lines_len[pos_y] = pos_x
        stdscr.move(cursor.pos_y, cursor.pos_x)

        k = stdscr.getkey()
        if k == "q":
            sys.exit(0)
        # elif k == "KEY_UP":
        #     cursor.move_up(1)
        # elif k == "KEY_DOWN":
        #     cursor.move_down(1)
        elif k == "KEY_LEFT":
            cursor.move_left(1)
        elif k == "KEY_RIGHT":
            cursor.move_right(1)
        # elif k == "KEY_BACKSPACE":
        #     if (cursor.pos_y, cursor.pos_x) > (0, 0):
        #         cursor.move_left(1)
        else:
            buffer.insert(k, cursor.pos_x)
            for _ in k:
                cursor.move_right(1)


if __name__ == "__main__":
    curses.wrapper(main)
