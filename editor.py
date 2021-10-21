import curses
import sys
import argparse
import tempfile
from enum import Enum


class CellType(Enum):
    GAP = 1
    EMPTY = 2


class Buffer:
    def __init__(self, text_before_buffer, text_after_buffer):
        self.buffer = [CellType.EMPTY] * 50

        self.gap_size = 10
        self.gap_left_index = 0
        self.gap_right_index = self.gap_left_index + self.gap_size - 1

        for i in range(self.gap_left_index, self.gap_right_index + 1):
            self.buffer[i] = CellType.GAP

        self.buffer_left_index = 0
        self.buffer_right_index = self.buffer_left_index + 49

        self.lines_len = dict()

        self.text_before_buffer = text_before_buffer
        self.text_after_buffer = text_after_buffer

        self.size = 10
        self.shift = 0

    def __len__(self):
        return len(self.buffer)

    def __getitem__(self, index):
        return self.buffer[index - self.shift]

    def grow(self, pos_x):
        temp = self.get_elements_to_move(pos_x)

        self.grow_gap(pos_x)

        self.insert_symbols_after_gap(pos_x, temp)

        self.gap_right_index += self.gap_size

    """собираем в список temp все элементы из буфера после gap_right_index, 
    чтобы потом их поместить после новых 10 гэпов"""

    def get_elements_to_move(self, pos_x):
        temp = []
        i = pos_x - self.shift
        while i < len(self.buffer):
            if self.buffer[i] == CellType.EMPTY:
                break
            temp.append(self.buffer[i])
            i += 1
        return temp

    """Создаем новые 10 (gap_size) гэпов внутри буфера. Если нужно, отсекаем 
    от начала не влезающие символы и записываем их в левый текст"""

    def grow_gap(self, pos_x):
        gap_size_counter = 0
        # если до конца буфера осталось меньше 10 (gap_size) символов
        if pos_x > len(self.buffer) - self.gap_size:
            i = pos_x - self.shift  # индекс внутри буфера
            # есть индексация всего текста (pos_x соответствует ей)
            # от 0 до бесконечности, а есть индексация внутри буфера от 0 до 49
            # (по длине буфера)
            while i < len(self.buffer):
                self.buffer[i] = CellType.GAP
                i += 1
                gap_size_counter += 1
            for _ in range(self.gap_size - gap_size_counter):
                self.text_before_buffer.write(
                    self.buffer.pop(0).encode('utf-8'))
                self.buffer += [CellType.GAP]
                self.shift += 1
                self.buffer_left_index += 1
                self.buffer_right_index += 1
        else:
            for i in range(self.gap_size):
                self.buffer[i + pos_x - self.shift] = CellType.GAP

    """Вставляем после нового гэпа символы, которые раньше достали"""

    def insert_symbols_after_gap(self, pos_x, temp):
        j = pos_x + self.gap_size - self.shift
        while j < len(self.buffer) and temp:
            self.buffer[j] = temp.pop(0)
            j += 1
        for _ in range(len(temp)):
            if self.buffer[0] is CellType.GAP:
                self.text_after_buffer.write(temp.pop().encode('utf-8'))
            else:
                self.text_before_buffer.write(self.buffer.pop(0).encode('utf-8'))
                self.buffer.append(temp.pop(0))
                self.shift += 1
                self.buffer_left_index += 1
                self.buffer_right_index += 1

    def move_gap_left(self, pos_x):
        while pos_x < self.gap_left_index:
            self.gap_left_index -= 1
            self.gap_right_index -= 1
            self.buffer[self.gap_right_index + 1 - self.shift] = self.buffer[
                self.gap_left_index - self.shift]
            self.buffer[self.gap_left_index - self.shift] = CellType.GAP

    def move_gap_right(self, pos_x):
        while pos_x > self.gap_left_index:
            self.gap_left_index += 1
            self.gap_right_index += 1
            self.buffer[self.gap_left_index - 1 - self.shift] = self.buffer[
                self.gap_right_index - self.shift]
            self.buffer[self.gap_right_index - self.shift] = CellType.GAP

    def move_buffer_left(self, pos_x):
        self.move_gap_left(self.buffer_left_index)
        while pos_x < self.gap_left_index:
            # записываем последний символ в правый файл
            self.text_after_buffer.write(self.buffer.pop(-1).encode('utf-8'))

            # сдвигаем gap
            self.gap_left_index -= 1
            self.gap_right_index -= 1

            # сдвигаем буфер
            self.shift -= 1
            self.buffer_left_index -= 1
            self.buffer_right_index -= 1

            # записываем в буфер после gap последний символ из левого файла
            self.text_before_buffer.seek(0)
            self.buffer[self.gap_right_index - self.shift] = \
                self.text_before_buffer.read().decode()[-1]
            # убираем последний символ из левого файла
            size = self.text_before_buffer.tell()
            self.text_before_buffer.truncate(size - 1)

            # добавляем к буферу в начало gap
            self.buffer.insert(0, CellType.GAP)

    def move_buffer_right(self, pos_x):
        self.move_gap_right(self.buffer_right_index - (self.gap_right_index -
                                                       self.gap_left_index))
        while pos_x > self.gap_left_index:
            # записываем первый символ в левый файл
            self.text_before_buffer.write(self.buffer.pop(0).encode('utf-8'))

            # записываем в буфер после gap последний символ из левого файла
            self.text_after_buffer.seek(0)
            self.buffer[self.gap_left_index - 1 - self.shift] = \
                self.text_after_buffer.read().decode()[-1]
            # убираем последний символ из левого файла
            size = self.text_after_buffer.tell()
            self.text_after_buffer.truncate(size - 1)

            # добавляем к буферу в начало gap
            self.buffer.append(CellType.GAP)

            # сдвигаем gap
            self.gap_left_index += 1
            self.gap_right_index += 1

            # сдвигаем буфер
            self.shift += 1
            self.buffer_left_index += 1
            self.buffer_right_index += 1

    def move_gap(self, pos_x):
        if pos_x < self.buffer_left_index:
            self.move_buffer_left(pos_x)
        elif pos_x > self.buffer_right_index:
            self.move_buffer_right(pos_x)
        elif pos_x < self.gap_left_index:
            self.move_gap_left(pos_x)
        else:
            self.move_gap_right(pos_x)

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

            self.buffer[self.gap_left_index - self.shift] = input[i]
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
        self.buffer[self.gap_left_index - self.shift] = CellType.GAP

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
            if self.pos_x + 1 < curses.COLS and self.pos_x < \
                    self.buffer.lines_len[self.pos_y] - 1:
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

    buffer = Buffer(tempfile.TemporaryFile(), tempfile.TemporaryFile())
    cursor = Cursor(0, 0, buffer)
    buffer.insert(text, cursor)

    while True:
        print_text(stdscr, buffer)

        stdscr.move(cursor.pos_y, cursor.pos_x)

        process_key(stdscr, buffer, cursor)


def print_text(stdscr, buffer):
    stdscr.erase()

    pos_x = pos_y = 0

    buffer.text_before_buffer.seek(0)
    text_before_buffer = buffer.text_before_buffer.read().decode()
    for char in text_before_buffer:
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

    for char in buffer.buffer:
        if char != CellType.GAP and char != CellType.EMPTY:
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

    buffer.text_after_buffer.seek(0)
    text_after_buffer = buffer.text_after_buffer.read().decode()[::-1]
    for char in text_after_buffer:
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