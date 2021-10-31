import argparse
import curses
import sys
import os.path


class Change:
    def __init__(self, command, index, input=None):
        self.command = command
        self.index = index
        self.input = input


class Cursor:
    def __init__(self, pos_y, pos_x):
        self.pos_y = pos_y
        self.pos_x = pos_x


class Page:
    def __init__(self, start, end, index):
        self.start = start
        self.end = end
        self.index = index

        self.original_start = self.start
        self.original_end = self.end


class FileModel:
    def __init__(self, file_size):
        self.file_regions = [Page(0, file_size - 1, 0)]

    def insert(self, input_str, cursor):
        pass

    def delete(self, cursor):
        pass


class Buffer:
    def __init__(self, model, file):
        self.model = model
        self.file = file
        self.buffer = []


class Editor:
    def __init__(self, filename):
        self.filename = filename

        file_size = os.path.getsize(filename)
        self.model = FileModel(file_size)

        self.file = open(filename, 'r')
        self.buffer = Buffer(self.model, self.file)

        self.chunk_size = 1024

    def insert(self, input_str, cursor):
        self.model.insert(input_str, cursor)

    def delete(self, cursor):
        self.model.delete(cursor)


class EditorUi:
    def __init__(self, filename):
        self.filename = filename
        self.cursor = Cursor(0, 0)
        self.editor = Editor(filename)

    def main(self, stdscr: curses.window):
        while True:
            self.print_text()
            self.process_key(stdscr, self.cursor)

    @staticmethod
    def process_key(stdscr, cursor):
        pass

    def print_text(self):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    editor = EditorUi(args.filename)
    curses.wrapper(editor.main)


if __name__ == "__main__":
    main()