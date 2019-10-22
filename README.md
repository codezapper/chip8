# chip8
Python Chip8 interpreter for text terminal

This will run most Chip8 roms on a UNIX-like terminal (Linux or OS X).

It runs on Python 3 and depends on curses for Python.

To use, change to the directory and run:

`./main.py <rom_file>`

A terminal with size of at least 32x32 character is needed.

Input is 1 to 1, meaning that keypad keys 0 to 9 are emulated as keys 0 to 9 and keypad keys A to F are emulated as keys a to f on the keyboard.

No sound yet.

![Space Invaders Screenshot](/space_invaders.png?raw=true "Space Invaders")
