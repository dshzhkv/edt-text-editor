import curses
import sys
import argparse


class Window:
    def __init__(self, n_rows, n_cols):
        self.n_rows = n_rows
        self.n_cols = n_cols


class Buffer:
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]

    def insert(self, cursor, string):
        pos_x, pos_y = cursor.pos_x, cursor.pos_y
        current = self.lines.pop(pos_y)
        new = current[:pos_x] + string + current[pos_x:]
        self.lines.insert(pos_y, new)

    def delete(self, cursor):
        pos_x, pos_y = cursor.pos_x, cursor.pos_y
        if (pos_y, pos_x) < (len(self.lines), len(self.lines[pos_y])):
            current = self.lines.pop(pos_y)
            if pos_x < len(current):
                new = current[:pos_x] + current[pos_x + 1:]
            else:
                if self.lines:
                    new = current + self.lines.pop(pos_y)
                else:
                    new = current
            self.lines.insert(pos_y, new)


class Cursor:
    def __init__(self, pos_y, pos_x, buffer):
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.buffer = buffer

    def move_up(self, steps):
        self.pos_y = self.pos_y - steps if self.pos_y > 0 else self.pos_y
        self.pos_x = min(self.pos_x, len(self.buffer[self.pos_y]))

    def move_down(self, steps):
        self.pos_y = self.pos_y + steps if self.pos_y < len(
            self.buffer) - 1 else self.pos_y
        self.pos_x = min(self.pos_x, len(self.buffer[self.pos_y]))

    def move_right(self, steps):
        self.pos_x = self.pos_x + steps if self.pos_x < len(
            self.buffer[self.pos_y]) else self.pos_x

    def move_left(self, steps):
        if self.pos_x > 0:
            self.pos_x -= steps
        else:
            if self.pos_y > 0:
                self.pos_y -= steps
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
                buffer.delete(cursor)
        else:
            buffer.insert(cursor, k)
            for _ in k:
                cursor.move_right(1)


if __name__ == "__main__":
    curses.wrapper(main)
