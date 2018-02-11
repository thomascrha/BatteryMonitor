#!/usr/bin/env python3

import sys, time
from daemon import config, LogginSystem, Daemon, threaded
import yaml
import argparse
import datetime
from gpiozero import Button
from gpiozero.pins.rpigpio import RPiGPIOPin
import os
import subprocess
import Adafruit_ADS1x15
import shlex
import psutil
import keyboard
'''
percentage:
        100%: 4.09  # 4.09
        75%: 3.68   # 3.76
        50%: 3.46   # 3.63
        25%: 3.35    # 3.5
        0%: 3.25     # 3.2
voltage:
        4.09: 100 # 4.09
        3.68: 75  # 3.76
        3.46: 50  # 3.63
        3.35: 25 # 3.5
        3.25: 0  # 3.2
'''

'''

import keyboard

keyboard.press_and_release('shift+s, space')

keyboard.write('The quick brown fox jumps over the lazy dog.')

# Press PAGE UP then PAGE DOWN to type "foobar".
keyboard.add_hotkey('page up, page down', lambda: keyboard.write('foobar'))

# Blocks until you press esc.
keyboard.wait('esc')

# Record events until 'esc' is pressed.
recorded = keyboard.record(until='esc')
# Then replay back at three times the speed.
keyboard.play(recorded, speed_factor=3)

# Type @@ then press space to replace with abbreviation.
keyboard.add_abbreviation('@@', 'my.long.email@example.com')
# Block forever.
keyboard.wait()

'''
def arguments_reader():

        parser = argparse.ArgumentParser(description='battery-monitor runner')
        parser.add_argument('operation',
                metavar='OPERATION',
                type=str,
                help='Operation with BatteryMonitor agent. Accepts any of these values: start, stop, restart, status',
                choices=['start', 'stop', 'restart', 'status'])
        args = parser.parse_args()
        operation = args.operation
        return operation
logfile = open('./battery-monitor.log', 'a+')                



#_KEYS = {'space':Key.space, 'enter': Key.enter, 
#                        'up' :Key.up, 'down': Key.down, 'left':Key.left,
#                        'right': Key.right, 'esc':Key.escape} 

class BatteryMonitor(Daemon):
        def press_key(self, key):
                if len(key) > 1:
                        self.keyboard.press(_KEYS[key])
                        self.keyboard.release(key)
                        return
                         
                self.keyboard.press(key)
                self.keyboard.release(key)
    
        def run(self):
                
                #fix this - most liekly implent a python config file allowing for logic - will also fix the voltages dict issue

                if 'methods' not in config.keys():
                        config['methods'] = {'shutdown':self.shutdown, 'monitor':self.display_icon } 
		
                if config['ads']['ADS1015']:
                        if config['ads']['ADS1115']:
                                print('unable to set up ADS - please have one value true on value false')

                                sys.exit(0)
                        self.ads = Adafruit_ADS1x15.ADS1015()
                elif config['ads']['ADS1115']:
                        if config['ads']['ADS1015']:
                                print('unable to set up ADS - please have one value true on value false')

                                sys.exit(0)
                        self.ads = Adafruit_ADS1x15.ADS1115()
                else:
                        print('unable to set up ADS - please have one value true on value false')
                        sys.exit(0)
                #self.keyboard = Controller()
                self.logger = logfile
                self.get_buttons()
                self.get_controller()
                self.check_controller()
                self.check_button()
                                           
        def get_controller(self):
                self.controller = dict()
                for control_name, control_attributes in config['controller'].items():
                        control_pin, control_keypress = control_attributes
                        self.controller[control_name] = tuple([Button(control_pin), control_keypress]) 
        
        @threaded
        def check_button(self):
                 while True:
                            self.battery_percent()
                            for buttontype, buttons in self.buttons.items():
                                    for button in buttons:
                                            if button[1].hold_time != 1:
                                                    button[1].when_held = config['methods'][buttontype]
                                            else:
                                                    button[1].when_pressed = config['methods'][buttontype]

        @threaded
        def check_controller(self):
                control_names = self.controller.keys()
                while True:
                        for control_name, control_attributes in self.controller.items():
                                control_button, control_keypress = control_attributes
                                control_button.when_pressed = keyboard.write(control_keypress)#press_key(control_keypress) 
                                       

        def process_spawner(self, subprocess_call):

                self.pngprocess = psutil.Process(subprocess_call.pid)
                try:
                        self.pngprocess.wait(timeout=3.0)
                except psutil.TimeoutExpired:
                        self.pngprocess.kill()
                        self.pngprocess = None
                        pass #raise
       
        def get_buttons(self):
                # shutdown_btn = Button(int(config['button']['shutdown']))#, hold_time=1)
                #monitor_btn = Button(int(config['button']['monitor'])) #, hold_time=2)

                self.buttons = dict()
                for i, ( buttontype, buttonattributes ) in enumerate(config['button'].items()):
                        buttonname = '{}_{}'.format(buttontype, i) 
                        buttonpin, buttonhold = buttonattributes
                        if buttontype not in self.buttons.keys():
                                self.buttons[buttontype] = list()
                                self.buttons[buttontype].append(tuple([buttonname, Button(buttonpin, hold_time=buttonhold)]))
                        else:
                                self.buttons[buttontype].append(tuple([buttonname, Button(buttonpin, hold_time=buttonhold)]))

                            
        def read_battery_voltage(self):
                total = 0.0
                loops = 0.0
                start = time.time()
                while (time.time() - start) <= config['votage_reading']['seconds']:
                        # Read the last ADC conversion value and print it out.
                        try:
				value = self.ads.read_adc(0, gain=config['gain'])
			except IOError: 
                                print 'ADS IC2 appears not to be working'
				return None
						
                        total += float(value)
                        loops += 1.0
                        time.sleep(config['votage_reading']['sleep'])

                value = total/loops

                return round(value, 2)
        def display_icon(self):
                
                self.logger.write('display_icon')
                if not self.percent:
                        self.percent = battery_percent
                command = '{}/pngview -b 0 -l 3000{} -x {} -y {} {}/battery{}.png &'.format(config['png']['path'], self.percent, 
                                                                                            config['png']['x'],config['png']['y'],
                                                                                            config['png']['icon'], self.percent)
                subprocess_call = subprocess.Popen(shlex.split(command))
                self.process_spawner(subprocess_call)
                if self.pngprocess:
                        self.pngprocess.kill()                 
    
        def battery_percent(self):
                raw_voltage = self.read_battery_voltage()
                self.logger.write('Raw Votage ' + str(raw_voltage)+ '\n')
		if raw_voltage:
                	self.voltage = round(raw_voltage * config['converstion-ratio'], 2)
                        self.logger.write('Votage ' + str(self.voltage) + '\n')
                        for key in config['voltages']:
                                if not self.voltage:
                                        self.voltage = round(raw_voltage * config['converstion-ratio'], 2)
                                        self.logger.write('Votage ' + str(self.voltage) + '\n')
         
                                if self.voltage in key:
                                        self.percent = config['voltages'][key] 
                                        break
                                self.percent = None 

		else:   
                        #add new state for non configured : create icon
			self.percent = 100
                        self.voltage = 4.1
                                #display appropriate icon.

        def shutdown(self):
                command = 'shutdown -h now'
                #print(command)
                subprocess.Popen(shlex.split(command))

        def restart(self):
                
                command = 'reboot'
                #print(command)
                subprocess.Popen(shlex.split(command))
                
        def reset(self):
                command = 'pkill retroarch & retroarch'
                #print(command)
                subprocess.Popen(shlex.split(command))
                
if __name__ == "__main__":

        action = arguments_reader()
        daemon = BatteryMonitor()

        if action == 'start':
                print("Starting BatteryMonitor agent")
                daemon.start()
                pid = daemon.get_pid()
                if not pid:
                        print("Unable run BatteryMonitor agent")
                else:
                        print("BatteryMonitor agent is running")

        elif action == 'stop':
                print("Stoping BatteryMonitor agent")
                daemon.stop()

        elif action == 'restart':
                print("Restarting BatteryMonitor agent")
                daemon.restart()

        elif action == 'status':
                print("Viewing BatteryMonitor agent status")
                pid = daemon.get_pid()

                if not pid:
                        print("BatteryMonitor agent isn't running")
                else:
                        print("BatteryMonitor agent is running")

        sys.exit(0)
