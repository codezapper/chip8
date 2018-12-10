import curses
from curses import wrapper
from random import randint
import time

def check_60hz(start_time, v_delay, v_sound):
    end_time = time.time()
    if (end_time - start_time) >= (1/60):
        start_time = time.time()
        v_delay = max(v_delay - 1, 0)
        v_sound = max(v_sound - 1, 0)
    return start_time, v_delay, v_sound

registers = dict()
keyboard = {}
PC = 0

def get_lines_representation(hex_list):
    lines = []
    for n in hex_list:
        s = ''
        bit = 0x80
        while bit > 0:
            if n & bit:
                s += '*'
            else:
                s += ' '
            bit >>= 1
        lines.append(s)

    return lines

def get_char_representation(hex_list):
    s = ''
    for n in hex_list:
        bit = 0x80
        while bit > 0:
            if n & bit:
                s += '*'
            else:
                s += ' '
            bit >>= 1
        s += "\n"

    return s

def set_register_to_value(x, y, nnn, n, kk):
    global registers

    registers[x] = kk

def set_register_to_register(x, y, nnn, n, kk):
    global registers

    if n == 0:
        registers[x] = registers[y]
    if n == 1:
        registers[x] = (registers[x] | registers[y])
    if n == 2:
        registers[x] = (registers[x] & registers[y])
    if n == 3:
        registers[x] = (registers[x] ^ registers[y])
    if n == 4:
        print('SUMMING')
        registers[x] = (registers[x] + registers[y])
        if (registers[x] > 0xFF):
            registers['F'] = 1
        else:
            registers['F'] = 0
        registers[x] = registers[x] & 0xFF
    if n == 5:
        registers[x] = (registers[x] - registers[y])
        if (registers[x] > 0):
            registers['F'] = 1
        else:
            registers['F'] = 0
    if n == 6:
        if (registers[x] & 0x1):
            registers['F'] = 1
        else:
            registers['F'] = 0
        registers[x] = (registers[x] >> 1)
    if n == 7:
        registers[x] = (registers[y] - registers[x])
        if (registers[x] > 0):
            registers['F'] = 1
        else:
            registers['F'] = 0
    if n == 0xE:
        if (registers[x] & 0x10000000):
            registers['F'] = 1
        else:
            registers['F'] = 0
        registers[x] = (registers[x] << 1)

def skip_if_key(x, y, nnn, n, kk):
    global keyboard, PC

    if (kk == 0x9E):
        if (keyboard[registers[x]] == 1):
            PC += 2

    if (kk == 0xA1):
        if (keyboard[registers[x]] == 0):
            PC += 2

def gosub(x, y, nnn, n, kk):
    global PC, SP, stack

    SP += 1
    stack[SP] = PC
    PC = nnn

def setI(x, y, nnn, n, kk):
    global registers

    registers['I'] = nnn

def jump_to_location(x, y, nnn, n, kk):
    global PC

    PC = nnn

def jump_to_location_v0(x, y, nnn, n, kk):
    global PC, registers

    PC = nnn + registers[0]

def clear_or_return(x, y, nnn, n, kk):
    global PC, SP, stack

    if (kk == 0xE0):
        #Clear the display
        #print('CLEARING DISPLAY')
        pass

    if (kk == 0xEE):
        PC = stack[SP]
        SP -= 1

def skip_if_equal(x, y, nnn, n, kk):
    global registers, PC

    if (registers[x] == kk):
        PC += 2

def skip_if_not_equal(x, y, nnn, n, kk):
    global registers, PC

    if (registers[x] != kk):
        PC += 2

def skip_if_register(x, y, nnn, n, kk):
    global registers, PC

    m = main_memory[PC] << 8 | main_memory[PC + 1]
    if (registers[x] == registers[y]):
        PC += 2

def add_to_register(x, y, nnn, n, kk):
    global registers

    registers[x] += kk

def skip_if_not_register(x, y, nnn, n, kk):
    global registers, PC

    if (registers[x] == registers[y]):
        PC += 2

def set_register_to_random(x, y, nnn, n, kk):
    global registers

    registers[x] = randint(0, 255) & kk


main_memory = [0] * 4096

main_memory[0:5] = [ 0xF0, 0x90, 0x90, 0x90, 0xF0 ]
main_memory[5:10] = [ 0x20, 0x60, 0x20, 0x20, 0x70 ]
main_memory[10:15] = [ 0xF0, 0x10, 0xF0, 0x80, 0xF0 ]
main_memory[15:20] = [ 0xF0, 0x10, 0xF0, 0x10, 0xF0 ]
main_memory[20:25] = [ 0x90, 0x90, 0xF0, 0x10, 0x10 ]
main_memory[25:30] = [ 0xF0, 0x80, 0xF0, 0x10, 0xF0 ]
main_memory[30:35] = [ 0xF0, 0x80, 0xF0, 0x90, 0xF0 ]
main_memory[35:40] = [ 0xF0, 0x10, 0x20, 0x40, 0x40 ]
main_memory[40:45] = [ 0xF0, 0x90, 0xF0, 0x90, 0xF0 ]
main_memory[45:50] = [ 0xF0, 0x90, 0xF0, 0x10, 0xF0 ]
main_memory[50:55] = [ 0xF0, 0x90, 0xF0, 0x90, 0x90 ]
main_memory[55:60] = [ 0xE0, 0x90, 0xE0, 0x90, 0xE0 ]
main_memory[60:65] = [ 0xF0, 0x80, 0x80, 0x80, 0xF0 ]
main_memory[65:70] = [ 0xE0, 0x90, 0x90, 0x90, 0xE0 ]
main_memory[70:75] = [ 0xF0, 0x80, 0xF0, 0x80, 0xF0 ]
main_memory[75:80] = [ 0xF0, 0x80, 0xF0, 0x80, 0x80 ]

video_memory = [([' '] * 64) for i in range(40)]

def display_n_at_x_y(x, y, nnn, n, kk):
    global registers, main_memory, video_memory, PC, sc

    start = registers['I']
    end = start + n
    bytes_to_display = main_memory[start:end]
    start_x = registers[x]
    start_y = registers[y]
    lines = get_lines_representation(bytes_to_display)

    registers['F'] = False
    for y in range(len(lines)):
        for x in range(len(lines[y])):
            if (video_memory[start_y + y][start_x + x] == lines[y][x]) and (lines[y][x] == '*'):
                registers['F'] = True
                video_memory[start_y + y][start_x + x] = ' '
            else:
                video_memory[start_y + y][start_x + x] = lines[y][x]

    sc.clear()
    for y in range(len(video_memory)):
        s = len(video_memory[y])
        for x in range(len(video_memory[y])):
            sc.addstr(y, x, video_memory[y][x])
    sc.addstr(0, 0, str(start_x) + ' - ' + str(start_y))
    sc.refresh()
    time.sleep(0.2)

def set_timer_or_load(x, y, nnn, n, kk):
    global registers, main_memory, PC

    if (kk == 0x07):
        registers[x] = v_delay

    if (kk == 0x0A):
        registers[x] = input()

    if (kk == 0x15):
        v_delay = registers[x]


    if (kk == 0x18):
        v_sound = registers[x]

    if (kk == 0x1E):
        print('INCREMENTING: ' + str(registers[x]))
        registers['I'] += registers[x]

    if (kk == 0x29):
        print('MULTIPLYING: ' + str(registers[x]) * 5)
        registers['I'] = registers[x] * 5

    if (kk == 0x33):
        hundreds = registers[x] - (registers[x] % 100)
        tenths = registers[x] - (hundreds * 100)
        print('MAIN MEMORY:', str(main_memory[PC]), str(main_memory[PC + 1]))
        print('SPLITTING: ' + str(hundreds) , str(tenths), registers[x] % 10)
        main_memory[registers['I']] = hundreds
        main_memory[registers['I'] + 1] = tenths
        main_memory[registers['I'] + 2] = registers[x] % 10

    if (kk == 0x55):
        print('0x55')
        for i in range(0, x):
            main_memory[registers['I'] + i] = registers['{:02x}'.format(i)]

    if (kk == 0x65):
        print('0x65')
        for i in range(0, x):
            registers['{:02x}'.format(i)] = main_memory[registers['I'] + i]

operations = {
    '0': clear_or_return,
    '1': jump_to_location,
    '2': gosub,
    '3': skip_if_equal,
    '4': skip_if_not_equal,
    '5': skip_if_register,
    '6': set_register_to_value,
    '7': add_to_register,
    '8': set_register_to_register,
    '9': skip_if_not_register,
    'a': setI,
    'b': jump_to_location_v0,
    'c': set_register_to_random,
    'd': display_n_at_x_y,
    'e': skip_if_key,
    'f': set_timer_or_load
}

sc = None

def main_new(stdscr):
    global sc

    sc = stdscr
    display_n_at_x_y(0, 0, 0, 0, 0)

def main(stdscr):
    global registers, keyboard, PC, SP, stack, main_memory, sc

    sc = stdscr
    start_time = time.time()
    stack = [0] * 16
    for v_index in range(0, 16):
        registers[v_index] = 0
        keyboard[v_index] = 0

    registers['I'] = 0

    v_delay = 0
    v_sound = 0
    PC = 512
    SP = 0

    with open("/Users/gabriele/chip8/ibm.ch8", "rb") as rom:
        main_memory[PC:] = rom.read()

    running = True

    while (running):
        instruction = main_memory[PC] << 8 | main_memory[PC + 1]
        op = '{:x}'.format((instruction & 0xF000) >> 12)
        nnn = instruction & 0x0FFF
        n = instruction & 0x000F
        x = (instruction & 0x0F00) >> 8
        y = (instruction & 0x00F0) >> 4
        kk = instruction & 0x00FF
#        print(op, instruction)
        if (op in operations):
            operations[op](x, y, nnn, n, kk)
        else:
            print('***** OP NOT FOUND: ' + str(op))
        PC += 2


#    stdscr.clear()
#    while (True):
#        [start_time, v_delay, v_sound] = check_60hz(start_time, v_delay, v_sound)
#        op0 = main_memory[PC]
#        op1 = main_memory[PC + 1]
#
#        stdscr.addstr(0, 0, '{} - {}'.format(((op0 << 8) & 0xF000) | op1, op1))
#        stdscr.refresh()

wrapper(main)
#main(None)
