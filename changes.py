import argparse
import curses
import sys
import os.path
import buffer


class Change:
    def __init__(self, command, cursor, input=None):
        self.command = command
        self.cursor = cursor
        self.input = input


class Page:
    def __init__(self, start, end, index):
        self.start = start
        self.end = end
        self.index = index

        self.original_start = self.start
        self.original_end = self.end


class FileModel:
    def __init__(self, file_size):

     def insert(self, input_str, cursor):
        pass

     def delete(self, cursor):
        pass


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


class Editor:
    def __init__(self, filename):
        self.filename = filename
 
        file_size = os.path.getsize(filename)
    
        self.file = open(filename)

        self.page_size = 4096
        self.pages = [Page(0, self.page_size - 1, 0)]

        self.current_page = self.pages[0]
        
        self.buffer = buffer.Buffer()
        self.read_n_bytes(self.page_size)
        self.changes = {}

    def insert(self, input_str, cursor):
        self.changes[self.current_page.index] = Change("paste", cursor,
                                                       input_str)
        self.buffer.insert(input_str, cursor)

    def delete(self, cursor):
        self.changes[self.current_page.index] = Change("remove", cursor)
        self.buffer.delete(cursor)

    def read_n_bytes(self, n):
        text = self.filename.read(n)
        self.buffer.insert(text, )


class EditorUi:
    def __init__(self, filename):
        self.filename = filename
        self.editor = Editor(filename)
        self.cursor = Cursor(0, 0, self.editor.buffer)

    def main(self, stdscr: curses.window):

        while True:
            self.clear()
            self.handle_key(stdscr, self.cursor)
            self.print_text()

    def handle_key(self, stdscr, cursor):
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
            self.editor.delete(cursor)
            cursor.move_left(1)
        else:
            self.editor.insert(k, cursor)
            cursor.move_right(len(k))

    def print_text(self):
        pass

    def clear(self):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    editor = EditorUi(args.filename)
    curses.wrapper(editor.main)


if __name__ == "__main__":
    main()