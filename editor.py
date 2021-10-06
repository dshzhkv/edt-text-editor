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

    def insert(self, input, cursor):
        pos_x = cursor.pos_x
        pos_y = cursor.pos_y

        if pos_y > 0:
            pos_x = self.count_real_pos_x(pos_x, pos_y)

        if pos_x != self.gap_left_index:
            self.move_gap(pos_x)

        self.insert_input(input, pos_x)

        self.update_lines_len(len(input), pos_y)

    def insert_input(self, input, pos_x):
        i = 0
        while i < len(input):
            if self.gap_right_index == self.gap_left_index:
                self.grow(pos_x)

            self.buffer[self.gap_left_index] = input[i]
            self.gap_left_index += 1
            i += 1
            pos_x += 1

    def update_lines_len(self, input_len, pos_y):
        if pos_y in self.lines_len:
            if self.lines_len[pos_y] == curses.COLS:
                self.lines_len[pos_y + 1] = 0
            self.lines_len[pos_y] = self.lines_len[pos_y] + input_len
        else:
            self.lines_len[pos_y] = input_len

    def delete(self, cursor):
        pos_x = cursor.pos_x
        pos_y = cursor.pos_y

        if pos_y > 0:
            pos_x = self.count_real_pos_x(pos_x, pos_y)

        if pos_x + 1 != self.gap_left_index:
            self.move_gap(pos_x + 1)

        self.gap_left_index -= 1
        self.buffer[self.gap_left_index] = CellType.GAP

    def count_real_pos_x(self, pos_x, pos_y):
        for k, v in self.lines_len.items():
            if k < pos_y:
                pos_x += v
        return pos_x


class Cursor:
    def __init__(self, pos_y, pos_x, buffer):
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.buffer = buffer

    def move_right(self, steps):
        for i in range(steps):
            if self.pos_x + 1 < curses.COLS and self.pos_x < self.buffer.lines_len[self.pos_y] - 1:
                self.pos_x += 1
            else:
                if (self.pos_y + 1) in self.buffer.lines_len:
                    self.pos_x = 0
                    self.pos_y += 1

    def move_left(self, steps):
        for i in range(steps):
            if self.pos_x == 0 and self.pos_y > 0:
                self.pos_y -= 1
                self.pos_x = self.buffer.lines_len[self.pos_y] - 1
            elif self.pos_x > 0:
                self.pos_x -= 1

    def move_up(self, steps):
        for i in range(steps):
            if self.pos_y > 0:
                if self.pos_x < self.buffer.lines_len[self.pos_y - 1]:
                    self.pos_y -= 1
                else:
                    self.pos_x = self.buffer.lines_len[self.pos_y - 1]
                    self.pos_y -= 1

    def move_down(self, steps):
        for i in range(steps):
            if self.pos_y + 1 in self.buffer.lines_len:
                if self.pos_x < self.buffer.lines_len[self.pos_y + 1]:
                    self.pos_y += 1
                else:
                    self.pos_x = self.buffer.lines_len[self.pos_y + 1]
                    self.pos_y += 1
            else:
                self.pos_x = self.buffer.lines_len[self.pos_y]


def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        text = f.read()

    window = Window(curses.LINES - 1, curses.COLS - 1)
    buffer = Buffer()
    cursor = Cursor(0, 0, buffer)
    buffer.insert(text, cursor)

    while True:
        print_text(stdscr, buffer)

        stdscr.move(cursor.pos_y, cursor.pos_x)

        process_key(stdscr, buffer, cursor)


def print_text(stdscr, buffer):
    stdscr.erase()

    pos_x = pos_y = 0

    for char in buffer.buffer:
        if char != CellType.GAP:
            stdscr.addstr(pos_y, pos_x, char)
            if char == '\n':
                buffer.lines_len[pos_y] = pos_x + 1
                pos_x = 0
                pos_y += 1
                buffer.lines_len[pos_y] = pos_x
                continue
            if pos_x == curses.COLS - 1:
                stdscr.addstr(pos_y, pos_x, char)
                buffer.lines_len[pos_y] = pos_x + 1
                pos_x = 0
                pos_y += 1
            else:
                stdscr.addstr(pos_y, pos_x, char)
                pos_x += 1
                buffer.lines_len[pos_y] = pos_x

        stdscr.addstr(8 + pos_y, 0, str(buffer.lines_len[pos_y]))


def process_key(stdscr, buffer, cursor):
    k = stdscr.getkey()
    if k == "q":
        sys.exit(0)
    elif k == "KEY_LEFT":
        cursor.move_left(1)
    elif k == "KEY_RIGHT":
        cursor.move_right(1)
    elif k == "KEY_UP":
        cursor.move_up(1)
    elif k == "KEY_DOWN":
        cursor.move_down(1)
    elif k == "KEY_BACKSPACE":
        buffer.delete(cursor)
        cursor.move_left(1)
    else:
        buffer.insert(k, cursor)
        cursor.move_right(len(k))


if __name__ == "__main__":
    curses.wrapper(main)
