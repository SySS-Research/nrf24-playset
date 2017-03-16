#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
  Keyboard library

  by Matthias Deeg <matthias.deeg@syss.de> and
  Gerhard Klostermeier <gerhard.klostermeier@syss.de>

  Copyright (c) 2016 SySS GmbH

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from struct import pack

# USB HID keyboard modifier
MODIFIER_NONE           = 0
MODIFIER_CONTROL_LEFT   = 1 << 0
MODIFIER_SHIFT_LEFT     = 1 << 1
MODIFIER_ALT_LEFT       = 1 << 2
MODIFIER_GUI_LEFT       = 1 << 3
MODIFIER_CONTROL_RIGHT  = 1 << 4
MODIFIER_SHIFT_RIGHT    = 1 << 5
MODIFIER_ALT_RIGHT      = 1 << 6
MODIFIER_GUI_RIGHT      = 1 << 7

# USB HID key codes
KEY_NONE                = 0x00
KEY_A                   = 0x04
KEY_B                   = 0x05
KEY_C                   = 0x06
KEY_D                   = 0x07
KEY_E                   = 0x08
KEY_F                   = 0x09
KEY_G                   = 0x0A
KEY_H                   = 0x0B
KEY_I                   = 0x0C
KEY_J                   = 0x0D
KEY_K                   = 0x0E
KEY_L                   = 0x0F
KEY_M                   = 0x10
KEY_N                   = 0x11
KEY_O                   = 0x12
KEY_P                   = 0x13
KEY_Q                   = 0x14
KEY_R                   = 0x15
KEY_S                   = 0x16
KEY_T                   = 0x17
KEY_U                   = 0x18
KEY_V                   = 0x19
KEY_W                   = 0x1A
KEY_X                   = 0x1B
KEY_Y                   = 0x1C
KEY_Z                   = 0x1D
KEY_1                   = 0x1E
KEY_2                   = 0x1F
KEY_3                   = 0x20
KEY_4                   = 0x21
KEY_5                   = 0x22
KEY_6                   = 0x23
KEY_7                   = 0x24
KEY_8                   = 0x25
KEY_9                   = 0x26
KEY_0                   = 0x27
KEY_RETURN              = 0x28
KEY_ESCAPE              = 0x29
KEY_BACKSPACE           = 0x2A
KEY_TAB                 = 0x2B
KEY_SPACE               = 0x2C
KEY_MINUS               = 0x2D
KEY_EQUAL               = 0x2E
KEY_BRACKET_LEFT        = 0x2F
KEY_BRACKET_RIGHT       = 0x30
KEY_BACKSLASH           = 0x31
KEY_EUROPE_1            = 0x32
KEY_SEMICOLON           = 0x33
KEY_APOSTROPHE          = 0x34
KEY_GRAVE               = 0x35
KEY_COMMA               = 0x36
KEY_PERIOD              = 0x37
KEY_SLASH               = 0x38
KEY_CAPS_LOCK           = 0x39
KEY_F1                  = 0x3A
KEY_F2                  = 0x3B
KEY_F3                  = 0x3C
KEY_F4                  = 0x3D
KEY_F5                  = 0x3E
KEY_F6                  = 0x3F
KEY_F7                  = 0x40
KEY_F8                  = 0x41
KEY_F9                  = 0x42
KEY_F10                 = 0x43
KEY_F11                 = 0x44
KEY_F12                 = 0x45
KEY_PRINT_SCREEN        = 0x46
KEY_SCROLL_LOCK         = 0x47
KEY_PAUSE               = 0x48
KEY_INSERT              = 0x49
KEY_HOME                = 0x4A
KEY_PAGE_UP             = 0x4B
KEY_DELETE              = 0x4C
KEY_END                 = 0x4D
KEY_PAGE_DOWN           = 0x4E
KEY_ARROW_RIGHT         = 0x4F
KEY_ARROW_LEFT          = 0x50
KEY_ARROW_DOWN          = 0x51
KEY_ARROW_UP            = 0x52
KEY_NUM_LOCK            = 0x53
KEY_KEYPAD_DIVIDE       = 0x54
KEY_KEYPAD_MULTIPLY     = 0x55
KEY_KEYPAD_SUBTRACT     = 0x56
KEY_KEYPAD_ADD          = 0x57
KEY_KEYPAD_ENTER        = 0x58
KEY_KEYPAD_1            = 0x59
KEY_KEYPAD_2            = 0x5A
KEY_KEYPAD_3            = 0x5B
KEY_KEYPAD_4            = 0x5C
KEY_KEYPAD_5            = 0x5D
KEY_KEYPAD_6            = 0x5E
KEY_KEYPAD_7            = 0x5F
KEY_KEYPAD_8            = 0x60
KEY_KEYPAD_9            = 0x61
KEY_KEYPAD_0            = 0x62
KEY_KEYPAD_DECIMAL      = 0x63
KEY_EUROPE_2            = 0x64
KEY_APPLICATION         = 0x65
KEY_POWER               = 0x66
KEY_KEYPAD_EQUAL        = 0x67
KEY_F13                 = 0x68
KEY_F14                 = 0x69
KEY_F15                 = 0x6A
KEY_CONTROL_LEFT        = 0xE0
KEY_SHIFT_LEFT          = 0xE1
KEY_ALT_LEFT            = 0xE2
KEY_GUI_LEFT            = 0xE3
KEY_CONTROL_RIGHT       = 0xE4
KEY_SHIFT_RIGHT         = 0xE5
KEY_ALT_RIGHT           = 0xE6
KEY_GUI_RIGHT           = 0xE7


# key mapping for printable characters of default German keyboard layout
KEYMAP_GERMAN = {
        ' ' : (MODIFIER_NONE, KEY_SPACE),
        '!' : (MODIFIER_SHIFT_LEFT, KEY_1),
        '"' : (MODIFIER_SHIFT_LEFT, KEY_2),
        '#' : (MODIFIER_NONE, KEY_EUROPE_1),
        '$' : (MODIFIER_SHIFT_LEFT, KEY_4),
        '%' : (MODIFIER_SHIFT_LEFT, KEY_5),
        '&' : (MODIFIER_SHIFT_LEFT, KEY_6),
        '(' : (MODIFIER_SHIFT_LEFT, KEY_8),
        ')' : (MODIFIER_SHIFT_LEFT, KEY_9),
        '*' : (MODIFIER_NONE, KEY_KEYPAD_MULTIPLY),
        '+' : (MODIFIER_NONE, KEY_KEYPAD_ADD),
        ',' : (MODIFIER_NONE, KEY_COMMA),
        '-' : (MODIFIER_NONE, KEY_KEYPAD_SUBTRACT),
        '.' : (MODIFIER_NONE, KEY_PERIOD),
        '/' : (MODIFIER_SHIFT_LEFT, KEY_7),
        '0' : (MODIFIER_NONE, KEY_0),
        '1' : (MODIFIER_NONE, KEY_1),
        '2' : (MODIFIER_NONE, KEY_2),
        '3' : (MODIFIER_NONE, KEY_3),
        '4' : (MODIFIER_NONE, KEY_4),
        '5' : (MODIFIER_NONE, KEY_5),
        '6' : (MODIFIER_NONE, KEY_6),
        '7' : (MODIFIER_NONE, KEY_7),
        '8' : (MODIFIER_NONE, KEY_8),
        '9' : (MODIFIER_NONE, KEY_9),
        ':' : (MODIFIER_SHIFT_LEFT, KEY_PERIOD),
        ';' : (MODIFIER_SHIFT_LEFT, KEY_COMMA),
        '<' : (MODIFIER_NONE, KEY_EUROPE_2),
        '=' : (MODIFIER_SHIFT_LEFT, KEY_0),
        '>' : (MODIFIER_SHIFT_LEFT, KEY_EUROPE_2),
        '?' : (MODIFIER_SHIFT_LEFT, KEY_MINUS),
        '@' : (MODIFIER_ALT_RIGHT, KEY_Q),
        'A' : (MODIFIER_SHIFT_LEFT, KEY_A),
        'B' : (MODIFIER_SHIFT_LEFT, KEY_B),
        'C' : (MODIFIER_SHIFT_LEFT, KEY_C),
        'D' : (MODIFIER_SHIFT_LEFT, KEY_D),
        'E' : (MODIFIER_SHIFT_LEFT, KEY_E),
        'F' : (MODIFIER_SHIFT_LEFT, KEY_F),
        'G' : (MODIFIER_SHIFT_LEFT, KEY_G),
        'H' : (MODIFIER_SHIFT_LEFT, KEY_H),
        'I' : (MODIFIER_SHIFT_LEFT, KEY_I),
        'J' : (MODIFIER_SHIFT_LEFT, KEY_J),
        'K' : (MODIFIER_SHIFT_LEFT, KEY_K),
        'L' : (MODIFIER_SHIFT_LEFT, KEY_L),
        'M' : (MODIFIER_SHIFT_LEFT, KEY_M),
        'N' : (MODIFIER_SHIFT_LEFT, KEY_N),
        'O' : (MODIFIER_SHIFT_LEFT, KEY_O),
        'P' : (MODIFIER_SHIFT_LEFT, KEY_P),
        'Q' : (MODIFIER_SHIFT_LEFT, KEY_Q),
        'R' : (MODIFIER_SHIFT_LEFT, KEY_R),
        'S' : (MODIFIER_SHIFT_LEFT, KEY_S),
        'T' : (MODIFIER_SHIFT_LEFT, KEY_T),
        'U' : (MODIFIER_SHIFT_LEFT, KEY_U),
        'V' : (MODIFIER_SHIFT_LEFT, KEY_V),
        'W' : (MODIFIER_SHIFT_LEFT, KEY_W),
        'X' : (MODIFIER_SHIFT_LEFT, KEY_X),
        'Y' : (MODIFIER_SHIFT_LEFT, KEY_Z),
        'Z' : (MODIFIER_SHIFT_LEFT, KEY_Y),
        '[' : (MODIFIER_ALT_RIGHT, KEY_8),
        '\\' : (MODIFIER_ALT_RIGHT, KEY_MINUS),
        ']' : (MODIFIER_ALT_RIGHT, KEY_9),
        '^' : (MODIFIER_NONE, KEY_GRAVE),
        '_' : (MODIFIER_SHIFT_LEFT, KEY_SLASH),
        '`' : (MODIFIER_SHIFT_LEFT, KEY_EQUAL),
        'a' : (MODIFIER_NONE, KEY_A),
        'b' : (MODIFIER_NONE, KEY_B),
        'c' : (MODIFIER_NONE, KEY_C),
        'd' : (MODIFIER_NONE, KEY_D),
        'e' : (MODIFIER_NONE, KEY_E),
        'f' : (MODIFIER_NONE, KEY_F),
        'g' : (MODIFIER_NONE, KEY_G),
        'h' : (MODIFIER_NONE, KEY_H),
        'i' : (MODIFIER_NONE, KEY_I),
        'j' : (MODIFIER_NONE, KEY_J),
        'k' : (MODIFIER_NONE, KEY_K),
        'l' : (MODIFIER_NONE, KEY_L),
        'm' : (MODIFIER_NONE, KEY_M),
        'n' : (MODIFIER_NONE, KEY_N),
        'o' : (MODIFIER_NONE, KEY_O),
        'p' : (MODIFIER_NONE, KEY_P),
        'q' : (MODIFIER_NONE, KEY_Q),
        'r' : (MODIFIER_NONE, KEY_R),
        's' : (MODIFIER_NONE, KEY_S),
        't' : (MODIFIER_NONE, KEY_T),
        'u' : (MODIFIER_NONE, KEY_U),
        'v' : (MODIFIER_NONE, KEY_V),
        'w' : (MODIFIER_NONE, KEY_W),
        'x' : (MODIFIER_NONE, KEY_X),
        'y' : (MODIFIER_NONE, KEY_Z),
        'z' : (MODIFIER_NONE, KEY_Y),
        '{' : (MODIFIER_ALT_RIGHT, KEY_7),
        '|' : (MODIFIER_ALT_RIGHT, KEY_EUROPE_2),
        '}' : (MODIFIER_ALT_RIGHT, KEY_0),
        '~' : (MODIFIER_ALT_RIGHT, KEY_BRACKET_RIGHT),
        u'\'' : (MODIFIER_SHIFT_LEFT, KEY_EUROPE_1),
        u'Ä' : (MODIFIER_SHIFT_LEFT, KEY_APOSTROPHE),
        u'Ö' : (MODIFIER_SHIFT_LEFT, KEY_SEMICOLON),
        u'Ü' : (MODIFIER_SHIFT_LEFT, KEY_BRACKET_LEFT),
        u'ä' : (MODIFIER_NONE, KEY_APOSTROPHE),
        u'ö' : (MODIFIER_NONE, KEY_SEMICOLON),
        u'ü' : (MODIFIER_NONE, KEY_BRACKET_LEFT),
        u'ß' : (MODIFIER_NONE, KEY_MINUS),
        u'€' : (MODIFIER_ALT_RIGHT, KEY_E)
        }


class CherryKeyboard:
    """CherryKeyboard (HID)"""

    def __init__(self, initData):
        """Initialize Cherry keyboard"""

        # set current keymap
        self.currentKeymap = KEYMAP_GERMAN

        # set AES counter
        self.counter = initData[11:]

        # set crypto key
        self.cryptoKey = initData[:11]


    def keyCommand(self, modifiers, keycode1, keycode2 = KEY_NONE, keycode3 = KEY_NONE,
            keycode4 = KEY_NONE, keycode5 = KEY_NONE, keycode6 = KEY_NONE):
        """Return AES encrypted keyboard data"""

        # generate HID keyboard data
        plaintext = pack("11B", modifiers, 0, keycode1, keycode2, keycode3, keycode4, keycode5, keycode6, 0, 0, 0)

        # encrypt the data with the set crypto key
        ciphertext = ""
        i = 0
        for b in plaintext:
            ciphertext += chr(ord(b) ^ ord(self.cryptoKey[i]))
            i += 1

        return ciphertext + self.counter


    def getKeystroke(self, keycode = KEY_NONE, modifiers = MODIFIER_NONE):
        """Get a keystroke for a given keycode"""
        keystrokes = []

        # key press
        keystrokes.append(self.keyCommand(modifiers, keycode))

        # key release
        keystrokes.append(self.keyCommand(MODIFIER_NONE, KEY_NONE))

        return keystrokes


    def getKeystrokes(self, string):
        """Get stream of keystrokes for a given string of printable ASCII characters"""
        keystrokes = []

        for char in string:
            # key press
            key = self.currentKeymap[char]
            keystrokes.append(self.keyCommand(key[0], key[1]))

            # key release
            keystrokes.append(self.keyCommand(MODIFIER_NONE, KEY_NONE))

        return keystrokes



class PerixxKeyboard:
    """PerixxKeyboard (HID)"""

    def __init__(self, initData):
        """Initialize Perixx keyboard"""

        # set current keymap
        self.currentKeymap = KEYMAP_GERMAN

        # set AES counter
        self.counter = initData[10:]

        # set crypto key
        self.cryptoKey = initData[:10]


    def keyCommand(self, modifiers, keycode1, keycode2 = KEY_NONE, keycode3 = KEY_NONE,
            keycode4 = KEY_NONE, keycode5 = KEY_NONE, keycode6 = KEY_NONE):
        """Return AES encrypted keyboard data"""

        # generate HID keyboard data
        plaintext = pack("10B", modifiers, 0, keycode1, keycode2, keycode3, keycode4, keycode5, keycode6, 0, 0)

        # encrypt the data with the set crypto key
        ciphertext = ""
        i = 0
        for b in plaintext:
            ciphertext += chr(ord(b) ^ ord(self.cryptoKey[i]))
            i += 1

        return ciphertext + self.counter


    def getKeystroke(self, keycode = KEY_NONE, modifiers = MODIFIER_NONE):
        """Get a keystroke for a given keycode"""
        keystrokes = []

        # key press
        keystrokes.append(self.keyCommand(modifiers, keycode))

        # key release
        keystrokes.append(self.keyCommand(MODIFIER_NONE, KEY_NONE))

        return keystrokes


    def getKeystrokes(self, string):
        """Get stream of keystrokes for a given string of printable ASCII characters"""
        keystrokes = []

        for char in string:
            # key press
            key = self.currentKeymap[char]
            keystrokes.append(self.keyCommand(key[0], key[1]))

            # key release
            keystrokes.append(self.keyCommand(MODIFIER_NONE, KEY_NONE))

        return keystrokes


class LogitechKeyboard:
    """Logitech Keyboard (HID)"""

    def __init__(self, initData):
        """Initialize Logitech keyboard"""

        # set current keymap
        self.currentKeymap = KEYMAP_GERMAN

        # set crypto key
        self.cryptoKey = initData[2:14]

        # Logitech packet after key release packet
        self.KEYUP = "\x00\x4F\x00\x01\x16\x00\x00\x00\x00\x9A"


    def checksum(self, data):
        checksum = 0

        for b in data:
            checksum -= ord(b)

        return pack("B", (checksum & 0xff))


    def keyCommand(self, modifiers, keycode1, keycode2 = KEY_NONE, keycode3 = KEY_NONE,
            keycode4 = KEY_NONE, keycode5 = KEY_NONE, keycode6 = KEY_NONE):
        """Return AES encrypted keyboard data"""

        # generate HID keyboard data plaintext
        plaintext = pack("12B", modifiers, 0, keycode1, keycode2, keycode3, keycode4, keycode5, keycode6, 0, 0, 0, 0)

        # encrypt the data with the set crypto key
        ciphertext = ""

        i = 0
        for b in plaintext:
            ciphertext += chr(ord(b) ^ ord(self.cryptoKey[i]))
            i += 1

        # generate Logitech Unifying paket
        data = "\x00\xD3" + ciphertext + 7 * "\x00"

        checksum = self.checksum(data)

        return data + checksum


    def getKeystroke(self, keycode = KEY_NONE, modifiers = MODIFIER_NONE):
        """Get a keystroke for a given keycode"""
        keystrokes = []

        # key press
        keystrokes.append(self.keyCommand(modifiers, keycode))

        # key release
        keystrokes.append(self.keyCommand(MODIFIER_NONE, KEY_NONE))
        keystrokes.append(self.KEYUP)

        return keystrokes


    def getKeystrokes(self, string):
        """Get stream of keystrokes for a given string of printable ASCII characters"""
        keystrokes = []

        for char in string:
            # key press
            key = self.currentKeymap[char]
            keystrokes.append(self.keyCommand(key[0], key[1]))

            # key release
            keystrokes.append(self.keyCommand(MODIFIER_NONE, KEY_NONE))
            keystrokes.append(self.KEYUP)

        return keystrokes


class LogitechPresenter:
    """Logitech Presenter (HID)"""


    def __init__(self):
        """Initialize Logitech Presenter keyboard"""

        # set current keymap
        self.currentKeymap = KEYMAP_GERMAN

        # magic packet sent after data packets
        self.magic_packet = "\x00\x4F\x00\x00\x55\x00\x00\x00\x00\x5C"


    def checksum(self, data):
        checksum = 0

        for b in data:
            checksum -= ord(b)

        return pack("B", (checksum & 0xff))


    def keyCommand(self, modifiers, keycode1, keycode2 = KEY_NONE, keycode3 = KEY_NONE,
            keycode4 = KEY_NONE, keycode5 = KEY_NONE, keycode6 = KEY_NONE):
        """Return keyboard data"""


        # generate HID keyboard data
        data = pack("9B", 0, 0xC1, modifiers, keycode1, keycode2, keycode3, keycode4, keycode5, keycode6)

        checksum = self.checksum(data)

        return data + checksum


    def getKeystroke(self, keycode = KEY_NONE, modifiers = MODIFIER_NONE):
        """Get a keystroke for a given keycode"""
        keystrokes = []

        # key press
        keystrokes.append(self.keyCommand(modifiers, keycode))

        # magic packet
        keystrokes.append(self.magic_packet)

        # key release
        keystrokes.append(self.keyCommand(MODIFIER_NONE, KEY_NONE))

        # magic packet
        keystrokes.append(self.magic_packet)


        return keystrokes


    def getKeystrokes(self, string):
        """Get stream of keystrokes for a given string of printable ASCII characters"""
        keystrokes = []

        for char in string:
            # key press
            key = self.currentKeymap[char]
            keystrokes.append(self.keyCommand(key[0], key[1]))

            # magic packet
            keystrokes.append(self.magic_packet)

            # key release
            keystrokes.append(self.keyCommand(MODIFIER_NONE, KEY_NONE))

            # magic packet
            keystrokes.append(self.magic_packet)

        return keystrokes

