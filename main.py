import display
import fonts
import memory
import registers
import instructions
import threading
import sys

import os
import time
from random import randint


def check_60hz():
    cpu_reg.T = max(cpu_reg.T - 1, 0)
    cpu_reg.S = max(cpu_reg.S - 1, 0)
    threading.Timer(0.17, check_60hz).start()

def display_n_at_x_y(codes):
    #OPCODE 'd'
    if (not display.draw_from_memory(cpu_reg.V[codes.x], cpu_reg.V[codes.y], main_memory, cpu_reg.I, cpu_reg.I + codes.n)):
        cpu_reg[0xF] = 0
    cpu_reg.PC += 2

def set_register_to_value(codes):
    #OPCODE '6'
    cpu_reg.V[codes.x] = codes.kk
    cpu_reg.PC += 2

def jump_to_location(codes):
    #OPCODE '1'
    cpu_reg.PC = codes.nnn

def jump_to_location_v0(codes):
    #OPCODE 'b'
    cpu_reg.PC = codes.nnn + cpu_reg.V[0]

def set_register_to_random(codes):
    #OPCODE 'c'
    cpu_reg.V[codes.x] = randint(0, 255) & codes.kk
    cpu_reg.PC += 2

def setI(codes):
    #OPCODE 'a'
    cpu_reg.I = codes.nnn
    cpu_reg.PC += 2


def skip_if_equal(codes):
    #OPCODE '3'
    cpu_reg.PC += 2
    if (cpu_reg.V[codes.x] == codes.kk):
        cpu_reg.PC += 2


def skip_if_not_equal(codes):
    #OPCODE '4'
    cpu_reg.PC += 2
    if (cpu_reg.V[codes.x] != codes.kk):
        cpu_reg.PC += 2


def skip_if_register(codes):
    #OPCODE '5'
    cpu_reg.PC += 2
    if (cpu_reg.V[codes.x] == cpu_reg.V[codes.y]):
        cpu_reg.PC += 2


def skip_if_not_register(codes):
    #OPCODE '5'
    cpu_reg.PC += 2
    if (cpu_reg.V[codes.x] != cpu_reg.V[codes.y]):
        cpu_reg.PC += 2


def add_to_register(codes):
    #OPCODE '7'
    cpu_reg.V[codes.x] += codes.kk
    cpu_reg.V[codes.x] %= 256
    cpu_reg.PC += 2

def gosub(codes):
    #OPCODE '2'
    cpu_reg.STACK[cpu_reg.SP] = cpu_reg.PC
    cpu_reg.SP += 1
    cpu_reg.PC = codes.nnn


def clear_or_return(codes):
    #OPCODE '0'
    if (codes.kk == 0xE0):
        display.clear()
        cpu_reg.PC += 2
    elif (codes.kk == 0xEE):
        cpu_reg.SP -= 1
        cpu_reg.PC = cpu_reg.STACK[cpu_reg.SP] + 2
    else:
        cpu_reg.PC += 2


def set_register_to_register(codes):
    #OPCODE '8'

    cpu_reg.PC += 2
    if (codes.n == 0x0):
        cpu_reg.V[codes.x] = cpu_reg.V[codes.y]

    if (codes.n == 0x1):
        cpu_reg.V[codes.x] = cpu_reg.V[codes.x] | cpu_reg.V[codes.y]

    if (codes.n == 0x2):
        cpu_reg.V[codes.x] = cpu_reg.V[codes.x] & cpu_reg.V[codes.y]

    if (codes.n == 0x3):
        cpu_reg.V[codes.x] = cpu_reg.V[codes.x] ^ cpu_reg.V[codes.y]

    if (codes.n == 0x4):
        cpu_reg.V[codes.x] += cpu_reg.V[codes.y]
        if (cpu_reg.V[codes.x] >= 256):
            cpu_reg.V[0xF] = 1
        else:
            cpu_reg.V[0xF] = 0
        cpu_reg.V[codes.x] %= 256

    if (codes.n == 0x5):
        cpu_reg.V[codes.x] -= cpu_reg.V[codes.y]
        if (cpu_reg.V[codes.x] < 0):
            cpu_reg.V[0xF] = 0
            cpu_reg.V[codes.x] += 256
        else:
            cpu_reg.V[0xF] = 1

    if (codes.n == 0x6):
        cpu_reg.V[0xF] = cpu_reg.V[codes.x] & 0x1
        cpu_reg.V[codes.y] = cpu_reg.V[codes.y] >> 1
        cpu_reg.V[codes.x] = cpu_reg.V[codes.y]

    if (codes.n == 0x7):
        cpu_reg.V[codes.x] = cpu_reg.V[codes.y] - cpu_reg.V[codes.x]
        if (cpu_reg.V[codes.x] < 0):
            cpu_reg.V[0xF] = 0
        else:
            cpu_reg.V[0xF] = 1

    if (codes.n == 0xE):
        cpu_reg.V[0xF] = (cpu_reg.V[codes.x] >> 7) & 0x1
        cpu_reg.V[codes.y] = cpu_reg.V[codes.y] << 1
        cpu_reg.V[codes.y] %= 256
        cpu_reg.V[codes.x] = cpu_reg.V[codes.y]


def set_timer_or_load(codes):
    #OPCODE 'f'

    cpu_reg.PC += 2
    if (codes.kk == 0x7):
        cpu_reg.V[codes.x] = cpu_reg.T

    if (codes.kk == 0x15):
        cpu_reg.T = cpu_reg.V[codes.x]

    if (codes.kk == 0x18):
        cpu_reg.S = cpu_reg.V[codes.x]

    if (codes.kk == 0x0A):
        c = display.getch()
        if (c >= 48) and (c <= 57):
            cpu_reg.V[codes.x] = c - 48
        elif (c >= 97) and (c <= 102):
            cpu_reg.V[codes.x] = c - 51

    if (codes.kk == 0x1E):
        cpu_reg.I += cpu_reg.V[codes.x]
        cpu_reg.I = cpu_reg.I % 0xFFF

    if (codes.kk == 0x29):
        cpu_reg.I = fonts.fonts_base() + (cpu_reg.V[codes.x] * 5)

    if (codes.kk == 0x33):
        hundreds = int((cpu_reg.V[codes.x] % 1000) / 100)
        tenths = int((cpu_reg.V[codes.x] % 100) / 10)
        units = cpu_reg.V[codes.x] % 10
        main_memory[cpu_reg.I] = hundreds
        main_memory[cpu_reg.I + 1] = tenths
        main_memory[cpu_reg.I + 2] = units

    if (codes.kk == 0x55):
        for i in range(0, codes.x + 1):
            main_memory[cpu_reg.I + i] = cpu_reg.V[i]
        # cpu_reg.I += codes.x + 1

    if (codes.kk == 0x65):
        for i in range(0, codes.x + 1):
            cpu_reg.V[i] = main_memory[cpu_reg.I + i]
        # cpu_reg.I += codes.x + 1

display = display.Display()
main_memory = memory.Memory()
cpu_reg = registers.Registers()

if (len(sys.argv) < 2):
    print('Usage: ' + sys.argv[0] + ' rom_file')
    sys.exit(1)

try:
    end = cpu_reg.PC + os.path.getsize(sys.argv[1])
except FileNotFoundError:
    print('File ' + sys.argv[1] + ' not found')
    sys.exit(1)

with open(sys.argv[1], "rb") as rom:
    main_memory[cpu_reg.PC:end] = rom.read()

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
    # 'e': skip_if_key,
    'f': set_timer_or_load
}

check_60hz()
running = True
while (running):
    if (cpu_reg.PC >= main_memory.memory_size - 1):
        running = False
    else:
        codes = instructions.Instruction([main_memory[cpu_reg.PC], main_memory[cpu_reg.PC + 1]])
        if (codes.op in operations):
            operations[codes.op](codes)
        # else:
        #     print('***** OP NOT FOUND: ' + str(codes.op))
