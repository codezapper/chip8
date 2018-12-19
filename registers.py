class Registers:
    def __init__(self):
        self.V = [0] * 16
        self.I = 0 # Index
        self.S = 0 # Sound
        self.T = 0 # Timer
        self.PC = 512
        self.SP = 0
        self.STACK = [0] * 16