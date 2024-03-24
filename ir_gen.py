#!/usr/bin/env python3

import sys
from enum import IntEnum


class Protocol(IntEnum):
    SIRC = 0x01
    Samsung32 = 0x2c


def fmt(k, name):
    protocol, command = k
    return f'''
name: {name}
type: parsed
protocol: {protocol.name}
address: {protocol:02X} 00 00 00
command: {command:02X} 00 00 00
'''


def gen_flipper(d):
    s = 'Filetype: IR signals file\nVersion: 1\n'
    for k, name in d.items():
        s += fmt(k, name)
    return s


def gen_unknown():
    return '\n'.join(
        f'{command:02X} '
        for command in range(0x00, 0xff)
        if (Protocol.Samsung32, command) not in known
    )


groups = {

    # undocumented buttons that do the same thing regardless of context
    'stateless': {
        (Protocol.Samsung32, 0xf8): 'Power on',
        (Protocol.Samsung32, 0xf9): 'Power off',
        (Protocol.Samsung32, 0xb8): 'HDMI 1',
        (Protocol.Samsung32, 0x85): 'HDMI 2',
        (Protocol.Samsung32, 0x80): 'AUX (RCA)',
        (Protocol.Samsung32, 0x7D): 'Portable (3.5mm)',
        (Protocol.Samsung32, 0x31): 'Optical',
        (Protocol.Samsung32, 0x91): 'ARC',
        (Protocol.Samsung32, 0x3B): 'USB',
        (Protocol.Samsung32, 0xf6): 'FM radio',
        (Protocol.Samsung32, 0xb9): 'iPod',
        (Protocol.Samsung32, 0x94): 'Nat plus',
    },

    # buttons on the remote
    'remote': {

        # row 0
        (Protocol.Samsung32, 0x1e): 'Power',
        (Protocol.Samsung32, 0x9a): 'Eject',
        (Protocol.Samsung32, 0x8a): 'Input, Function',

        # row 1
        (Protocol.Samsung32, 0x41): '1',
        (Protocol.Samsung32, 0x42): '2',
        (Protocol.Samsung32, 0x43): '3',

        # row 2
        (Protocol.Samsung32, 0x44): '4',
        (Protocol.Samsung32, 0x45): '5',
        (Protocol.Samsung32, 0x46): '6',

        # row 3
        (Protocol.Samsung32, 0x47): '7',
        (Protocol.Samsung32, 0x48): '8',
        (Protocol.Samsung32, 0x49): '9',

        # row 4
        (Protocol.Samsung32, 0xb0): 'Clear',
        (Protocol.Samsung32, 0x4b): '0',
        (Protocol.Samsung32, 0x4e): 'Repeat',

        # row 5
        (Protocol.Samsung32, 0x06): 'Previous',
        (Protocol.Samsung32, 0x53): 'Rewind',
        (Protocol.Samsung32, 0x52): 'Fast forward',
        (Protocol.Samsung32, 0x07): 'Next',

        # row 6
        (Protocol.Samsung32, 0x05): 'Stop',
        (Protocol.Samsung32, 0x04): 'Play',
        (Protocol.Samsung32, 0x4f): 'Pause',

        # row 7
        (Protocol.Samsung32, 0x66): 'Speaker level',
        (Protocol.Samsung32, 0x17): 'Volume up',
        (Protocol.Samsung32, 0xb6): 'Optical (toggle)',

        # row 8
        (Protocol.Samsung32, 0x2f): 'Sound effect',
        (Protocol.Samsung32, 0x16): 'Volume down',
        (Protocol.Samsung32, 0x1f): 'Mute',

        # row 9
        (Protocol.Samsung32, 0xa5): 'Home',
        (Protocol.Samsung32, 0x90): '3D sound',
        (Protocol.Samsung32, 0xa3): 'Info/menu',

        # row 10
        (Protocol.Samsung32, 0xa7): 'Up, Preset +',

        # row 11
        (Protocol.Samsung32, 0xa8): 'Left, Tuning -',
        (Protocol.Samsung32, 0xaa): 'Enter',
        (Protocol.Samsung32, 0xa9): 'Right, Tuning +',

        # row 12
        (Protocol.Samsung32, 0xa6): 'Down, Preset -',

        # row 13
        (Protocol.Samsung32, 0xa2): 'Back',
        (Protocol.Samsung32, 0xaf): 'Title/pop up',
        (Protocol.Samsung32, 0xa4): 'Disc menu',

        # row 14
        (Protocol.Samsung32, 0x6c): 'Red, RDS',
        (Protocol.Samsung32, 0x6d): 'Green, PTY',
        (Protocol.Samsung32, 0x6e): 'Yellow, PTY search',
        (Protocol.Samsung32, 0x6f): 'Blue, Mono/Stereo',

        # row 15
        (Protocol.Samsung32, 0xab): 'Subtitle',
        (Protocol.Samsung32, 0x36): 'Audio',
        (Protocol.Samsung32, 0xc2): 'Sleep',

        # row 16
        (Protocol.Samsung32, 0xd3): 'Music ID',
        (Protocol.Samsung32, 0x30): '*1',
        (Protocol.Samsung32, 0x83): '*2',

        # row 17
        (Protocol.SIRC, 0x15): 'TV Power',
        (Protocol.SIRC, 0x12): 'TV Volume up',
        (Protocol.SIRC, 0x10): 'TV Channel up',

        # row 18
        (Protocol.SIRC, 0x7c): 'TV AV/Input',
        (Protocol.SIRC, 0x13): 'TV Volume down',
        (Protocol.SIRC, 0x11): 'TV Channel down',
    },

    # undocumented, slightly different versions of existing buttons
    'alt': {
        (Protocol.Samsung32, 0x35): 'Sound effect (no menu)',
        (Protocol.Samsung32, 0x67): 'Home, Stop',
    },

    # undocumented debug functionality
    'debug': {
        (Protocol.Samsung32, 0xea): 'Factory reset',
        (Protocol.Samsung32, 0xf0): 'Debug',
        (Protocol.Samsung32, 0xf1): 'Test SPK',
        (Protocol.Samsung32, 0xf7): 'Display test, power',
    },

    # undocumented, blanks the screen momentarily, but nothing else happens
    'blank': {(Protocol.Samsung32, c): f'blank ({c:02X})' for c in range(0xe1, 0xea)},

    # receiver lights up, but nothing happens
    'noop': {
        (Protocol.Samsung32, c): f'noop ({c:02X})'
        for c in (
            0x00, 0x03, 0x0B, 0x1D, 0x34, 0x3C, 0x3F, 0x4A,
            0x4D, 0x59, 0x5E, 0x60, 0x61, 0x62, 0x71, 0x74,
            0x79, 0x7A, 0x7E, 0x82, 0x86, 0x8B, 0x8C, 0xA1,
            0xAD, 0xAE, 0xB1, 0xB2, 0xB3, 0xB4, 0xBB, 0xBC,
            0xCF, 0xD4, 0xD5, 0xD6, 0xEB, 0xEC, 0xED, 0xEE,
            0xEF, 0xF2, 0xF3, 0xF4, 0xF5, 0xFA, 0xFB, 0xFE,
        )
    },

    # receiver doesn't light up, nothing happens
    'dead': {
        (Protocol.Samsung32, c): f'noop ({c:02X})'
        for c in (
            0x01, 0x02, 0x08, 0x09, 0x0A, 0x0C, 0x0D, 0x0E,
            0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x18,
            0x19, 0x1A, 0x1B, 0x1C, 0x20, 0x21, 0x22, 0x23,
            0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B,
            0x2C, 0x2D, 0x2E, 0x32, 0x33, 0x37, 0x38, 0x39,
            0x3A, 0x3D, 0x3E, 0x40, 0x4C, 0x50, 0x51, 0x54,
            0x55, 0x56, 0x57, 0x58, 0x5A, 0x5B, 0x5C, 0x5D,
            0x5F, 0x63, 0x64, 0x65, 0x68, 0x69, 0x6A, 0x6B,
            0x70, 0x72, 0x73, 0x75, 0x76, 0x77, 0x78, 0x7B,
            0x7C, 0x7F, 0x81, 0x84, 0x87, 0x88, 0x89, 0x8D,
            0x8E, 0x8F, 0x92, 0x93, 0x95, 0x96, 0x97, 0x98,
            0x99, 0x9B, 0x9C, 0x9D, 0x9E, 0x9F, 0xA0, 0xAC,
            0xB5, 0xB7, 0xBA, 0xBD, 0xBE, 0xBF, 0xC0, 0xC1,
            0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA,
            0xCB, 0xCC, 0xCD, 0xCE, 0xD0, 0xD1, 0xD2, 0xD7,
            0xD8, 0xD9, 0xDA, 0xDB, 0xDC, 0xDD, 0xDE, 0xDF,
            0xE0, 0xFC, 0xFD,
        )
    },
}


if __name__ == "__main__":
    usage = f"Usage: {sys.argv[0]} (useful | extra | stretch)"

    if len(sys.argv) != 2:
        print(usage)
    elif sys.argv[1] == 'useful':
        print(gen_flipper(groups['stateless'] | groups['remote']))
    elif sys.argv[1] == 'extra':
        print(gen_flipper(groups['debug'] | groups['alt']))
    elif sys.argv[1] == 'stretch':
        print(gen_flipper(groups['blank'] | groups['noop']))
    else:
        print(usage)
