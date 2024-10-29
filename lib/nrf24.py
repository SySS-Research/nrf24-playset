#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Copyright (C) 2016 Bastille Networks

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
  
   
  Einstein2150 (Update 2024):
  This program has been migrated and further developed for use with
  Python 3 by Einstein2150. The author acknowledges that ongoing
  enhancements and updates to the codebase may continue in the future.
  Users should be aware that the use of this program is at their own
  risk, and the author accepts no responsibility for any damages that
  may arise from its use. It is the user's responsibility to ensure 
  that their use of the program complies with all applicable laws 
  and regulations.
  
  

"""

import usb
import logging
import sys

# Check pyusb dependency
try:
    from usb import core as _usb_core
except ImportError as ex:
    print('''
------------------------------------------
| PyUSB was not found or is out of date. |
------------------------------------------

Please update PyUSB using pip:

sudo pip install -U -I pip && sudo pip install -U -I pyusb
''')
    sys.exit(1)

# USB commands
TRANSMIT_PAYLOAD               = 0x04
ENTER_SNIFFER_MODE             = 0x05
ENTER_PROMISCUOUS_MODE         = 0x06
ENTER_TONE_TEST_MODE           = 0x07
TRANSMIT_ACK_PAYLOAD           = 0x08
SET_CHANNEL                    = 0x09
GET_CHANNEL                    = 0x0A
ENABLE_LNA_PA                  = 0x0B
TRANSMIT_PAYLOAD_GENERIC       = 0x0C
ENTER_PROMISCUOUS_MODE_GENERIC = 0x0D
RECEIVE_PAYLOAD                = 0x12

# RF data rates
RF_RATE_250K = 0
RF_RATE_1M   = 1
RF_RATE_2M   = 2

# nRF24LU1+ radio dongle
class nrf24:

    usb_timeout = 2500  # Sufficiently long timeout for use in a VM

    def __init__(self, index=0):
        try:
            self.dongle = list(usb.core.find(idVendor=0x1915, idProduct=0x0102, find_all=True))[index]
            self.dongle.set_configuration()
        except usb.core.USBError as ex:
            raise ex
        except Exception:
            raise Exception('Cannot find USB dongle.')

    # Put the radio in pseudo-promiscuous mode
    def enter_promiscuous_mode(self, prefix=[]):
        self.send_usb_command(ENTER_PROMISCUOUS_MODE, [len(prefix)] + list(prefix))
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
        logging.debug(f'Entered promiscuous mode with address prefix {":".join("{:02X}".format(b) for b in prefix)}')

    # Put the radio in pseudo-promiscuous mode without CRC checking
    def enter_promiscuous_mode_generic(self, prefix=[], rate=RF_RATE_2M, payload_length=32):
        self.send_usb_command(ENTER_PROMISCUOUS_MODE_GENERIC, [len(prefix), rate, payload_length] + list(prefix))
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
        logging.debug(f'Entered generic promiscuous mode with address prefix {":".join("{:02X}".format(b) for b in prefix)}')

    # Put the radio in ESB "sniffer" mode (ESB mode w/o auto-acking)
    def enter_sniffer_mode(self, address):
        if isinstance(address, str):
            address = address.encode()
        self.send_usb_command(ENTER_SNIFFER_MODE, [len(address)] + list(address))
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
        logging.debug(f'Entered sniffer mode with address {":".join("{:02X}".format(b) for b in address[::-1])}')

    # Put the radio into continuous tone (TX) test mode
    def enter_tone_test_mode(self):
        self.send_usb_command(ENTER_TONE_TEST_MODE, [])
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
        logging.debug('Entered continuous tone test mode')

    # Receive a payload if one is available
    def receive_payload(self):
        self.send_usb_command(RECEIVE_PAYLOAD, [])
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)

    # Transmit a generic (non-ESB) payload
    def transmit_payload_generic(self, payload, address=b"\x33\x33\x33\x33\x33"):
        data = [len(payload), len(address)] + list(payload) + list(address)
        self.send_usb_command(TRANSMIT_PAYLOAD_GENERIC, data)
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)[0] > 0

    # Transmit an ESB payload
    def transmit_payload(self, payload, timeout=4, retransmits=15):
        data = [len(payload), timeout, retransmits] + list(payload)
        self.send_usb_command(TRANSMIT_PAYLOAD, data)
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)[0] > 0

    # Transmit an ESB ACK payload
    def transmit_ack_payload(self, payload):
        data = [len(payload)] + list(payload)
        self.send_usb_command(TRANSMIT_ACK_PAYLOAD, data)
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)[0] > 0

    # Set the RF channel
    def set_channel(self, channel):
        channel = min(channel, 125)
        self.send_usb_command(SET_CHANNEL, [channel])
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
        logging.debug(f'Tuned to {channel}')

    # Get the current RF channel
    def get_channel(self):
        self.send_usb_command(GET_CHANNEL, [])
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)

    # Enable the LNA (CrazyRadio PA)
    def enable_lna(self):
        self.send_usb_command(ENABLE_LNA_PA, [])
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)

    # Send a USB command
    def send_usb_command(self, request, data):
        data = [request] + list(data)
        self.dongle.write(0x01, data, timeout=nrf24.usb_timeout)
