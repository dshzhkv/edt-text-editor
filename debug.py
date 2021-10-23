from enum import Enum
import tempfile


class CellType(Enum):
    GAP = 1
    EMPTY = 2


class Direction(Enum):
    Left = -1
    Right = 1


class Border:
    def __init__(self, left_index, right_index):
        self.left = left_index
        self.right = right_index

    def move(self, steps):
        self.left += steps
        self.right += steps


class Buffer:
    def __init__(self, text_before_buffer, text_after_buffer, window_width):
        self.buffer_size = 50
        self.buffer_border = Border(0, self.buffer_size - 1)

        self.gap_size = 10
        self.gap_border = Border(0, self.gap_size - 1)

        self.buffer = [CellType.GAP] * self.gap_size + \
                      [CellType.EMPTY] * (self.buffer_size - self.gap_size)

        self.lines_len = dict()
        self.lines_with_line_breaks = []

        self.text_before_buffer = text_before_buffer
        self.text_after_buffer = text_after_buffer

        self.shift = 0

        self.window_width = window_width

    def __len__(self):
        return len(self.buffer)

    def __getitem__(self, index):
        return self.buffer[index - self.shift]

    def grow(self, pos_x):
        temp = self.get_elements_to_move(pos_x)

        self.grow_gap(pos_x)

        self.insert_symbols_after_gap(pos_x, temp)

        self.gap_border.right += self.gap_size

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
                self.buffer_border.move(1)
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
                self.text_after_buffer.write(temp.pop(-1).encode('utf-8'))
            else:
                self.text_before_buffer.write(
                    self.buffer.pop(0).encode('utf-8'))
                self.buffer.append(temp.pop(0))
                self.shift += 1
                self.buffer_border.move(1)

    def move_gap(self, pos_x, direction):
        while pos_x != self.gap_border.left:
            self.gap_border.move(direction.value)
            if direction is Direction.Left:
                i = self.gap_border.right + 1 - self.shift
                g = self.gap_border.left - self.shift
            else:
                i = self.gap_border.left - 1 - self.shift
                g = self.gap_border.right - self.shift
            self.buffer[i], self.buffer[g] = self.buffer[g], CellType.GAP

    def move_buffer_left(self, pos_x):
        self.move_gap(self.buffer_border.left, Direction.Left)
        while pos_x < self.gap_border.left:
            # записываем последний символ в правый файл
            self.text_after_buffer.write(self.buffer.pop(-1).encode('utf-8'))

            # сдвигаем gap
            self.gap_border.move(-1)

            # сдвигаем буфер
            self.shift -= 1
            self.buffer_border.move(-1)

            # записываем в буфер после gap последний символ из левого файла
            self.text_before_buffer.seek(0)
            self.buffer[self.gap_border.right - self.shift] = \
                self.text_before_buffer.read().decode()[-1]
            # убираем последний символ из левого файла
            size = self.text_before_buffer.tell()
            self.text_before_buffer.truncate(size - 1)

            # добавляем к буферу в начало gap
            self.buffer.insert(0, CellType.GAP)

    def move_buffer_right(self, pos_x):
        self.move_gap(self.buffer_border.right - (self.gap_border.right -
                                                  self.gap_border.left),
                      Direction.Right)
        while pos_x > self.gap_border.left:
            # записываем первый символ в левый файл
            self.text_before_buffer.write(self.buffer.pop(0).encode('utf-8'))

            # записываем в буфер после gap последний символ из левого файла
            self.text_after_buffer.seek(0)
            self.buffer[self.gap_border.left - 1 - self.shift] = \
                self.text_after_buffer.read().decode()[-1]
            # убираем последний символ из левого файла
            size = self.text_after_buffer.tell()
            self.text_after_buffer.truncate(size - 1)

            # добавляем к буферу в начало gap
            self.buffer.append(CellType.GAP)

            # сдвигаем gap
            self.gap_border.move(1)

            # сдвигаем буфер
            self.shift += 1
            self.buffer_border.move(1)

    def move_to_cursor(self, pos_x):
        if pos_x < self.buffer_border.left:
            self.move_buffer_left(pos_x)
        elif pos_x > self.buffer_border.right:
            self.move_buffer_right(pos_x)
        elif pos_x < self.gap_border.left:
            self.move_gap(pos_x, Direction.Left)
        else:
            self.move_gap(pos_x, Direction.Right)

    def insert(self, input_string, cursor):
        pos_x = cursor.pos_x
        pos_y = cursor.pos_y

        if pos_y > 0:
            pos_x = self.count_real_pos_x(pos_x, pos_y)

        if pos_x != self.gap_border.left:
            self.move_to_cursor(pos_x)

        self.insert_input(input_string, pos_x, pos_y)

    def insert_input(self, input_string, pos_x, pos_y):
        for char in input_string:
            if self.gap_border.left == self.gap_border.right:
                self.grow(pos_x)

            self.buffer[self.gap_border.left - self.shift] = char

            if char == '\n' or pos_x == self.window_width - 1:
                self.lines_with_line_breaks.append(pos_y)
                pos_y += 1
                pos_x = 0
            else:
                pos_x += 1
                if pos_y not in self.lines_len.keys():
                    self.lines_len[pos_y] = 1
                else:
                    self.lines_len[pos_y] += 1

            self.gap_border.left += 1

    def delete(self, cursor):
        pos_x = cursor.pos_x
        pos_y = cursor.pos_y

        if pos_y > 0:
            pos_x = self.count_real_pos_x(pos_x, pos_y)

        if pos_x != self.gap_border.left:
            self.move_to_cursor(pos_x)

        self.buffer[pos_x - 1 - self.shift] = CellType.GAP
        self.gap_border.left -= 1
        self.lines_len[pos_y] -= 1

        if self.lines_len[pos_y] == 0 and pos_y + 1 in self.lines_len.keys():
            self.lines_len[pos_y] = self.lines_len[pos_y + 1]
            self.lines_len[pos_y + 1] = 0

    def count_real_pos_x(self, pos_x, pos_y):
        for k, v in self.lines_len.items():
            if k < pos_y:
                pos_x += v
                if k in self.lines_with_line_breaks:
                    pos_x += 1
        return pos_x


class Cursor:
    def __init__(self, pos_y, pos_x, buffer):
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.buffer = buffer


def main():
    buffer = Buffer(tempfile.NamedTemporaryFile(), tempfile.NamedTemporaryFile(), 120)
    with open("1.txt") as file:
        text = file.read()

    buffer.insert(text, Cursor(0, 0, buffer))

    for i in range(4, -1, -1):
        buffer.delete(Cursor(1, i, buffer))
    for i in range(13, -1, -1):
        buffer.delete(Cursor(0, i, buffer))

    print_text(buffer)


def print_text(buffer):
    result = ''

    buffer.text_before_buffer.seek(0)
    text_before_buffer = buffer.text_before_buffer.read().decode()
    for char in text_before_buffer:
        result += char
    for char in buffer.buffer:
        if char == CellType.GAP:
            result += 'G'
        elif char == CellType.EMPTY:
            result += '_'
        else:
            result += char
    buffer.text_after_buffer.seek(0)
    text_after_buffer = buffer.text_after_buffer.read().decode()[::-1]
    for char in text_after_buffer:
        result += char
    print(result)


if __name__ == "__main__":
    main()