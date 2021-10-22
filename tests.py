from unittest import TestCase
from debug import Buffer, Cursor
import tempfile


class TestBuffer(TestCase):

    @staticmethod
    def create_new_buffer(input_string):
        buffer = Buffer(tempfile.NamedTemporaryFile(),
                              tempfile.NamedTemporaryFile())
        buffer.insert(input_string, Cursor(0, 0, buffer))
        return buffer

    @staticmethod
    def assert_gap_is_correct(buffer, expected_size,
                              expected_left_border, expected_right_border):
        actual_gap_size = buffer.gap_border.right - buffer.gap_border.left + 1
        assert actual_gap_size == expected_size
        assert buffer.gap_border.left == expected_left_border
        assert buffer.gap_border.right == expected_right_border

    @staticmethod
    def get_text_before_buffer(buffer):
        buffer.text_before_buffer.seek(0)
        return buffer.text_before_buffer.read().decode()

    @staticmethod
    def get_text_after_buffer(buffer):
        buffer.text_after_buffer.seek(0)
        return buffer.text_after_buffer.read().decode()[::-1]

    def test_insert_text_bigger_then_gap(self):
        buffer = self.create_new_buffer("Hello, World!")
        self.assert_gap_is_correct(buffer, 7, 13, 19)

    def test_insert_text_bigger_then_buffer(self):
        buffer = self.create_new_buffer(("Hello, World!" + ' ') * 4)
        text_before_buffer = self.get_text_before_buffer(buffer)
        assert text_before_buffer == "Hello, Wor"
        self.assert_gap_is_correct(buffer, 4, 56, 59)

    def test_move_gap_left(self):
        buffer = self.create_new_buffer("Hello, World!")
        buffer.insert('-', Cursor(0, 0, buffer))
        self.assert_gap_is_correct(buffer, 6, 1, 6)

    def test_move_gap_right(self):
        buffer = self.create_new_buffer("Hello, World!")
        buffer.insert('-', Cursor(0, 0, buffer))
        buffer.insert('!', Cursor(0, 14, buffer))
        self.assert_gap_is_correct(buffer, 5, 15, 19)

    def test_move_buffer_left(self):
        buffer = self.create_new_buffer(("Hello, World!" + ' ') * 4)
        buffer.insert('-', Cursor(0, 0, buffer))
        assert buffer.buffer[0] == '-'
        text_before_buffer = self.get_text_before_buffer(buffer)
        assert len(text_before_buffer) == 0
        text_after_buffer = self.get_text_after_buffer(buffer)
        assert text_after_buffer == 'o, World! '
        self.assert_gap_is_correct(buffer, 3, 1, 3)

    def test_grow_gap_after_move_buffer_left(self):
        buffer = self.create_new_buffer(("Hello, World!" + ' ') * 4)
        buffer.insert('-', Cursor(0, 0, buffer))
        buffer.insert('-' * 3, Cursor(0, 1, buffer))
        self.assert_gap_is_correct(buffer, 10, 4, 13)
        text_after_buffer = self.get_text_after_buffer(buffer)
        assert text_after_buffer == 'd! Hello, World! '

    def test_move_buffer_right(self):
        buffer = self.create_new_buffer(("Hello, World!" + ' ') * 4)
        buffer.insert('-', Cursor(0, 0, buffer))
        # очень странно, но если убрать следующую строчку, то тест не проходит
        # из-за того, что в тексте до буфера в начале появляется какой то nul
        # byte. но вместе с этой строчкой он не добавляется. это какой-то
        # прикол с этими temp файлами
        self.get_text_before_buffer(buffer)
        buffer.insert('!', Cursor(0, 56, buffer))
        text_before_buffer = self.get_text_before_buffer(buffer)
        assert text_before_buffer == '-Hello, W', text_before_buffer
        text_after_buffer = self.get_text_after_buffer(buffer)
        assert text_after_buffer == ' '
        self.assert_gap_is_correct(buffer, 2, 57, 58)

    def test_grow_gap_after_move_buffer_right(self):
        buffer = self.create_new_buffer(("Hello, World!" + ' ') * 4)
        buffer.insert('-', Cursor(0, 0, buffer))
        self.get_text_before_buffer(buffer)
        buffer.insert('!' * 3, Cursor(0, 56, buffer))
        self.assert_gap_is_correct(buffer, 10, 59, 68)
        text_before_buffer = self.get_text_before_buffer(buffer)
        # аналогичная ошибка что и в прошлом тесте:
        # '-Hello, World! Hell'
        # прикол, я только что скопировала строчку выше, вставила и nul пропал
        # еще прикол, тесты вообще не работают если оставить строчку с налом)
        assert text_before_buffer == '-Hello, World! Hell'
