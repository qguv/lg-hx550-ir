#!/usr/bin/env python3

from enum import IntEnum


class Protocol(IntEnum):
    SIRC = 0x01
    Samsung32 = 0x2c

stateless = {
    (Protocol.Samsung32, 0xf8): 'Power on',
    (Protocol.Samsung32, 0xf9): 'Power off',
    (Protocol.Samsung32, 0xb8): 'HDMI 1',
    (Protocol.Samsung32, 0xb9): 'iPod',
    (Protocol.Samsung32, 0xf6): 'FM radio',
}

remote = {
    (Protocol.Samsung32, 0x1e): 'Power',
    (Protocol.Samsung32, 0x9a): 'Eject',
    (Protocol.Samsung32, 0x8a): 'Input, Function',

    (Protocol.Samsung32, 0x41): '1',
    (Protocol.Samsung32, 0x42): '2',
    (Protocol.Samsung32, 0x43): '3',

    (Protocol.Samsung32, 0x44): '4',
    (Protocol.Samsung32, 0x45): '5',
    (Protocol.Samsung32, 0x46): '6',

    (Protocol.Samsung32, 0x47): '7',
    (Protocol.Samsung32, 0x48): '8',
    (Protocol.Samsung32, 0x49): '9',

    (Protocol.Samsung32, 0xb0): 'Clear',
    (Protocol.Samsung32, 0x4b): '0',
    (Protocol.Samsung32, 0x4e): 'Repeat',

    (Protocol.Samsung32, 0x06): 'Previous',
    (Protocol.Samsung32, 0x53): 'Rewind',
    (Protocol.Samsung32, 0x52): 'Fast forward',
    (Protocol.Samsung32, 0x07): 'Next',

    (Protocol.Samsung32, 0x05): 'Stop',
    (Protocol.Samsung32, 0x04): 'Play',
    (Protocol.Samsung32, 0x4f): 'Pause',

    (Protocol.Samsung32, 0x66): 'Speaker level',
    (Protocol.Samsung32, 0x17): 'Volume up',
    (Protocol.Samsung32, 0xb6): 'Optical',

    (Protocol.Samsung32, 0x2f): 'Sound effect',
    (Protocol.Samsung32, 0x16): 'Volume down',
    (Protocol.Samsung32, 0x1f): 'Mute',

    (Protocol.Samsung32, 0xa5): 'Home',
    (Protocol.Samsung32, 0x90): '3D sound',
    (Protocol.Samsung32, 0xa3): 'Info/menu',

    (Protocol.Samsung32, 0xa7): 'Up, Preset +',

    (Protocol.Samsung32, 0xa8): 'Left, Tuning -',
    (Protocol.Samsung32, 0xaa): 'Enter',
    (Protocol.Samsung32, 0xa9): 'Right, Tuning +',

    (Protocol.Samsung32, 0xa6): 'Down, Preset -',

    (Protocol.Samsung32, 0xa2): 'Back',
    (Protocol.Samsung32, 0xaf): 'Title/pop up',
    (Protocol.Samsung32, 0xa4): 'Disc menu',

    (Protocol.Samsung32, 0x6c): 'Red, RDS',
    (Protocol.Samsung32, 0x6d): 'Green, PTY',
    (Protocol.Samsung32, 0x6e): 'Yellow, PTY search',
    (Protocol.Samsung32, 0x6f): 'Blue, Mono/Stereo',

    (Protocol.Samsung32, 0xab): 'Subtitle',
    (Protocol.Samsung32, 0x36): 'Audio',
    (Protocol.Samsung32, 0xc2): 'Sleep',

    (Protocol.Samsung32, 0xd3): 'Music ID',
    (Protocol.Samsung32, 0x30): '*1',
    (Protocol.Samsung32, 0x83): '*2',

    (Protocol.SIRC, 0x15): 'TV Power',
    (Protocol.SIRC, 0x12): 'TV Volume up',
    (Protocol.SIRC, 0x10): 'TV Channel up',

    (Protocol.SIRC, 0x7c): 'TV AV/Input',
    (Protocol.SIRC, 0x13): 'TV Volume down',
    (Protocol.SIRC, 0x11): 'TV Channel down',
}

debug = {
    (Protocol.Samsung32, 0xea): 'Factory reset',
    (Protocol.Samsung32, 0xf0): 'Debug',
    (Protocol.Samsung32, 0xf1): 'Test SPK',
    (Protocol.Samsung32, 0xf7): 'Display test, power',
}

useless = {
    (Protocol.Samsung32, 0xe1): 'Blank (E1)',
    (Protocol.Samsung32, 0xe2): 'Blank (E2)',
    (Protocol.Samsung32, 0xe3): 'Blank (E3)',
    (Protocol.Samsung32, 0xe4): 'Blank (E4)',
    (Protocol.Samsung32, 0xe5): 'Blank (E5)',
    (Protocol.Samsung32, 0xe6): 'Blank (E6)',
    (Protocol.Samsung32, 0xe7): 'Blank (E7)',
    (Protocol.Samsung32, 0xe8): 'Blank (E8)',
    (Protocol.Samsung32, 0xe9): 'Blank (E9)',

    # receiver lights up, but nothing happens
    (Protocol.Samsung32, 0xfa): 'noop (FA)',
    (Protocol.Samsung32, 0xfb): 'noop (FB)',
    (Protocol.Samsung32, 0xfe): 'noop (FE)',

    # unrecognized
    (Protocol.Samsung32, 0xfc): 'dead (FC)',
    (Protocol.Samsung32, 0xfd): 'dead (FD)',
}

known = stateless | remote | debug | useless


def fmt(k, name):
    protocol, command = k
    return f'''\
name: {name}
type: parsed
protocol: {protocol.name}
address: {protocol:02X} 00 00 00
command: {command:02X} 00 00 00
'''


def gen_flipper():
    s = 'Filetype: IR signals file\nVersion: 1\n'
    for k, name in known.items():
        s += fmt(k, name)
    for command in range(0x00, 0xff):
        k = (Protocol.Samsung32, command)
        if k not in known:
            name = f"0x{command:02X}"
            s += fmt(k, name)
    return s


def gen_yaml():
    return '\n'.join(f'- "{name}"' for name in known.values())


def print_unknown():
    for command in range(0x00, 0xff):
        k = (Protocol.Samsung32, command)
        if k not in known:
            print(f'{command:02X} ')


if __name__ == "__main__":
    print(gen_flipper())
