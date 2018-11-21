# Timers - Every 60Hz decrease register by 1
# If it the sound register, buzz unless the register is 0

#import curses
#from curses import wrapper
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

def set_register_to_value(x, y, z, b):
    global registers

    registers[x] = b

def set_register_to_register(x, y, z, b):
    global registers

    if z == 0:
        registers[x] = registers[y]
    if z == 1:
        registers[x] = (registers[x] | registers[y])
    if z == 2:
        registers[x] = (registers[x] & registers[y])
    if z == 3:
        registers[x] = (registers[x] ^ registers[y])
    if z == 4:
        registers[x] = (registers[x] + registers[y])
        if (registers[x] > 0xFF):
            registers['0xf'] = 1
        else:
            registers['0xf'] = 0
        registers[x] = registers[x] & 0xFFFFFFFF;
    if z == 5:
        registers[x] = (registers[x] - registers[y])
        if (registers[x] > 0):
            registers['0xf'] = 1
        else:
            registers['0xf'] = 0
    if z == 6:
        if (registers[x] & 0x1):
            registers['0xf'] = 1
        else:
            registers['0xf'] = 0
        registers[x] = (registers[x] >> 1)
    if z == 7:
        registers[x] = (registers[y] - registers[x])
        if (registers[x] > 0):
            registers['0xf'] = 1
        else:
            registers['0xf'] = 0
    if z == 0xE:
        if (registers[x] & 0x10000000):
            registers['0xf'] = 1
        else:
            registers['0xf'] = 0
        registers[x] = (registers[x] << 1)

def skip_if_key(x, y, z, b):
    global keyboard, PC

    if (b == 0x9E):
        if (keyboard[registers[x]] == 1):
            PC += 2

    if (b == 0xA1):
        if (keyboard[registers[x]] == 0):
            PC += 2

def gosub(x, y, z, b):
    global PC, SP, stack

    SP += 1
    stack.append(PC)
    pc = x + b

operations = {
    '0x20': gosub,
    '0x60': set_register_to_value,
    '0x80': set_register_to_register,
    '0xe0': skip_if_key
}


def main(stdscr):
    global registers, keyboard, PC, SP, stack

    start_time = time.time()
    file_memory = []
    stack = []
    for v_index in range(0, 16):
        registers[v_index] = 0
        keyboard[v_index] = 0

    v_delay = 0
    v_sound = 0
    PC = 0
    SP = 0

    with open("guess.ch8", "rb") as rom:
        file_memory = rom.read()

    running = True

    while (running):
        op = '0x{:02x}'.format((file_memory[PC] & 0xF0))
        x = file_memory[PC] & 0x0F
        y = (file_memory[PC + 1] & 0xF0) >> 4
        z = file_memory[PC + 1] & 0x0F
        b = file_memory[PC + 1]
        print(op)
        if (op in operations):
            operations[op](x, y, z, b)
        PC += 2


#    stdscr.clear()
#    while (True):
#        [start_time, v_delay, v_sound] = check_60hz(start_time, v_delay, v_sound)
#        op0 = file_memory[PC]
#        op1 = file_memory[PC + 1]
#
#        stdscr.addstr(0, 0, '{} - {}'.format(((op0 << 8) & 0xF000) | op1, op1))
#        stdscr.refresh()

#wrapper(main)
main(None)
