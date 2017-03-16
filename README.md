# nRF24 Playset

The nRF24 Playset is a collection of software tools for wireless input
devices like keyboards, mice, and presenters based on Nordic Semiconductor 
nRF24 transceivers, e.g. nRF24LE1 and nRF24LU1+.

All software tools support USB dongles 
[nrf-research-firme](https://github.com/BastilleResearch/nrf-research-firmware)
by the Bastille Threat Research Team (many thanks to @marcnewlin)
 

## Requirements

- nRF24LU1+ USB radio dongle with flashed [nrf-research-firmware](https://github.com/BastilleResearch/nrf-research-firmware) by the Bastille Threat Research Team, e. g.
	* [Bitcraze CrazyRadio PA USB dongle](https://www.bitcraze.io/crazyradio-pa/)
	* Logitech Unifying dongle (model C-U0007, Nordic Semiconductor based)
- Python2
- PyUSB
- PyGame for GUI-based tools


## Tools


### cherry_attack.py

Proof-of-concept software tool to demonstrate the replay and keystroke injection
vulnerabilities of the wireless keyboard Cherry B.Unlimited AES

![Cherry Attack PoC](https://github.com/SySS-Research/nrf24-playset/blob/master/images/cherry_attack_poc.png)


### keystroke_injector.py

Proof-of-concept software tool to demonstrate the keystroke injection
vulnerability of some AES encrypted wireless keyboards

Usage:

```
# python2 keystroke_injector.py --help
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
# python2 logitech_presenter.py --help
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
# python2 radioactivemouse.py --help
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
# python2 simple_replay.py --help
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
