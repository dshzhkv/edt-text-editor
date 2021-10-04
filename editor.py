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
    def __init__(self, cursor):
        # self.text = lines
        self.buffer = [CellType.GAP] * 50
        self.gap_size = 10
        self.cursor = cursor
        self.gap_left_index = self.cursor.pos_x
        self.gap_right_index = self.gap_left_index + self.gap_size - 1
        self.size = 10

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
    def __init__(self, pos_y, pos_x):
        self.pos_y = pos_y
        self.pos_x = pos_x

    def move_right(self, steps):
        self.pos_x += steps

    def move_left(self, steps):
        self.pos_x -= steps


def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        text = f.read()

    window = Window(curses.LINES - 1, curses.COLS - 1)
    cursor = Cursor(0, 0)
    buffer = Buffer(cursor)
    buffer.insert(text, cursor.pos_x)

    while True:
        stdscr.erase()

        pos_x = pos_y = 0

        for i in buffer.buffer:
            if i != CellType.GAP:
                stdscr.addstr(pos_y, pos_x, i)
                pos_x += 1

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
