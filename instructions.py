class Instruction:
    def __init__(self, bytes):
        self.instruction = bytes[0] << 8 | bytes[1]
        self.op = '{:x}'.format((self.instruction & 0xF000) >> 12)
        self.nnn = self.instruction & 0x0FFF
        self.n = self.instruction & 0x000F
        self.x = (self.instruction & 0x0F00) >> 8
        self.y = (self.instruction & 0x00F0) >> 4
        self.kk = self.instruction & 0x00FF
        # print(self.op, self.nnn, self.n, self.x, self.y, self.kk)
        # print(self.op)
