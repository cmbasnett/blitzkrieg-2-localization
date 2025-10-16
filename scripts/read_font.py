from ctypes import Structure, c_uint8, c_uint16, c_int32, c_uint32, sizeof
import struct

class Character(Structure):
    _fields_ = [
        ('unknown1', c_uint8),
        ('unknown2', c_uint8),
        ('unicode', c_uint16),
    ]

    def __repr__(self):
        return chr(self.unicode)



class Glyph(Structure):
    _pack_ = 1
    _fields_ = [
        ('unknown1', c_uint8), # always 2
        ('unknown2', c_uint8), # always 56 ???
        ('x_start', c_uint32),
        ('y_start', c_uint32),
        ('x_end', c_uint32),
        ('y_end', c_uint32),
        ('baseline', c_int32),
        ('width', c_int32),
        ('x_advance', c_int32),
    ]

    def __repr__(self):
        data = {
            'x_start': self.x_start,
            'y_start': self.y_start,
            'x_end': self.x_end,
            'y_end': self.y_end,
            'baseline': self.baseline,
            'width': self.width, # maybe this is actually *width*?
            'x_advance': self.x_advance,
        }
        return str(data)

    @property
    def width(self):
        return self.x_end - self.x_start

    @property
    def height(self):
        return self.y_end - self.y_start

def unpack(fmt, buffer, offset):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, buffer[offset:offset+size])


def dumptxtbin(binary_path: str):
    with open(binary_path, 'rb') as f:
        buffer = f.read()
        size_offset = 0x54

        # TODO: read the header into bytes
        # header = list(buffer[0:size_offset])
        #0x34

        # TODO: there seems to be an incrementing number every 6 bytes. maybe this is some sort of serialization schema?

        font_size_offset = 0x30
        characters_offset = 0x5e

        s = '['
        for byte in buffer[0:characters_offset]:
            s += str(byte).rjust(3) + '・'
        print(s)

        font_size = unpack('I', buffer, font_size_offset)[0]
        character_count = struct.unpack('I', buffer[size_offset:size_offset+4])[0]

        unknown_offset1 = 0x3c
        unknown_offset2 = 0x42

        unknown1 = unpack('I', buffer, unknown_offset1)[0]
        unknown2 = unpack('I', buffer, unknown_offset2)[0]

        # things that might be in here:
        # * row count
        # * fallback character index
        # * texture size
        # * channel count?
        # * fontgen version? try different versions and see if the header differs at all. the JP ones seem to differ dramatically for some reason.

        # [4, 8]
        # [4, 0, 0, 0] # maybe a version or perhaps channel count for the texture
        # [1, 12, 1, 8]
        # # u4 (most are [160/192, 251/252, 66/174, 17/1]); the JP one is an outlier.
        # [0, 18, 12, 17, 50, 2]
        # # u4 (again, most are [160/192/0, 251/252, 66/174]); JP 0 and 174 are outliers
        # [1, 2]
        # # u2
        # [0, 0, 1]
        # # u2
        # [0, 0, 0, 8]
        # # u4
        # [1]
        # # u4 [always ends in 00 00]
        # # seems like these are incrementing (10..15), followed by a number which corresponds to half the size of the proceeding value? very odd.
        # [10, 8]
        # # u4
        # [11, 8]
        # # u4
        # [12, 8]
        # # u4
        # [13, 8]
        # # u4
        # [14, 2]
        # # u1
        # [15, 4]
        # # u2
        # [1]
        # # u4
        # [3, 8]
        # # CHARACTER COUNT u4
        # [4, 8]
        # # u4 (always [133, 1, 0, 0]) (389)? maybe a static size of some sort

        # there are 6 bytes preceeding is 8 bytes 
        offset = characters_offset
        chars = []

        # print(hex(offset)) # some of these values may be relative offsets??
        
        # Characters
        for i in range(character_count):
            char = Character.from_buffer_copy(buffer, offset)
            offset += sizeof(Character)
            chars.append(char)

        # Glyphs
        glyphs = []
        for i in range(character_count):
            glyph = Glyph.from_buffer_copy(buffer, offset)
            offset += sizeof(Glyph)
            glyphs.append(glyph)
        
        # print(hex(offset))

if __name__ == '__main__':
    # TODO: run through a dump of the main font data

    import os
    from pathlib import Path
    for root, dirs, files in os.walk('/home/colinb/Desktop/Blitzkrieg 2/texts/Bin/Fonts/'):
        for file in files:
            path = Path(root) / file
            # print('*' * 20)
            # print(path)
            # print('*' * 20)
            dumptxtbin(path)

    dumptxtbin('./Output/Bin/Fonts/0E16E454-C6F2-4BE0-A290-BCB0A7D9640C')