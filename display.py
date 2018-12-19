import fonts
import time
import curses
from random import randint

MAX_X_COORDINATE = 64 + 1
MAX_Y_COORDINATE = 32 + 1

class Display:
    def __init__(self):
        self.init_display()

    def init_display(self):
        self.display = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.display.keypad(True)
        self.clear()

    def restore_display(self):
        curses.nocbreak()
        self.display.keypad(False)
        curses.echo()
        curses.endwin()

    def get_lines_representation(self, hex_list):
        lines = []
        for n in hex_list:
            s = ''
            bit = 0x80
            while bit > 0:
                if n & bit:
                    s += '#'
                else:
                    s += ' '
                bit >>= 1
            lines.append(s)

        return lines

    def set_pixel(self, x, y, c):
        x = x % MAX_X_COORDINATE
        y = y % MAX_Y_COORDINATE
        if (self.video_memory[y][x] == '#') and (c == '#'):
            self.video_memory[y][x] = ' '
            self.display.addstr(y, x, self.video_memory[y][x])
        else:
            self.video_memory[y][x] = c
            self.display.addstr(y, x, self.video_memory[y][x])
            return True
        return False

    def clear(self):
        self.video_memory = [([' '] * MAX_X_COORDINATE) for i in range(MAX_Y_COORDINATE)]
        self.refresh()

    def refresh(self):
        for y in range(MAX_Y_COORDINATE):
            for x in range(MAX_X_COORDINATE):
                self.display.addstr(y, x, self.video_memory[y][x])
        self.display.refresh()

    def set_lines(self, lines, start_x, start_y):
        y = start_y
        cleared_pixel = False
        for line in lines:
            x = start_x
            for b in line:
                if (self.set_pixel(x, y, b)):
                    cleared_pixel = True
                x += 1
            y += 1
        # self.refresh()
        self.display.refresh()
        return cleared_pixel

    def draw_font(self, start_x, start_y, c):
        lines = self.get_lines_representation(fonts.fonts()[c])
        return self.set_lines(lines, start_x, start_y)

    def draw_from_memory(self, start_x, start_y, main_memory, start_index, end_index):
        lines = self.get_lines_representation(main_memory[start_index:end_index])
        return self.set_lines(lines, start_x, start_y)

    def getch(self):
        return self.display.getch()
