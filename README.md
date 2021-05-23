# Window-blinds-control

## Quick description

I started this project to build something what will remotely close generic swedish blinds in one of my living room windows. 
It was annoying for me to get up from my laptop, and walk over to the window, every time when sun came out.

##Project utilizes:
- Raspberry Pi Zero
- Nema 17 stepper motor
- A4988 stepper motor driver
- Mini DC-DC 12-24V To 5V 3A Step Down Power Supply
- AZDelivery 3 x KY-024 Magnetic Hall Sensor Module
- ADS1115 ADC 16bit 4-Channel Module
- 12V 1A DC Power Supply
- Mini magnet 
- 3x resistors 
- 1x 100 mF capacitor
- 4x simple buttons

## Features:
- I can connect to Raspberry through bluetooth and control blinds thanks to bluedot library
- There are 2 buttons connected to Raspberry Pi 3 sitting on my desk, which let me control blinds too. After button being pressed, RP3 sends UDP packets on WiFi to RPZ's address
- There are 2 buttons connected directly to RPZ which open and close blinds
- Blinds automatically open at 6:05 in the morning and close at 21:00.