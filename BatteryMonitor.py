#!/usr/bin/env python3

import sys, time
from daemon import config, LogginSystem, Daemon
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

class BatteryMonitor(Daemon):
        def run(self):
                
                #fix this - most liekly implent a python config file allowing for logic - will also fix the voltages dict issue

                if 'methods' not in config.keys():
                        config['methods'] = {'shutdown':self.shutdown, 'monitor':self.display_icon() } 
		
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

                self.logger = logfile
                self.get_buttons()

                while True:
                            self.battery_percent()
                            for buttontype, buttons in self.buttons.items():
                                    for button in buttons:
                                            if button[1].hold_time != 1:
                                                    button[1].when_held = config['methods'][buttontype]
                                            else:
                                                    if button[2]:
                                                            button[1].when_pressed = config['methods'][buttontype](toggle = True)
                                                    else:
                                                            button[1].when_pressed = config['methods'][buttontype](toggle =False 

                            
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
                        button_name = '{}_{}'.format(buttontype, i) 
                        button_pin, button_hold, button_toggle = buttonattributes
                        if button_type not in self.buttons.keys():
                                self.buttons[button_type] = list()
                                if button_toggle:
                                        button_togglestate = False
                                        self.buttons[button_type].append(tuple([buttonname, Button(buttonpin, hold_time=buttonhold), button_togglestate]))
                                else:
                                        self.buttons[button_type].append(tuple([buttonname, Button(buttonpin, hold_time=buttonhold)]))

                        else:
                                if button_toggle:
                                        button_togglestate = False
                                        self.buttons[button_type].append(tuple([buttonname, Button(buttonpin, hold_time=buttonhold), button_togglestate]))
                                else:
                                        self.buttons[button_type].append(tuple([buttonname, Button(buttonpin, hold_time=buttonhold)]))



                            
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

        def do_button(self, button):
                try:
                        button_name, button, button_togglestate, button_method = button
                except:
                        button_name, button button_method = button
                        button_togglestate = None

                if button_togglestate not is None:
                        #toggle
                        if button_togglestate:
                                #turn off
                                display_icon(button_togglestate)
                        else:
                                #turn on
                                display_icon(button_togglestate)

                else:
                        #no toggle


        def display_icon(self, runing):
                self.logger.write('display_icon')
                if not self.percent:
                        self.percent = battery_percent
                command = '{}/pngview -b 0 -l 3000{} -x {} -y {} {}/battery{}.png &'.format(config['png']['path'], self.percent, 
                                                                                            config['png']['x'],config['png']['y'],
                                                                                            config['png']['icon'], self.percent)
                if toggle:
                        subprocess_call = subprocess.Popen(shlex.split(command)).communicate()  
                else:
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
                if self.combo:
                        
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
