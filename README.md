# python3 compatible nRF24 Playset

The nRF24 Playset is a collection of software tools for wireless input
devices like keyboards, mice, and presenters based on Nordic Semiconductor 
nRF24 transceivers, e.g. nRF24LE1 and nRF24LU1+.

All software tools support USB dongles with the
[nrf-research-firmware](https://github.com/BastilleResearch/nrf-research-firmware)
by the Bastille Threat Research Team (many thanks to @marcnewlin)


## Migration from Python 2 to Python 3

This project has been migrated from Python 2 to Python 3. The codebase has been thoroughly updated to take advantage of Python 3's features, syntax improvements, and enhanced libraries. Users should ensure that they are using a Python 3.x interpreter to run the script. Compatibility with Python 2 is no longer supported, and users are encouraged to upgrade their environments accordingly.
 

## Requirements

- nRF24LU1+ USB radio dongle with flashed python3 compatible [nrf-research-firmware](https://github.com/Einstein2150/nrf-research-firmware) 
	* [Bitcraze CrazyRadio PA USB dongle](https://www.bitcraze.io/crazyradio-pa/)
	* Logitech Unifying dongle (model C-U0007, Nordic Semiconductor based)
- Python3
- PyUSB
- PyGame for GUI-based tools


## Tools


### cherry_attack.py v.1.1 by Einstein2150

Proof-of-concept software tool to demonstrate the replay and keystroke injection
vulnerabilities of the wireless keyboard Cherry B.Unlimited AES

#### New commandline Features

The `-key` parameter specifies the cryptographic key used for the Cherry keyboard. It must be provided in a hex format (16 bytes) without spaces or special characters

The `-adr` parameter specifies the device address of the Cherry keyboard. This address must also be in hex format (5 bytes) and formatted similarly to the key, with pairs of hexadecimal digits separated by colons (e.g., 00:11:22:33:44).

The `-p` or `--payload` parameter allows users to pass a custom payload that will be used during the attack. This gives users more flexibility when conducting their tests and attacks.

The new `-x` or `--execute` option allows users to execute an attack immediately without using the application's user interface. When both the `-p` (payload) and `-x` options are provided at startup, the attack is executed with the supplied payload right away.

**Example:**

```
bash
python cherry_attack.py -key 1234567890123456789012 -adr 00:11:22:33:44 -p "Your custom payload" -x
```

#### New insights in cherrys encryption

During testing with the extensions, I [@Einstein2150](https://github.com/Einstein2150) also noticed that multiple valid keys for keystroke injection can be concurrently valid at the same time. With the enhanced debugging output, the keys along with their corresponding device MAC addresses are documented as entries in the log. Feel free to collect as many working keys for your device as you can.


### keystroke_injector.py

Proof-of-concept software tool to demonstrate the keystroke injection
vulnerability of some AES encrypted wireless keyboards

Usage:

```
# python3 keystroke_injector.py --help
        _____  ______ ___  _  _     _____  _                      _  
       |  __ \|  ____|__ \| || |   |  __ \| |                    | |     
  _ __ | |__) | |__     ) | || |_  | |__) | | __ _ _   _ ___  ___| |_       
 | '_ \|  _  /|  __|   / /|__   _| |  ___/| |/ _` | | | / __|/ _ \ __|    
 | | | | | \ \| |     / /_   | |   | |    | | (_| | |_| \__ \  __/ |_   
 |_| |_|_|  \_\_|    |____|  |_|   |_|    |_|\__,_|\__, |___/\___|\__|
                                                    __/ |             
                                                   |___/              
Keystroke Injector v0.7 by Matthias Deeg - SySS GmbH (c) 2016
usage: keystroke_injector.py [-h] [-a ADDRESS] [-c N [N ...]] -d DEVICE

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        Address of nRF24 device
  -c N [N ...], --channels N [N ...]
                        ShockBurst RF channel
  -d DEVICE, --device DEVICE
                        Target device (supported: cherry, perixx)

```

### logitech_attack.py

Proof-of-concept software tool similar to **cherry_attack.py** to demonstrate
the replay and keystroke injection vulnerabilities of the AES encrypted
wireless desktop set Logitech MK520


## logitech_presenter.py

Proof-of-concept software tool to demonstrate the keystroke injection
vulnerability of nRF24-based Logitech wireless presenters

Usage:

```
# python3 logitech_presenter.py --help
        _____  ______ ___  _  _     _____  _                      _  
       |  __ \|  ____|__ \| || |   |  __ \| |                    | |     
  _ __ | |__) | |__     ) | || |_  | |__) | | __ _ _   _ ___  ___| |_       
 | '_ \|  _  /|  __|   / /|__   _| |  ___/| |/ _` | | | / __|/ _ \ __|    
 | | | | | \ \| |     / /_   | |   | |    | | (_| | |_| \__ \  __/ |_   
 |_| |_|_|  \_\_|    |____|  |_|   |_|    |_|\__,_|\__, |___/\___|\__|
                                                    __/ |             
                                                   |___/              
Logitech Wireless Presenter Attack Tool v1.0 by Matthias Deeg - SySS GmbH (c) 2016
usage: logitech_presenter.py [-h] [-a ADDRESS] [-c N [N ...]]

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        Address of nRF24 device
  -c N [N ...], --channels N [N ...]
                        ShockBurst RF channel

```

## logitech_presenter_gui.py

GUI-based version of the proof-of-concept software tool **logitech_presenter.py**


## radioactivemouse.py

Proof-of-Concept software tool to demonstrate mouse spoofing attacks exploiting
unencrypted and unauthenticated wireless mouse communication

Usage:

```
# python3 radioactivemouse.py --help
        _____  ______ ___  _  _     _____  _                      _  
       |  __ \|  ____|__ \| || |   |  __ \| |                    | |     
  _ __ | |__) | |__     ) | || |_  | |__) | | __ _ _   _ ___  ___| |_       
 | '_ \|  _  /|  __|   / /|__   _| |  ___/| |/ _` | | | / __|/ _ \ __|    
 | | | | | \ \| |     / /_   | |   | |    | | (_| | |_| \__ \  __/ |_   
 |_| |_|_|  \_\_|    |____|  |_|   |_|    |_|\__,_|\__, |___/\___|\__|
                                                    __/ |             
                                                   |___/              
Radioactive Mouse v0.8 by Matthias Deeg - SySS GmbH (c) 2016
usage: radioactivemouse.py [-h] -a ADDRESS -c CHANNEL -d DEVICE -x ATTACK

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        Address of nRF24 device
  -c CHANNEL, --channel CHANNEL
                        ShockBurst RF channel
  -d DEVICE, --device DEVICE
                        Target device (supported: microsoft, cherry)
  -x ATTACK, --attack ATTACK
                        Attack vector (available: win7_german)

```

A demo video illustrating a mouse spoofing attack is available on YouTube:
[Radioactive Mouse States the Obvious](https://www.youtube.com/watch?v=PkR8EODee44)

![Radioactive Mouse States the Obvious PoC Screeshot](https://github.com/SySS-Research/nrf24-playset/blob/master/images/radioactive_mouse_poc1.png)

![Radioactive Mouse States the Obvious PoC Screeshot](https://github.com/SySS-Research/nrf24-playset/blob/master/images/radioactive_mouse_poc2.png)


## simple_replay.py

Proof-of-Concept software tool to demonstrate replay vulnerabilities of
different wireless desktop sets using nRF24 ShockBurst radio communication

Usage:

```
# python3 simple_replay.py --help
        _____  ______ ___  _  _     _____  _                      _  
       |  __ \|  ____|__ \| || |   |  __ \| |                    | |     
  _ __ | |__) | |__     ) | || |_  | |__) | | __ _ _   _ ___  ___| |_       
 | '_ \|  _  /|  __|   / /|__   _| |  ___/| |/ _` | | | / __|/ _ \ __|    
 | | | | | \ \| |     / /_   | |   | |    | | (_| | |_| \__ \  __/ |_   
 |_| |_|_|  \_\_|    |____|  |_|   |_|    |_|\__,_|\__, |___/\___|\__|
                                                    __/ |             
                                                   |___/              
Simple Replay Tool v0.2 by Matthias Deeg - SySS GmbH (c) 2016
usage: simple_replay.py [-h] [-a ADDRESS] [-c N [N ...]]

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        Address of nRF24 device
  -c N [N ...], --channels N [N ...]
                        ShockBurst RF channel

```

## Disclaimer

Use at your own risk. Do not use without full consent of everyone involved.
For educational purposes only.
