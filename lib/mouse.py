#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
  Mouse library

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

__version__ = '0.8'
__author__ = 'Matthias Deeg'


from struct import pack, unpack

# USB HID mouse buttons
MOUSE_BUTTON_NONE       = 0
MOUSE_BUTTON_LEFT       = 1 << 0
MOUSE_BUTTON_RIGHT      = 1 << 1
MOUSE_BUTTON_MIDDLE     = 1 << 2
MOUSE_WHEEL_UP          = 1
MOUSE_WHEEL_DOWN        = -1


class CherryMouse:
    """CherryMouse (HID)"""

    def __init__(self):
        """Initialize Cherry mouse"""

        # mouse button state
        self.left_button = False
        self.middle_button = False
        self.right_button = False


    def move(self, x = 0, y = 0, wheel = 0, button = MOUSE_BUTTON_NONE):
        """Move the mouse"""

        if x > 127:
            x = 127
        elif x < -127:
            x = -127

        if y > 127:
            y = 127
        elif y < -127:
            y = -127

        data = pack("5b", 0x01, button, x, y, wheel)

        return data


    def click(self, button):
        """Click a mouse button"""

        return self.move(0, 0, 0, button)


class MicrosoftMouse:
    """MicrosoftMouse"""

    def __init__(self):
        """Initialize Microsoft mouse"""

        # mouse button state
        self.left_button = False
        self.middle_button = False
        self.right_button = False

        # packet counter
        self.packet_counter = 0


    def checksum(self, data):
        checksum = 0xff

        for b in data:
            checksum ^= ord(b)

        return checksum


    def move(self, x = 0, y = 0, wheel = 0, button = MOUSE_BUTTON_NONE):
        """Move the mouse"""

        if x > 127:
            x = 127
        elif x < -127:
            x = -127

        if y > 127:
            y = 127
        elif y < -127:
            y = -127

        # increase the packet counter
        self.packet_counter += 1

        counter = pack("<h", self.packet_counter)
        mouse_button = pack("b", button)
        x_bytes = pack("<h", x)
        y_bytes = pack("<h", y)
        wheel_bytes = pack("<h", wheel)

        # build mouse move packet
        data = "\x08\x90\x0D\x01" + counter + "\x40\x00" + mouse_button + x_bytes + y_bytes + wheel_bytes + "\x00\x00\x01"

        # calculate checksum
        chksum = pack("B", self.checksum(data))

        return data + chksum


    def click(self, button):
        """Click a mouse button"""

        return self.move(0, 0, 0, button)


class LogitechMouse:
    """LogitechMouse"""

    def __init__(self):
        """Initialize Logitech mouse"""

        # mouse button state
        self.left_button = False
        self.middle_button = False
        self.right_button = False


    def checksum(self, data):
        checksum = 0x100

        for b in data:
            checksum -= ord(b)

        return checksum & 0xff


    def move(self, x = 0, y = 0, wheel = 0, button = MOUSE_BUTTON_NONE):
        """Move the mouse"""

        if x > 127:
            x = 127
        elif x < -127:
            x = -127

        if y > 127:
            y = 127
        elif y < -127:
            y = -127

        mouse_button = pack("b", button)
        x_bytes = pack("<h", x)
        y_bytes = pack("<h", y)
        wheel_bytes = pack("<h", wheel)

        # Logitech uses 12 bit values for x, y and wheel, so we need some
        # ugly hacker style bit operation magic
        x1 = unpack("B", x_bytes[1])[0] & 0xf
        y0 = unpack("B", y_bytes[0])[0] & 0xf

        x_y = pack("B", x1 ^ (y0 << 4))

        # build mouse move packet
        data = "\x00\xC2" + mouse_button + "\x00" + x_bytes[0] + x_y + y_bytes[1] + wheel_bytes

        # calculate checksum
        chksum = pack("B", self.checksum(data))

        return data + chksum


    def click(self, button):
        """Click a mouse button"""

        return self.move(0, 0, 0, button)


class PerixxMouse:
    """PerixxMouse"""

    def __init__(self):
        """Initialize Perixx mouse"""

        # mouse button state
        self.left_button = False
        self.middle_button = False
        self.right_button = False


    def move(self, x = 0, y = 0, wheel = 0, button = MOUSE_BUTTON_NONE):
        """Move the mouse"""

        if x > 127:
            x = 127
        elif x < -127:
            x = -127

        if y > 127:
            y = 127
        elif y < -127:
            y = -127

        x_bytes = pack("<h", x)
        y_bytes = pack("<h", y)

        # Perixx uses 12 bit values for x, y and wheel, so we need some
        # ugly hacker style bit operation magic
        x1 = unpack("B", x_bytes[1])[0] & 0xf
        y0 = unpack("B", y_bytes[0])[0] & 0xf

        x_y = pack("B", x1 ^ (y0 << 4))

        # build mouse move packet
        data = "\x02" + x_bytes[0] + x_y + y_bytes[1] + "\xA9\x10"

        return data


    def click(self, button = MOUSE_BUTTON_NONE, wheel = 0):
        """Click a mouse button"""

        mouse_button = pack("b", button)
        wheel_byte = pack("b", wheel)

        # build mouse click packet
        data = "\x01" + mouse_button + wheel_byte + "\x72\xA9\x10"

        return data

