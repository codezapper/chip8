import fonts

class Memory:
    def __init__(self):
        self.memory_size = 4096
        self._content = [0] * self.memory_size
        for i in range(0, 16):
            self._content[fonts.fonts_base()+(i * 5):fonts.fonts_base()+(i * 5)] = fonts.fonts()['{:x}'.format(i)]

    def __getitem__(self, index):
        return self._content[index]

    def __setitem__(self, index, value):
        self._content[index] = value

    # @property
    # def content(self):
    #     return self._content

    # @content.setter
    # def address(self, value):
    #     self._content[address] = value
